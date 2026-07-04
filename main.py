import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from Book import Book
from Category import Category

BASE_URL = "https://books.toscrape.com/"

RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

resp = requests.get(f"{BASE_URL}/index.html")
soup = BeautifulSoup(resp.content, "lxml")

categories_list = soup.find("div", class_ = "side_categories").find_all("li")

categories = []

for category in categories_list:
    link = category.find("a")["href"]
    name = category.find("a").text.strip()
    cat = Category(name, link)
    categories.append(cat)

print("Select a category:")
for i, cat in enumerate(categories):
    print(f"{i}: {cat.name}")

selected_index = int(input("Enter the number of the category you want to select: "))
selected_cat = categories[selected_index]

print(f"You selected: {selected_cat.name} with link: {selected_cat.link}")

resp = requests.get(f"{BASE_URL}/{selected_cat.link}")
soup = BeautifulSoup(resp.content, "lxml")

books_list = soup.find("ol", class_ = "row").find_all("li")
book_links = []

for book in books_list:
    href = book.find("h3").find("a")["href"]
    link = urljoin(resp.url, href)
    book_links.append(link)

for link in book_links:
    print(f"Book link: {link}")
    resp = requests.get(link)
    soup = BeautifulSoup(resp.content, "lxml")
    img_src = soup.find("div", id = "product_gallery").find("img")["src"]
    book_img_link = urljoin(resp.url, img_src)
    book_title = soup.find("article", class_ = "product_page").find("h1").text.strip()
    price_text = soup.find("p", class_ = "price_color").text.strip()
    price = float(re.search(r"[\d.]+", price_text).group())

    stock_text = soup.find("p", class_ = "availability").text.strip()
    stock_match = re.search(r"\d+", stock_text)
    stock = int(stock_match.group()) if stock_match else 0

    rating_word = soup.find("p", class_ = "star-rating")["class"][1]
    rating = RATING_WORDS.get(rating_word, 0)
    description = soup.find("div", id = "product_description").find_next_sibling("p").text.strip()

    book = Book(book_title, link, book_img_link, price, stock, rating, description)
    
    print(f"Book title: {book.title}")
    print(f"Book image link: {book.img_link}")
    print(f"Book price: {book.price}")
    print(f"Book stock: {book.stock}")
    print(f"Book rating: {book.rating}")
    print(f"Book description: {book.description}")
