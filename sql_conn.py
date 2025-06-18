import os
import sqlite3
import mysql.connector
from configparser import ConfigParser
from sqlite3 import IntegrityError as sqlite3_IntegrityError
from mysql.connector import Error, ProgrammingError, OperationalError, IntegrityError


class SqlConn(mysql.connector.MySQLConnection):
    """
    Child class of mysql.connector that is useful for streamlining connecting and working with a mysql server
    """
    def __init__(self, host, port, user, password, database=None):
        try:
            super().__init__(host=host, port=port, user=user, password=password, database=database)
            # print("Connection to MySQL DB successful")
            self.initialized = True
        except Error:
            print(f"Error: '{Error}'")
            self.initialized = False

    @staticmethod
    def sql_query(db_query, db_table, drop = False):
        """
        Used to query a database when not expecting a result
        For ex: CREATE, INSERT, UPDATE
        :param db_query:
        :param db_table:
        :param drop:
        """
        conn = SqlConn.connect_db()
        cursor = conn.cursor()
        if drop and db_table != "":
            cursor.execute(f"""
                DROP TABLE IF EXISTS {db_table};
                """)  # Execute a drop command
            conn.commit()  # commit the drop query
        try:
            cursor.execute(db_query)
            conn.commit()
            conn.close()  # close the connection
        except IntegrityError:
            conn.close()
            raise IntegrityError


    @staticmethod
    def sql_query_result(db_query, print_out=False):
        """
        Used for querying a database when expecting a result
        For ex: SELECT
        :param db_query:
        :param print_out:
        :return: a list object contain the result
        """
        conn = SqlConn.connect_db()
        cursor = conn.cursor()  # cursor
        try:
            cursor.execute(db_query)  # execute the query
        except ProgrammingError:
            raise ProgrammingError
        rows = cursor.fetchall()  # fetch all the output
        if print_out:
            for row in rows:
                print(row)
        conn.close()  # close the connection
        return rows

    @staticmethod
    def get_last_id(db_table):
        """
        Useful when adding to a database to obtain the highest ID,
        so you can increment it for the next line
        :param db_table:
        :return: an int max id
        """
        last_id = SqlConn.sql_query_result(f"""SELECT MAX(ID) FROM {db_table};""")
        last_id = last_id[0][0]  # last_id is a list of tuples, so the value we want is at that index
        if last_id is None:
            last_id = 0
        return last_id

    @staticmethod
    def connect_db():
        """
        Calls method that retrieved data about sql connection
        :return: a connection object
        """
        try:
            conn = SqlConn.set_config()
            return conn
        except OperationalError:
            print("MySQL Connection failed")
            exit()

    @staticmethod
    def set_config():
        """
        Load data from config.ini into memory
        :return: a connection object
        """
        try:
            db_connection = SqlConn.read_config("config.ini", "DB-CONNECTION")
            conn = SqlConn(db_connection["host"], int(db_connection["port"]),
                           db_connection["user"], db_connection["password"], db_connection["database"])
            if not conn.is_connected():
                raise OperationalError
            return conn
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
        """
        Reads the config file for sql user settings
        :param file_name:
        :param settings:
        :return: a SectionProxy object of the whole ConfigParser
        """
        # read the file
        config_object = ConfigParser()
        if not os.path.exists(file_name):
            raise FileNotFoundError
        config_object.read(file_name)

        # get config options
        values = config_object[settings]
        return values

    def __del__(self):
        if self.is_connected() and self.initialized:
            self.close()
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.is_connected() and self.initialized:
            self.close()
        return False


class Sqlite3Conn(sqlite3.Connection):
    """
    Child class of sqlite3.Connection in order to streamline usage of work with sqlite3 db file
    """
    def __init__(self, db_file):
        super().__init__(db_file + ".sqlite3")

    @staticmethod
    def sql_query(db_query, db_table, drop=False):
        """
        Used to query a database when not expecting a result
        For ex: CREATE, INSERT, UPDATE
        :param db_query:
        :param db_table:
        :param drop:
        """
        conn = Sqlite3Conn.connect_db()
        cursor = conn.cursor()
        if drop and db_table != "":
            cursor.execute(f"""
                DROP TABLE IF EXISTS {db_table};
                """)  # Execute a drop command
            conn.commit()  # commit the drop query
        try:
            cursor.execute(db_query)
            conn.commit()
            conn.close()  # close the connection
        except sqlite3_IntegrityError:
            conn.close()
            raise sqlite3_IntegrityError

    @staticmethod
    def get_last_id(db_table):
        """
        Useful when adding to a database to obtain the highest ID,
        so you can increment it for the next line
        :param db_table:
        :return: an int max id
        """
        last_id = Sqlite3Conn.sql_query_result(f"""SELECT MAX(ID) FROM {db_table};""")
        last_id = last_id[0][0]  # last_id is a list of tuples, so the value we want is at that index
        if last_id is None:
            last_id = 0
        return last_id

    @staticmethod
    def sql_query_result(db_query, print_out=False):
        """
        Used for querying a database when expecting a result
        For ex: SELECT
        :param db_query:
        :param print_out:
        :return: a list object contain the result
        """
        conn = Sqlite3Conn.connect_db()
        cursor = conn.cursor()  # cursor
        try:
            cursor.execute(db_query)  # execute the query
        except ProgrammingError:
            raise ProgrammingError
        rows = cursor.fetchall()  # fetch all the output
        if print_out:
            for row in rows:
                print(row)
        # conn.close()  # close the connection
        return rows

    @staticmethod
    def connect_db():
        """
        Calls method that retrieved data about sql connection
        :return: a connection object
        """
        try:
            conn = Sqlite3Conn.set_config()
            return conn
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
    def set_config():
        """
        Load data from config.ini into memory
        :return: a connection object
        """
        try:
            db_connection = Sqlite3Conn.read_config("config.ini", "DB-CONNECTION")
            conn = Sqlite3Conn(db_connection["database"])
            return conn
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
        """
        Reads the config file for sql user settings
        :param file_name:
        :param settings:
        :return: a SectionProxy object of the whole ConfigParser
        """
        # read the file
        config_object = ConfigParser()
        if not os.path.exists(file_name):
            raise FileNotFoundError
        config_object.read(file_name)

        # get config options
        values = config_object[settings]
        return values

    def __del__(self):
        self.close()


class SqlDB:
    """
    class that is used to make connection to a sql server or file, user setting dependant
    """
    @staticmethod
    def sql_query(db_query, db_table, drop=False, use_sqlite3=False):
        if use_sqlite3:
            Sqlite3Conn.sql_query(db_query, db_table, drop)
        else:
            SqlConn.sql_query(db_query, db_table, drop)

    @staticmethod
    def sql_query_result(db_query, print_out=False, use_sqlite3=False):
        if use_sqlite3:
            return Sqlite3Conn.sql_query_result(db_query, print_out)
        else:
            return SqlConn.sql_query_result(db_query, print_out)

    @staticmethod
    def get_last_id(db_table, use_sqlite3=False):
        if use_sqlite3:
            return Sqlite3Conn.get_last_id(db_table)
        else:
            return SqlConn.get_last_id(db_table)

    @staticmethod
    def connect_db(use_sqlite3=False):
        if use_sqlite3:
            return Sqlite3Conn.connect_db()
        else:
            return SqlConn.connect_db()

