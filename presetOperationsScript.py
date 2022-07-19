# presetOperationsScript used for reading info from .dmmp files
# Functions: get_list_of_mods_from_file, get_additional_arguments_from_file, get_custom_map_and_skill


def get_list_of_mods_from_file(preset_name):
    with open(f'ModPresets\\{preset_name}.dmmp', 'r') as PresetFile:
        mods_from_list = PresetFile.readlines()

    for mod in mods_from_list:
        mods_from_list[mods_from_list.index(mod)] = mod.split('\n')[0]

    mods_from_list = [mod for mod in mods_from_list if ' #' not in mod]

    return mods_from_list


def get_additional_arguments_from_file(preset_name):
    with open(f'ModPresets\\{preset_name}.dmmp', 'r') as PresetFile:
        info_from_file = PresetFile.readlines()

    try:
        args = info_from_file[len(info_from_file)-1].split(' #ARGS: ', 1)[1]
        args = args.split(' ')
        args.pop(len(args) - 1)
    except IndexError:
        return []

    return args


def get_custom_map_and_skill(preset_name):
    with open(f'ModPresets\\{preset_name}.dmmp', 'r') as PresetFile:
        info_from_file = PresetFile.readlines()

    try:
        cmap = ''
        cskill = ''
        for line in info_from_file:
            if ' #MAP: ' in line:
                cmap = line.split(' #MAP: ')[1].replace('\n', '')
            if ' #SKILL: ' in line:
                cskill = line.split(' #SKILL: ')[1].replace('\n', '')

        return [cmap, cskill]
    except:
        return ['', '']