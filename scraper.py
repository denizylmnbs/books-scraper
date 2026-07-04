import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from Book import Book
from Category import Category

BASE_URL = "https://books.toscrape.com/"

RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def fetch_categories(session=None):
    http = session or requests
    resp = http.get(f"{BASE_URL}index.html")
    soup = BeautifulSoup(resp.content, "lxml")

    categories_list = soup.find("div", class_="side_categories").find_all("li")

    categories = []
    for category in categories_list:
        link = category.find("a")["href"]
        name = category.find("a").text.strip()
        categories.append(Category(name, urljoin(resp.url, link)))

    return categories


def fetch_books_for_category(category, session=None):
    http = session or requests
    links = []
    page_url = category.link

    while page_url:
        resp = http.get(page_url)
        soup = BeautifulSoup(resp.content, "lxml")

        books_list = soup.find("ol", class_="row").find_all("li")
        for book in books_list:
            href = book.find("h3").find("a")["href"]
            links.append(urljoin(resp.url, href))

        next_link = soup.find("li", class_="next")
        if next_link:
            page_url = urljoin(resp.url, next_link.find("a")["href"])
        else:
            page_url = None

    return links


def fetch_book_detail(link, category_name, session=None):
    http = session or requests
    resp = http.get(link)
    soup = BeautifulSoup(resp.content, "lxml")

    img_src = soup.find("div", id="product_gallery").find("img")["src"]
    book_img_link = urljoin(resp.url, img_src)
    book_title = soup.find("article", class_="product_page").find("h1").text.strip()
    price_text = soup.find("p", class_="price_color").text.strip()
    price = float(re.search(r"[\d.]+", price_text).group())

    stock_text = soup.find("p", class_="availability").text.strip()
    stock_match = re.search(r"\d+", stock_text)
    stock = int(stock_match.group()) if stock_match else 0

    rating_word = soup.find("p", class_="star-rating")["class"][1]
    rating = RATING_WORDS.get(rating_word, 0)
    description = soup.find("div", id="product_description").find_next_sibling("p").text.strip()

    return Book(book_title, link, book_img_link, price, stock, rating, description, category_name)


def fetch_image_bytes(img_link, session=None):
    http = session or requests
    resp = http.get(img_link)
    return resp.content
