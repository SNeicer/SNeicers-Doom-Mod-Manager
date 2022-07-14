#

def getListOfModsFromFile(presetName):
    with open(f'ModPresets\\{presetName}.dmmp', 'r') as PresetFile:
        modsFromList = PresetFile.readlines()

    for mod in modsFromList:
        modsFromList[modsFromList.index(mod)] = mod.split('\n')[0]

    modsFromList = [mod for mod in modsFromList if ' #' not in mod]

    return modsFromList

def getAdditionalArgumentsFromFile(presetName):
    with open(f'ModPresets\\{presetName}.dmmp', 'r') as PresetFile:
        infoFromFile = PresetFile.readlines()

    try:
        args = infoFromFile[len(infoFromFile)-1].split(' #ARGS: ', 1)[1]
        args = args.split(' ')
        args.pop(len(args) - 1)
    except IndexError:
        return []

    return args

def getCustomMapAndSkill(presetName):
    with open(f'ModPresets\\{presetName}.dmmp', 'r') as PresetFile:
        infoFromFile = PresetFile.readlines()

    try:
        cmap = ''
        cskill = ''
        for line in infoFromFile:
            if ' #MAP: ' in line:
                cmap = line.split(' #MAP: ')[1].replace('\n', '')
            if ' #SKILL: ' in line:
                cskill = line.split(' #SKILL: ')[1].replace('\n', '')

        return [cmap, cskill]
    except:
        return ['', '']