import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import pandas as pd
import unicodedata

from plotting import create_plot_from_dataframe
from utils import resource_path
from ToolTip import ToolTip

max_graph_num = 10


class ExcelPlotApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Messwerte zu Diagramm")

        self.left_axis_buttons = {}  # {'add': add_btn, 'remove': remove_btn}
        self.right_axis_buttons = {}

        self.filepath = ""
        self.df = None
        self.logo_path = ""
        self.standard_logo_path = ""

        try:
            self.master.iconbitmap(resource_path("app/resources/Logo_Raug.ico"))
        except:
            pass

        logo_file = resource_path("app/resources/Logo_Raug-klein.png")
        if os.path.exists(logo_file):
            img = Image.open(logo_file)
            self.logo_img = ImageTk.PhotoImage(img)
            logo_label = tk.Label(master, image=self.logo_img, borderwidth=0)
            logo_label.place(relx=1.0, y=0, anchor="ne")

        tk.Label(master, text="Diagramm-Titel:").pack()
        self.title_var = tk.StringVar()
        tk.Entry(master, textvariable=self.title_var).pack()

        tk.Label(master, text="Datum (optional, z.B. 26.08.2026):").pack()
        self.date_var = tk.StringVar()
        self.date_entry = tk.Entry(master, textvariable=self.date_var)
        self.date_entry.pack()
        ToolTip(
            self.date_entry,
            "Falls ausgefüllt, wird das Datum oben links über dem Diagramm angezeigt. Leer lassen = nichts anzeigen.",
        )

        self.load_frame = tk.Frame(master)
        self.load_frame.pack(pady=10)
        self.load_button = tk.Button(
            self.load_frame, text="Excel-Datei öffnen", command=self.load_file
        )
        self.load_button.pack(side="left")
        self.check_excel = tk.Label(
            self.load_frame, text="✔", fg="green", font=("Arial", 14)
        )
        self.check_excel.pack(side="left", padx=5)
        self.check_excel.pack_forget()

        tk.Label(master, text="Feinheit des Grids (z.B. 1=Standard, 2=feiner):").pack()
        self.tick_fine_var = tk.StringVar(value="1")
        self.tick_entry = tk.Entry(master, textvariable=self.tick_fine_var)
        self.tick_entry.pack()
        ToolTip(
            self.tick_entry,
            "Je höher die Zahl, desto feiner wird das Grid. Die Abstände zwischen den Hauptstrichen werden kleiner.",
        )

        tk.Label(master, text="Diagrammgröße in % (z.B. 100 = Standard):").pack()
        self.size_percent_var = tk.StringVar(value="100")
        self.size_percent_entry = tk.Entry(master, textvariable=self.size_percent_var)
        self.size_percent_entry.pack()
        ToolTip(
            self.size_percent_entry,
            "Skaliert die Größe des Diagramms. 100% entspricht der Standardgröße (A4 quer).",
        )

        xaxis_frame = tk.Frame(master)
        xaxis_frame.pack(pady=10)

        tk.Label(xaxis_frame, text="X-Achse Beschriftung:").pack(side="left")
        self.xlabel_var = tk.StringVar()
        tk.Entry(xaxis_frame, textvariable=self.xlabel_var, width=20).pack(
            side="left", padx=(5, 15)
        )

        tk.Label(xaxis_frame, text="Spaltenname der X-Achse:").pack(side="left")
        self.col1_var = tk.StringVar()
        self.col1_combo = ttk.Combobox(
            xaxis_frame, textvariable=self.col1_var, state="readonly", width=20
        )
        self.col1_combo.pack(side="left", padx=5)

        tk.Label(master, text="Y-Achse links Beschriftung:").pack()
        self.ylabel_var = tk.StringVar()
        tk.Entry(master, textvariable=self.ylabel_var).pack()

        tk.Label(master, text="Y-Achse rechts Beschriftung:").pack()
        self.ylabel2_var = tk.StringVar()
        tk.Entry(master, textvariable=self.ylabel2_var).pack()

        # Container für beide Achsen
        self.yaxis_container = tk.Frame(master)
        self.yaxis_container.pack(pady=10, fill="x")

        # Achsen-Bereiche erstellen
        (
            self.line_label_vars_left,
            self.col_vars_left,
            self.color_vars_left,
            self.graph_frames_left,
        ) = self.create_axis_section(self.yaxis_container, "Linke Y-Achse")
        (
            self.line_label_vars_right,
            self.col_vars_right,
            self.color_vars_right,
            self.graph_frames_right,
        ) = self.create_axis_section(self.yaxis_container, "Rechte Y-Achse")

        self.starts_at_min_var = tk.BooleanVar()
        self.starts_at_min_check_box = tk.Checkbutton(
            master,
            text="Y-Achsenstart bei Datenminimum",
            variable=self.starts_at_min_var,
        )
        self.starts_at_min_check_box.pack(padx=10)
        ToolTip(
            self.starts_at_min_check_box,
            "Falls aktiviert, startet die Y-Achse bei dem kleinsten Wert der Daten statt bei 0.",
        )

        # Logo-Bereich
        self.logo_frame = tk.Frame(master)
        self.logo_frame.pack(pady=5)
        self.logo_button = tk.Button(
            self.logo_frame,
            text="Externes Logo auswählen (optional)",
            command=self.select_logo,
        )
        self.logo_button.pack(side="left")
        self.check_logo = tk.Label(
            self.logo_frame, text="✔", fg="green", font=("Arial", 14)
        )
        self.check_logo.pack(side="left", padx=5)
        self.check_logo.pack_forget()
        self.standard_logo_var = tk.BooleanVar()
        self.standard_logo_check_box = tk.Checkbutton(
            self.logo_frame,
            text="Standard Logo (Raug)",
            variable=self.standard_logo_var,
            command=self.toggle_standard_logo,
        )
        self.standard_logo_check_box.pack(side="right", padx=10)
        ToolTip(
            self.standard_logo_check_box,
            "Falls aktiviert, wird das Standard-Logo von RAUG verwendet.",
        )

        tk.Button(
            master,
            text="Diagramm erstellen & als PDF speichern",
            command=self.create_plot,
        ).pack(pady=10)

    def create_axis_section(self, parent, axis_name):
        frame = tk.Frame(parent, bd=2, relief="groove", padx=5, pady=5)
        frame.pack(side="left", expand=True, fill="both", padx=5)

        tk.Label(frame, text=axis_name, font=("Arial", 10, "bold")).pack()

        graph_list = []
        label_vars = []
        col_vars = []
        color_vars = []

        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=5)

        def add_graph():
            if len(graph_list) >= max_graph_num:
                return
            row = tk.Frame(frame)
            row.pack(fill="x", pady=2)

            lbl_var = tk.StringVar()
            col_var = tk.StringVar()
            color_var = tk.StringVar(value="blau")

            tk.Label(row, text=f"Kurvenbezeichnung {len(graph_list) + 1}:").pack(
                side="left", padx=2
            )
            tk.Entry(row, textvariable=lbl_var, width=12).pack(side="left", padx=2)

            columns = self.df.columns.tolist() if self.df is not None else []
            col_combo = ttk.Combobox(
                row, textvariable=col_var, width=15, state="readonly", values=columns
            )
            col_combo.pack(side="left", padx=2)

            color_combo = ttk.Combobox(
                row,
                textvariable=color_var,
                width=10,
                state="readonly",
                values=[
                    "rot",
                    "blau",
                    "grün",
                    "schwarz",
                    "gelb",
                    "orange",
                    "lila",
                    "pink",
                ],
            )
            color_combo.pack(side="left", padx=2)

            graph_list.append(row)
            label_vars.append(lbl_var)
            col_vars.append(col_var)
            color_vars.append(color_var)

            if len(graph_list) >= max_graph_num:
                add_btn.config(state="disabled")
            if len(graph_list) > 0:
                remove_btn.config(state="normal")

        def remove_graph():
            if not graph_list:
                return
            graph_list[-1].destroy()
            graph_list.pop()
            label_vars.pop()
            col_vars.pop()
            color_vars.pop()

            if len(graph_list) < max_graph_num:
                add_btn.config(state="normal")
            if len(graph_list) == 0:
                remove_btn.config(state="disabled")

        add_btn = tk.Button(btn_frame, text="+", command=add_graph)
        add_btn.pack(side="left")
        ToolTip(add_btn, "Hinzufügen von Graphen")
        remove_btn = tk.Button(
            btn_frame, text="–", command=remove_graph, state="disabled"
        )
        remove_btn.pack(side="left", padx=5)
        ToolTip(remove_btn, "Entfernen von Graphen")

        if axis_name.startswith("Linke"):
            self.left_axis_buttons["add"] = add_btn
            self.left_axis_buttons["remove"] = remove_btn
        else:
            self.right_axis_buttons["add"] = add_btn
            self.right_axis_buttons["remove"] = remove_btn

        return label_vars, col_vars, color_vars, graph_list

    def toggle_standard_logo(self):
        if self.standard_logo_var.get():
            self.standard_logo_path = resource_path(
                "app/resources/Logo_Raug-Diagramm.png"
            )
            self.logo_path = self.standard_logo_path
            self.check_logo.pack_forget()
        else:
            self.standard_logo_path = ""
            self.logo_path = ""
            self.check_logo.pack_forget()

    def load_file(self):
        self.filepath = filedialog.askopenfilename(
            filetypes=[("Excel-Dateien", "*.xlsx *.xls")]
        )
        if self.filepath:
            try:
                self.df = pd.read_excel(self.filepath, decimal=",")
                self.df.columns = [
                    unicodedata.normalize("NFC", col).strip() for col in self.df.columns
                ]
                messagebox.showinfo(
                    "Datei geladen", "Spalten gefunden:\n" + ", ".join(self.df.columns)
                )
                self.check_excel.pack(side="left", padx=5)

                # Update X-Achse Combobox
                self.col1_combo["values"] = self.df.columns.tolist()

                # Alte Graph-Zeilen löschen und Listen zurücksetzen
                for frames, label_vars, col_vars, color_vars, buttons in [
                    (
                        self.graph_frames_left,
                        self.line_label_vars_left,
                        self.col_vars_left,
                        self.color_vars_left,
                        self.left_axis_buttons,
                    ),
                    (
                        self.graph_frames_right,
                        self.line_label_vars_right,
                        self.col_vars_right,
                        self.color_vars_right,
                        self.right_axis_buttons,
                    ),
                ]:
                    while frames:
                        f = frames.pop()
                        f.destroy()
                    label_vars.clear()
                    col_vars.clear()
                    color_vars.clear()

                    # Buttons auf Ausgangszustand zurücksetzen
                    if buttons:
                        buttons["add"].config(state="normal")
                        buttons["remove"].config(state="disabled")

            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Laden der Datei:\n{e}")

    def select_logo(self):
        path = filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.png;*.jpg;*.jpeg;*.bmp"),
                ("All files", "*.*"),
            ]
        )
        if path:
            self.logo_path = path
            self.standard_logo_var.set(False)
            self.standard_logo_path = ""
            messagebox.showinfo("Logo", "Logo ausgewählt: " + path)
            self.check_logo.pack(side="left", padx=5)

    def create_plot(self):
        if self.df is None:
            messagebox.showerror("Fehler", "Bitte zuerst eine Excel-Datei laden.")
            return

        x_col = self.col1_var.get().strip()
        if not x_col:
            messagebox.showerror("Fehler", "Bitte eine X-Achse-Spalte angeben.")
            return

        try:
            tick_factor = float(self.tick_fine_var.get())
        except:
            tick_factor = 1.0

        try:
            size_percent = float(self.size_percent_var.get())
            if size_percent <= 0:
                size_percent = 100.0
        except:
            size_percent = 100.0

        try:
            y_configs = []
            graph_count = 0

            # Linke Achse
            for lbl_var, col_var, color_var in zip(
                self.line_label_vars_left, self.col_vars_left, self.color_vars_left
            ):
                col = col_var.get().strip()
                if not col:
                    continue
                graph_count += 1
                label = lbl_var.get().strip() or f"Graph {graph_count}"
                color = color_var.get().strip() or "blau"
                y_configs.append(
                    {"col": col, "label": label, "axis": "left", "color": color}
                )

            # Rechte Achse
            for lbl_var, col_var, color_var in zip(
                self.line_label_vars_right, self.col_vars_right, self.color_vars_right
            ):
                col = col_var.get().strip()
                if not col:
                    continue
                graph_count += 1
                label = lbl_var.get().strip() or f"Graph {graph_count}"
                color = color_var.get().strip() or "blau"
                y_configs.append(
                    {"col": col, "label": label, "axis": "right", "color": color}
                )

            output_path = create_plot_from_dataframe(
                df=self.df,
                filepath=self.filepath,
                x_col=x_col,
                y_configs=y_configs,
                title=self.title_var.get().strip(),
                date_text=self.date_var.get().strip(),
                xlabel=self.xlabel_var.get().strip(),
                ylabel=self.ylabel_var.get().strip(),
                ylabel2=self.ylabel2_var.get().strip(),
                logo_path=self.logo_path or self.standard_logo_path,
                tick_factor=tick_factor,
                is_startpoint_min_val=self.starts_at_min_var.get(),
                size_percent=size_percent,
            )

            messagebox.showinfo("Gespeichert", f"PDF gespeichert unter:\n{output_path}")
            if os.name == "nt":
                os.startfile(output_path)

        except Exception as e:
            messagebox.showerror("Fehler beim Erstellen des Diagramms", str(e))
