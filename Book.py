class Book:
    def __init__(self, title, link, img_link, price, stock, rating, description):
        self.title = title
        self.link = link
        self.img_link = img_link
        self.price = price
        self.stock = stock
        self.rating = rating
        self.description = description

    @property
    def title(self):
        return self._title
    
    @title.setter
    def title(self, value):
        if not isinstance(value, str):
            raise ValueError("Title must be a string")
        self._title = value

    @property
    def link(self):
        return self._link
    
    @link.setter
    def link(self, value):
        if not isinstance(value, str):
            raise ValueError("Link must be a string")
        self._link = value

    @property
    def img_link(self):
        return self._img_link
    
    @img_link.setter
    def img_link(self, value):
        if not isinstance(value, str):
            raise ValueError("Image link must be a string")
        self._img_link = value
    
    @property
    def price(self):
        return self._price
    
    @price.setter
    def price(self, value):
        if not isinstance(value, float):
            raise ValueError("Price must be a float")
        self._price = value

    @property
    def stock(self):
        return self._stock
    
    @stock.setter
    def stock(self, value):
        if not isinstance(value, int):
            raise ValueError("Stock must be an integer")
        self._stock = value

    @property
    def rating(self):
        return self._rating
    
    @rating.setter
    def rating(self, value):
        if not isinstance(value, int):
            raise ValueError("Rating must be an integer")
        self._rating = value

    @property
    def description(self):
        return self._description
    
    @description.setter
    def description(self, value):
        if not isinstance(value, str):
            raise ValueError("Description must be a string")
        self._description = value


    def __str__(self):
        return f"Book(title={self.title}, price={self.price}, stock={self.stock}, rating={self.rating}"
    
    def __repr__(self):
        return f"Book(title={self.title}, link={self.link}, img_link={self.img_link}, price={self.price}, stock={self.stock}, rating={self.rating}, description={self.description})"
    
    
    
    