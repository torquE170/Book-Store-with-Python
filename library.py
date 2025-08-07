import sqlite3
from book import Book
from sql_conn import SqlDB
from user_settings import UserSettings
from mysql.connector import IntegrityError, ProgrammingError


class Library:
    """
    Is a list of LibraryEntries
    """

    def __init__(self, entries=None):
        if entries is None:
            entries = list()
        self.entries = entries

    def __repr__(self):
        if len(self.entries):
            typed_out = "-" * 60 + "\n"
        else:
            typed_out = ""
        last_entry = self.entries.pop()
        for entry in self.entries:
            typed_out += f"{entry}\n"
            typed_out += "-" * 60 + "\n"
        typed_out += f"{last_entry}\n"
        typed_out += f" END ".center(60, "-")
        typed_out += "\n"
        return typed_out

    def add_entry(self, new_book):
        """
        Asks user for a quantity, then appends the new book to the entries list
        :param new_book:
        """
        quantity = int(input("quantity: "))
        new_entry = LibraryEntry(new_book, quantity)
        self.entries.append(new_entry)


class LibraryEntry:
    """
    Is a Book with quantity and availability
    """

    def __init__(self, book: Book, quantity=None, available=None):
        self.book = book
        self.quantity = quantity
        if available is None:
            self.available = quantity
        else:
            self.available = available

    def __repr__(self):
        typed_out = f"{self.book}\n"
        if self.quantity is not None:
            typed_out += f"Quantity = {self.quantity}, Available = {self.available}"
        return typed_out

    @staticmethod
    def get_entry():
        """
        Adds to Book.get_book() and furthermore gets Quantity as well
        :return:
        """
        new_book = Book.get_book()
        quantity = int(input("Quantity: "))
        new_entry = LibraryEntry(new_book, quantity)
        return new_entry


class BookStore:
    """
    Is a list of BookStoreEntries
    """

    db_table = "BookStore"

    def __init__(self, entries=None):
        # recheck how objects are made - entries list is sometimes empty
        if entries is None:
            entries = list()
        self.entries = entries

    def __repr__(self):
        typed_out = f" {UserSettings.user_library_name} ".center(60, "-")
        typed_out += "\n"
        if not len(self.entries):
            typed_out += "Empty library\n"
        else:
            last_entry = self.entries.pop()
            for entry in self.entries:
                typed_out += f"{entry}\n"
                typed_out += "-" * 60 + "\n"
            typed_out += f"{last_entry}\n"
        typed_out += f" END ".center(60, "-")
        typed_out += "\n"
        return typed_out

    @staticmethod
    def save_entry_to_store(table, new_entry):
        """
        Add to database a book store entry object
        :param table:
        :param new_entry:
        """
        try:
            new_id = SqlDB.get_last_id(table, UserSettings.use_sqlite3) + 1
            new_entry.save_entry_to_db(new_id, table)
        except (ProgrammingError, sqlite3.OperationalError):
            print(f"Table {table} not available")
            print()
            try:
                BookStore.init_db(table)
                print(f"Created new table {table}")
                print()
                new_id = SqlDB.get_last_id(table, UserSettings.use_sqlite3) + 1
                new_entry.save_entry_to_db(new_id, table)
            except (ProgrammingError, sqlite3.OperationalError):
                print(f"Tried to make new {table}, and failed")
                print("Exiting")
                print()
                return
            except (IntegrityError, sqlite3.IntegrityError):
                print(f"Book not added! \"{new_entry.entry.book.name}\" is already in store")
                print()
            return

    @staticmethod
    def add_entry(table=db_table):
        """
        Add a book from keyboard and save it to database
        :param table:
        """
        if UserSettings.at_cli:
            UserSettings.clear()
        print(f" Add book ".center(60, "-"))
        new_entry = BookStoreEntry.get_entry()
        try:
            new_id = SqlDB.get_last_id(table, UserSettings.use_sqlite3) + 1
            new_entry.save_entry_to_db(new_id, table)
        except (ProgrammingError, sqlite3.OperationalError):
            print(f"Table {table} not available")
            print()
            try:
                BookStore.init_db(table)
                print(f"Created new table {table}")
                print()
                new_id = SqlDB.get_last_id(table, UserSettings.use_sqlite3) + 1
                new_entry.save_entry_to_db(new_id, table)
            except (ProgrammingError, sqlite3.OperationalError):
                print(f"Tried to make new {table}, and failed")
                print("Exiting")
                print()
                return
            except (IntegrityError, sqlite3.IntegrityError):
                print(f"Book not added! \"{new_entry.entry.book.name}\" is already in store")
                print()
            return

    @staticmethod
    def list_entries(table=db_table, print_out=True):
        """
        List all library entries from a specific library table
        :param table:
        :param print_out: Set to true to print result to console rather than returning it
        """
        if UserSettings.at_cli:
            UserSettings.clear()
        list_query = f"""
            SELECT ID, Name, Author, Quantity, Available FROM {table};
        """
        try:
            books_list = SqlDB.sql_query_result(list_query, use_sqlite3=UserSettings.use_sqlite3)
        except (ProgrammingError, sqlite3.OperationalError):
            print(f"Table {table} not available")
            print()
            return None
        book_store_list = list()
        for entry in books_list:
            book_store_list.append(
                BookStoreEntry(LibraryEntry(Book(entry[1], entry[2]), entry[3], entry[4]), entry[0]))
        if print_out:
            book_store = BookStore(book_store_list)
            print(book_store)
            return None
        else:
            return book_store_list

    @staticmethod
    def search_book(table=db_table):
        """
        Fuzzy search a library table by either book name or author
        Prints the results
        :param table:
        """
        if UserSettings.at_cli:
            UserSettings.clear()

        search_by = ""
        opt = -1
        while opt != 0:
            print("Search books by:")
            print("1 - Name")
            print("2 - Author")
            print()
            print("0 - Cancel")
            opt = UserSettings.read_menu_option(">> ")
            print()
            if opt == 1:
                search_by = "Name"
                break
            if opt == 2:
                search_by = "Author"
                break
            if opt == 0:
                print("Search canceled")
                return
        if UserSettings.at_cli:
            UserSettings.clear()
        keyword = input(f"Search books by {search_by}: ")

        queried_books = BookStore()
        search_query = f"""
            SELECT ID, Name, Author, Quantity, Available FROM {table} WHERE {search_by} LIKE "%{keyword}%";
        """
        try:
            result_list = SqlDB.sql_query_result(search_query, use_sqlite3=UserSettings.use_sqlite3)
        except (ProgrammingError, sqlite3.OperationalError):
            print(f"Table {table} not available")
            print()
            return
        for entry in result_list:
            queried_books.entries.append(
                BookStoreEntry(LibraryEntry(Book(entry[1], entry[2]), entry[3], entry[4]), entry[0]))
        if len(queried_books.entries):
            print(queried_books)  # or return it
        else:
            print("No results\n")

    @staticmethod
    def search_book_by_name(keyword, table=db_table):
        """
        Fuzzy search a library table by name
        :param keyword:
        :param table:
        :return: A single book store entry object
        """
        queried_books = BookStore()
        # if multiple words add split and formulate '%keyword%' into '%keyword[0]%' or '%keyword[1]%' or '%keyword[2]%'
        search_query = f"""
            SELECT ID, Name, Author, Quantity, Available FROM {table} WHERE Name LIKE \'%{keyword}%\';
        """
        try:
            result_list = SqlDB.sql_query_result(search_query, use_sqlite3=UserSettings.use_sqlite3)
            for entry in result_list:
                queried_books.entries.append(
                    BookStoreEntry(LibraryEntry(Book(entry[1], entry[2]), entry[3], entry[4]), entry[0]))
            if len(queried_books.entries):
                return queried_books.entries[0]
            else:
                return None
        except (ProgrammingError, sqlite3.OperationalError):
            print(f"Table {table} not available")
            print()
            return None

    @staticmethod
    def delete_book(table=db_table):
        """
        Deletes a book from database by either ID or Name
        :param table:
        """
        if UserSettings.at_cli:
            UserSettings.clear()

        delete_by = ""
        opt = -1
        while opt != 0:
            print("Delete book by:")
            print("1 - ID")
            print("2 - Name")
            print()
            print("0 - Cancel")
            opt = UserSettings.read_menu_option(">> ")
            print()
            if opt == 1:
                delete_by = "ID"
                break
            if opt == 2:
                delete_by = "Name"
                break
            if opt == 0:
                print("Delete operation canceled")
                return
        if UserSettings.at_cli:
            UserSettings.clear()

        value = ""
        if delete_by == "ID":
            value = int(input("ID: "))
        if delete_by == "Name":
            value = input("Name: ")
            value = f"\"{value}\""

        # recheck delete logic
        delete_statement = f"""
            DELETE FROM {table} WHERE {delete_by}={value};
        """
        try:
            SqlDB.sql_query(delete_statement, table, use_sqlite3=UserSettings.use_sqlite3)
        except (ProgrammingError, sqlite3.OperationalError):
            print(f"Table {table} not available")
            print()
            return
        print()
        select_query = f"""
            SELECT ID, Name FROM {table}
            WHERE {delete_by} = {value};
        """
        result = SqlDB.sql_query_result(select_query, use_sqlite3=UserSettings.use_sqlite3)
        if len(result) == 0:
            print(f"Book with {delete_by}: {value} has been deleted")
            print()

    @staticmethod
    def loaned_one(book):
        """
        When loaning a book this will decrement the available books in the database table
        :param book:
        """
        query = f"""
            UPDATE {UserSettings.user_library_name} 
            SET Available = {book.entry.available - 1} 
            WHERE Name = \"{book.entry.book.name}\";
        """
        SqlDB.sql_query(query, UserSettings.user_library_name, use_sqlite3=UserSettings.use_sqlite3)

    @staticmethod
    def add_stock(table, book: LibraryEntry, quantity: int, available: int):
        """
        When trying to add a book that already exists, this method will be called and will
        increment the quantity and availability of that book
        :param table:
        :param book:
        :param quantity:
        :param available:
        """
        query = f"""
            UPDATE {table} 
            SET Quantity = {book.entry.quantity + quantity}, Available = {book.entry.available + available}
            WHERE Name = \"{book.entry.book.name}\";
        """
        SqlDB.sql_query(query, UserSettings.user_library_name, use_sqlite3=UserSettings.use_sqlite3)

    @staticmethod
    def return_one(book):
        """
        When a client returns a book this will increment the available books to reflect the action
        :param book:
        """
        query = f"""
            UPDATE {UserSettings.user_library_name} 
            SET Available = {book.entry.available + 1} 
            WHERE Name = \"{book.entry.book.name}\";
        """
        SqlDB.sql_query(query, UserSettings.user_library_name, use_sqlite3=UserSettings.use_sqlite3)

    @staticmethod
    def init_db(table, drop=False):
        """
        Will initialize a table for storing books
        :param table: will be the library name
        :param drop:
        """
        init_query = f'''
            CREATE TABLE {table} (
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
        SqlDB.sql_query(init_query, table, drop, UserSettings.use_sqlite3)


class BookStoreEntry:
    """
    Is a LibraryEntry with an ID, useful for storing in database
    """

    def __init__(self, store_entry: LibraryEntry, db_id=None):
        self.entry = store_entry
        self.db_id = db_id

    def __repr__(self):
        typed_out = f"ID: {self.db_id}\n"
        typed_out += f"{self.entry}"
        return typed_out

    @staticmethod
    def get_entry():
        """
        Uses LibraryEntry.get_entry() to gather from user information then returns an object
        :return: a book store entry object
        """
        new_lib_entry = LibraryEntry.get_entry()
        # next_id = SqlDB.get_last_id(BookStore.db_table, UserSettings.use_sqlite3) + 1
        book_store_entry = BookStoreEntry(new_lib_entry)
        return book_store_entry

    def save_entry_to_db(self, new_id, table=BookStore.db_table):
        """
        Saves the object that is called on, to database as a book store entry
        If the book is already in the table, it will increment quantity and availability
        :param new_id:
        :param table:
        :return: self
        """
        insert_query = f"""
            INSERT INTO {table} (ID, Name, Author, Quantity, Available)
            VALUES ({new_id}, "{self.entry.book.name}", "{self.entry.book.author}", {self.entry.quantity}, {self.entry.available});
        """
        try:
            SqlDB.sql_query(insert_query, table, use_sqlite3=UserSettings.use_sqlite3)
            print(f"Book added! \"{self.entry.book.name}\" has been saved to {table} library")
            print()
        except (IntegrityError, sqlite3.IntegrityError):
            print(f"Book \"{self.entry.book.name}\" already in library. Adding available copies")
            print()
            book = BookStore.search_book_by_name(self.entry.book.name, table)
            if book is not None:
                BookStore.add_stock(table, book, self.entry.quantity, self.entry.available)
        return self


class BookStores:
    """
    A list of BookStoresEntry
    """

    db_table = "Libraries"

    def __init__(self, entries=None):
        if entries is None:
            entries = list()
        self.entries = entries

    def __repr__(self):
        typed_out = f" {BookStores.db_table} ".center(60, "-")
        typed_out += "\n"

        has_last_entry = False
        if not len(self.entries):
            typed_out += "Empty list\n"
        else:
            last_entry = self.entries.pop()
            has_last_entry = True

        for entry in self.entries:
            typed_out += f"{entry}\n"
            typed_out += "-" * 60 + "\n"

        if has_last_entry:
            typed_out += f"{last_entry}\n"
        typed_out += f" END ".center(60, "-")
        typed_out += "\n"
        return typed_out

    @staticmethod
    def init_db(table=db_table, drop=False):
        """
        Called when there is no Libraries table to send a CREATE TABLE
        :param table:
        :param drop:
        """
        init_query = f"""
            CREATE TABLE {table} (
            ID INT NOT NULL,
            Library VARCHAR(50) NOT NULL UNIQUE,
            PRIMARY KEY(ID)
            );
        """
        SqlDB.sql_query(init_query, table, drop, UserSettings.use_sqlite3)

    @staticmethod
    def save_library_to_db(library_name, table=db_table):
        """
        Saves a library name to the Library table
        :param library_name:
        :param table:
        """
        try:
            next_id = SqlDB.get_last_id(table, UserSettings.use_sqlite3) + 1
        except (ProgrammingError, sqlite3.OperationalError):
            BookStores.init_db()
            next_id = SqlDB.get_last_id(table, UserSettings.use_sqlite3) + 1

        insert_query = f"""
            INSERT INTO {table} (ID, Library)
            VALUES ({next_id}, "{library_name}");
        """
        try:
            SqlDB.sql_query(insert_query, table, use_sqlite3=UserSettings.use_sqlite3)
        except (IntegrityError, sqlite3.IntegrityError):
            print(f"Library {library_name} was already saved to the list.")
            print()
            return
        print(f"Library {library_name} saved to libraries list.")
        print()

    @staticmethod
    def list_libraries(table=db_table):
        """
        Scans for library tables that aren't saved to the list yet\n
        Prints all the available libraries
        :param table:
        """
        if UserSettings.at_cli:
            UserSettings.clear()
        # look for tables that are libraries and not save in the libraries list
        BookStores.scan_library_tables()
        UserSettings.wait_for_enter()
        if UserSettings.at_cli:
            UserSettings.clear()
        stores_list = BookStores()
        select_query = f"""
            SELECT * FROM {table};
        """
        try:
            libraries_list = SqlDB.sql_query_result(select_query, use_sqlite3=UserSettings.use_sqlite3)
        except (ProgrammingError, sqlite3.OperationalError):
            print(f"Table {table} not available")
            print()
            return

        for entry in libraries_list:
            stores_list.entries.append(BookStoresEntry(entry[0], entry[1]))
        print(stores_list)  # or return it

    @staticmethod
    def del_library(table=db_table, use_sqlite3=UserSettings.use_sqlite3):
        """
        Deletes a library from the Library table
        :param use_sqlite3:
        :param table:
        """
        # then drop the library table
        if UserSettings.at_cli:
            UserSettings.clear()

        if use_sqlite3:
            print("Delete for sqlite3 not yet implemented")
            print()
            return None

        # Prevention against deleting the last library if it has loaned books
        select_statement = f"""
            SELECT LibraryName FROM {UserSettings.loans_table_name};
        """
        # a list of tuples
        result = SqlDB.sql_query_result(select_statement, use_sqlite3=UserSettings.use_sqlite3)
        has_orders = False
        if len(result):
            has_orders = True

        delete_by = ""
        opt = -1
        while opt != 0:
            print("Delete library by:")
            print("1 - ID")
            print("2 - Library")
            print()
            print("0 - Cancel")
            opt = UserSettings.read_menu_option(">> ")
            print()
            if opt == 1:
                delete_by = "ID"
                break
            if opt == 2:
                delete_by = "Library"
                break
            if opt == 0:
                print("Delete operation canceled")
                return None
        if UserSettings.at_cli:
            UserSettings.clear()

        value = ""
        if delete_by == "ID":
            value = int(input("ID: "))
        if delete_by == "Library":
            value = input("Library: ")
            value = f"\"{value}\""

        print()

        all_libraries_query = f"""
            SELECT * FROM {table};
        """
        all_libraries_list = SqlDB.sql_query_result(all_libraries_query, use_sqlite3=UserSettings.use_sqlite3)
        is_last_library = False
        if len(all_libraries_list) < 2:
            is_last_library = True

        target_library_name = list()
        for entry in all_libraries_list:
            if delete_by == "ID":
                if value == entry[0]:
                    target_library_name.append(entry[0])
                    target_library_name.append(entry[1])
                    break
            if delete_by == "Library":
                if value.strip("\"") == entry[1]:
                    target_library_name.append(entry[0])
                    target_library_name.append(entry[1])
                    break

        # it will delete only if library is not last and no books are loaned from it
        if not is_last_library or not has_orders:
            name = ""
            if delete_by == "ID":
                name = input("Confirm by entering library name: ")
                if target_library_name[1] == name:
                    print("Confirmed")
                else:
                    print("Canceled")
                    print()
                    return None

            if delete_by == "Library":
                db_id = int(input("Confirm by entering library id: "))
                if target_library_name[0] == db_id:
                    print("Confirmed")
                else:
                    print("Canceled")
                    print()
                    return None

            # Distribute the books to the rest of the libraries
            # Get a list of books from the library in question
            target_library_book_list = BookStore.list_entries(target_library_name[1], False)
            target_libraries = list()
            for entry in all_libraries_list:
                if entry[1] == target_library_name[1]:
                    continue
                else:
                    target_libraries.append((entry[0], entry[1]))

            # if this is not the last library, then we can distribute the books
            if not is_last_library:
                # here we'll deal with the books that we already have in a library
                i = 0  # "i" is not moving because every book that we go through we pop out of the list
                distributed_books = 0
                while i < len(target_library_book_list):
                    book = target_library_book_list[i]
                    target_libraries_inv_sel = list(target_libraries)
                    for library in target_libraries:
                        library_book_list = BookStore.list_entries(library[1], False)
                        for in_store_book in library_book_list:
                            if book.entry.book.name == in_store_book.entry.book.name:
                                # we are eliminating libraries with that book
                                target_libraries_inv_sel.remove((library[0], library[1]))
                                break
                        else:
                            continue
                        if library == target_libraries[-1]:
                            break

                    # now we have a list of libraries that don't have that book
                    if len(target_libraries_inv_sel):
                        # distribute books to the inverse selection of libraries
                        index_for_distribution = distributed_books % len(target_libraries_inv_sel)
                        BookStore.save_entry_to_store(target_libraries_inv_sel[index_for_distribution][1], BookStoreEntry(LibraryEntry(Book(book.entry.book.name, book.entry.book.author), book.entry.quantity, book.entry.available)))
                        target_library_book_list.pop(i)
                        distributed_books += 1
                    elif len(target_libraries):
                        # distribute books to all the libraries
                        index_for_distribution = distributed_books % len(target_libraries)
                        BookStore.save_entry_to_store(target_libraries[index_for_distribution][1], BookStoreEntry(LibraryEntry(Book(book.entry.book.name, book.entry.book.author), book.entry.quantity, book.entry.available)))
                        target_library_book_list.pop(i)
                        distributed_books += 1

            drop_query = f"""DROP TABLE {target_library_name[1]};"""
            SqlDB.sql_query(drop_query, target_library_name[1], UserSettings.use_sqlite3)

            # Change the current library to the next or previous one if last
            select_query = f"""
                SELECT * FROM {table};
            """
            result = SqlDB.sql_query_result(select_query, use_sqlite3=UserSettings.use_sqlite3)
            if len(result) < 1:
                UserSettings.user_library_name = "n/a"
            else:
                for i in range(len(result) - 1):
                    if delete_by == "Library" and value.strip("\"") == result[i][1] or delete_by == "ID" and name == \
                            result[i][1]:
                        UserSettings.user_library_name = result[i + 1][1]
                if delete_by == "Library" and value.strip("\"") == result[len(result) - 1][
                    1] or delete_by == "ID" and name == result[len(result) - 1][1]:
                    UserSettings.user_library_name = result[len(result) - 2][1]
                UserSettings.edit_config("config.ini", "USER-LIBRARY", "library_table", UserSettings.user_library_name)

            # Delete the library from the library list
            delete_statement = f"""
                DELETE FROM {table} WHERE {delete_by}={value};
            """
            SqlDB.sql_query(delete_statement, table, use_sqlite3=UserSettings.use_sqlite3)
            print()
            select_query = f"""
                SELECT ID, Library FROM {table}
                WHERE {delete_by} = {value};
            """
            result = SqlDB.sql_query_result(select_query, use_sqlite3=UserSettings.use_sqlite3)
            if delete_by == "Library":
                id_word = "name"
            else:
                id_word = delete_by
            if len(result) == 0:
                print(f"Library identified by {id_word}: {value} has been deleted")
                print()
        else:
            print(f"Cannot delete last library: \"{target_library_name[1]}\" while books are still loaned from it")
            print("Return all the books before trying again")
            print()
        return None

    @staticmethod
    def scan_library_tables():

        if UserSettings.use_sqlite3:
            print("Please use a dedicated mysql server if you want to use the scan method")
            print()
            return

        tables_query = """SHOW TABLES;"""
        tables_result = SqlDB.sql_query_result(tables_query, use_sqlite3=UserSettings.use_sqlite3)
        tables = list()
        for entry in tables_result:
            tables.append(entry[0])

        i = 0
        while i < len(tables):
            query = f"""DESC {tables[i]};"""
            result = SqlDB.sql_query_result(query, use_sqlite3=UserSettings.use_sqlite3)
            is_library = False
            for j in range(len(result)):
                if result[j][0] == "Author" or result[j][0] == "Publisher":
                    is_library = True
                    break
            if not is_library:
                tables.pop(i)
            else:
                i += 1

        for table in tables:
            BookStores.save_library_to_db(table)


class BookStoresEntry:
    """
    An object for storing an id and library name
    """

    def __init__(self, db_id=0, name=""):
        self.db_id = db_id
        self.name = name

    def __repr__(self):
        typed_out = f"ID: {self.db_id:<3} Name: {self.name:<15s}"
        return typed_out

    def get_entry(self):
        self.db_id = int(input("ID = "))
        self.name = input("Name = ")
