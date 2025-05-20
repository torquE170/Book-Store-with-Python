import random

import bcrypt
from mysql.connector import IntegrityError

from book import Book
from sql_conn import SqlDB
from user import User


class Library:

    def __init__(self, entries = None):
        if entries is None:
            entries = list()
        self.entries = entries

    def __repr__(self):
        if len(self.entries):
            typed_out = "-" * 60 + "\n"
        else:
            typed_out = ""
        for entry in self.entries:
            typed_out += f"{entry}\n"
            typed_out += "-" * 60 + "\n"
        return typed_out

    def add_entry(self, new_book):
        quantity = int(input("quantity: "))
        new_entry = LibraryEntry(new_book, quantity)
        self.entries.append(new_entry)

class LibraryEntry:

    def __init__(self, book: Book, quantity, available = None):
        self.book = book
        self.quantity = quantity
        if available is None:
            self.available = quantity
        else:
            self.available = available

    def __repr__(self):
        typed_out = f"{self.book}\n"
        typed_out += f"Quantity = {self.quantity}, Available = {self.available}"
        return typed_out

class BookStore:

    db_table = "BookStore"
    def __init__(self, entries = None):
        if entries is None:
            entries = list()
        self.entries = entries

    def __repr__(self):
        if len(self.entries):
            typed_out = "-" * 60 + "\n"
        else:
            typed_out = ""
        for entry in self.entries:
            typed_out += f"{entry}\n"
            typed_out += "-" * 60 + "\n"
        return typed_out

    def add_entry(self, new_entry):
        next_id = SqlDB.get_last_id(BookStore.db_table, User.use_sqlite3) + 1
        # self.entries.append(BookStoreEntry(new_entry, next_id))
        this_entry = BookStoreEntry(new_entry, next_id)
        try:
            saved_entry = this_entry.save_to_db()
            self.entries.append(saved_entry)
        except IntegrityError:
            print(f"Book {this_entry.entry.book.name} already in store")

    @staticmethod
    def list_entries():
        book_store = BookStore()
        list_query = f"""
        SELECT ID, Name, Author, Quantity, Available FROM {BookStore.db_table};
        """
        books_list = SqlDB.sql_query_result(list_query, use_sqlite3=User.use_sqlite3)
        for entry in books_list:
            book_store.entries.append(BookStoreEntry(LibraryEntry(Book(entry[1], entry[2]), entry[3], entry[4]), entry[0]))
        print(book_store)  # or return it

    @staticmethod
    def init_db(db_table, drop = False):
        conn = SqlDB.connect_db(User.use_sqlite3)
        cursor = conn.cursor()
        query_init = f'''
            CREATE TABLE {db_table} (
            ID INT NOT NULL,
            Name VARCHAR(50) NOT NULL UNIQUE,
            Author VARCHAR(128) NOT NULL,
            Quantity INT NOT NULL,
            Available INT NOT NULL,
            Publisher VARCHAR(50),
            Genre VARCHAR(128),
            PRIMARY KEY(ID)
        );
        '''
        SqlDB.sql_query(query_init, db_table, drop, User.use_sqlite3)

class BookStoreEntry:

    def __init__(self, store_entry: LibraryEntry, db_id = None):
        self.entry = store_entry
        self.db_id = db_id

    def __repr__(self):
        typed_out = f"ID: {self.db_id}\n"
        typed_out += f"{self.entry}"
        return typed_out

    def save_to_db(self):
        insert_query = f"""
        INSERT INTO {BookStore.db_table} (ID, Name, Author, Quantity, Available)
        VALUES ({self.db_id}, "{self.entry.book.name}", "{self.entry.book.author}", {self.entry.quantity}, {self.entry.available});
        """
        SqlDB.sql_query(insert_query, BookStore.db_table, use_sqlite3=User.use_sqlite3)
        print(f"Book {self.entry.book.name} has been saved to database")
        print()
        return self
