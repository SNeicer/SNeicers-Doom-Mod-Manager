def getListOfModsFromFile(presetName):
    modsFromList = []
    with open(f'ModPresets\\{presetName}.dmmp', 'r') as PresetFile:
        modsFromList = PresetFile.readlines()

    for mod in range(len(modsFromList)):
        splittedMod = modsFromList[mod].split('\n')
        modsFromList[mod] = splittedMod[0]

    return modsFromList

