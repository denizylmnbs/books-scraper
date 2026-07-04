from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

import analysis
from gui.chart_utils import MplCanvas, color_cycle
from gui.styles import GOLD, GREEN, RED

PAGE_NAMES = ["Overview", "Category", "Rating", "Price", "Stock"]
CATEGORY_METRICS = [
    ("Book count", "book_count"),
    ("Avg price", "avg_price"),
    ("Avg rating", "avg_rating"),
]


def stat_label(text, value_style=""):
    label = QLabel(text)
    if value_style:
        label.setStyleSheet(value_style)
    return label


class ReportDialog(QDialog):
    def __init__(self, books, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reports")
        self.resize(980, 680)

        self._df = analysis.books_to_dataframe(books)
        self._category_summary = analysis.category_summary(self._df)
        self._rating_distribution = analysis.rating_distribution(self._df)
        self._stock_summary = analysis.stock_summary(self._df)

        self._build_ui()
        self.page_list.setCurrentRow(0)

    def _build_ui(self):
        root_layout = QHBoxLayout(self)

        self.page_list = QListWidget()
        self.page_list.setFixedWidth(160)
        self.page_list.addItems(PAGE_NAMES)
        self.page_list.currentRowChanged.connect(self._show_page)
        root_layout.addWidget(self.page_list)

        right_layout = QVBoxLayout()
        root_layout.addLayout(right_layout, stretch=1)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_overview_page())
        self.stack.addWidget(self._build_category_page())
        self.stack.addWidget(self._build_rating_page())
        self.stack.addWidget(self._build_price_page())
        self.stack.addWidget(self._build_stock_page())
        right_layout.addWidget(self.stack, stretch=1)

        export_bar = QHBoxLayout()
        export_bar.addStretch()
        export_csv_button = QPushButton("Export CSV")
        export_csv_button.clicked.connect(self._on_export_csv)
        export_bar.addWidget(export_csv_button)

        export_excel_button = QPushButton("Export Excel")
        export_excel_button.clicked.connect(self._on_export_excel)
        export_bar.addWidget(export_excel_button)
        right_layout.addLayout(export_bar)

    def _show_page(self, index):
        self.stack.setCurrentIndex(index)

    def _build_overview_page(self):
        page = QWidget()
        layout = QGridLayout(page)
        layout.setSpacing(16)

        stats = analysis.price_stats(self._df)
        tiles = [
            ("Total books", str(len(self._df))),
            ("Categories", str(self._df["category"].nunique())),
            ("Avg price", f"£{stats['mean']:.2f}"),
            ("Avg rating", f"{self._df['rating'].mean():.2f} / 5"),
            ("In stock", f"{(self._df['in_stock'].mean() * 100):.0f}%"),
        ]
        for index, (title, value) in enumerate(tiles):
            row, col = divmod(index, 3)
            tile = QVBoxLayout()
            tile.setSpacing(2)
            tile.addWidget(stat_label(title, "color: #7a6a58;"))
            tile.addWidget(stat_label(value, "font-size: 18pt; font-weight: 600; color: #3b2a20;"))
            container = QWidget()
            container.setLayout(tile)
            layout.addWidget(container, row, col, alignment=Qt.AlignTop)

        layout.setRowStretch(layout.rowCount(), 1)
        return page

    def _build_category_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Rank by:"))
        self.category_metric_combo = QComboBox()
        for label, key in CATEGORY_METRICS:
            self.category_metric_combo.addItem(label, key)
        self.category_metric_combo.currentIndexChanged.connect(self._redraw_category_chart)
        controls.addWidget(self.category_metric_combo)
        controls.addStretch()
        layout.addLayout(controls)

        self.category_canvas = MplCanvas(figsize=(6, 4.5))
        layout.addWidget(self.category_canvas, stretch=1)

        self._redraw_category_chart()
        return page

    def _redraw_category_chart(self):
        metric = self.category_metric_combo.currentData()
        top = analysis.top_n_categories(self._category_summary, metric, n=15).iloc[::-1]

        self.category_canvas.clear()
        self.category_canvas.axes.barh(top["category"], top[metric], color=GOLD, zorder=3)
        metric_label = next(text for text, key in CATEGORY_METRICS if key == metric)
        self.category_canvas.axes.set_title(f"Top Categories by {metric_label}")
        self.category_canvas.draw()

    def _build_rating_page(self):
        page = QWidget()
        layout = QHBoxLayout(page)

        pie_canvas = MplCanvas(figsize=(4, 4))
        labels = [f"{rating}★" for rating in self._rating_distribution["rating"]]
        counts = self._rating_distribution["book_count"]
        pie_canvas.axes.pie(
            counts,
            labels=labels,
            colors=color_cycle(len(labels)),
            textprops={"color": "#3b2a20"},
            autopct="%1.0f%%",
        )
        pie_canvas.axes.set_title("Rating Distribution")
        layout.addWidget(pie_canvas)

        bar_canvas = MplCanvas(figsize=(4, 4))
        bar_canvas.axes.bar(labels, self._rating_distribution["avg_price"], color=GOLD, zorder=3)
        bar_canvas.axes.set_title("Avg Price by Rating")
        layout.addWidget(bar_canvas)

        return page

    def _build_price_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        stats = analysis.price_stats(self._df)
        stats_bar = QHBoxLayout()
        for title, value in [
            ("Min", f"£{stats['min']:.2f}"),
            ("Max", f"£{stats['max']:.2f}"),
            ("Mean", f"£{stats['mean']:.2f}"),
            ("Median", f"£{stats['median']:.2f}"),
        ]:
            tile = QVBoxLayout()
            tile.addWidget(stat_label(title, "color: #7a6a58;"))
            tile.addWidget(stat_label(value, "font-size: 14pt; font-weight: 600; color: #3b2a20;"))
            container = QWidget()
            container.setLayout(tile)
            stats_bar.addWidget(container)
        layout.addLayout(stats_bar)

        counts, edges = analysis.price_histogram_bins(self._df, bins=12)
        canvas = MplCanvas(figsize=(6, 3.5))
        widths = [edges[i + 1] - edges[i] for i in range(len(edges) - 1)]
        centers = [(edges[i] + edges[i + 1]) / 2 for i in range(len(edges) - 1)]
        canvas.axes.bar(centers, counts, width=widths, color=GOLD, zorder=3, edgecolor="#f6efe0")
        canvas.axes.set_title("Price Distribution")
        canvas.axes.set_xlabel("Price (£)")
        canvas.axes.set_ylabel("Books")
        layout.addWidget(canvas, stretch=1)

        return page

    def _build_stock_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        canvas = MplCanvas(figsize=(4, 4))
        canvas.axes.pie(
            self._stock_summary["book_count"],
            labels=self._stock_summary["status"],
            colors=[GREEN, RED],
            textprops={"color": "#3b2a20"},
            autopct="%1.0f%%",
        )
        canvas.axes.set_title("Stock Status")
        layout.addWidget(canvas, alignment=Qt.AlignHCenter)

        return page

    def _on_export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "books.csv", "CSV files (*.csv)")
        if not path:
            return
        try:
            analysis.export_to_csv(self._df, path)
        except OSError as e:
            QMessageBox.warning(self, "Export failed", str(e))
            return
        QMessageBox.information(self, "Export complete", f"Saved to {path}")

    def _on_export_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Excel", "books.xlsx", "Excel files (*.xlsx)")
        if not path:
            return
        sheets = {
            "Books": self._df,
            "CategorySummary": self._category_summary,
            "RatingSummary": self._rating_distribution,
            "StockSummary": self._stock_summary,
        }
        try:
            analysis.export_to_excel(sheets, path)
        except OSError as e:
            QMessageBox.warning(self, "Export failed", str(e))
            return
        QMessageBox.information(self, "Export complete", f"Saved to {path}")
