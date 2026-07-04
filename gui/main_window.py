from collections import defaultdict

from PySide6.QtCore import Qt, QTimer, QThreadPool
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from gui.book_card import BookCard
from gui.book_detail_dialog import BookDetailDialog
from gui.workers import FetchCategoriesWorker, FetchCategoryBooksWorker, FetchImageWorker

GRID_COLUMN_WIDTH = 210


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Books Explorer")
        self.resize(1100, 720)

        self._threadpool = QThreadPool()
        self._categories = []
        self._categories_by_name = {}
        self._book_cache = {}
        self._pixmap_cache = {}
        self._current_category = None
        self._current_books = []
        self._pending_category_link = None
        self._active_workers = set()
        self._pending_report = False

        self._build_ui()
        self._start_category_fetch()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        splitter = QSplitter(Qt.Horizontal)
        root_layout.addWidget(splitter)

        self.category_list = QListWidget()
        self.category_list.setFixedWidth(220)
        self.category_list.itemClicked.connect(self._on_category_item_clicked)
        splitter.addWidget(self.category_list)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(1, 1)

        filter_bar = QHBoxLayout()
        right_layout.addLayout(filter_bar)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search by title…")
        filter_bar.addWidget(self.search_box, stretch=1)

        self.rating_combo = QComboBox()
        self.rating_combo.addItem("Any rating", 0)
        for r in range(1, 6):
            self.rating_combo.addItem(f"{r}+ stars", r)
        filter_bar.addWidget(self.rating_combo)

        filter_bar.addWidget(QLabel("Min £"))
        self.min_price_spin = QDoubleSpinBox()
        self.min_price_spin.setRange(0, 10000)
        self.min_price_spin.setDecimals(2)
        filter_bar.addWidget(self.min_price_spin)

        filter_bar.addWidget(QLabel("Max £"))
        self.max_price_spin = QDoubleSpinBox()
        self.max_price_spin.setRange(0, 10000)
        self.max_price_spin.setDecimals(2)
        self.max_price_spin.setValue(10000)
        filter_bar.addWidget(self.max_price_spin)

        self.report_button = QPushButton("Reports")
        self.report_button.setEnabled(False)
        self.report_button.clicked.connect(self._on_reports_clicked)
        filter_bar.addWidget(self.report_button)

        self._filter_timer = QTimer(self)
        self._filter_timer.setSingleShot(True)
        self._filter_timer.setInterval(300)
        self._filter_timer.timeout.connect(self._apply_filters)

        self.search_box.textChanged.connect(lambda _: self._filter_timer.start())
        self.rating_combo.currentIndexChanged.connect(lambda _: self._filter_timer.start())
        self.min_price_spin.valueChanged.connect(lambda _: self._filter_timer.start())
        self.max_price_spin.valueChanged.connect(lambda _: self._filter_timer.start())

        self.loading_label = QLabel("")
        self.loading_label.setObjectName("loadingLabel")
        right_layout.addWidget(self.loading_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        right_layout.addWidget(self.scroll_area, stretch=1)

        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(14)
        self.scroll_area.setWidget(self.grid_container)

    def _run_worker(self, worker):
        # QThreadPool.start() does not keep a Python reference alive, so an
        # unreferenced QRunnable can be garbage-collected mid-flight. Hold a
        # strong reference until its signals fire, then release it.
        self._active_workers.add(worker)
        worker.signals.finished.connect(lambda *_: self._active_workers.discard(worker))
        worker.signals.error.connect(lambda *_: self._active_workers.discard(worker))
        self._threadpool.start(worker)

    def _start_category_fetch(self):
        self.loading_label.setText("Loading categories…")
        worker = FetchCategoriesWorker()
        worker.signals.finished.connect(self._on_categories_loaded)
        worker.signals.error.connect(self._on_error)
        self._run_worker(worker)

    def _on_categories_loaded(self, categories):
        self.loading_label.setText("")
        self._categories = categories
        self._categories_by_name = {category.name: category for category in categories}
        self.category_list.clear()
        for category in categories:
            self.category_list.addItem(category.name)
        self.report_button.setEnabled(bool(categories))

    def _on_category_item_clicked(self, item):
        index = self.category_list.row(item)
        category = self._categories[index]
        self._on_category_selected(category)

    def _on_category_selected(self, category):
        self._current_category = category

        if category.link in self._book_cache:
            self._current_books = self._book_cache[category.link]
            self._apply_filters()
            return

        if self._pending_category_link is not None:
            return

        self._pending_category_link = category.link
        self.category_list.setEnabled(False)
        self.loading_label.setText(f"Loading {category.name}…")
        self._clear_grid()

        worker = FetchCategoryBooksWorker(category)
        worker.signals.finished.connect(
            lambda books, link=category.link: self._on_books_loaded(link, books)
        )
        worker.signals.error.connect(self._on_error)
        self._run_worker(worker)

    def _on_books_loaded(self, category_link, books):
        self._book_cache[category_link] = books
        self._cache_books_by_real_category(books)
        self._pending_category_link = None
        self.category_list.setEnabled(True)
        self.loading_label.setText("")

        if self._current_category and self._current_category.link == category_link:
            self._current_books = books
            self._apply_filters()

        self._maybe_fulfill_pending_report()

    def _cache_books_by_real_category(self, books):
        # A fetched listing (e.g. the catalogue-wide "Books" category) can
        # contain books from many real categories (per Book.category, read
        # from each detail page's breadcrumb). Group them so those other
        # categories are already cached and open instantly.
        grouped = defaultdict(list)
        for book in books:
            if book.category:
                grouped[book.category].append(book)

        for name, group in grouped.items():
            category = self._categories_by_name.get(name)
            if category and category.link not in self._book_cache:
                self._book_cache[category.link] = group

    def _on_error(self, message):
        failed_link = self._pending_category_link
        self._pending_category_link = None
        self.category_list.setEnabled(True)
        self.loading_label.setText("")
        QMessageBox.warning(self, "Error", message)
        self._maybe_fulfill_pending_report(failed_link)

    def _on_reports_clicked(self):
        books_category = self._categories[0]
        cached = self._book_cache.get(books_category.link)
        if cached is not None:
            self._show_reports(cached)
            return

        self._pending_report = True
        self.report_button.setEnabled(False)
        self.category_list.setCurrentRow(0)
        self._on_category_selected(books_category)

    def _show_reports(self, books):
        from gui.report_dialog import ReportDialog

        ReportDialog(books, self).exec()

    def _maybe_fulfill_pending_report(self, failed_link=None):
        if not self._pending_report:
            return

        books_category = self._categories[0]
        cached = self._book_cache.get(books_category.link)
        if cached is not None:
            self._pending_report = False
            self.report_button.setEnabled(True)
            self._show_reports(cached)
        elif failed_link == books_category.link:
            # The Books fetch itself just failed -- give up instead of
            # retrying the same failing request forever.
            self._pending_report = False
            self.report_button.setEnabled(True)
        elif self._pending_category_link is None:
            self._on_category_selected(books_category)

    def _apply_filters(self):
        search_text = self.search_box.text().strip().lower()
        min_rating = self.rating_combo.currentData()
        min_price = self.min_price_spin.value()
        max_price = self.max_price_spin.value()

        filtered = [
            book
            for book in self._current_books
            if (not search_text or search_text in book.title.lower())
            and book.rating >= min_rating
            and min_price <= book.price <= max_price
        ]
        self._rebuild_grid(filtered)

    def _clear_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _rebuild_grid(self, books):
        self._clear_grid()

        available_width = self.scroll_area.viewport().width()
        columns = max(1, available_width // GRID_COLUMN_WIDTH)

        for index, book in enumerate(books):
            row, col = divmod(index, columns)
            card = BookCard(book)
            card.clicked.connect(self._on_card_clicked)
            self.grid_layout.addWidget(card, row, col)
            self._load_thumbnail(card, book)

    def _load_thumbnail(self, card, book):
        cached = self._pixmap_cache.get(book.img_link)
        if cached is not None:
            card.set_thumbnail(cached)
            return

        worker = FetchImageWorker(book.img_link)
        worker.signals.finished.connect(
            lambda data, c=card, link=book.img_link: self._on_thumbnail_loaded(c, link, data)
        )
        self._run_worker(worker)

    def _on_thumbnail_loaded(self, card, img_link, data):
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        self._pixmap_cache[img_link] = pixmap
        try:
            card.set_thumbnail(pixmap)
        except RuntimeError:
            pass

    def _on_card_clicked(self, book):
        dialog = BookDetailDialog(book, self)

        cached = self._pixmap_cache.get(book.img_link)
        if cached is not None:
            dialog.set_cover_pixmap(cached)
        else:
            worker = FetchImageWorker(book.img_link)
            worker.signals.finished.connect(
                lambda data, d=dialog, link=book.img_link: self._set_dialog_cover(d, link, data)
            )
            self._run_worker(worker)

        dialog.exec()

    def _set_dialog_cover(self, dialog, img_link, data):
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        self._pixmap_cache[img_link] = pixmap
        dialog.set_cover_pixmap(pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._current_books:
            self._filter_timer.start()
