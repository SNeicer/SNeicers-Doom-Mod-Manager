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
import datetime
import resources
import presetOperationsScript as Pos
import sys
import importlib
import traceback as tbacks

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
    config['ADDITIONAL'] = {'save_additional': False, 'save_cprompt': False, 'language': 'English'}
    with open('config.ini', 'w') as configFile:
        config.write(configFile)

if 'ADDITIONAL' not in config.sections():  # If config is from an older version, add new additional settings to it
    config['ADDITIONAL'] = {'save_additional': False, 'save_cprompt': False, 'language': 'English'}
    with open('config.ini', 'w') as configFile:
        config.write(configFile)

if 'language' not in config['ADDITIONAL']:  # If config is from an older version, add new language setting
    config['ADDITIONAL']['language'] = 'English'
    with open('config.ini', 'w') as configFile:
        config.write(configFile)


# Custom exception hook that will display critical errors and write log files
def sdmm_exception_hook(exctype, value, traceback):
    MWindow.show()
    # print(tbacks.format_exc(traceback)) - Only for code debugging
    with open('Error log from ' + str(datetime.date.today()) + '.log', mode='w') as log_file:
        log_file.write(f'exctype: {exctype}\nvalue: {value}\ntraceback: {tbacks.format_exc()}\n')
    info_box = QtWidgets.QMessageBox()
    info_box.critical(MWindow, 'Error!', f'Type: {exctype}\nValue: {value}\nTraceback: {tbacks.format_exc()}\n\nError '
                                         f'log file '
                                         f'created! Report this by creating a new issue on github!')


# Setting up custom exception hook
sys.excepthook = sdmm_exception_hook


# Function to show and hide main mod manager window
# Used in functions: show_hide_on_doubleclick, update_tray_menu
def show_hide_mwindow():
    match MWindow.isHidden():
        case True:
            MWindow.show()
        case False:
            MWindow.hide()
        case _:
            MWindow.show()


# Self-explanatory...
# Used in function: apply_config
def get_bool_from_string(string):
    if string == 'False':
        return False
    else:
        return True


# Function to launch the game with selected preset from tray menu
# Used only at line 525
@PyQt5.QtCore.pyqtSlot(QtWidgets.QAction)
def preset_selected(preset):
    launchScript.launch_game_advanced(config['PATHS']['sourceport_executable'], config['PATHS']['mod_folder'],
                                      Pos.get_list_of_mods_from_file(preset.text()), True,
                                      Pos.get_additional_arguments_from_file(preset.text()),
                                      Pos.get_custom_map_and_skill(preset.text()),
                                      Pos.get_extra_args(preset.text()))


# Triggers show_hide_mwindow function after double clicking at tray icon
# Used only at line 524
@PyQt5.QtCore.pyqtSlot(QtWidgets.QSystemTrayIcon.ActivationReason)
def show_hide_on_doubleclick(reason):
    if reason == QtWidgets.QSystemTrayIcon.DoubleClick:
        show_hide_mwindow()


# Fully updates tray menu by reconstructing it
# Used in functions: create_new_preset, delete_preset
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


def update_tray_menu_localization():
    trm_presets.setTitle(MWindow.lang.trayMenu_launchFromPreset)
    trma_main_quit.setText(MWindow.lang.trayMenu_quit)
    trma_main_windowVisibility.setText(MWindow.lang.trayMenu_showHideManager)
    trma_main_launchVanilla.setText(MWindow.lang.trayMenu_launchVanilla)


# Main Window class witch holds ui and functions to it
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("Main.ui", self)  # Loading ui file
        self.show()
        self.lang = self.startload_localization()
        self.apply_localization(False)
        self.reload_language_cbox()
        self.set_cbox_locale_label()
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
        self.cBox_language.currentTextChanged.connect(self.load_localization)

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
    # Used in initialization of MainWindow class
    def apply_config(self):
        self.lineE_SourcePortDir.setText(config['PATHS']['sourceport_executable'])
        self.lineE_ModDir.setText(config['PATHS']['mod_folder'])
        self.check_SaveAdditional.setChecked(get_bool_from_string(config['ADDITIONAL']['save_additional']))
        self.check_SaveCommandPrompt.setChecked(get_bool_from_string(config['ADDITIONAL']['save_cprompt']))

    # Resetting contents of language combo box to existing ones
    # Used in initialization of MainWindow class
    def reload_language_cbox(self):
        self.cBox_language.clear()
        existing_localizations = glob.glob('*.py', root_dir='localization\\')
        for locale in range(0, len(existing_localizations)):
            splitted_locale_name = existing_localizations[locale].split('.py')[0]
            self.cBox_language.addItem(splitted_locale_name)

    # Trying to load localization from config
    # if localization doesn't exist anymore, triggering failsafe and reverting back to english
    # Used in initialization of MainWindow class
    def startload_localization(self):
        info_box = QtWidgets.QMessageBox()
        if os.path.exists(f"localization/{config['ADDITIONAL']['language']}.py"):
            return importlib.import_module(f"localization.{config['ADDITIONAL']['language']}")
        else:
            info_box.critical(self, 'Error!', 'Localization file not found! Reverting back to English!')
            config['ADDITIONAL']['language'] = 'English'
            self.write_config_changes()
            return importlib.import_module('localization.English')

    # Loads up new localization variables to use
    # Used in initialization of MainWindow class
    def load_localization(self):
        info_box = QtWidgets.QMessageBox()
        if os.path.exists(f"localization/{self.cBox_language.currentText()}.py") and config['ADDITIONAL']['language'] != self.cBox_language.currentText():
            try:
                self.lang = importlib.import_module(f"localization.{self.cBox_language.currentText()}")
                config['ADDITIONAL']['language'] = self.cBox_language.currentText()
                self.write_config_changes()
                self.apply_localization(True)
            except:
                info_box.critical(self, 'Error!', 'Localization file failed importing! Reverting back to English!')
                self.lang = importlib.import_module('localization.English')
        else:
            info_box.critical(self, 'Error!', 'Localization file not found! Reverting back to English!')
            self.lang = importlib.import_module('localization.English')

    # Applies localization variables to texts
    # Used in function load_localization and in initialization of MainWindow class
    def apply_localization(self, update_menu):
        self.label_SourcePortDir.setText(self.lang.mainUi_sourceLabel)
        self.btn_BrowseModDir.setText(self.lang.mainUi_browseBtn)
        self.btn_BrowseSourcePortDir.setText(self.lang.mainUi_browseBtn)
        self.label_ModDir.setText(self.lang.mainUi_modDirLabel)
        self.tabw_MainTabs.setTabText(self.tabw_MainTabs.indexOf(self.tab), self.lang.mainUi_mainTab)
        self.check_AVG.setText(self.lang.addiUi_avgCheck)
        self.check_FastMonsters.setText(self.lang.addiUi_fmonCheck)
        self.check_NoMonsters.setText(self.lang.addiUi_nomonCheck)
        self.check_RespawningMonsters.setText(self.lang.addiUi_respmonCheck)
        self.check_NoAutoExec.setText(self.lang.addiUi_dissableAExecCheck)
        self.gBox_CustomStartMap.setTitle(self.lang.addiUi_customMapGroupBox)
        self.label_CustomMapName.setText(self.lang.addiUi_customMapLabel)
        self.gBox_CustomDifficulty.setTitle(self.lang.addiUi_customDifficultyGroupBox)
        self.label_CustomDifficulty.setText(self.lang.addiUi_customDifficultyLabel)
        self.label_CommandPrompt.setText(self.lang.addiUi_extraParamsLabel)
        self.check_SaveAdditional.setText(self.lang.addiUi_saveAdditionalSettingsCheck)
        self.check_SaveCommandPrompt.setText(self.lang.addiUi_saveExtraParamsCheck)
        self.tabw_MainTabs.setTabText(self.tabw_MainTabs.indexOf(self.tab_2), self.lang.mainUi_additionalTab)
        self.btn_LoadPreset.setText(self.lang.mainUi_loadPresetBtn)
        self.btn_SavePreset.setText(self.lang.mainUi_savePresetBtn)
        self.label_Preset.setText(self.lang.mainUi_presetLabel)
        self.label_language.setText(self.lang.mainUi_languageLabel)
        if update_menu:
            update_tray_menu_localization()

    # Updates combobox to match saved language in config
    # Used in initialization of MainWindow class
    def set_cbox_locale_label(self):
        found_index = self.cBox_language.findText(config['ADDITIONAL']['language'])
        if found_index != -1:
            self.cBox_language.setCurrentIndex(found_index)
        else:
            self.cBox_language.setCurrentIndex(0)

    # Saves changed things in config
    # Used in functions: set_mod_folder, set_save_additional_settings, load_localization
    # and in set_sourceport_executable
    @staticmethod
    def write_config_changes():
        with open('config.ini', 'w') as config_file:
            config.write(config_file)

    # Getting full path to sourceport executable
    # Used in initialization of MainWindow class
    def set_sourceport_executable(self):
        dir_to_exe = QtWidgets.QFileDialog.getOpenFileName(self, self.lang.fileDialog_setGzDoom, "C:\\",
                                                           "GzDoom (gzdoom.exe)")
        if dir_to_exe[0] != '':
            self.lineE_SourcePortDir.setText(dir_to_exe[0])
            config['PATHS']['sourceport_executable'] = dir_to_exe[0]
            self.write_config_changes()

    # Saving additional settings
    # Used in initialization of MainWindow class
    def set_save_additional_settings(self):
        config['ADDITIONAL']['save_additional'] = str(self.check_SaveAdditional.isChecked())
        config['ADDITIONAL']['save_cprompt'] = str(self.check_SaveCommandPrompt.isChecked())
        self.write_config_changes()

    # Adding or removing argument from ActiveArgs list after ui interaction
    # Used in initialization of MainWindow class
    def select_additional_argument(self, new_arg):
        if new_arg in self.ActiveArgs:
            self.ActiveArgs.remove(new_arg)
        else:
            self.ActiveArgs.append(new_arg)

        self.statusBar.showMessage(f'{self.lang.statusBar_curArgs}{self.ActiveArgs}')

    # REWRITE SOMEHOW!
    # Used in function: load_preset
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

        self.statusBar.showMessage(f'{self.lang.statusBar_curArgs}{self.ActiveArgs}')

    # Getting full path to the mod folder
    # Used in initialization of MainWindow class
    def set_mod_folder(self):
        cached_mod_folder = self.lineE_ModDir.text()
        dir_to_mod_folder = QtWidgets.QFileDialog.getExistingDirectory(self, self.lang.fileDialog_setModFolder, 'C:\\',
                                                                       QtWidgets.QFileDialog.ShowDirsOnly)
        if dir_to_mod_folder != '' and dir_to_mod_folder != cached_mod_folder:
            self.lineE_ModDir.setText(dir_to_mod_folder)
            config['PATHS']['mod_folder'] = dir_to_mod_folder
            self.write_config_changes()
            self.list_ActiveMods.clear()
            self.refresh_mod_list()

    # Deleting all activated mods from inactive mod list
    # Used in functions: load_preset, refresh_mod_list
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
                        self.statusBar.showMessage(self.lang.statusBar_deletingMods)
                        break

    # Activating a mod
    # Used in initialization of MainWindow class
    def activate_mod(self):
        try:
            self.list_ActiveMods.addItem(self.list_Mods.takeItem(self.list_Mods.row(self.list_Mods.selectedItems()[0])))
        except:
            pass

    # Deactivating a mod
    # Used in initialization of MainWindow class
    def deactivate_mod(self):
        try:
            self.list_Mods.addItem(
                self.list_ActiveMods.takeItem(self.list_ActiveMods.row(self.list_ActiveMods.selectedItems()[0])))
        except:
            pass

    # Saving all mods and arguments to preset
    # Used in initialization of MainWindow class
    def save_preset(self):
        info_box = QtWidgets.QMessageBox()
        active_count = self.list_ActiveMods.count()
        if self.cBox_ActivePreset.currentText() != '' and active_count > 0:
            with open(f'ModPresets\\{self.cBox_ActivePreset.currentText()}.dmmp', 'w') as PresetFile:
                for mod in range(active_count):
                    active_mod_name = self.list_ActiveMods.item(mod).text()
                    PresetFile.write(f'{active_mod_name}\n')
                if config['ADDITIONAL']['save_cprompt'] == 'True':
                    PresetFile.write(' #EXTRA: ')
                    PresetFile.write(self.tEdit_CustomCommandPrompt.toPlainText() + '\n')
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
            info_box.information(self, self.lang.infoBox_savingPresetTitle, self.lang.infoBox_savingPresetText)
        else:
            info_box.warning(self, self.lang.infoBox_savingPresetTitle, self.lang.infoBox_savingPresetErrorText)

    # Loading all names of existing presets from ModPresets folder
    # Used in initialization of MainWindow class
    # Used in functions: create_new_preset, delete_preset
    def load_presets_in_cbox(self):
        presets = glob.glob('*.dmmp', root_dir='ModPresets\\')
        self.cBox_ActivePreset.clear()
        if len(presets) > 0:
            for preset in presets:
                self.cBox_ActivePreset.addItem(preset.split('.dmmp')[0])

    # Creating a new preset file with custom name
    # Used in initialization of MainWindow class
    def create_new_preset(self):
        try:
            info_box = QtWidgets.QMessageBox()
            preset_name = QtWidgets.QInputDialog.getText(self, self.lang.inputDialog_newPresetTitle,
                                                         self.lang.inputDialog_newPresetText,
                                                         QtWidgets.QLineEdit.Normal, '')
            if preset_name[1]:
                if preset_name[0] != '' and preset_name[0][0] != '.':
                    if not os.path.exists(f'ModPresets\\{preset_name[0]}.dmmp'):
                        if re.match(self.presetNameValidator, preset_name[0]) is not None:
                            with open(f'ModPresets\\{preset_name[0]}.dmmp', 'w'):
                                pass
                            self.load_presets_in_cbox()
                            self.cBox_ActivePreset.setCurrentIndex(self.cBox_ActivePreset.findText(preset_name[0]))
                            info_box.information(self, self.lang.infoBox_newPresetTitle,
                                                 self.lang.infoBox_newPresetCreatedText.format(pname=preset_name[0]))
                            update_tray_menu()
                        else:
                            info_box.warning(self, self.lang.infoBox_newPresetTitle,
                                             self.lang.infoBox_newPresetRegexErrorText)
                    else:
                        info_box.warning(self, self.lang.infoBox_newPresetTitle,
                                         self.lang.infoBox_newPresetAlrExists.format(pname=preset_name[0]))
                else:
                    info_box.warning(self, self.lang.infoBox_newPresetTitle, self.lang.infoBox_newPresetNoNameError)
        except Exception as ex:
            self.statusBar.showMessage(ex)

    # Fully deleting preset from existence
    # Used in initialization of MainWindow class
    def delete_preset(self):
        try:
            info_box = QtWidgets.QMessageBox()
            if self.cBox_ActivePreset.currentText() != '':
                preset_temp_name = self.cBox_ActivePreset.currentText()
                sure_box = QtWidgets.QMessageBox()
                sure_box_result = sure_box.question(self, self.lang.messageBox_delPresetTitle,
                                                    self.lang.messageBox_delPresetText.format(pname=preset_temp_name),
                                                    sure_box.Yes | sure_box.No)

                if sure_box_result == sure_box.Yes:
                    try:
                        os.remove(f'ModPresets\\{preset_temp_name}.dmmp')
                        self.load_presets_in_cbox()
                        info_box.information(self, self.lang.infoBox_delPresetTitle,
                                             self.lang.infoBox_delPresetSucText.format(pname=preset_temp_name))
                        update_tray_menu()
                    except Exception as ex:
                        self.statusBar.showMessage(ex)
            else:
                info_box.warning(self, self.lang.infoBox_delPresetTitle, self.lang.infoBox_delPresetNothingText)
        except Exception as ex:
            self.statusBar.showMessage(ex)

    # Upping mod priority in active mods list
    # Used in initialization of MainWindow class
    def up_mod_priority(self):
        try:
            selected_mod_row = self.list_ActiveMods.currentRow()
            selected_mod = self.list_ActiveMods.takeItem(selected_mod_row)

            self.list_ActiveMods.insertItem(selected_mod_row - 1, selected_mod)
            self.list_ActiveMods.setCurrentRow(selected_mod_row - 1)
        except Exception as ex:
            self.statusBar.showMessage(ex)

    # Lowering mod priority in active mods list
    # Used in initialization of MainWindow class
    def lower_mod_priority(self):
        try:
            selected_mod_row = self.list_ActiveMods.currentRow()
            selected_mod = self.list_ActiveMods.takeItem(selected_mod_row)

            self.list_ActiveMods.insertItem(selected_mod_row + 1, selected_mod)
            self.list_ActiveMods.setCurrentRow(selected_mod_row + 1)
        except Exception as ex:
            self.statusBar.showMessage(ex)

    # Refreshing list of inactive mods and deleting all active mods from inactive list
    # Used in initialization of MainWindow class
    # Used in functions: load_preset, set_mod_folder
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
    # Used in initialization of MainWindow class
    def load_preset(self):
        try:
            info_box = QtWidgets.QMessageBox()
            self.list_ActiveMods.clear()
            self.refresh_mod_list()
            if self.cBox_ActivePreset.currentText() != '':
                mod_list = Pos.get_list_of_mods_from_file(self.cBox_ActivePreset.currentText())
                arg_list = Pos.get_additional_arguments_from_file(self.cBox_ActivePreset.currentText())
                cmap_andcskill = Pos.get_custom_map_and_skill(self.cBox_ActivePreset.currentText())
                extra_args = Pos.get_extra_args(self.cBox_ActivePreset.currentText())
                if len(arg_list) > 0:
                    self.ActiveArgs = arg_list
                if cmap_andcskill[0] != '':
                    self.tEdit_CustomStartMapName.setText(cmap_andcskill[0])
                    self.gBox_CustomStartMap.setChecked(True)
                if cmap_andcskill[1] != '':
                    self.gBox_CustomDifficulty.setChecked(True)
                    self.cBox_CustomDifficulty.setCurrentIndex(int(cmap_andcskill[1]) - 1)
                if extra_args != '':
                    self.tEdit_CustomCommandPrompt.setPlainText(extra_args)
                for mod in range(len(mod_list)):
                    if ' #' not in mod_list[mod]:
                        self.list_ActiveMods.addItem(mod_list[mod])
                self.delete_active_from_inactive_mods()
                self.set_checks_for_additional_arguments()
                info_box.information(self, self.lang.infoBox_loadPresetTitle,
                                     self.lang.infoBox_loadPresetSucText.format(pname=self.cBox_ActivePreset.currentText()))
            else:
                info_box.warning(self, self.lang.infoBox_loadPresetTitle, self.lang.infoBox_loadPresetNothingText)
        except Exception as ex:
            self.statusBar.showMessage("ERROR! " + str(ex))

    # Launching game with currently selected in ui mods and arguments
    # Used in initialization of MainWindow class
    def launch_game(self):
        mods_to_launch_with = []
        getted_cmap_and_cskill = [self.tEdit_CustomStartMapName.toPlainText(),
                                  self.cBox_CustomDifficulty.currentText().split('skill ')[1].replace(')', '')]
        extra_args = self.tEdit_CustomCommandPrompt.toPlainText()
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
                                                      [getted_cmap_and_cskill[0], ''], extra_args)
                case 2:
                    launchScript.launch_game_advanced(config['PATHS']['sourceport_executable'],
                                                      config['PATHS']['mod_folder'],
                                                      mods_to_launch_with, True, self.ActiveArgs,
                                                      ['', getted_cmap_and_cskill[1]], extra_args)
                case 3:
                    launchScript.launch_game_advanced(config['PATHS']['sourceport_executable'],
                                                      config['PATHS']['mod_folder'],
                                                      mods_to_launch_with, True, self.ActiveArgs,
                                                      [getted_cmap_and_cskill[0], getted_cmap_and_cskill[1]],
                                                      extra_args)
                case _:
                    launchScript.launch_game_advanced(config['PATHS']['sourceport_executable'],
                                                      config['PATHS']['mod_folder'],
                                                      mods_to_launch_with, True, self.ActiveArgs,
                                                      ['', ''], extra_args)
        else:
            match run_code:
                case 1:
                    launchScript.launch_game_advanced(config['PATHS']['sourceport_executable'],
                                                      config['PATHS']['mod_folder'],
                                                      [], False, self.ActiveArgs, [getted_cmap_and_cskill[0], ''],
                                                      extra_args)
                case 2:
                    launchScript.launch_game_advanced(config['PATHS']['sourceport_executable'],
                                                      config['PATHS']['mod_folder'],
                                                      [], False, self.ActiveArgs, ['', getted_cmap_and_cskill[1]],
                                                      extra_args)
                case 3:
                    launchScript.launch_game_advanced(config['PATHS']['sourceport_executable'],
                                                      config['PATHS']['mod_folder'],
                                                      [], False, self.ActiveArgs,
                                                      [getted_cmap_and_cskill[0], getted_cmap_and_cskill[1]],
                                                      extra_args)
                case _:
                    launchScript.launch_game_advanced(config['PATHS']['sourceport_executable'],
                                                      config['PATHS']['mod_folder'],
                                                      [], False, self.ActiveArgs,
                                                      ['', ''], extra_args)


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
trm_presets = QtWidgets.QMenu(MWindow.lang.trayMenu_launchFromPreset)
trma_main_quit = QtWidgets.QAction(MWindow.lang.trayMenu_quit)
trma_main_windowVisibility = QtWidgets.QAction(MWindow.lang.trayMenu_showHideManager)
trma_main_launchVanilla = QtWidgets.QAction(MWindow.lang.trayMenu_launchVanilla)

# Updating their contents
update_tray_menu()

# Connecting events to functions, setting a context menu for tray icon and making it visible
trma_main_quit.triggered.connect(app.quit)
trma_main_windowVisibility.triggered.connect(show_hide_mwindow)
trma_main_launchVanilla.triggered.connect(
    lambda: launchScript.launch_game_advanced(config['PATHS']['sourceport_executable'],
                                              config['PATHS']['mod_folder'],
                                              [], False, [], ['', '']))
trayApp.activated.connect(show_hide_on_doubleclick)
trm_presets.triggered.connect(preset_selected)
trayApp.setContextMenu(trm_main)
trayApp.setVisible(True)

# Executing the whole thing
app.exec()
