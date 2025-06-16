import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "sys", "class_")))
from TerminalApp import TerminalApp
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "sys", "class_", "win", "system_class", "animations")))
from JumpingButton import JumpingButton
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "sys", "class_", "win", "system_class", "errors")))
from DeathScreen import DeathScreen
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "sys", "class_", "win", "system_class", "styles")))
from ToggleSwitch import ToggleSwitch
from Input import Input

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "sys", "class_", "win", "Widgets")))
from CalendarWidget import CalendarWidget
from VolumeControlWidget import VolumeControlWidget
from WifiWindow import WifiWindow

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps", "local")))
from init import DraggableResizableWindow
from cmd_window import CmdWindow
from browser_window import BrowserWindow
from settings_window import SettingsWindow

from updater import UpdateDialog
from updater import *

