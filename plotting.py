import os
import matplotlib.pyplot as plt
from numpy import round
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib.ticker import MultipleLocator
import pandas as pd
from PIL import Image
from utils import convert_to_datetime, get_nice_tick_interval, resource_path


def create_plot_from_dataframe(
    df,
    filepath,
    x_col,
    y_configs,
    title,
    xlabel,
    ylabel,
    ylabel2,
    logo_path="",
    tick_factor=1.0,
    is_startpoint_min_val=False,
    size_percent=100.0,
    date_text="",
):
    if x_col not in df.columns:
        raise ValueError(f"Spalte '{x_col}' nicht gefunden.")

    # Farbzuordnung (mindestens 8 Farben)
    color_map = {
        "rot": "red",
        "blau": "blue",
        "grün": "green",
        "schwarz": "black",
        "gelb": "yellow",
        "orange": "orange",
        "lila": "purple",
        "pink": "pink",
    }

    x_raw = df[x_col]
    x = (
        x_raw
        if pd.api.types.is_numeric_dtype(x_raw)
        or pd.api.types.is_datetime64_any_dtype(x_raw)
        else x_raw.apply(convert_to_datetime)
    )
    valid_x_mask = ~x.isna()
    x_valid = x[valid_x_mask]

    fig, ax = plt.subplots(figsize=(11.69, 8.27), dpi=200)
    ax2 = None

    y_data_left = []
    y_data_right = []

    for config in y_configs:
        col = config["col"]
        label = config["label"]
        axis = config.get("axis", "left")
        color_choice = config.get("color", "").lower()
        color = color_map.get(color_choice, color_choice if color_choice else None)
        if not col or col not in df.columns:
            continue

        y = pd.to_numeric(df[col], errors="coerce")
        valid_y_mask = y.notna()
        valid_mask = valid_x_mask & valid_y_mask

        x_clean = x[valid_mask]
        y_clean = y[valid_mask].astype(float)

        if y_clean.empty:
            continue

        entry = (x_clean, y_clean, label, color)
        if axis == "left":
            y_data_left.append(entry)
        else:
            if not ax2:
                ax2 = ax.twinx()
            y_data_right.append(entry)

    ax.set_xlim(x.min(), x.max())

    for x_vals, y_vals, label, color in y_data_left:
        ax.plot(x_vals, y_vals, label=label, color=color)

    if ax2:
        for x_vals, y_vals, label, color in y_data_right:
            ax2.plot(x_vals, y_vals, label=label, color=color)

    # Legende
    lines_1, labels_1 = ax.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels() if ax2 else ([], [])
    ax.legend(
        lines_1 + lines_2,
        labels_1 + labels_2,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        ncol=10,
    )

    # X-Achse formatieren
    if pd.api.types.is_datetime64_any_dtype(x_valid):
        locator = mdates.AutoDateLocator()
        formatter = mdates.DateFormatter("%d.%m.%Y\n%H:%M")
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(locator)

        ax.figure.canvas.draw()

        major_ticks = locator()
        if len(major_ticks) >= 2:
            major_step_days = major_ticks[1] - major_ticks[0]

            # Minor-Schritt = 1/5 vom Major-Schritt
            minor_step_days = major_step_days / 5.0

            # Locator für Minor-Ticks bauen
            ax.xaxis.set_minor_locator(MultipleLocator(minor_step_days))
    else:
        xmin, xmax = x_valid.min(), x_valid.max()
        if xmin > 0:
            xmin = 0
        major_x_interval = get_nice_tick_interval(xmin, xmax, 5) / tick_factor
        ax.xaxis.set_major_locator(MultipleLocator(major_x_interval))
        ax.xaxis.set_minor_locator(MultipleLocator(major_x_interval / 5))
        ax.set_xlim(xmin, xmax)

    if y_data_left:
        all_left = pd.concat([y for _, y, _, _ in y_data_left])
        ymin_left, ymax_left = all_left.min(), all_left.max()
        if not is_startpoint_min_val:
            ymin_left = 0
        else:
            ymin_left *= 0.9
        if ymin_left == ymax_left or ymax_left - ymin_left <= 0.01:
            ymax_left += 1
        margin_left = ymax_left * 1.1
        ax.set_ylim(ymin_left, margin_left)
        major_y_left = get_nice_tick_interval(ymin_left, ymax_left, 5) / tick_factor
        ax.yaxis.set_major_locator(ticker.MultipleLocator(major_y_left))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(major_y_left / 5))

    # --- WICHTIG: jetzt zeichnen lassen ---
    fig.canvas.draw()

    # Y-Achse rechts unabhängig skalieren, aber gleiche Positionen übernehmen
    if ax2 and y_data_right:
        all_right = pd.concat([y for _, y, _, _ in y_data_right])

        # Startwert 0 erzwingen
        ymin_right = all_right.min()
        ymax_right = all_right.max()

        if not is_startpoint_min_val:
            ymin_right = 0
        else:
            ymin_right *= 0.9

        if ymax_right == 0:
            ymax_right = 1
        ymax_right *= 1.1  # kleiner Puffer nach oben

        ax2.set_ylim(ymin_right, ymax_right)

        # map left major ticks -> right coords
        y0l, y1l = ax.get_ylim()
        y0r, y1r = ax2.get_ylim()
        left_major = ax.get_yticks()
        frac = (left_major - y0l) / (y1l - y0l)
        right_major = y0r + frac * (y1r - y0r)
        ax2.yaxis.set_major_locator(ticker.FixedLocator(round(right_major, 3)))

        # this is optional but you can mirror minor ticks too
        left_minor = ax.yaxis.get_minorticklocs()
        if len(left_minor):
            frac_m = (left_minor - y0l) / (y1l - y0l)
            right_minor = y0r + frac_m * (y1r - y0r)
            ax2.yaxis.set_minor_locator(ticker.FixedLocator(right_minor))

    # Achsentitel
    ax.set_title(title or "Diagramm")
    ax.set_xlabel(xlabel or "x-Achse")
    ax.set_ylabel(ylabel or "y-Achse 1")
    if ax2:
        ax2.set_ylabel(ylabel2 or "y-Achse 2")

    if date_text:
        ax.text(
            0.0,
            1.06,
            date_text,
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=10,
        )

    # Raster
    ax.grid(True, which="major", linestyle="-", linewidth=0.5)
    ax.grid(True, which="minor", linestyle="--", linewidth=0.3)

    # Optional: Logo
    if logo_path:
        try:
            logo_img = Image.open(resource_path(logo_path))
            dpi = fig.dpi
            fig_width, fig_height = fig.get_size_inches()
            width_frac = logo_img.width / (dpi * fig_width)
            height_frac = logo_img.height / (dpi * fig_height)
            left = 1 - width_frac - 0.01
            bottom = 1 - height_frac - 0.01
            ax_logo = fig.add_axes(
                [left, bottom, width_frac, height_frac], anchor="NE", zorder=10
            )
            ax_logo.imshow(logo_img)
            ax_logo.axis("off")
            plt.subplots_adjust(left=0.065, right=0.93, top=0.88, bottom=0.16)
        except Exception as e:
            print(f"Logo konnte nicht geladen werden: {e}")
    else:
        plt.subplots_adjust(left=0.08, right=0.95, top=0.92, bottom=0.16)

    scale = size_percent / 100.0

    fig.canvas.draw()  # aktuelle Layout-Position sicherstellen

    pos = ax.get_position()  # Position der Achse in Seiten-Anteilen (0–1)
    cx = pos.x0 + pos.width / 2
    cy = pos.y0 + pos.height / 2
    new_width = pos.width * scale
    new_height = pos.height * scale
    new_x0 = cx - new_width / 2
    new_y0 = cy - new_height / 2

    ax.set_position([new_x0, new_y0, new_width, new_height])
    if ax2:
        ax2.set_position([new_x0, new_y0, new_width, new_height])

    # Speichern
    output_path = os.path.splitext(filepath)[0] + "_Diagramm.pdf"
    fig.savefig(output_path)

    plt.close(fig)
    return output_path
