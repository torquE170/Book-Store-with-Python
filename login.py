import sqlite3
from user import User
from getpass import getpass
from sql_conn import SqlDB
from mysql.connector import ProgrammingError


class Login:
    @staticmethod
    def failed_login_menu():
        option = -1
        while option != 0:
            print("1 - Register a user")
            print("2 - Reset your password")
            print()
            print("0 - Exit")
            option = User.read_menu_option(">> ")
            print()
            if option == 1:
                return User.register_user()
            elif option == 2:
                valid = False
                while not valid:
                    print("Reset password form")
                    username = input("Username: ")
                    print()
                    db_table = "Users_db"
                    select_query = f"""SELECT Username, isActive FROM {db_table};"""
                    result = SqlDB.sql_query_result(select_query, use_sqlite3=User.use_sqlite3)
                    for result_user in result:
                        if username == result_user[0]:
                            valid = True
                            break
                    if not valid:
                        print(f"Username {username} doesn't exist")
                        print()

                return User.reset_password(username)
            elif option == 0:
                print("Good bye")
                print()

    @staticmethod
    def login_form():
        user = Login.login_user()
        exit_flag = False
        while not exit_flag:
            if user is not None:
                if (not user.is_active and not user.has_password
                    or not user.is_active and user.has_password and user.is_admin
                    or user.is_active and not user.has_password):
                    user.user_setup()
                elif user.session_id == "request_logout":
                    user = Login.login_user()
                elif user.session_id == "request_exit":
                    exit_flag = True
                    break
                if user is not None:
                    if not user.is_active and user.has_password and not user.is_admin:
                        print("User has been deactivated, contact admin")
                        print()
                        user = Login.login_user()
                if user is not None:
                    if user.is_active and user.has_password:
                        user.logged_user_menu()
            else:
                print("Login failed, try again later.")
                print()
                user = Login.failed_login_menu()
                if user is None:
                    exit_flag = True

    @staticmethod
    def login_user():
        hold_clear = False
        tries = 0
        while tries < 3:
            if User.at_cli and not hold_clear:
                User.clear()
            else:
                hold_clear = False
            print("Enter your username and password")
            username = input("Username: ")
            if User.at_cli:
                password = getpass()
                print()
            else:
                password = input("Password: ")
                print()
            username_check = False
            password_check = False
            active_check = False
            db_table = "Users_db"
            select_query = f"""SELECT Username, passwordHash, isActive FROM {db_table};"""
            try:
                result = SqlDB.sql_query_result(select_query, use_sqlite3=User.use_sqlite3)
            except ProgrammingError:
                User.init_db("Users_db", True)
                result = None
            except sqlite3.OperationalError:
                User.init_db("Users_db", True)
                result = None
            if result is not None:
                for result_user in result:
                    if username == result_user[0]:
                        username_check = True
                        if result_user[1] is not None:
                            if User.checkhash(password, result_user[1]):
                                password_check = True
                        if result_user[2]:
                            active_check = True
                        if result_user[1] is None:
                            has_password = 0
                        else:
                            has_password = 1
                        # recheck this condition
                        if username_check:
                            select_query = f"""SELECT Username, fullName, isAdmin, isActive, passwordHash FROM {db_table} WHERE Username = "{result_user[0]}";"""
                            result_user = SqlDB.sql_query_result(select_query, use_sqlite3=User.use_sqlite3)[0]
                            if result_user[4] is None:
                                has_password = 0
                            else:
                                has_password = 1
                            return User(result_user[0], full_name=result_user[1], is_admin=result_user[2], is_active=result_user[3], has_password=has_password)

            print("Invalid login credentials.")
            print()
            hold_clear = True
            tries += 1

User.set_config()
Login.login_form()
