# LaunchGame Script used for launching the game
# Functions: LaunchGame (Deprecated), LaunchGameAdvanced
import os

def LaunchGame(gzdoomPath, modPath, mods, IsModded): # - THIS FUNCTION IS GOING TO BE DELETED AFTER PRE-RELEASE! -
    if IsModded:
        cPrompt = f'{gzdoomPath} -file '

        for mod in mods:
            cPrompt += f'{modPath}\\{mod} '

        os.system(cPrompt)
    else:
        cPrompt = f'{gzdoomPath}'
        os.system(cPrompt)

def LaunchGameAdvanced(gzdoomPath, modPath, mods, IsModded, aArgs, cmapAndCskill): # New launch game function, use this instead of LaunchGame
    if IsModded:
        cPrompt = f'{gzdoomPath} -file '

        for mod in mods:
            cPrompt += f'{modPath}/{mod} '

        if aArgs != []:
            for arg in aArgs:
                cPrompt += f'{arg} '

        if cmapAndCskill[0] != '':
            cPrompt += f'-warp {cmapAndCskill[0]} '

        if cmapAndCskill[1] != '':
            cPrompt += f'-skill {cmapAndCskill[1]}'

        print(cPrompt)

        os.system(cPrompt)
    else:
        cPrompt = f'{gzdoomPath} '
        for arg in aArgs:
            cPrompt += f'{arg} '
        print(cPrompt)
        os.system(cPrompt)