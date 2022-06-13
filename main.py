import PyQt5.QtCore
from PyQt5 import QtWidgets, uic, QtGui
import configparser, sys, glob, os, launchScript, qdarkstyle
import modListFromFile as mlff

config = configparser.ConfigParser()
config.read('config.ini')

try:
    os.makedirs('ModPresets')
except Exception as E:
    pass

if config.sections() == []:
    config['PATHS'] = {'sourceport_executable' : 'C:\\Games\\GzDoom\\gzdoom.exe',
                       'mod_folder' : 'C:\\Games\\GzDoom\\Mods'}
    with open('config.ini', 'w') as configFile:
        config.write(configFile)

class BreakToNextActiveMod(Exception):
    pass

def showAndHideMainWindow():
    if MWindow.isHidden():
        MWindow.show()
    else:
        MWindow.hide()

@PyQt5.QtCore.pyqtSlot(QtWidgets.QAction)
def presetChoosed(preset):
    launchScript.LaunchGame(config['PATHS']['sourceport_executable'], config['PATHS']['mod_folder'], mlff.getListOfModsFromFile(preset.text()), True)

@PyQt5.QtCore.pyqtSlot(QtWidgets.QSystemTrayIcon.ActivationReason)
def showHideDoubleClick(reason):
    if reason == QtWidgets.QSystemTrayIcon.DoubleClick:
        showAndHideMainWindow()

def updateTrayMenu():
    trm_main.clear()
    trm_presets.clear()

    existingPresets = glob.glob('*.dmmp', root_dir='ModPresets\\')

    for preset in range(0, len(existingPresets)):
        splittedPresetName = existingPresets[preset].split('.dmmp')[0]
        trm_presets.addAction(splittedPresetName)

    trm_main.addMenu(trm_presets)
    trm_main.addSeparator()
    trm_main.addAction(trma_main_launchVanilla)
    trm_main.addAction(trma_main_windowVisibility)
    trm_main.addSeparator()
    trm_main.addAction(trma_main_quit)

    trma_main_quit.triggered.connect(app.quit)
    trma_main_windowVisibility.triggered.connect(showAndHideMainWindow)
    trma_main_launchVanilla.triggered.connect(lambda: launchScript.LaunchGame(config['PATHS']['sourceport_executable'], config['PATHS']['mod_folder'], [], False))

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("Main.ui", self)
        self.show()
        self.setFixedSize(self.size().width(), self.size().height())
        self.setWindowIcon(QtGui.QIcon('icon.ico'))
        self.ApplyConfig()
        self.LoadPresetsInCombobox()
        self.list_Mods.setSortingEnabled(True)
        self.RefreshModList()

        self.btn_BrowseSourcePortDir.clicked.connect(self.SetSourcePortExecutable)
        self.btn_BrowseModDir.clicked.connect(self.SetModFolder)
        self.btn_RefreshMods.clicked.connect(self.RefreshModList)
        self.btn_ActivateMod.clicked.connect(self.ActivateMod)
        self.btn_DisableMod.clicked.connect(self.DeactivateMod)
        self.btn_Play.clicked.connect(self.LaunchGame)
        self.btn_UpSelected.clicked.connect(self.UpModPriority)
        self.btn_DownSelected.clicked.connect(self.LowerModPriority)
        self.btn_AddNewPreset.clicked.connect(self.CreateNewPreset)
        self.btn_SavePreset.clicked.connect(self.SavePreset)
        self.btn_DeletePreset.clicked.connect(self.DeletePreset)
        self.btn_LoadPreset.clicked.connect(self.LoadPreset)


    def ApplyConfig(self):
        self.lineE_SourcePortDir.setText(config['PATHS']['sourceport_executable'])
        self.lineE_ModDir.setText(config['PATHS']['mod_folder'])

    def WriteChangesToConfig(self):
        with open('config.ini', 'w') as configFile:
            config.write(configFile)

    def SetSourcePortExecutable(self):
        dirToExe = QtWidgets.QFileDialog.getOpenFileName(self, "Select source port executable (.exe)", "C:\\", "Executable (*.exe)")
        if dirToExe[0] != '':
            self.lineE_SourcePortDir.setText(dirToExe[0])
            config['PATHS']['sourceport_executable'] = dirToExe[0]
            self.WriteChangesToConfig()

    def SetModFolder(self):
        cachedModFolder = self.lineE_ModDir.text()
        dirToModFolder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select mod folder", 'C:\\', QtWidgets.QFileDialog.ShowDirsOnly)
        if dirToModFolder != '' and dirToModFolder != cachedModFolder:
            self.lineE_ModDir.setText(dirToModFolder)
            config['PATHS']['mod_folder'] = dirToModFolder
            self.WriteChangesToConfig()
            self.list_ActiveMods.clear()
            self.RefreshModList()

    def DeleteAllActiveModsFromInactiveList(self):
        inactiveCount = self.list_Mods.count()
        activeCount = self.list_ActiveMods.count()

        if activeCount > 0 and inactiveCount > 0:
            for activeMod in range(0, activeCount):
                activeModName = self.list_ActiveMods.item(activeMod).text()
                for inactiveMod in range(0, inactiveCount):
                    inactiveModName = self.list_Mods.item(inactiveMod).text()
                    if activeModName == inactiveModName:
                        self.list_Mods.takeItem(inactiveMod)
                        self.statusBar.showMessage('Deleting activated mods from inactive mod list...')
                        #modToDelete = None
                        break


    def ActivateMod(self):
        try:
            self.list_ActiveMods.addItem(self.list_Mods.takeItem(self.list_Mods.row(self.list_Mods.selectedItems()[0])))
        except:
            pass

    def DeactivateMod(self):
        try:
            self.list_Mods.addItem(self.list_ActiveMods.takeItem(self.list_ActiveMods.row(self.list_ActiveMods.selectedItems()[0])))
        except:
            pass


    def SavePreset(self):
        infoBox = QtWidgets.QMessageBox()
        activeCount = self.list_ActiveMods.count()
        if self.cBox_ActivePreset.currentText() != '' and activeCount > 0:
            with open(f'ModPresets\\{self.cBox_ActivePreset.currentText()}.dmmp', 'w') as PresetFile:
                for mod in range(activeCount):
                    activeModName = self.list_ActiveMods.item(mod).text()
                    PresetFile.write(f'{activeModName}\n')
            infoBox.information(self, 'Saving preset', 'Preset saved successfully!')
        else:
            infoBox.warning(self, 'Saving preset', 'Preset isn\'t selected or there is nothing to save!')

    def LoadPresetsInCombobox(self):
        presets = glob.glob('*.dmmp', root_dir='ModPresets\\')
        self.cBox_ActivePreset.clear()
        if len(presets) > 0:
            for preset in presets:
                self.cBox_ActivePreset.addItem(preset.split('.dmmp')[0])


    def CreateNewPreset(self):
        try:
            infoBox = QtWidgets.QMessageBox()
            presetName = QtWidgets.QInputDialog.getText(self, 'Creating new preset', 'Name your new preset:', QtWidgets.QLineEdit.Normal, '')
            if presetName[1]:
                if presetName[0] != '':
                    if not os.path.exists(f'ModPresets\\{presetName[0]}.dmmp'):
                        with open(f'ModPresets\\{presetName[0]}.dmmp', 'w') as PresetFile:
                            pass
                        self.LoadPresetsInCombobox()
                        infoBox.information(self, 'Creating new preset', f'Preset {presetName[0]} is successfully created!')
                        updateTrayMenu()
                    else:
                        infoBox.warning(self, 'Creating new preset', f'Preset {presetName[0]} already exists!')
                else:
                    infoBox.warning(self, 'Creating new preset', f'Can\'t create a preset with no name!')
        except Exception as E:
            self.statusBar.showMessage(E)

    def DeletePreset(self):
        try:
            infoBox = QtWidgets.QMessageBox()
            if self.cBox_ActivePreset.currentText() != '':
                presetTempName = self.cBox_ActivePreset.currentText()
                sureBox = QtWidgets.QMessageBox()
                sureBoxResult = sureBox.question(self, 'Deleting preset', f'Are you sure to delete {presetTempName} preset?', sureBox.Yes | sureBox.No)

                if sureBoxResult == sureBox.Yes:
                    try:
                        os.remove(f'ModPresets\\{presetTempName}.dmmp')
                        self.LoadPresetsInCombobox()
                        infoBox.information(self, 'Deleting preset', f'Preset {presetTempName} is successfully deleted!')
                        updateTrayMenu()
                    except Exception as E:
                        self.statusBar.showMessage(E)
            else:
                infoBox.warning(self, 'Deleting preset', 'There is nothing to delete!')
        except Exception as E:
            self.statusBar.showMessage(E)

    def UpModPriority(self):
        try:
            selectedModRow = self.list_ActiveMods.currentRow()
            selectedMod = self.list_ActiveMods.takeItem(selectedModRow)

            self.list_ActiveMods.insertItem(selectedModRow - 1, selectedMod)
            self.list_ActiveMods.setCurrentRow(selectedModRow - 1)
        except Exception as E:
            self.statusBar.showMessage(E)

    def LowerModPriority(self):
        try:
            selectedModRow = self.list_ActiveMods.currentRow()
            selectedMod = self.list_ActiveMods.takeItem(selectedModRow)

            self.list_ActiveMods.insertItem(selectedModRow + 1, selectedMod)
            self.list_ActiveMods.setCurrentRow(selectedModRow + 1)
        except Exception as E:
            self.statusBar.showMessage(E)


    def RefreshModList(self):
        if config['PATHS']['mod_folder'] != None:
            allPkThrees = glob.glob('*.pk3', root_dir=config['PATHS']['mod_folder'])
            allWads = glob.glob('*.wad', root_dir=config['PATHS']['mod_folder'])
            allMods = allPkThrees + allWads

            self.list_Mods.clear()
            if len(allMods) > 0:
                for mod in allMods:
                    self.list_Mods.addItem(mod)
            self.DeleteAllActiveModsFromInactiveList()

    def LoadPreset(self):
        try:
            infoBox = QtWidgets.QMessageBox()
            self.list_ActiveMods.clear()
            self.RefreshModList()
            if self.cBox_ActivePreset.currentText() != '':
                modList = mlff.getListOfModsFromFile(self.cBox_ActivePreset.currentText())
                for mod in range(len(modList)):
                    self.list_ActiveMods.addItem(modList[mod])
                infoBox.information(self, 'Loading preset', f'Preset {self.cBox_ActivePreset.currentText()} is successfully loaded!')
                self.DeleteAllActiveModsFromInactiveList()
            else:
                infoBox.warning(self, 'Loading preset', f'There is nothing to load!')
        except Exception as E:
            self.statusBar.showMessage(E)


    def LaunchGame(self):
        modsToLaunchWith = []
        for mod in range(self.list_ActiveMods.count()):
            modsToLaunchWith.append(self.list_ActiveMods.item(mod).text())

        if modsToLaunchWith != []:
            launchScript.LaunchGame(config['PATHS']['sourceport_executable'], config['PATHS']['mod_folder'], modsToLaunchWith, True)
        else:
            launchScript.LaunchGame(config['PATHS']['sourceport_executable'], config['PATHS']['mod_folder'], modsToLaunchWith, False)


app = QtWidgets.QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)
app.setStyleSheet(qdarkstyle.load_stylesheet())
MWindow = MainWindow()

trayAppIcon = QtGui.QIcon('icon.ico')
trayApp = QtWidgets.QSystemTrayIcon(trayAppIcon, parent=app)
trayApp.setToolTip('SNeicer\'s Doom Mod Manager')

trm_main = QtWidgets.QMenu() # trm - tray menu, trma - tray menu action
trm_presets = QtWidgets.QMenu("Launch from preset")
trma_main_quit = QtWidgets.QAction("Quit")
trma_main_windowVisibility = QtWidgets.QAction("Show/Hide Manager")
trma_main_launchVanilla = QtWidgets.QAction("Launch vanilla (no mods)")

updateTrayMenu()

trayApp.activated.connect(showHideDoubleClick)
trm_presets.triggered.connect(presetChoosed)
trayApp.setContextMenu(trm_main)
trayApp.setVisible(True)

app.exec()