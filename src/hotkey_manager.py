import sys

from pynput import keyboard

from PySide6.QtCore import (
    QKeyCombination,
    QObject,
    Qt,
    Signal,
)

from PySide6.QtGui import QKeySequence

def keycombo_to_pynput_str(key_combo):
    modifier_map = {
        Qt.ShiftModifier: '<shift>',
        Qt.ControlModifier: '<ctrl>',
        Qt.AltModifier: '<alt>',
        Qt.MetaModifier: '<cmd>',
    }
    if sys.platform == 'darwin':
        # qt swaps control/meta modfiiers on mac
        modifier_map[Qt.ControlModifier], modifier_map[Qt.MetaModifier] = modifier_map[Qt.MetaModifier], modifier_map[Qt.ControlModifier] 

    result = []
    for mod_bit,mod_str in modifier_map.items():
        if key_combo.keyboardModifiers() & mod_bit == mod_bit:
            result.append(mod_str)

    key_as_string = QKeySequence(key_combo.key()).toString()
    if key_as_string != '':
        result.append(key_as_string.lower())

    return '+'.join(result)


class HotkeyManager(QObject):
    hotkey_triggered = Signal(str, QKeyCombination)

    def __init__(self):
        super().__init__()
        self.action_keys = {}

    def set_hotkey(self, name, key_combo):
        if name in self.action_keys:
            self.remove_hotkey(name)

        if key_combo is None:
            return

        thread = keyboard.GlobalHotKeys({
            keycombo_to_pynput_str(key_combo): lambda:self.hotkey_triggered.emit(name, key_combo)
        })
        thread.start()
        self.action_keys[name] = {
            'combo': key_combo,
            'thread': thread,
        }

    def get_hotkey(self, name):
        if name in self.action_keys:
            return self.action_keys[name]['combo']

    def remove_hotkey(self, name):
        if name not in self.action_keys:
            return
        
        self.action_keys[name]['thread'].stop()
        del self.action_keys[name]
