# SNeicer's Doom Mod Manager (Version 1.2)#
# GitHub: https://github.com/SNeicer/SNeicers-Doom-Mod-Manager #
# Discord: SNeicer#1342 #
# EMail: b2jnz7hlw@mozmail.com #

import PyQt5.QtCore
from PyQt5 import QtWidgets, uic, QtGui
import configparser
import sys
import glob
import os
import launchScript
import qdarkstyle
import re
import resources
import presetOperationsScript as Pos

config = configparser.ConfigParser()
config.read('config.ini')  # Reading config

# Trying to make ModPresets folder
try:
    os.makedirs('ModPresets')
except WindowsError as E:
    pass

if not config.sections():  # If config is empty, fill it with default values
    config['PATHS'] = {'sourceport_executable': 'C:\\Games\\GzDoom\\gzdoom.exe',
                       'mod_folder': 'C:\\Games\\GzDoom\\Mods'}
    config['ADDITIONAL'] = {'save_additional': False, 'save_cprompt': False}
    with open('config.ini', 'w') as configFile:
        config.write(configFile)

if 'ADDITIONAL' not in config.sections():  # If config is from an older version, add new additional settings to it
    config['ADDITIONAL'] = {'save_additional': False, 'save_cprompt': False}
    with open('config.ini', 'w') as configFile:
        config.write(configFile)


# Function to show and hide main mod manager window
# Used in functions: show_hide_on_doubleclick (Line 73), update_tray_menu (Line 96)
def show_hide_mwindow():
    if MWindow.isHidden():
        MWindow.show()
    else:
        MWindow.hide()


# Self-explanatory...
# Used in function: apply_config (Line 159 and 160)
def get_bool_from_string(string):
    if string == 'False':
        return False
    else:
        return True


# Function to launch the game with selected preset from tray menu
# Used only at line 506
@PyQt5.QtCore.pyqtSlot(QtWidgets.QAction)
def preset_selected(preset):
    launchScript.launch_game_advanced(config['PATHS']['sourceport_executable'], config['PATHS']['mod_folder'],
                                      Pos.get_list_of_mods_from_file(preset.text()), True,
                                      Pos.get_additional_arguments_from_file(preset.text()),
                                      Pos.get_custom_map_and_skill(preset.text()))


# Triggers show_hide_mwindow function after double clicking at tray icon
# Used only at line 505
@PyQt5.QtCore.pyqtSlot(QtWidgets.QSystemTrayIcon.ActivationReason)
def show_hide_on_doubleclick(reason):
    if reason == QtWidgets.QSystemTrayIcon.DoubleClick:
        show_hide_mwindow()


# Fully updates tray menu by reconstructing it
# Used in functions: create_new_preset (Line 314), delete_preset (Line 344) and in line 502
def update_tray_menu():
    trm_main.clear()
    trm_presets.clear()

    existing_presets = glob.glob('*.dmmp', root_dir='ModPresets\\')

    for preset in range(0, len(existing_presets)):
        splitted_preset_name = existing_presets[preset].split('.dmmp')[0]
        trm_presets.addAction(splitted_preset_name)

    trm_main.addMenu(trm_presets)
    trm_main.addSeparator()
    trm_main.addAction(trma_main_launchVanilla)
    trm_main.addAction(trma_main_windowVisibility)
    trm_main.addSeparator()
    trm_main.addAction(trma_main_quit)

    trma_main_quit.triggered.connect(app.quit)
    trma_main_windowVisibility.triggered.connect(show_hide_mwindow)
    trma_main_launchVanilla.triggered.connect(
        lambda: launchScript.launch_game_advanced(config['PATHS']['sourceport_executable'], config['PATHS']['mod_folder'],
                                                  [], False, [], ['', '']))


# Main Window class witch holds ui and functions to it
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("Main.ui", self)  # Loading ui file
        self.show()
        self.setFixedSize(self.size().width(), self.size().height())  # Making window unresizable (For now...)
        self.setWindowIcon(QtGui.QIcon('icon.ico'))
        self.ActiveArgs = []  # Var that stores launch arguments
        self.apply_config()  # Calling some functions on startup
        self.load_presets_in_cbox()
        self.list_Mods.setSortingEnabled(True)
        self.refresh_mod_list()

        # Connecting buttons to their functions and adding hotkeys
        self.btn_BrowseSourcePortDir.clicked.connect(self.set_sourceport_executable)
        self.btn_BrowseModDir.clicked.connect(self.set_mod_folder)
        self.btn_RefreshMods.clicked.connect(self.refresh_mod_list)
        self.btn_RefreshMods.setShortcut('ctrl+r')
        self.btn_ActivateMod.clicked.connect(self.activate_mod)
        self.btn_ActivateMod.setShortcut('ctrl+right')
        self.btn_DisableMod.clicked.connect(self.deactivate_mod)
        self.btn_DisableMod.setShortcut('ctrl+left')
        self.btn_Play.clicked.connect(self.launch_game)
        self.btn_Play.setShortcut('ctrl+p')
        self.btn_UpSelected.clicked.connect(self.up_mod_priority)
        self.btn_UpSelected.setShortcut('ctrl+up')
        self.btn_DownSelected.clicked.connect(self.lower_mod_priority)
        self.btn_DownSelected.setShortcut('ctrl+down')
        self.btn_AddNewPreset.clicked.connect(self.create_new_preset)
        self.btn_AddNewPreset.setShortcut('ctrl+n')
        self.btn_SavePreset.clicked.connect(self.save_preset)
        self.btn_SavePreset.setShortcut('ctrl+s')
        self.btn_DeletePreset.clicked.connect(self.delete_preset)
        self.btn_DeletePreset.setShortcut('ctrl+d')
        self.btn_LoadPreset.clicked.connect(self.load_preset)
        self.btn_LoadPreset.setShortcut('ctrl+l')

        # Additional Settings
        self.check_FastMonsters.clicked.connect(lambda: self.select_additional_argument('-fast'))
        self.check_RespawningMonsters.clicked.connect(lambda: self.select_additional_argument('-respawn'))
        self.check_NoMonsters.clicked.connect(lambda: self.select_additional_argument('-nomonsters'))
        self.check_NoAutoExec.clicked.connect(lambda: self.select_additional_argument('-noautoexec'))
        self.check_AVG.clicked.connect(lambda: self.select_additional_argument('-avg'))

        # Save additional settings checks
        self.check_SaveAdditional.clicked.connect(self.set_save_additional_settings)
        self.check_SaveCommandPrompt.clicked.connect(self.set_save_additional_settings)

        # Input Validator
        self.presetNameValidator = re.compile(r'^[a-zA-Z0-9_. -]*$')

    # Getting values from config
    # Used in initialization of MainWindow class (Line 111)
    def apply_config(self):
        self.lineE_SourcePortDir.setText(config['PATHS']['sourceport_executable'])
        self.lineE_ModDir.setText(config['PATHS']['mod_folder'])
        self.check_SaveAdditional.setChecked(get_bool_from_string(config['ADDITIONAL']['save_additional']))
        self.check_SaveCommandPrompt.setChecked(get_bool_from_string(config['ADDITIONAL']['save_cprompt']))

    # Saves changed things in config
    # Used in functions: set_mod_folder (Line 223), set_save_additional_settings (Line 185)
    # and in set_sourceport_executable (Line 178)
    @staticmethod
    def write_config_changes():
        with open('config.ini', 'w') as config_file:
            config.write(config_file)

    # Getting full path to sourceport executable
    # Used in initialization of MainWindow class (Line 117)
    def set_sourceport_executable(self):
        dir_to_exe = QtWidgets.QFileDialog.getOpenFileName(self, "Select gzdoom executable (gzdoom.exe)", "C:\\",
                                                           "GzDoom (gzdoom.exe)")
        if dir_to_exe[0] != '':
            self.lineE_SourcePortDir.setText(dir_to_exe[0])
            config['PATHS']['sourceport_executable'] = dir_to_exe[0]
            self.write_config_changes()

    # Saving additional settings
    # Used in initialization of MainWindow class (Line 148, 149)
    def set_save_additional_settings(self):
        config['ADDITIONAL']['save_additional'] = str(self.check_SaveAdditional.isChecked())
        config['ADDITIONAL']['save_cprompt'] = str(self.check_SaveCommandPrompt.isChecked())
        self.write_config_changes()

    # Adding or removing argument from ActiveArgs list after ui interaction
    # Used in initialization of MainWindow class (Line 141, 142, 143, 144, 145)
    def select_additional_argument(self, new_arg):
        if new_arg in self.ActiveArgs:
            self.ActiveArgs.remove(new_arg)
        else:
            self.ActiveArgs.append(new_arg)

        self.statusBar.showMessage(f'Current active arguments: {self.ActiveArgs}')

    # Warning! Yandere dev moment below! Skip to line 212 to end this cringefest!
    # REWRITE SOMEHOW!
    # Used in function: load_preset (Line 414)
    def set_checks_for_additional_arguments(self):
        if '-fast' in self.ActiveArgs:
            self.check_FastMonsters.setChecked(True)
        if '-respawn' in self.ActiveArgs:
            self.check_RespawningMonsters.setChecked(True)
        if '-nomonsters' in self.ActiveArgs:
            self.check_NoMonsters.setChecked(True)
        if '-noautoexec' in self.ActiveArgs:
            self.check_NoAutoExec.setChecked(True)
        if '-avg' in self.ActiveArgs:
            self.check_AVG.setChecked(True)

        self.statusBar.showMessage(f'Current active arguments: {self.ActiveArgs}')

    # Getting full path to the mod folder
    # Used in initialization of MainWindow class (Line 118)
    def set_mod_folder(self):
        cached_mod_folder = self.lineE_ModDir.text()
        dir_to_mod_folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select mod folder", 'C:\\',
                                                                       QtWidgets.QFileDialog.ShowDirsOnly)
        if dir_to_mod_folder != '' and dir_to_mod_folder != cached_mod_folder:
            self.lineE_ModDir.setText(dir_to_mod_folder)
            config['PATHS']['mod_folder'] = dir_to_mod_folder
            self.write_config_changes()
            self.list_ActiveMods.clear()
            self.refresh_mod_list()

    # Deleting all activated mods from inactive mod list
    # Used in functions: load_preset (Line 413), refresh_mod_list (Line 389)
    def delete_active_from_inactive_mods(self):
        inactive_count = self.list_Mods.count()
        active_count = self.list_ActiveMods.count()

        if active_count > 0 and inactive_count > 0:
            for activeMod in range(0, active_count):
                active_mod_name = self.list_ActiveMods.item(activeMod).text()
                for inactiveMod in range(0, inactive_count):
                    inactive_mod_name = self.list_Mods.item(inactiveMod).text()
                    if active_mod_name == inactive_mod_name:
                        self.list_Mods.takeItem(inactiveMod)
                        self.statusBar.showMessage('Deleting activated mods from inactive mod list...')
                        break

    # Activating a mod
    # Used in initialization of MainWindow class (Line 121)
    def activate_mod(self):
        try:
            self.list_ActiveMods.addItem(self.list_Mods.takeItem(self.list_Mods.row(self.list_Mods.selectedItems()[0])))
        except:
            pass

    # Deactivating a mod
    # Used in initialization of MainWindow class (Line 123)
    def deactivate_mod(self):
        try:
            self.list_Mods.addItem(
                self.list_ActiveMods.takeItem(self.list_ActiveMods.row(self.list_ActiveMods.selectedItems()[0])))
        except:
            pass

    # Saving all mods and arguments to preset
    # Used in initialization of MainWindow class (Line 133)
    def save_preset(self):
        info_box = QtWidgets.QMessageBox()
        active_count = self.list_ActiveMods.count()
        if self.cBox_ActivePreset.currentText() != '' and active_count > 0:
            with open(f'ModPresets\\{self.cBox_ActivePreset.currentText()}.dmmp', 'w') as PresetFile:
                for mod in range(active_count):
                    active_mod_name = self.list_ActiveMods.item(mod).text()
                    PresetFile.write(f'{active_mod_name}\n')
                if config['ADDITIONAL']['save_additional'] == 'True':
                    if self.gBox_CustomStartMap.isChecked():
                        PresetFile.write(' #MAP: ')
                        PresetFile.write(self.tEdit_CustomStartMapName.toPlainText() + '\n')
                    if self.gBox_CustomDifficulty.isChecked():
                        PresetFile.write(' #SKILL: ')
                        skill_to_write = self.cBox_CustomDifficulty.currentText().split('skill ')[1].replace(')',
                                                                                                             '') + '\n'
                        PresetFile.write(skill_to_write)
                    if self.ActiveArgs:
                        PresetFile.write(' #ARGS: ')
                        for arg in self.ActiveArgs:
                            PresetFile.write(f'{arg} ')
            info_box.information(self, 'Saving preset', 'Preset saved successfully!')
        else:
            info_box.warning(self, 'Saving preset', 'Preset isn\'t selected or there is nothing to save!')

    # Loading all names of existing presets from ModPresets folder
    # Used in initialization of MainWindow class (Line 112)
    # Used in functions: create_new_preset (Line 310), delete_preset (Line 341)
    def load_presets_in_cbox(self):
        presets = glob.glob('*.dmmp', root_dir='ModPresets\\')
        self.cBox_ActivePreset.clear()
        if len(presets) > 0:
            for preset in presets:
                self.cBox_ActivePreset.addItem(preset.split('.dmmp')[0])

    # Creating a new preset file with custom name
    # Used in initialization of MainWindow class (Line 131)
    def create_new_preset(self):
        try:
            info_box = QtWidgets.QMessageBox()
            preset_name = QtWidgets.QInputDialog.getText(self, 'Creating new preset', 'Name your new preset:',
                                                         QtWidgets.QLineEdit.Normal, '')
            if preset_name[1]:
                if preset_name[0] != '':
                    if not os.path.exists(f'ModPresets\\{preset_name[0]}.dmmp'):
                        if re.match(self.presetNameValidator, preset_name[0]) is not None:
                            with open(f'ModPresets\\{preset_name[0]}.dmmp', 'w'):
                                pass
                            self.load_presets_in_cbox()
                            self.cBox_ActivePreset.setCurrentIndex(self.cBox_ActivePreset.findText(preset_name[0]))
                            info_box.information(self, 'Creating new preset',
                                                 f'Preset {preset_name[0]} is successfully created!')
                            update_tray_menu()
                        else:
                            info_box.warning(self, 'Creating new preset',
                                             'Invalid name!\nUse only letters from A to Z and characters "-", "_", '
                                             '" ", "."!')
                    else:
                        info_box.warning(self, 'Creating new preset', f'Preset {preset_name[0]} already exists!')
                else:
                    info_box.warning(self, 'Creating new preset', f'Can\'t create a preset with no name!')
        except Exception as ex:
            self.statusBar.showMessage(ex)

    # Fully deleting preset from existence
    # Used in initialization of MainWindow class (Line 135)
    def delete_preset(self):
        try:
            info_box = QtWidgets.QMessageBox()
            if self.cBox_ActivePreset.currentText() != '':
                preset_temp_name = self.cBox_ActivePreset.currentText()
                sure_box = QtWidgets.QMessageBox()
                sure_box_result = sure_box.question(self, 'Deleting preset',
                                                    f'Are you sure to delete {preset_temp_name} preset?',
                                                    sure_box.Yes | sure_box.No)

                if sure_box_result == sure_box.Yes:
                    try:
                        os.remove(f'ModPresets\\{preset_temp_name}.dmmp')
                        self.load_presets_in_cbox()
                        info_box.information(self, 'Deleting preset',
                                             f'Preset {preset_temp_name} is successfully deleted!')
                        update_tray_menu()
                    except Exception as ex:
                        self.statusBar.showMessage(ex)
            else:
                info_box.warning(self, 'Deleting preset', 'There is nothing to delete!')
        except Exception as ex:
            self.statusBar.showMessage(ex)

    # Upping mod priority in active mods list
    # Used in initialization of MainWindow class (Line 127)
    def up_mod_priority(self):
        try:
            selected_mod_row = self.list_ActiveMods.currentRow()
            selected_mod = self.list_ActiveMods.takeItem(selected_mod_row)

            self.list_ActiveMods.insertItem(selected_mod_row - 1, selected_mod)
            self.list_ActiveMods.setCurrentRow(selected_mod_row - 1)
        except Exception as ex:
            self.statusBar.showMessage(ex)

    # Lowering mod priority in active mods list
    # Used in initialization of MainWindow class (Line 129)
    def lower_mod_priority(self):
        try:
            selected_mod_row = self.list_ActiveMods.currentRow()
            selected_mod = self.list_ActiveMods.takeItem(selected_mod_row)

            self.list_ActiveMods.insertItem(selected_mod_row + 1, selected_mod)
            self.list_ActiveMods.setCurrentRow(selected_mod_row + 1)
        except Exception as ex:
            self.statusBar.showMessage(ex)

    # Refreshing list of inactive mods and deleting all active mods from inactive list
    # Used in initialization of MainWindow class (Line 114, 119)
    # Used in functions: load_preset (Line 397), set_mod_folder (Line 225)
    def refresh_mod_list(self):
        if config['PATHS']['mod_folder'] is not None:
            all_pk_threes = glob.glob('*.pk3', root_dir=config['PATHS']['mod_folder'])
            all_wads = glob.glob('*.wad', root_dir=config['PATHS']['mod_folder'])
            all_mods = all_pk_threes + all_wads

            self.list_Mods.clear()
            if len(all_mods) > 0:
                for mod in all_mods:
                    self.list_Mods.addItem(mod)
            self.delete_active_from_inactive_mods()

    # Loading mods and arguments from a preset file
    # Used in initialization of MainWindow class (Line 137)
    def load_preset(self):
        try:
            info_box = QtWidgets.QMessageBox()
            self.list_ActiveMods.clear()
            self.refresh_mod_list()
            if self.cBox_ActivePreset.currentText() != '':
                mod_list = Pos.get_list_of_mods_from_file(self.cBox_ActivePreset.currentText())
                arg_list = Pos.get_additional_arguments_from_file(self.cBox_ActivePreset.currentText())
                cmap_andcskill = Pos.get_custom_map_and_skill(self.cBox_ActivePreset.currentText())
                if len(arg_list) > 0:
                    self.ActiveArgs = arg_list
                if cmap_andcskill[0] != '':
                    self.tEdit_CustomStartMapName.setText(cmap_andcskill[0])
                    self.gBox_CustomStartMap.setChecked(True)
                if cmap_andcskill[1] != '':
                    self.gBox_CustomDifficulty.setChecked(True)
                    self.cBox_CustomDifficulty.setCurrentIndex(int(cmap_andcskill[1]) - 1)
                for mod in range(len(mod_list)):
                    if ' #' not in mod_list[mod]:
                        self.list_ActiveMods.addItem(mod_list[mod])
                self.delete_active_from_inactive_mods()
                self.set_checks_for_additional_arguments()
                info_box.information(self, 'Loading preset',
                                     f'Preset {self.cBox_ActivePreset.currentText()} is successfully loaded!')
            else:
                info_box.warning(self, 'Loading preset', f'There is nothing to load!')
        except Exception as ex:
            self.statusBar.showMessage(ex)

    # Launching game with currently selected in ui mods and arguments
    # Used in initialization of MainWindow class (Line 125)
    def launch_game(self):
        mods_to_launch_with = []
        getted_cmap_and_cskill = [self.tEdit_CustomStartMapName.toPlainText(),
                                  self.cBox_CustomDifficulty.currentText().split('skill ')[1].replace(')', '')]
        for mod in range(self.list_ActiveMods.count()):
            mods_to_launch_with.append(self.list_ActiveMods.item(mod).text())

        run_code = 0  # 1 - Only cmap, 2 - Only cskill, 3 - Both

        if self.gBox_CustomStartMap.isChecked() and getted_cmap_and_cskill[0] != '':  # cmap check
            run_code += 1

        if self.gBox_CustomDifficulty.isChecked() and getted_cmap_and_cskill[1] != '':  # cskill check
            run_code += 2

        if mods_to_launch_with:
            match run_code:
                case 1:
                    launchScript.launch_game_advanced(config['PATHS']['sourceport_executable'],
                                                      config['PATHS']['mod_folder'],
                                                      mods_to_launch_with, True, self.ActiveArgs,
                                                      [getted_cmap_and_cskill[0], ''])
                case 2:
                    launchScript.launch_game_advanced(config['PATHS']['sourceport_executable'],
                                                      config['PATHS']['mod_folder'],
                                                      mods_to_launch_with, True, self.ActiveArgs,
                                                      ['', getted_cmap_and_cskill[1]])
                case 3:
                    launchScript.launch_game_advanced(config['PATHS']['sourceport_executable'],
                                                      config['PATHS']['mod_folder'],
                                                      mods_to_launch_with, True, self.ActiveArgs,
                                                      [getted_cmap_and_cskill[0], getted_cmap_and_cskill[1]])
                case _:
                    launchScript.launch_game_advanced(config['PATHS']['sourceport_executable'],
                                                      config['PATHS']['mod_folder'],
                                                      mods_to_launch_with, True, self.ActiveArgs,
                                                      ['', ''])
        else:
            match run_code:
                case 1:
                    launchScript.launch_game_advanced(config['PATHS']['sourceport_executable'],
                                                      config['PATHS']['mod_folder'],
                                                      [], False, self.ActiveArgs, [getted_cmap_and_cskill[0], ''])
                case 2:
                    launchScript.launch_game_advanced(config['PATHS']['sourceport_executable'],
                                                      config['PATHS']['mod_folder'],
                                                      [], False, self.ActiveArgs, ['', getted_cmap_and_cskill[1]])
                case 3:
                    launchScript.launch_game_advanced(config['PATHS']['sourceport_executable'],
                                                      config['PATHS']['mod_folder'],
                                                      [], False, self.ActiveArgs,
                                                      [getted_cmap_and_cskill[0], getted_cmap_and_cskill[1]])
                case _:
                    launchScript.launch_game_advanced(config['PATHS']['sourceport_executable'],
                                                      config['PATHS']['mod_folder'],
                                                      [], False, self.ActiveArgs,
                                                      ['', ''])


# Making application to launch
app = QtWidgets.QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)
app.setStyleSheet(qdarkstyle.load_stylesheet())
MWindow = MainWindow()  # Creating a main window

# Creating a tray icon
trayAppIcon = QtGui.QIcon('icon.ico')
trayApp = QtWidgets.QSystemTrayIcon(trayAppIcon, parent=app)
trayApp.setToolTip('SNeicer\'s Doom Mod Manager')

# Creating menus for tray
trm_main = QtWidgets.QMenu()  # trm - tray menu, trma - tray menu action
trm_presets = QtWidgets.QMenu("Launch from preset")
trma_main_quit = QtWidgets.QAction("Quit")
trma_main_windowVisibility = QtWidgets.QAction("Show/Hide Manager")
trma_main_launchVanilla = QtWidgets.QAction("Launch vanilla (no mods)")

# Updating their contents
update_tray_menu()

# Connecting events to functions, setting a context menu for tray icon and making it visible
trayApp.activated.connect(show_hide_on_doubleclick)
trm_presets.triggered.connect(preset_selected)
trayApp.setContextMenu(trm_main)
trayApp.setVisible(True)

# Executing the whole thing
app.exec()
