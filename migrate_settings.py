#!/usr/bin/env python3
from qgis.PyQt.QtCore import QSettings

def migrate_settings():
    s = QSettings()
    old = "FloatingProtractor"
    new = "FloatingCompass"
    
    s.beginGroup(old)
    keys = s.childKeys()
    settings = {k: s.value(k) for k in keys}
    s.endGroup()
    
    if keys:
        s.beginGroup(new)
        for k, v in settings.items():
            s.setValue(k, v)
        s.endGroup()
        print(f"Migrated {len(keys)} settings")
    else:
        print("No settings to migrate")

if __name__ == "__main__":
    migrate_settings()
