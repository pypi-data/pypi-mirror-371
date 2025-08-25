import epal




if __name__ == "__main__":
    epal.Window(1, 1, epal.Color(255, 255, 255))

    asset_manager = epal.AssetManager()
    asset_manager.add("Dog", "./dog.jpg", epal.AssetType.Image)
    asset_manager.add("Green Sky", "./green_sky.mp3", epal.AssetType.Audio)

    asset_manager.dump_asset_pack("test.eap")