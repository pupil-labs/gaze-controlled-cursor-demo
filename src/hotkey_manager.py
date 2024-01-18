from system_hotkey import SystemHotkey

from PySide6.QtCore import (
    QKeyCombination,
    QObject,
    Qt,
    Signal,
)

from PySide6.QtGui import QKeySequence

def keycombo_to_str_tuple(key_combo):
    modifier_map = {
        Qt.ShiftModifier: 'shift',
        Qt.ControlModifier: 'control',
        Qt.AltModifier: 'alt',
        Qt.MetaModifier: 'meta',
    }

    result = []
    for mod_bit,mod_str in modifier_map.items():
        if key_combo.keyboardModifiers() & mod_bit == mod_bit:
            result.append(mod_str)

    key_as_string = QKeySequence(key_combo.key()).toString()
    if key_as_string != '':
        result.append(key_as_string.lower())

    return result


class HotkeyManager(QObject):
    hotkey_triggered = Signal(str, QKeyCombination)

    def __init__(self):
        super().__init__()
        self.hk = SystemHotkey()

        self.action_keys = {}

    def set_hotkey(self, name, key_combo):
        if name in self.action_keys:
            self.remove_hotkey(name)

        if key_combo is None:
            return

        self.action_keys[name] = key_combo
        self.hk.register(keycombo_to_str_tuple(key_combo), callback=lambda _:self.hotkey_triggered.emit(name, key_combo))

    def get_hotkey(self, name):
        if name in self.action_keys:
            return self.action_keys[name]

    def remove_hotkey(self, name):
        key_combo = self.action_keys[name]
        self.hk.unregister(keycombo_to_str_tuple(key_combo))

        del self.action_keys[name]
