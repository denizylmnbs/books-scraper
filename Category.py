class Category:
    def __init__(self, name, link):
        self.name = name
        self.link = link

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError("Name must be a string")
        self._name = value

    @property
    def link(self):
        return self._link

    @link.setter
    def link(self, value):
        if not isinstance(value, str):
            raise ValueError("Link must be a string")
        self._link = value

    def __str__(self):
        return f"Category: {self.name}"
    
    def __repr__(self):
        return f"Category(name={self.name}, link={self.link})"
    
    