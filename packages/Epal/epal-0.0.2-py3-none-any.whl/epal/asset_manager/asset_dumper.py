from . import asset as ass
import io
import ctypes
from typing import TypeVar, Type
import pygame

from ..utils import EpalLogger

import pickle


__logger__ = EpalLogger("AssetDumper")

def generate_header() -> bytearray:
    header = b'EPAL'

    return header

def convert_asset_to_bytes(asset : ass.Asset):
    ret = b''

    if asset.asset_type == ass.AssetType.Image:
        ret += pickle.dumps(pygame.image.tobytes(asset.get(), "RGBA"))

    if asset.asset_type == ass.AssetType.Audio:
        ret += pickle.dumps(asset.get().get_raw())

    return ret

def generate_offset_table(offsets : dict[str, int]) -> bytearray:
    __logger__.log("Generating offset table")
    ret = b''
    for asset in offsets.keys():
        ret += asset.encode()
        ret += b'\0'
        ret += ctypes.c_uint64(offsets[asset]["byteoffset"])
        ret += ctypes.c_uint64(offsets[asset]["len"])
        ret += ctypes.c_uint8(offsets[asset]["type"])

        if offsets[asset]["type"] == 0:
            ret += ctypes.c_uint64(offsets[asset]["size"][0])
            ret += ctypes.c_uint64(offsets[asset]["size"][1])
    
    for asset in offsets.keys():
        offsets[asset]["byteoffset"] += len(ret) + 4

    ret = b''
    for asset in offsets.keys():
        ret += asset.encode()
        ret += b'\0'
        ret += ctypes.c_uint64(offsets[asset]["byteoffset"])
        ret += ctypes.c_uint64(offsets[asset]["len"])
        ret += ctypes.c_uint8(offsets[asset]["type"])

        if offsets[asset]["type"] == 0:
            ret += ctypes.c_uint64(offsets[asset]["size"][0])
            ret += ctypes.c_uint64(offsets[asset]["size"][1])

    return ret

def dump(assets, file : io.BytesIO):
    __logger__.log(f"Dumping assets to {file.name}")
    assets.load_assets()
    header = generate_header()
    length = len(header)

    content = header

    offsets = {}

    asset_data = b''
    for asset in assets.__assets__:
        asset_in_bytes = convert_asset_to_bytes(asset)
        offsets[asset.name] = {}
        offsets[asset.name]["byteoffset"] = length
        offsets[asset.name]["len"] = len(asset_in_bytes)

        if asset.asset_type == ass.AssetType.Image:
            offsets[asset.name]["size"] = (asset.get().get_size())
            offsets[asset.name]["type"] = 0
        if asset.asset_type == ass.AssetType.Audio:
            offsets[asset.name]["type"] = 1


        length += len(asset_in_bytes)
        asset_data += asset_in_bytes

    content += generate_offset_table(offsets)
    content += b'OTEN'
    content += asset_data

    __logger__.log("Writing to file")
    file.write(content)

class InvalidAssetPackHeaderException(Exception):
    def __init__(self, filename : str, *args: object) -> None:
        self.filename = filename
        super().__init__(*args)

    def __str__(self) -> str:
        return f"{self.filename} has an invalid header"

def load_asset_offset_value(file : io.BytesIO) -> tuple[str, int, int, ass.AssetType, list]:
    if file.read(4) == b"OTEN":
        return ("END_OF_TABLE", 0)
    
    file.seek(file.tell() - 4)

    c = file.read(1)
    buf = ""
    while c != b'\x00':
        buf += c.decode()
        c = file.read(1)

    offset = file.read(8)
    offset = int.from_bytes(offset, byteorder="little")

    length = file.read(8)
    length = int.from_bytes(length, byteorder="little")

    extra = []

    type = int.from_bytes(file.read(1), byteorder="little")
    if type == 0:
        type = ass.AssetType.Image
        extra.append((int.from_bytes(file.read(8), byteorder="little"), int.from_bytes(file.read(8), byteorder="little")))

    if type == 1:
        type = ass.AssetType.Audio

    return (buf, offset, length, type, extra)


LoadType = TypeVar("LoadType")
def load(file : io.BytesIO, type : Type[LoadType]) -> LoadType:
    __logger__.log(f"Loading asset pack binary {file.name}")
    header = file.read(4)
    if header != b'EPAL': raise InvalidAssetPackHeaderException(file.name)
    
    offset_table = {}

    __logger__.log("Reading offset table")
    offset = (0, 0)
    while offset[0] != "END_OF_TABLE":
        offset = load_asset_offset_value(file)
        if offset[0] != "END_OF_TABLE": 
            offset_table[offset[0]] = {}
            offset_table[offset[0]]["byteoffset"] = offset[1]
            offset_table[offset[0]]["len"] = offset[2]
            offset_table[offset[0]]["type"] = offset[3]

            if offset_table[offset[0]]["type"] == ass.AssetType.Image:
                offset_table[offset[0]]["size"] = offset[4][0]

    ret = type()

    __logger__.log("Loading and creating assets")
    for asset_offset in offset_table.keys():
        file.seek(offset_table[asset_offset]["byteoffset"])
        data = pickle.loads(file.read(offset_table[asset_offset]["len"]))
        ret.add_asset(ass.Asset.__load_from_binary__(asset_offset, data, offset_table[asset_offset]))
    
    return ret