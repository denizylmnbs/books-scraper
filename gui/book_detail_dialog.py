from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from gui.book_card import stars_text

DETAIL_THUMB_WIDTH = 220
DETAIL_THUMB_HEIGHT = 300


class BookDetailDialog(QDialog):
    def __init__(self, book, parent=None):
        super().__init__(parent)
        self.book = book

        self.setWindowTitle(book.title)
        self.resize(560, 420)

        root_layout = QHBoxLayout(self)

        self.cover_label = QLabel()
        self.cover_label.setFixedSize(DETAIL_THUMB_WIDTH, DETAIL_THUMB_HEIGHT)
        self.cover_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.cover_label.setStyleSheet("background-color: #efe6d0; border-radius: 6px;")
        root_layout.addWidget(self.cover_label)

        info_layout = QVBoxLayout()
        root_layout.addLayout(info_layout, stretch=1)

        title_label = QLabel(book.title)
        title_label.setObjectName("dialogTitle")
        title_label.setWordWrap(True)
        info_layout.addWidget(title_label)

        if book.category:
            category_label = QLabel(book.category)
            category_label.setObjectName("bookCategory")
            info_layout.addWidget(category_label)

        price_label = QLabel(f"£{book.price:.2f}")
        price_label.setObjectName("bookPrice")
        price_label.setStyleSheet("font-size: 13pt;")
        info_layout.addWidget(price_label)

        stars_label = QLabel(stars_text(book.rating))
        stars_label.setObjectName("bookStars")
        info_layout.addWidget(stars_label)

        stock_label = QLabel("In stock" if book.stock > 0 else "Out of stock")
        stock_label.setObjectName("bookStockOk" if book.stock > 0 else "bookStockOut")
        info_layout.addWidget(stock_label)

        description_edit = QTextEdit()
        description_edit.setReadOnly(True)
        description_edit.setPlainText(book.description)
        info_layout.addWidget(description_edit, stretch=1)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        info_layout.addWidget(close_button, alignment=Qt.AlignRight)

    def set_cover_pixmap(self, pixmap):
        scaled = pixmap.scaled(
            DETAIL_THUMB_WIDTH, DETAIL_THUMB_HEIGHT, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.cover_label.setPixmap(scaled)
