# EJ-ITFactory-Python-Project

###### A CLI experience with login and user management for keeping records of user defined items.
### As a logged in administrator you can:
1) Manage users(list, add, remove, promote, demote, user status - active/deactivated)

## Config file
An ini config file, that: 
1) Sets connect data for a mysql server. 
2) Config parameter to use an internal sqlite3 db file or use a mysql server
3) Sets getpass() as function for reading password when in terminal 
and uses "clear" commands for windows and linux

## A log text file
1) A txt log file with login time, date and a unique session id so the app keeps a record

## Next steps
1) Add ability for a user to add a database completely defined by him 
   - Add the ability for a user to manipulate entries in that database

### Technical information
1) Used python packages:
   - pip v25.0.1
   - bcrypt v4.2.1 - for hashing and checking clear text password against hash
   - mysql-connector-python v9.2.0 - for connecting to a standalone mysql server
   - ConfigParser (default Python library) - for parsing a .ini file for some user set config options
   - getpass (default Python library) - getpass() for terminal, shoulder surfing safe password entry
   - uuid (default Python library) - for generating a unique session ID for each user once they log in
   - sqlite3 (default Python library) - for using a .sqlite3 database file instead of a mysql server in case that requirement isn't met
   - sys, os (default Python library) - for clearing the screen on windows and linux systems when running in terminal
 
### First time use instructions
- First time you start the program, it will generate a new database (mySQL/sqlite3 - user choice)
- It will create a new admin user with admin privileges
- First time you will have to log in with user: admin and password: adminadmin
- You will be prompted to change them both