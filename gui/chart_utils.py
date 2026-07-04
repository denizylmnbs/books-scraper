from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from gui.styles import CREAM, CREAM_LIGHT, ESPRESSO, TAN_BORDER

CHART_PALETTE = ["#8c2f39", "#b8892b", "#3f9d5c", "#6b4d8a", "#3f7fc4"]


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, figsize=(5, 3.2)):
        figure = Figure(figsize=figsize, facecolor=CREAM, constrained_layout=True)
        super().__init__(figure)
        self.setParent(parent)
        self.axes = figure.add_subplot(111)
        self._style_axes()

    def _style_axes(self):
        axes = self.axes
        axes.set_facecolor(CREAM_LIGHT)

        for spine_name, spine in axes.spines.items():
            if spine_name in ("bottom", "left"):
                spine.set_color(TAN_BORDER)
            else:
                spine.set_visible(False)

        axes.tick_params(colors=ESPRESSO, labelsize=8)
        axes.xaxis.label.set_color(ESPRESSO)
        axes.yaxis.label.set_color(ESPRESSO)
        axes.title.set_color(ESPRESSO)
        axes.grid(True, axis="both", color=TAN_BORDER, linewidth=0.6, alpha=0.6, zorder=0)

    def clear(self):
        self.axes.clear()
        self._style_axes()


def color_cycle(n):
    return [CHART_PALETTE[i % len(CHART_PALETTE)] for i in range(n)]
