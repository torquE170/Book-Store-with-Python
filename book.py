

class Book:
    """
    Information about a book Name, Author, and optional, Publisher and Genre
    """

    def __init__(self, name = None, author = None, publisher = None, genre = None):
        self.name = name
        self.author = author
        self.publisher = publisher
        self.genre = genre

    def __repr__(self):
        typed_out = f"Name: {self.name}\n"
        if self.genre is not None:
            typed_out += f"Genre: {self.genre}\n"
        typed_out += f"Author: {self.author}"
        if self.publisher is not None:
            typed_out += f", Publisher: {self.publisher}"
        return typed_out

    @staticmethod
    def get_book():
        """
        Get from the keyboard the basic form of Book object, just Name and Author
        :return:
        """
        new_book = Book()
        new_book.name = input("name: ")
        new_book.author = input("author: ")
        return new_book

