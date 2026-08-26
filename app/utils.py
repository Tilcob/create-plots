# utils.py

import datetime
import pandas as pd
import numpy as np
import sys
import os

def resource_path(relative_path):
    """Gibt den absoluten Pfad zur Ressource zurück,
    auch wenn das Programm als PyInstaller-exe läuft."""
    try:
        # PyInstaller temporärer Ordner
        base_path = sys._MEIPASS
    except Exception:
        # Normales Python-Script: Arbeitsverzeichnis nehmen
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def convert_to_datetime(val):
    """Konvertiert Zeit oder Strings in datetime."""
    if isinstance(val, datetime.time):
        return datetime.datetime.combine(datetime.date(2000, 1, 1), val)
    try:
        return pd.to_datetime(val)
    except:
        return pd.NaT

def show_checkmark(button, check_label, master):
    """Platziert das grüne Häkchen neben einem Button."""
    button.update_idletasks()
    bx = button.winfo_rootx()
    by = button.winfo_rooty()
    bw = button.winfo_width()
    bh = button.winfo_height()

    mx = master.winfo_rootx()
    my = master.winfo_rooty()

    rel_x = bx - mx + bw + 5
    rel_y = by - my + bh // 2 - 10

    check_label.place(x=rel_x, y=rel_y)

def get_nice_tick_interval(vmin, vmax, target_steps=5, factor=1.0):
    """Berechnet ein angenehmes Intervall für Achsenticks."""
    target_steps *= factor
    if vmin == vmax:
        vmin -= 1
        vmax += 1
    raw_interval = (vmax - vmin) / target_steps
    exponent = np.floor(np.log10(raw_interval))
    fraction = raw_interval / 10**exponent
    if fraction <= 1:
        nice_fraction = 1
    elif fraction <= 2:
        nice_fraction = 2
    elif fraction <= 5:
        nice_fraction = 5
    else:
        nice_fraction = 10
    return nice_fraction * 10**exponent

def resource_path(relative_path):
    """
    Gibt den absoluten Pfad zur Datei zurück – funktioniert auch mit pyinstaller --onefile.
    """
    try:
        # Wenn gebundelt (Onefile), liegt alles in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)