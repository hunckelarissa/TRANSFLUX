"""Небольшие SVG-графики для синтетических сценариев.

Без внешних библиотек: файл можно открыть в браузере и увидеть,
как состояние, уверенность и угроза менялись по шагам.
"""

from pathlib import Path
import html


def save_lines(path, title, panels, xlabel="шаг"):
    """Сохранить многопанельный график линий.

    panels: список словарей
        title, ylabel,
        series: [{name, values, color}],
        hlines: [{y, label, color}] (необязательно),
        events: [{index, label}] (необязательно, рисуются на каждой панели).
    """
    width = 820
    margin_left = 72
    margin_right = 24
    panel_height = 168
    panel_gap = 28
    header = 40
    footer = 28
    plot_width = width - margin_left - margin_right
    height = header + footer + len(panels) * panel_height + (len(panels) - 1) * panel_gap

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fbfcfd"/>',
        f'<text x="{margin_left}" y="26" font-family="Segoe UI, sans-serif" '
        f'font-size="16" fill="#1f2933">{_esc(title)}</text>',
    ]

    for panel_index, panel in enumerate(panels):
        top = header + panel_index * (panel_height + panel_gap)
        parts.extend(_panel(
            panel, margin_left, top, plot_width, panel_height, xlabel if panel_index == len(panels) - 1 else ""
        ))

    parts.append("</svg>")
    _write(path, "\n".join(parts))


def save_bars(path, title, categories, series, ylabel):
    """Столбцы. series: [{name, values, color}], values той же длины, что categories."""
    width = 820
    height = 420
    margin_left = 72
    margin_right = 24
    margin_top = 78
    margin_bottom = 88
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    flat = [value for item in series for value in item["values"]]
    ymax = max(flat) if flat else 1
    if ymax == 0:
        ymax = 1
    ymax *= 1.15

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fbfcfd"/>',
        f'<text x="{margin_left}" y="28" font-family="Segoe UI, sans-serif" '
        f'font-size="16" fill="#1f2933">{_esc(title)}</text>',
        f'<text x="{margin_left}" y="50" font-family="Segoe UI, sans-serif" '
        f'font-size="13" fill="#52606d">{_esc(ylabel)}</text>',
    ]

    for tick in range(5):
        value = ymax * tick / 4
        y = margin_top + plot_height - (value / ymax) * plot_height
        parts.append(
            f'<line x1="{margin_left}" y1="{y:.1f}" x2="{margin_left + plot_width}" '
            f'y2="{y:.1f}" stroke="#e4e7eb"/>'
        )
        parts.append(
            f'<text x="{margin_left - 8}" y="{y + 4:.1f}" text-anchor="end" '
            f'font-family="Segoe UI, sans-serif" font-size="11" fill="#52606d">'
            f'{_esc(_num(value))}</text>'
        )

    group_width = plot_width / max(len(categories), 1)
    bar_width = min(48, group_width / (len(series) + 1.5))
    for cat_index, category in enumerate(categories):
        bars_width = len(series) * bar_width + max(len(series) - 1, 0) * 6
        origin = margin_left + cat_index * group_width + (group_width - bars_width) / 2
        for series_index, item in enumerate(series):
            value = item["values"][cat_index]
            bar_height = (value / ymax) * plot_height
            x = origin + series_index * (bar_width + 6)
            y = margin_top + plot_height - bar_height
            parts.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" '
                f'fill="{item["color"]}"/>'
            )
            parts.append(
                f'<text x="{x + bar_width / 2:.1f}" y="{y - 4:.1f}" text-anchor="middle" '
                f'font-family="Segoe UI, sans-serif" font-size="11" fill="#1f2933">'
                f'{_esc(_num(value))}</text>'
            )
        label_x = margin_left + cat_index * group_width + group_width / 2
        parts.append(
            f'<text x="{label_x:.1f}" y="{margin_top + plot_height + 20}" text-anchor="middle" '
            f'font-family="Segoe UI, sans-serif" font-size="12" fill="#1f2933">{_esc(category)}</text>'
        )

    legend_x = margin_left
    legend_y = height - 18
    for item in series:
        parts.append(f'<rect x="{legend_x}" y="{legend_y - 10}" width="12" height="12" fill="{item["color"]}"/>')
        parts.append(
            f'<text x="{legend_x + 16}" y="{legend_y}" font-family="Segoe UI, sans-serif" '
            f'font-size="12" fill="#1f2933">{_esc(item["name"])}</text>'
        )
        legend_x += 16 + len(item["name"]) * 7 + 18

    parts.append("</svg>")
    _write(path, "\n".join(parts))


def _panel(panel, left, top, plot_width, plot_height, xlabel):
    series = panel["series"]
    values = [value for item in series for value in item["values"]]
    hlines = panel.get("hlines", [])
    values.extend(line["y"] for line in hlines)
    ymin = min(values) if values else 0
    ymax = max(values) if values else 1
    if ymin == ymax:
        ymin -= 1
        ymax += 1
    pad = (ymax - ymin) * 0.12
    ymin -= pad
    ymax += pad

    length = max(len(item["values"]) for item in series)
    parts = [
        f'<text x="{left}" y="{top + 14}" font-family="Segoe UI, sans-serif" '
        f'font-size="13" fill="#1f2933">{_esc(panel["title"])}</text>'
    ]
    inner_top = top + 24
    inner_height = plot_height - 40

    for tick in range(4):
        value = ymin + (ymax - ymin) * tick / 3
        y = inner_top + inner_height - (value - ymin) / (ymax - ymin) * inner_height
        parts.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_width}" y2="{y:.1f}" stroke="#e4e7eb"/>'
        )
        parts.append(
            f'<text x="{left - 8}" y="{y + 4:.1f}" text-anchor="end" '
            f'font-family="Segoe UI, sans-serif" font-size="11" fill="#52606d">{_esc(_num(value))}</text>'
        )

    def x_of(index):
        if length == 1:
            return left + plot_width / 2
        return left + index / (length - 1) * plot_width

    def y_of(value):
        return inner_top + inner_height - (value - ymin) / (ymax - ymin) * inner_height

    for event in panel.get("events", []):
        x = x_of(event["index"])
        parts.append(
            f'<line x1="{x:.1f}" y1="{inner_top}" x2="{x:.1f}" y2="{inner_top + inner_height}" '
            f'stroke="#9b2226" stroke-dasharray="3 3"/>'
        )
        parts.append(
            f'<text x="{x + 4:.1f}" y="{inner_top + 12}" font-family="Segoe UI, sans-serif" '
            f'font-size="11" fill="#9b2226">{_esc(event["label"])}</text>'
        )

    for line in hlines:
        y = y_of(line["y"])
        color = line.get("color", "#9b2226")
        parts.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_width}" y2="{y:.1f}" '
            f'stroke="{color}" stroke-dasharray="5 4"/>'
        )
        parts.append(
            f'<text x="{left + 4}" y="{y - 4:.1f}" '
            f'font-family="Segoe UI, sans-serif" font-size="11" fill="{color}">{_esc(line["label"])}</text>'
        )

    legend_x = left + plot_width - 8
    for item in reversed(series):
        label = item["name"]
        legend_x -= len(label) * 7 + 22
        parts.append(f'<rect x="{legend_x}" y="{top + 4}" width="10" height="10" fill="{item["color"]}"/>')
        parts.append(
            f'<text x="{legend_x + 14}" y="{top + 13}" font-family="Segoe UI, sans-serif" '
            f'font-size="11" fill="#1f2933">{_esc(label)}</text>'
        )
        points = " ".join(
            f"{x_of(index):.1f},{y_of(value):.1f}" for index, value in enumerate(item["values"])
        )
        parts.append(f'<polyline fill="none" stroke="{item["color"]}" stroke-width="2" points="{points}"/>')

    if xlabel:
        parts.append(
            f'<text x="{left + plot_width / 2}" y="{inner_top + inner_height + 28}" text-anchor="middle" '
            f'font-family="Segoe UI, sans-serif" font-size="12" fill="#52606d">{_esc(xlabel)}</text>'
        )
    return parts


def _num(value):
    if abs(value - round(value)) < 0.05 and abs(value) >= 10:
        return str(int(round(value)))
    if abs(value) >= 10:
        return f"{value:.1f}"
    return f"{value:.2f}"


def _esc(text):
    return html.escape(str(text), quote=True)


def _write(path, text):
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
