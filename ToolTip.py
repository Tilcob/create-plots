import tkinter as tk

class ToolTip:
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.after_id = None
        
        widget.bind("<Enter>", self.schedule_show)
        widget.bind("<Leave>", self.hide_tooltip)
        
    def schedule_show(self, event=None):
        # Falls schon ein Timer läuft, abbrechen
        self.cancel_scheduled()
        # Timer setzen
        self.after_id = self.widget.after(self.delay, self.show_tooltip)

    def cancel_scheduled(self):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        
    def show_tooltip(self, event=None):
        self.cancel_scheduled()
        if self.tooltip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Kein Rahmen/Fensterleisten
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw, text=self.text, justify='left',
            background="#ffffe0", relief='solid', borderwidth=1,
            font=("tahoma", 9)
        )
        label.pack(ipadx=4, ipady=2)
        
    def hide_tooltip(self, event=None):
        self.cancel_scheduled()
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None