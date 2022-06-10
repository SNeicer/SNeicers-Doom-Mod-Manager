#import os, glob
import os

def LaunchGame(gzdoomPath, modPath, mods, IsModded):
    if IsModded:
        cPrompt = f'{gzdoomPath} -file '

        for mod in mods:
            cPrompt += f'{modPath}\\{mod} '

        #print(cPrompt)

        os.system(cPrompt)
    else:
        cPrompt = f'{gzdoomPath}'
        #print(cPrompt)
        os.system(cPrompt)