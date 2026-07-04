import requests
from PySide6.QtCore import QObject, QRunnable, Signal

import scraper


class WorkerSignals(QObject):
    finished = Signal(object)
    error = Signal(str)


class FetchCategoriesWorker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()

    def run(self):
        try:
            categories = scraper.fetch_categories()
        except Exception as e:
            self.signals.error.emit(str(e))
            return
        self.signals.finished.emit(categories)


class FetchCategoryBooksWorker(QRunnable):
    def __init__(self, category):
        super().__init__()
        self.category = category
        self.signals = WorkerSignals()

    def run(self):
        try:
            with requests.Session() as session:
                links = scraper.fetch_books_for_category(self.category, session=session)
                books = [
                    scraper.fetch_book_detail(link, self.category.name, session=session)
                    for link in links
                ]
        except Exception as e:
            self.signals.error.emit(str(e))
            return
        self.signals.finished.emit(books)


class FetchImageWorker(QRunnable):
    def __init__(self, img_link):
        super().__init__()
        self.img_link = img_link
        self.signals = WorkerSignals()

    def run(self):
        try:
            data = scraper.fetch_image_bytes(self.img_link)
        except Exception as e:
            self.signals.error.emit(str(e))
            return
        self.signals.finished.emit(data)
