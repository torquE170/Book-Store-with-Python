import os
import sys
import uuid
import bcrypt
from getpass import getpass
from sql_conn import SqlConn, Sqlite3Conn
from configparser import ConfigParser


class User:
    at_cli = 0  # toggle to 1 to use getpass when at cli for password entry
    use_sqlite3 = 0  # toggle to 1 to use a local sqlite3 file as a database
    def __init__(self, username, full_name = None, is_admin = 0, is_active = 0, has_password = 0):
        self.session_id = uuid.uuid4()
        self.username = username
        self.full_name = full_name
        self.is_admin = is_admin
        self.is_active = is_active
        self.has_password = has_password

    @staticmethod
    def set_config():
        try:
            user_settings = User.read_config("config.ini", "USER-SETTINGS")
            User.at_cli = int(user_settings["at_cli"])
            User.use_sqlite3 = int(user_settings["use_sqlite3"])
        except ValueError:
            print("Invalid config file")
            exit()
        except KeyError:
            print("Missing key in config file")
            exit()
        except FileNotFoundError:
            print("Missing config file")
            exit()

    @staticmethod
    def read_config(file_name, settings):
        # read the file
        config_object = ConfigParser()
        if not os.path.exists(file_name):
            raise FileNotFoundError
        config_object.read(file_name)

        # get config options
        values = config_object[settings]
        return values

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
        else:
            print("You're not supposed to be here")

    @staticmethod
    def list_users():
        db_table = "Users_db"
        list_query = f"""
        SELECT ID, Username, isAdmin, isActive FROM {db_table};
        """
        if not User.use_sqlite3:
            user_list = SqlConn.sql_query_result(list_query)
        else:
            user_list = Sqlite3Conn.sql_query_result(db_table, list_query)
        # pprint(user_list)
        if User.at_cli:
            User.clear()
        print(f"{"ID":>3s}  {"Username":<15s} {"isAdmin":>7s}  {"isActive":>8s}")
        for user in user_list:
            print(f"{user[0]:>3}  {user[1]:<15s} {user[2]:>7}  {user[3]:>8}")
        print()

    def promote_user(self):
        self.set_admin(1)

    def demote_user(self):
        self.set_admin(0)

    def set_admin(self, state):
        db_table = "Users_db"
        update_query = f"""UPDATE {db_table}
        SET isAdmin = {state}
        WHERE Username = "{self.username}";
        """
        if not User.use_sqlite3:
            SqlConn.sql_query(update_query, db_table)
        else:
            Sqlite3Conn.sql_query(update_query, db_table)
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
        valid = False
        while not valid:
            print("Promotion user form")
            username = input("Username: ")
            print()
            db_table = "Users_db"
            select_query = f"""SELECT Username, isActive FROM {db_table};"""
            if not User.use_sqlite3:
                result = SqlConn.sql_query_result(select_query)
            else:
                result = Sqlite3Conn.sql_query_result(db_table, select_query)
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
        valid = False
        while not valid:
            print("Demotion user form")
            username = input("Username: ")
            print()
            db_table = "Users_db"
            select_query = f"""SELECT Username, isActive FROM {db_table};"""
            if not User.use_sqlite3:
                result = SqlConn.sql_query_result(select_query)
            else:
                result = Sqlite3Conn.sql_query_result(db_table, select_query)
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
        db_table = "Users_db"
        update_query = f"""UPDATE {db_table}
                SET isActive = {state}
                WHERE Username = "{self.username}";
                """
        if not User.use_sqlite3:
            SqlConn.sql_query(update_query, db_table)
        else:
            Sqlite3Conn.sql_query(update_query,db_table)
        if self.is_active:
            been_active = True
        else:
            been_active = False
        self.is_active = state
        if not self.is_active and been_active:
            print(f"User {self.username} has been deactivated")
            print()
        elif self.is_active and not been_active:
            print(f"User {self.username} has been activated")
            print()

    @staticmethod
    def set_active_by_user(state):
        """
        Args:
            state: 0 for inactive
                   1 for active
        """
        valid = False
        while not valid:
            print(f"{"Activate" if state else "Deactivate"} user form")
            username = input("Username: ")
            print()
            db_table = "Users_db"
            select_query = f"""SELECT Username, isActive FROM {db_table};"""
            if not User.use_sqlite3:
                result = SqlConn.sql_query_result(select_query)
            else:
                result = Sqlite3Conn.sql_query_result(db_table, select_query)
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
        db_table = "Users_db"
        delete_query = f"""DELETE FROM {db_table}
        WHERE Username = "{self.username}";
        """
        if not User.use_sqlite3:
            SqlConn.sql_query(delete_query, db_table)
        else:
            Sqlite3Conn.sql_query(delete_query, db_table)
        select_query = f"""SELECT Username FROM {db_table}
        WHERE Username = "{self.username}"
        """
        if not User.use_sqlite3:
            result = SqlConn.sql_query_result(select_query)
        else:
            result = Sqlite3Conn.sql_query_result(db_table, select_query)
        if len(result) == 0:
            print(f"User {self.username} has been deleted")
            print()

    @staticmethod
    def delete_user_by_name():
        valid = False
        last_admin = False
        while not valid and not last_admin:
            print("Delete user form")
            username = input("Username: ")
            print()
            db_table = "Users_db"
            select_query = f"""SELECT Username, isAdmin, isActive FROM {db_table};"""
            if not User.use_sqlite3:
                result = SqlConn.sql_query_result(select_query)
            else:
                result = Sqlite3Conn.sql_query_result(db_table, select_query)
            for result_user in result:
                if username == result_user[0]:
                    select_query = f"""SELECT Username FROM {db_table} WHERE isAdmin = 1;"""
                    if not User.use_sqlite3:
                        result = SqlConn.sql_query_result(select_query)
                    else:
                        result = Sqlite3Conn.sql_query_result(db_table, select_query)
                    if len(result) == 1:
                        print(f"Cannot delete last admin {result[0][0]}")
                        print()
                        last_admin = True
                        break
                    valid = True
                    delete_user = User(result_user[0], is_active=result_user[1])
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
            if valid:
                if not delete_user.is_active:
                    delete_user.delete_user()

    def set_username(self):
        db_table = "Users_db"
        username = input("Username: ")
        update_query = f"""UPDATE {db_table}
        SET Username = "{username}"
        WHERE Username = "{self.username}";
        """
        if not User.use_sqlite3:
            SqlConn.sql_query(update_query, db_table)
        else:
            Sqlite3Conn.sql_query(update_query, db_table)
        self.username = username

    def set_password(self):
        db_table = "Users_db"
        if User.at_cli:
            password1 = "password1"
            password2 = "password2"
            while password1 != password2:
                password1 = getpass()
                password2 = getpass("Retype password: ")
                if password1 != password2:
                    print("Passwords don't match, try again!")
            password = password1
        else:
            password1 = "password1"
            password2 = "password2"
            while password1 != password2:
                password1 = input("Password: ")
                password2 = input("Retype password: ")
                if password1 != password2:
                    print("Passwords don't match, try again!")
            password = password1
        salt = bcrypt.gensalt()
        password_hash = User.hashpw(password, salt)
        update_query = f"""UPDATE {db_table} 
        SET passwordHash = "{password_hash}",
        passwordSalt = "{salt.decode("utf-8")}"
        WHERE Username = "{self.username}";
        """
        if not User.use_sqlite3:
            SqlConn.sql_query(update_query, db_table)
        else:
            Sqlite3Conn.sql_query(update_query, db_table)
        self.has_password = 1
        print("Password has been set")
        print()

    def set_full_name(self):
        db_table = "Users_db"
        full_name = input("Full name: ")
        print()
        update_query = f"""UPDATE {db_table}
                SET fullName = "{full_name}"
                WHERE Username = "{self.username}";
                """
        if not User.use_sqlite3:
            SqlConn.sql_query(update_query, db_table)
        else:
            Sqlite3Conn.sql_query(update_query, db_table)
        self.full_name = full_name
        print(f"User {self.username} now has \"{self.full_name}\" as display name")
        print()

    @staticmethod
    def reset_password(username):
        print(f"Reset password for {username}")
        db_table = "Users_db"
        if User.at_cli:
            password1 = "password1"
            password2 = "password2"
            while password1 != password2:
                password1 = getpass()
                password2 = getpass("Retype password: ")
                if password1 != password2:
                    print("Passwords don't match, try again!")
            password = password1
        else:
            password1 = "password1"
            password2 = "password2"
            while password1 != password2:
                password1 = input("Password: ")
                password2 = input("Retype password: ")
                if password1 != password2:
                    print("Passwords don't match, try again!")
            password = password1
        salt = bcrypt.gensalt()
        password_hash = User.hashpw(password, salt)
        update_query = f"""UPDATE {db_table} 
            SET passwordHash = "{password_hash}",
            passwordSalt = "{salt.decode("utf-8")}"
            WHERE Username = "{username}";
            """
        if not User.use_sqlite3:
            SqlConn.sql_query(update_query, db_table)
        else:
            Sqlite3Conn.sql_query(update_query, db_table)
        print("Password has been reset")
        print()
        query = f"""SELECT Username, isAdmin, isActive 
        FROM {db_table} 
        WHERE Username = "{username}";
        """
        if not User.use_sqlite3:
            result = SqlConn.sql_query_result(query)[0]
        else:
            result = Sqlite3Conn.sql_query_result(db_table, query)[0]
        user = User(result[0], is_admin=result[1], is_active=result[2], has_password=1)
        return user

    @staticmethod
    def register_form(active = 1):
        if User.at_cli:
            User.clear()
        print("Register a user")
        valid = False
        while not valid:
            username = input("Username: ")
            db_table = "Users_db"
            select_query = f"""SELECT Username FROM {db_table};"""
            if not User.use_sqlite3:
                names = SqlConn.sql_query_result(select_query)
            else:
                names = Sqlite3Conn.sql_query_result(db_table, select_query)
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
        db_table = "Users_db"
        if not User.use_sqlite3:
            next_id = SqlConn.get_last_id(db_table) + 1
        else:
            next_id = Sqlite3Conn.get_last_id(db_table) + 1
        insert_query = f"""
        INSERT INTO {db_table} (ID, Username, isAdmin, isActive)
        VALUES ({next_id}, "{username}",  0, 0);
        """
        if not User.use_sqlite3:
            SqlConn.sql_query(insert_query, db_table)
        else:
            Sqlite3Conn.sql_query(insert_query, db_table)
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
            if User.at_cli and not hold_clear:
                User.clear()
            else:
                hold_clear = False
            print("1 - Log out")
            print("2 - User details")
            print("3 - Set full name")
            if self.is_admin:
                print("4 - List users")
            if self.is_admin:
                print("5 - Register user")
            if self.is_admin:
                print("6 - Activate a user")
            if self.is_admin:
                print("7 - Deactivate a user")
            if self.is_admin:
                print("8 - Delete a user")
            if self.is_admin:
                print("9 - Promote a user")
            if self.is_admin:
                print("10 - Demote a admin")
            print()
            print("0 - Exit")
            option = User.read_menu_option(">> ")
            print()
            if option == 1:
                self.session_id = "request_logout"
                print("Logged out")
                print()
                hold_clear = True
                return self
            elif option == 2:
                if User.at_cli:
                    User.clear()
                print(f"User ", end = "")
                print(f"{self.username}" if self.full_name is None else f"{self.full_name}({self.username})")
                print(f"Session ID: {self.session_id}")
                print("Is active" if self.is_active else "Isn't active", end = " and ")
                print("is admin" if self.is_admin else "isn't admin")
                print()
                hold_clear = True
            elif option == 3:
                self.set_full_name()
                hold_clear = True
            elif option == 4 and self.is_admin:
                User.list_users()
                hold_clear = True
            elif option == 5 and self.is_admin:
                User.register_form(0)
                hold_clear = True
            elif option == 6 and self.is_admin:
                User.set_active_by_user(1)
                hold_clear = True
            elif option == 7 and self.is_admin:
                User.set_active_by_user(0)
                hold_clear = True
            elif option == 8 and self.is_admin:
                User.delete_user_by_name()
                hold_clear = True
            elif option == 9 and self.is_admin:
                User.promote_user_by_name()
                hold_clear = True
            elif option == 10 and self.is_admin:
                User.demote_user_by_name()
                hold_clear = True
            elif option == 0:
                self.session_id = "request_exit"
                print("Good bye!")
                print()
                return self

    @staticmethod
    def read_menu_option(prompt):
        while True:
            try:
                number = int(input(prompt))
                return number
            except ValueError:
                return -1

    @staticmethod
    def clear():
        if "win" in sys.platform:
            os.system("cls")
        elif "linux" in sys.platform:
            os.system("clear")

    @staticmethod
    def init_db(db_table, drop=False):
        if not User.use_sqlite3:
            conn = SqlConn.connect_db()
        else:
            conn = Sqlite3Conn.connect_db(db_table)
        cursor = conn.cursor()
        query_init = f'''
        CREATE TABLE {db_table} (
        ID INT NOT NULL,
        Username VARCHAR(50) NOT NULL UNIQUE,
        fullName VARCHAR(128),
        isAdmin INT NOT NULL,
        isActive INT NOT NULL,
        passwordHash VARCHAR(128),
        passwordSalt VARCHAR(128),
        PRIMARY KEY(ID)
        );
        '''
        if not User.use_sqlite3:
            SqlConn.sql_query(query_init, db_table, drop)
        else:
            Sqlite3Conn.sql_query(query_init, db_table, drop)
        if not User.use_sqlite3:
            next_id = SqlConn.get_last_id(db_table) + 1
        else:
            next_id = Sqlite3Conn.get_last_id(db_table) + 1
        salt = bcrypt.gensalt()
        password_hash = User.hashpw("adminadmin", salt)
        query_admin = f'''
        INSERT INTO {db_table} (ID, Username, isAdmin, isActive, passwordHash, passwordSalt)
        VALUES ({next_id}, "admin",  1, 0, "{password_hash}", "{salt.decode("utf-8")}");
        '''
        if not User.use_sqlite3:
            SqlConn.sql_query(query_admin, db_table)
        else:
            Sqlite3Conn.sql_query(query_admin, db_table)

    @staticmethod
    def hashpw(password, salt):
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def checkhash(password, hashed_password):
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
