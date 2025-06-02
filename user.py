import uuid
import bcrypt
import logging

from loans import Loans
from sql_conn import SqlDB
from getpass import getpass
from user_settings import UserSettings
from library import BookStore, BookStores


class User:
    db_table = "Users"
    def __init__(self, username, full_name = None, is_admin = 0, is_active = 0, has_password = 0,
                 request_logout = 0, request_exit = 0, correct_password = 0, password_tries = 0):
        self.session_id = uuid.uuid4()
        self.username = username
        self.full_name = full_name
        self.is_admin = is_admin
        self.is_active = is_active
        self.has_password = has_password
        self.request_logout = request_logout
        self.request_exit = request_exit
        self.correct_password = correct_password
        self.password_tries = password_tries

    def user_setup(self):
        if not self.is_active:
            if self.is_admin:
                print("As a security practice it is recommended that\n"
                      "you change the name of admin account and its password")
                self.set_username()
                print("Set a admin password.")
            else:
                print("Set a password.")
            self.set_password()
            self.set_active(1)
        elif self.is_active and not self.has_password:
            if self.is_admin:
                print("As a security practice it is recommended that\n"
                      "you change the name of admin account and its password")
                self.set_username()
                print("Set a admin password.")
            else:
                print("Set a password.")
            self.set_password()
            self.set_active(1)
        else:
            print("You're not supposed to be here.")


    @staticmethod
    def list_users():
        list_query = f"""
        SELECT ID, Username, isAdmin, isActive FROM {User.db_table};
        """
        user_list = SqlDB.sql_query_result(list_query, use_sqlite3=UserSettings.use_sqlite3)
        if UserSettings.at_cli:
            UserSettings.clear()
        print(f"{"ID":>3s}  {"Username":<15s} {"isAdmin":>7s}  {"isActive":>8s}")
        for user in user_list:
            print(f"{user[0]:>3}  {user[1]:<15s} {user[2]:>7}  {user[3]:>8}")
        print()

    def promote_user(self):
        self.set_admin(1)

    def demote_user(self):
        self.set_admin(0)

    def set_admin(self, state):
        update_query = f"""UPDATE {User.db_table}
        SET isAdmin = {state}
        WHERE Username = "{self.username}";
        """
        SqlDB.sql_query(update_query, User.db_table, use_sqlite3=UserSettings.use_sqlite3)
        if self.is_admin:
            been_admin = True
        else:
            been_admin = False
        self.is_admin = 1
        if not self.is_admin and been_admin:
            print(f"User {self.username} has been demoted")
            print()
        else:
            print(f"User {self.username} has been promoted")
            print()

    @staticmethod
    def promote_user_by_name():
        if UserSettings.at_cli:
            UserSettings.clear()
        valid = False
        while not valid:
            print(" Promotion user form ".center(60, "-"))
            username = input("Username: ")
            print()
            select_query = f"""SELECT Username, isActive FROM {User.db_table};"""
            result = SqlDB.sql_query_result(select_query, use_sqlite3=UserSettings.use_sqlite3)
            for result_user in result:
                if username == result_user[0]:
                    valid = True
                    promote_user = User(result_user[0], is_active=result_user[1])
                    break
            if not valid:
                print(f"Username {username} doesn't exist")
                print()
        promote_user.promote_user()

    @staticmethod
    def demote_user_by_name():
        if UserSettings.at_cli:
            UserSettings.clear()
        valid = False
        while not valid:
            print(" Demotion user form ".center(60, "-"))
            username = input("Username: ")
            print()
            select_query = f"""SELECT Username, isActive FROM {User.db_table};"""
            result = SqlDB.sql_query_result(select_query, use_sqlite3=UserSettings.use_sqlite3)
            for result_user in result:
                if username == result_user[0]:
                    valid = True
                    demote_user = User(result_user[0], is_active=result_user[1])
                    break
            if not valid:
                print(f"Username {username} doesn't exist")
                print()
        demote_user.demote_user()

    def set_active(self, state):
        """
        Args:
            state: 0 for inactive
                   1 for active
        """
        update_query = f"""UPDATE {User.db_table}
                SET isActive = {state}
                WHERE Username = "{self.username}";
                """
        SqlDB.sql_query(update_query, User.db_table, use_sqlite3=UserSettings.use_sqlite3)
        if self.is_active:
            been_active = True
        else:
            been_active = False
        self.is_active = state
        if not self.is_active:
            if been_active:
                print(f"User {self.username} has been deactivated")
                print()
            else:
                print(f"User {self.username} was already inactive")
                print()
        elif self.is_active:
            if not been_active:
                print(f"User {self.username} has been activated")
                print()
            else:
                print(f"User {self.username} was already active")
                print()


    @staticmethod
    def set_active_by_user(state):
        """
        Args:
            state: 0 for inactive
                   1 for active
        """
        if UserSettings.at_cli:
            UserSettings.clear()
        valid = False
        while not valid:
            print(f" {"Activate" if state else "Deactivate"} user form ".center(60, "-"))
            username = input("Username: ")
            print()
            select_query = f"""SELECT Username, isActive FROM {User.db_table};"""
            result = SqlDB.sql_query_result(select_query, use_sqlite3=UserSettings.use_sqlite3)
            for result_user in result:
                if username == result_user[0]:
                    valid = True
                    reset_user = User(result_user[0], is_active=result_user[1])
                    break
            if not valid:
                print(f"Username {username} doesn't exist")
                print()

        reset_user.set_active(state)

    def delete_user(self):
        delete_query = f"""DELETE FROM {User.db_table}
        WHERE Username = "{self.username}";
        """
        SqlDB.sql_query(delete_query, User.db_table, use_sqlite3=UserSettings.use_sqlite3)
        select_query = f"""SELECT Username FROM {User.db_table}
        WHERE Username = "{self.username}"
        """
        result = SqlDB.sql_query_result(select_query, use_sqlite3=UserSettings.use_sqlite3)
        if len(result) == 0:
            print(f"User {self.username} has been deleted")
            print()

    @staticmethod
    def delete_user_by_name():
        if UserSettings.at_cli:
            UserSettings.clear()
        valid = False
        last_admin = False
        while not valid:
            print(" Delete user form ".center(60, "-"))
            username = input("Username: ")
            print()
            select_query = f"""SELECT Username, isAdmin, isActive FROM {User.db_table};"""
            result = SqlDB.sql_query_result(select_query, use_sqlite3=UserSettings.use_sqlite3)
            for result_user in result:
                if username == result_user[0]:
                    if result_user[1]:
                        select_query = f"""SELECT Username FROM {User.db_table} WHERE isAdmin = 1;"""
                        result = SqlDB.sql_query_result(select_query, use_sqlite3=UserSettings.use_sqlite3)
                        if len(result) == 1:
                            print(f"Cannot delete last admin {result[0][0]}")
                            print()
                            last_admin = True
                            break
                    valid = True
                    if not last_admin and valid:
                        delete_user = User(result_user[0], is_admin=result_user[1], is_active=result_user[2])
                    break
            if not valid and not last_admin:
                print(f"Username {username} doesn't exist")
                print()
        if valid:
            if delete_user.is_active:
                print(f"{delete_user.username} is active.")
                while True:
                    option = input("Are you sure you want to continue?(Y/n): ")
                    print()
                    if option.strip().lower() == "y" or option.strip().lower() == "":
                        delete_user.delete_user()
                        break
                    elif option.strip().lower() == "n":
                        print("No user has been deleted")
                        print()
                        return
            else:
                delete_user.delete_user()

    def set_username(self):
        username = input("Username: ")
        update_query = f"""UPDATE {User.db_table}
        SET Username = "{username}"
        WHERE Username = "{self.username}";
        """
        SqlDB.sql_query(update_query, User.db_table, use_sqlite3=UserSettings.use_sqlite3)
        self.username = username

    def set_password(self):
        if UserSettings.at_cli:
            password1 = "password1"
            password2 = "password2"
            while password1 != password2:
                password1 = getpass()
                password2 = getpass("Retype password: ")
                if password1 != password2:
                    print("Passwords don't match, try again!")
                    print()
            password = password1
        else:
            password1 = "password1"
            password2 = "password2"
            while password1 != password2:
                password1 = input("Password: ")
                password2 = input("Retype password: ")
                if password1 != password2:
                    print("Passwords don't match, try again!")
                    print()
            password = password1
        salt = bcrypt.gensalt()
        password_hash = User.hashpw(password, salt)
        update_query = f"""UPDATE {User.db_table} 
        SET passwordHash = "{password_hash}"
        WHERE Username = "{self.username}";
        """
        # passwordSalt = "{salt.decode("utf-8")}"
        SqlDB.sql_query(update_query, User.db_table, use_sqlite3=UserSettings.use_sqlite3)
        self.has_password = 1
        self.correct_password = 1
        print("Password has been set")
        User.wait_for_enter()
        print()

    def set_full_name(self):
        if UserSettings.at_cli:
            UserSettings.clear()
        print(" Set user fullname ".center(60, "-"))
        full_name = input("Full name: ")
        print()
        update_query = f"""UPDATE {User.db_table}
                SET fullName = "{full_name}"
                WHERE Username = "{self.username}";
                """
        SqlDB.sql_query(update_query, User.db_table, use_sqlite3=UserSettings.use_sqlite3)
        self.full_name = full_name
        print(f"User {self.username} now has \"{self.full_name}\" as display name")
        print()

    def details(self):
        if UserSettings.at_cli:
            UserSettings.clear()
        print(f"User ", end="")
        print(f"{self.username}" if self.full_name is None else f"{self.full_name}({self.username})")
        print(f"Session ID: {self.session_id}")
        print("Is active" if self.is_active else "Isn't active", end=" and ")
        print("is admin" if self.is_admin else "isn't admin")
        print()

    @staticmethod
    def reset_password(username):
        print(f"Reset password for {username}")
        if UserSettings.at_cli:
            password1 = "password1"
            password2 = "password2"
            while password1 != password2:
                password1 = getpass()
                password2 = getpass("Retype password: ")
                if password1 != password2:
                    print()
                    print("Passwords don't match, try again!")
                    print()
            password = password1
        else:
            password1 = "password1"
            password2 = "password2"
            while password1 != password2:
                password1 = input("Password: ")
                password2 = input("Retype password: ")
                if password1 != password2:
                    print()
                    print("Passwords don't match, try again!")
                    print()
            password = password1
        salt = bcrypt.gensalt()
        password_hash = User.hashpw(password, salt)
        update_query = f"""UPDATE {User.db_table} 
            SET passwordHash = "{password_hash}"
            WHERE Username = "{username}";
            """
        # passwordSalt = "{salt.decode("utf-8")}"
        SqlDB.sql_query(update_query, User.db_table, use_sqlite3=UserSettings.use_sqlite3)
        print()
        print("Password has been reset")
        User.wait_for_enter()

        query = f"""SELECT Username, isAdmin, isActive 
        FROM {User.db_table} 
        WHERE Username = "{username}";
        """
        result = SqlDB.sql_query_result(query, use_sqlite3=UserSettings.use_sqlite3)[0]
        user = User(result[0], is_admin=result[1], is_active=result[2], has_password=1, correct_password=1)
        return user

    @staticmethod
    def register_form(active = 1):
        if UserSettings.at_cli:
            UserSettings.clear()
        print(" Register a user ".center(60, "-"))
        valid = False
        while not valid:
            username = input("Username: ")
            select_query = f"""SELECT Username FROM {User.db_table};"""
            names = SqlDB.sql_query_result(select_query, use_sqlite3=UserSettings.use_sqlite3)
            for name in names:
                if username == name[0]:
                    print(f"Username {name[0]} already exists")
                    valid = False
                    break
            else:
                valid = True
        print(f"username {username} is valid")
        print()

        new_user = User.add_new_user(username)
        if active:
            new_user.set_password()
        new_user.set_active(active)
        return new_user

    @staticmethod
    def add_new_user(username):
        next_id = SqlDB.get_last_id(User.db_table, UserSettings.use_sqlite3) + 1
        insert_query = f"""
        INSERT INTO {User.db_table} (ID, Username, isAdmin, isActive)
        VALUES ({next_id}, "{username}",  0, 0);
        """
        SqlDB.sql_query(insert_query, User.db_table, use_sqlite3=UserSettings.use_sqlite3)
        print(f"User {username} has been registered and needs activation")
        print()
        return User(username, is_admin=0, is_active=0)

    @staticmethod
    def register_user():
        user = User.register_form()
        return user

    def logged_user_menu(self):
        hold_clear = False
        option = -1
        while option != 0 or option != 1:
            if UserSettings.at_cli and not hold_clear:
                UserSettings.clear()
            else:
                hold_clear = False
            print(" 1 - Log out")
            print(" 2 - User details")
            print(" 3 - Set full user name")
            print("   -")
            if self.is_admin:
                print(" 4 - List users")
                print(" 5 - Register user")
                print(" 6 - Activate a user")
                print(" 7 - Deactivate a user")
                print(" 8 - Delete a user")
                print(" 9 - Promote a user")
                print("10 - Demote a admin")
            else:
                print(f" 4 - Select library (Current: {UserSettings.user_library_name})")
                print(" 5 - List libraries")
                print(" 6 - Delete a library")
                print("   -")
                print(" 7 - List all books")
                print(" 8 - Search books")
                print(" 9 - Add book")
                print("10 - Remove book")
                print("   -")
                print("11 - List lent books")
                print("12 - Lend a book")
                print("13 - Return a book")
            print()
            print("0 - Exit")
            option = UserSettings.read_menu_option(">> ")
            print()
            if option == 1:
                self.request_logout = 1
                print("Logged out")
                print()
                hold_clear = True
                return self
            elif option == 2:
                self.details()
                hold_clear = True
            elif option == 3:
                self.set_full_name()
                hold_clear = True
            elif option == 4:
                if self.is_admin:
                    User.list_users()
                    hold_clear = True
                else:
                    User.set_library()
                    hold_clear = True
            elif option == 5:
                if self.is_admin:
                    User.register_form(0)
                    hold_clear = True
                else:
                    BookStores.list_libraries()
                    hold_clear = True
            elif option == 6:
                if self.is_admin:
                    User.set_active_by_user(1)
                    hold_clear = True
                else:
                    BookStores.del_library()
                    hold_clear = True
            elif option == 7:
                if self.is_admin:
                    User.set_active_by_user(0)
                    hold_clear = True
                else:
                    BookStore.list_entries(UserSettings.user_library_name)
                    hold_clear = True
            elif option == 8:
                if self.is_admin:
                    User.delete_user_by_name()
                    hold_clear = True
                else:
                    BookStore.search_book(UserSettings.user_library_name)
                    hold_clear = True
            elif option == 9:
                if self.is_admin:
                    User.promote_user_by_name()
                    hold_clear = True
                else:
                    BookStore.add_entry(UserSettings.user_library_name)
                    hold_clear = True
            elif option == 10:
                if self.is_admin:
                    User.demote_user_by_name()
                    hold_clear = True
                else:
                    BookStore.delete_book(UserSettings.user_library_name)
                    hold_clear = True
            elif option == 11:
                if self.is_admin:
                    print("Nothing here")
                    hold_clear = True
                else:
                    Loans.list_loans()
                    hold_clear = True
            elif option == 12:
                if self.is_admin:
                    print("Nothing here")
                    hold_clear = True
                else:
                    Loans.loan_book()
                    hold_clear = True
            elif option == 13:
                if self.is_admin:
                    print("Nothing here")
                    hold_clear = True
                else:

                    hold_clear = True
            elif option == 0:
                self.request_exit = 1
                print("Good bye!")
                print()
                return self
        return None

    @staticmethod
    def set_library():
        if UserSettings.at_cli:
            UserSettings.clear()
        UserSettings.user_library_name = input("Library name: ")
        UserSettings.edit_config("config.ini", "USER-LIBRARY", "name", UserSettings.user_library_name)
        BookStores.save_to_db(UserSettings.user_library_name)
        print()

    def log_to_file(self):
        logging.basicConfig(filename="Users.log",
                            filemode='a',
                            format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.INFO)

        if self.request_logout or self.request_exit:
            action = "out"
        else:
            action = "in"
        logging.info(f'{self.username} logged {action} with session_id = {self.session_id}')

    @staticmethod
    def init_db(table, drop = False):
        query_init = f'''
        CREATE TABLE {table} (
        ID INT NOT NULL,
        Username VARCHAR(50) NOT NULL UNIQUE,
        fullName VARCHAR(128),
        isAdmin INT NOT NULL,
        isActive INT NOT NULL,
        passwordHash VARCHAR(128),
        PRIMARY KEY(ID)
        );
        '''
        SqlDB.sql_query(query_init, table, drop, UserSettings.use_sqlite3)
        next_id = SqlDB.get_last_id(table, UserSettings.use_sqlite3) + 1
        salt = bcrypt.gensalt()
        password_hash = User.hashpw("adminadmin", salt)
        query_admin = f'''
        INSERT INTO {table} (ID, Username, isAdmin, isActive, passwordHash)
        VALUES ({next_id}, "admin",  1, 0, "{password_hash}");
        '''
        SqlDB.sql_query(query_admin, table, use_sqlite3=UserSettings.use_sqlite3)
        return None

    @staticmethod
    def wait_for_enter():
        print()
        input("Press enter to continue...")
        print()

    @staticmethod
    def hashpw(password, salt):
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def checkhash(password, hashed_password):
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

