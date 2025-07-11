# Book-Store-with-Python

###### A CLI experience with login and user management for keeping records of available and lent books to clients
### As a logged-in administrator you can:
1) Manage users(list, add, remove, promote, demote, user status - active/deactivated)
### As a logged-in user you can:
1) Select working library (possibility to have multiple individual libraries)
2) Manage available books(add, remove)
2) Lend books to clients
3) Receive returned books from clients

## Config file
An ini config file, that: 
1) Sets connect data for a mysql server.
2) Config parameter to use an internal sqlite3 db file or use a mysql server
3) Sets `getpass()` as function for reading password when in terminal 
and uses `clear` commands for windows and linux
4) Selects the working books library for the user

## A log text file
1) A txt log file with login time, date and a unique session id so the app keeps a record

## Next steps
1) When removing a library, add functionality:
   - distribute books in that library to other libraries that have more of that book
   - modify quantities and available counters 
   - distribute equally books that aren't present elsewhere
   - drop table in the database

### Technical information
#### 1) Used python packages:
   - pip v25.1.1
   - bcrypt v4.3.0 - for hashing and checking clear text password against hash
   - mysql-connector-python v9.3.0 - for connecting to a standalone mysql server
   - ConfigParser (default Python library) - for parsing a `.ini` file for some user set config options
   - getpass (default Python library) - `getpass()` for terminal, shoulder surfing safe password entry
   - uuid (default Python library) - for generating a unique session ID for each user once they log in
   - sqlite3 (default Python library) - for using a `.sqlite3` database file instead of a mysql server in case that requirement isn't met
   - sys, os (default Python library) - for clearing the screen on windows and linux systems when running in terminal
#### 2) Requirements:
   - have python installed, you can check to see if it's installed by typing `py --version` in terminal
   - have set up a standalone mysql server with `user = python-user`, `password = python-password` 
     and `database = python` which would be the database name or schema, 
     highly recommended to set up a different password
 
## First time use instructions
- Start the program at terminal by running `py book_store.py` so it generates the required files, it will exit automatically
- Look for `config.ini` and modify `at_cli = 0` to `at_cli = 1` so the terminal clears and hides passwords, start the program again
- If the sqlite3 db is in use, under `[DB-CONNECTION]` only the `database` key is used, 
the others can have random values or miss entirely
- First time you start the program, it will generate a new database (mySQL/sqlite3 - 
user choice in `config.ini` look for `[USER-LIBRARY]` with key `name = BookStore`)
- It will create a new admin user with admin privileges
- You will have to log in with user: `admin` and password: `adminadmin`
- You will be prompted to change them both