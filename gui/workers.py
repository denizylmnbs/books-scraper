from concurrent.futures import ThreadPoolExecutor

import requests
from PySide6.QtCore import QObject, QRunnable, Signal

import scraper

DETAIL_FETCH_WORKERS = 16


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
                # pool_maxsize must cover all concurrent detail-fetch threads below,
                # otherwise they queue up waiting for a free pooled connection.
                adapter = requests.adapters.HTTPAdapter(pool_maxsize=DETAIL_FETCH_WORKERS)
                session.mount("https://", adapter)
                session.mount("http://", adapter)

                links = scraper.fetch_books_for_category(self.category, session=session)

                with ThreadPoolExecutor(max_workers=DETAIL_FETCH_WORKERS) as executor:
                    books = list(
                        executor.map(
                            lambda link: scraper.fetch_book_detail(
                                link, self.category.name, session=session
                            ),
                            links,
                        )
                    )
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
