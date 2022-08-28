# launchScript used for launching the game
# Functions: LaunchGameAdvanced
import os


def launch_game_advanced(gzdoom_path, mod_path, mods, is_modded, a_args, cmap_and_cskill, extra_args=''):
    if is_modded:
        c_prompt = f'{gzdoom_path} -file '

        for mod in mods:
            c_prompt += f'{mod_path}/{mod} '

        if a_args:
            for arg in a_args:
                c_prompt += f'{arg} '

        if cmap_and_cskill[0] != '':
            c_prompt += f'-warp {cmap_and_cskill[0]} '

        if cmap_and_cskill[1] != '':
            c_prompt += f'-skill {cmap_and_cskill[1]} '

        if extra_args != '' and extra_args is not None:
            c_prompt += extra_args

        print(c_prompt)

        os.system(c_prompt)
    else:
        c_prompt = f'{gzdoom_path} '
        for arg in a_args:
            c_prompt += f'{arg} '
        if extra_args != '':
            c_prompt += extra_args
        print(c_prompt)
        os.system(c_prompt)
