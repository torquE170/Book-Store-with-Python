import sqlite3
from book import Book
from library import BookStore, LibraryEntry
from sql_conn import SqlDB
from user_settings import UserSettings
from mysql.connector import ProgrammingError


class Loans:
    """
    Collection of loans related methods
    """

    db_table = "Loans"
    @staticmethod
    def init_db(table = db_table, drop = False):
        """
        Creates a new Loans table to store all loans information
        :param table:
        :param drop:
        """
        init_query = f'''
            CREATE TABLE {table} (
            ID INT NOT NULL,
            ClientName VARCHAR(128) NOT NULL,
            BookName VARCHAR(128) NOT NULL,
            BookAuthor VARCHAR(128) NOT NULL,
            LibraryName VARCHAR(128) NOT NULL,
            PRIMARY KEY(ID)
            );
        '''
        SqlDB.sql_query(init_query, table, drop, UserSettings.use_sqlite3)

    @staticmethod
    def list_loans(table = db_table):
        """
        Queries the database for all loans
        :param table:
        :return:
        """
        if UserSettings.at_cli:
            UserSettings.clear()

        list_query = f"""
            SELECT * FROM {table};
        """
        try:
            result = SqlDB.sql_query_result(list_query, use_sqlite3=UserSettings.use_sqlite3)
        except (ProgrammingError, sqlite3.OperationalError):
            print(f"Table {table} not available")
            print()
            return
        column_width = [len("ID"), len("Client"), len("Book Name"), len("Book Author"), len("Library Name")]
        for entry in result:
            if len(str(entry[0])) + 2 > column_width[0]:
                column_width[0] = len(str(entry[0])) + 2
            for column in range(1, len(entry)):
                if len(entry[column]) + 2 > column_width[column]:
                    column_width[column] = len(entry[column]) + 2
        total_width = sum(column_width) + 3

        # print or return it
        print(f" Loans ".center(total_width, "-"))
        print(f"{"ID":>{column_width[0]}} {"Client":<{column_width[1]}} {"Book Name":<{column_width[2]}} {"Book Author":<{column_width[3]}} {"Library":<{column_width[4]}}")
        print("-" * total_width)
        for entry in result:
            print(f"{entry[0]:>{column_width[0]}} {entry[1]:<{column_width[1]}} {entry[2]:<{column_width[2]}} {entry[3]:<{column_width[3]}} {entry[4]:<{column_width[4]}}")
        print(f" END ".center(total_width, "-"))
        print()

    @staticmethod
    def loan_book(table = db_table):
        """
        Form for a user to loan a book
        :param table:
        """
        if UserSettings.at_cli:
            UserSettings.clear()
        print(f" Rent book ".center(60, "-"))
        name = input("Client name: ")
        book_found = False
        while not book_found:
            book_name = input("Book name: ")
            if book_name.strip().upper() == "SKIP":
                print(f" END ".center(60, "-"))
                return
            print()
            book = BookStore.search_book_by_name(book_name, UserSettings.user_library_name)
            if book is None:
                print("Book not found\n")
            else:
                book_found = True

        loan_entry = LoansEntry(client_name=name, book=book)
        if loan_entry.book.entry.available > 0:
            try:
                loan_entry.db_id = SqlDB.get_last_id(table, UserSettings.use_sqlite3) + 1
                loan_entry.save_to_db()
                print(f" END ".center(60, "-"))
                BookStore.loaned_one(loan_entry.book)
            except (ProgrammingError, sqlite3.OperationalError):
                print(f"Table {table} not available")
                print()
                try:
                    Loans.init_db()
                    print(f"Created new table {table}")
                    print()
                    loan_entry.db_id = SqlDB.get_last_id(table, UserSettings.use_sqlite3) + 1
                    loan_entry.save_to_db()
                    BookStore.loaned_one(loan_entry.book)
                    print(f" END ".center(60, "-"))
                except (ProgrammingError, sqlite3.OperationalError):
                    print(f"Tried to make new {table}, and failed")
                    print("Exiting")
                    print()
                    print(f" END ".center(60, "-"))
                    return
                return

        else:
            print("No more available copies")
            print()
            return

    @staticmethod
    def return_book(table = db_table):
        """
        Form for a user to recieve a loaned book
        :param table:
        """
        if UserSettings.at_cli:
            UserSettings.clear()
        print(f" Return book ".center(60, "-"))
        name = input("Client name: ")
        book_found = False
        while not book_found:
            book_name = input("Book name: ")
            if book_name.strip().upper() == "SKIP":
                print(f" END ".center(60, "-"))
                return
            print()
            book = BookStore.search_book_by_name(book_name, UserSettings.user_library_name)
            if book is None:
                print("Book not found\n")
            else:
                book_found = True

        try:
            order = Loans.search_order(name, book.entry.book.name, UserSettings.user_library_name)
        except (ProgrammingError, sqlite3.OperationalError):
            print(f"Table {table} not available")
            print()
            return

        BookStore.return_one(book)

        delete_statement = f"""
            DELETE FROM {Loans.db_table} 
            WHERE ClientName = \"{order.client_name}\" AND BookName = \"{order.book.book.name}\";
        """
        SqlDB.sql_query(delete_statement, Loans.db_table, use_sqlite3=UserSettings.use_sqlite3)

        # Add some check to see the success of all the operations
        print(f"{order.client_name} returned {order.book.book.name}")
        print()

    @staticmethod
    def search_order(client_name, book_name, library_name):
        """
        Search the database for a specific loaned book
        :param client_name:
        :param book_name:
        :param library_name:
        :return: a LoansEntry object
        """
        search_statement = f"""SELECT * FROM {Loans.db_table} 
            WHERE ClientName = \"{client_name}\" AND BookName = \"{book_name}\" AND LibraryName = \"{library_name}\";  
        """
        result = SqlDB.sql_query_result(search_statement, use_sqlite3=UserSettings.use_sqlite3)
        order = LoansEntry(result[0][0], result[0][1], LibraryEntry(Book(result[0][2], result[0][3])))
        return order


class LoansEntry:
    """
    A singular loan entry (a row in the database), containing all information about a loaned book
    """

    def __init__(self, db_id = 0, client_name = "", book : LibraryEntry = None):
        self.db_id = db_id
        self.client_name = client_name
        self.book = book

    def __repr__(self):
        typed_out = f"ID: {self.db_id} "
        typed_out += f"Client: {self.client_name}\n"
        typed_out += f"{self.book}"
        return typed_out

    def save_to_db(self, table = Loans.db_table):
        """
        Save a singular loan in the database
        :param table:
        :return: a LoansEntry object to be used in the context of saving an entry
        """
        insert_query = f"""
            INSERT INTO {table} (ID, ClientName, BookName, BookAuthor, LibraryName)
            VALUES ({self.db_id}, "{self.client_name}", "{self.book.entry.book.name}", "{self.book.entry.book.author}", "{UserSettings.user_library_name}");
        """
        SqlDB.sql_query(insert_query, table, use_sqlite3=UserSettings.use_sqlite3)
        print(f"{self.client_name} loaned {self.book.entry.book.name} book.")
        print()
        return self
