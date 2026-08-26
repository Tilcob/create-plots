# main.py

import tkinter as tk
from gui import ExcelPlotApp

def on_closing():
    import sys
    try:
        root.quit()
        root.destroy()
    except Exception:
        pass
    finally:
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    app = ExcelPlotApp(root)
    root.mainloop()