from PySide6.QtCore import QRect, Qt, Signal
from PySide6.QtGui import QFont, QFontMetrics, QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

CARD_WIDTH = 190
CARD_HEIGHT = 400
THUMB_WIDTH = 160
THUMB_HEIGHT = 200
TITLE_WIDTH = THUMB_WIDTH
TITLE_HEIGHT = 64

TITLE_FONT = QFont("Georgia")
TITLE_FONT.setBold(True)
TITLE_FONT.setPointSizeF(10.5)


def stars_text(rating):
    return "★" * rating + "☆" * (5 - rating)


def fit_title(title, width=TITLE_WIDTH, max_height=TITLE_HEIGHT):
    metrics = QFontMetrics(TITLE_FONT)

    def wrapped_height(text):
        return metrics.boundingRect(QRect(0, 0, width, 10_000), Qt.TextWordWrap, text).height()

    if wrapped_height(title) <= max_height:
        return title

    words = title.split()
    for count in range(len(words) - 1, 0, -1):
        candidate = " ".join(words[:count]).rstrip(",.;:-") + "…"
        if wrapped_height(candidate) <= max_height:
            return candidate

    return title[:1] + "…"


class BookCard(QFrame):
    clicked = Signal(object)

    def __init__(self, book, parent=None):
        super().__init__(parent)
        self.book = book

        self.setObjectName("bookCard")
        self.setFixedSize(CARD_WIDTH, CARD_HEIGHT)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(THUMB_WIDTH, THUMB_HEIGHT)
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setStyleSheet("background-color: #efe6d0; border-radius: 6px;")
        layout.addWidget(self.thumbnail_label, alignment=Qt.AlignHCenter)

        self.title_label = QLabel(fit_title(book.title))
        self.title_label.setObjectName("bookTitle")
        self.title_label.setWordWrap(True)
        self.title_label.setFixedHeight(TITLE_HEIGHT)
        self.title_label.setAlignment(Qt.AlignTop)
        if self.title_label.text() != book.title:
            self.title_label.setToolTip(book.title)
        layout.addWidget(self.title_label)

        self.price_label = QLabel(f"£{book.price:.2f}")
        self.price_label.setObjectName("bookPrice")
        layout.addWidget(self.price_label)

        self.stars_label = QLabel(stars_text(book.rating))
        self.stars_label.setObjectName("bookStars")
        layout.addWidget(self.stars_label)

        self.stock_label = QLabel("In stock" if book.stock > 0 else "Out of stock")
        self.stock_label.setObjectName("bookStockOk" if book.stock > 0 else "bookStockOut")
        layout.addWidget(self.stock_label)

        layout.addStretch()

    def set_thumbnail(self, pixmap: QPixmap):
        scaled = pixmap.scaled(
            THUMB_WIDTH, THUMB_HEIGHT, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.thumbnail_label.setPixmap(scaled)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.book)
        super().mousePressEvent(event)
