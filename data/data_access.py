import sqlite3
from flask import g

def get_db():
    # if 'db' not in g:
    #     g.db = sqlite3.connect('banking.db')
    # return g.db
    return sqlite3.connect('banking.db')

# create a function to seed the sqlite database with some data
def seed_database():
    # connect to the sqlite database
    conn = get_db()
    # create a cursor object
    cursor = conn.cursor()
    # create a table to store the account details if it doesn't exist
    cursor.execute("CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY, account_number TEXT, account_holder TEXT, balance REAL)")
    # insert some sample data into the accounts table if it doesn't exist
    cursor.execute("INSERT OR IGNORE INTO accounts (account_number, account_holder, balance) VALUES ('1234567890', 'Alice', 1000.0)")
    cursor.execute("INSERT OR IGNORE INTO accounts (account_number, account_holder, balance) VALUES ('2345678901', 'Bob', 2000.0)")
    cursor.execute("INSERT OR IGNORE INTO accounts (account_number, account_holder, balance) VALUES ('3456789012', 'Charlie', 3000.0)")

    # INSERT some data in transactions table if it doesn't exist
    cursor.execute("CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY, account_number TEXT, transaction_type TEXT, amount REAL, transaction_date TEXT)")
    cursor.execute("INSERT INTO transactions (account_number, transaction_type, amount, transaction_date) SELECT '1234567890', 'credit', 1000.0, '2022-01-01' WHERE NOT EXISTS (SELECT 1 FROM transactions WHERE account_number='1234567890')")
    cursor.execute("INSERT INTO transactions (account_number, transaction_type, amount, transaction_date) SELECT '2345678901', 'credit', 2000.0, '2022-01-01' WHERE NOT EXISTS (SELECT 1 FROM transactions WHERE account_number='2345678901')")
    cursor.execute("INSERT INTO transactions (account_number, transaction_type, amount, transaction_date) SELECT '3456789012', 'credit', 3000.0, '2022-01-01' WHERE NOT EXISTS (SELECT 1 FROM transactions WHERE account_number='3456789012')")

    # insert some sample data into the credit card details table if it doesn't exist
    cursor.execute("CREATE TABLE IF NOT EXISTS credit_card_details (credit_card_number TEXT PRIMARY KEY, card_holder TEXT, expiry_date TEXT, cvv TEXT, credit_limit REAL, available_credit REAL)")
    cursor.execute("INSERT OR IGNORE INTO credit_card_details (credit_card_number, card_holder, expiry_date, cvv, credit_limit, available_credit) VALUES ('1234567890123456', 'Alice', '01/25', '123', 5000.0, 5000.0)")
    cursor.execute("INSERT OR IGNORE INTO credit_card_details (credit_card_number, card_holder, expiry_date, cvv, credit_limit, available_credit) VALUES ('2345678901234567', 'Bob', '01/25', '234', 6000.0, 6000.0)")
    cursor.execute("INSERT OR IGNORE INTO credit_card_details (credit_card_number, card_holder, expiry_date, cvv, credit_limit, available_credit) VALUES ('3456789012345679', 'Charlie', '01/25', '345', 7000.0, 7000.0)")
    # commit the changes
    conn.commit()
    # close the cursor
    cursor.close()
    # close the connection
    conn.close()

# create a function to get account details from a sqlite database
def get_account_details(account_number):
    # connect to the sqlite database
    conn = get_db()
    # create a cursor object
    cursor = conn.cursor()
    # execute a query to get the account details
    cursor.execute("SELECT * FROM accounts WHERE account_number=?", (account_number,))
    # fetch the account details
    account_details = cursor.fetchone()
    # close the cursor
    cursor.close()
    # close the connection
    conn.close()
    # return the account details
    return account_details

def get_transaction_details(account_number):
    # connect to the sqlite database
    conn = get_db()
    # create a cursor object
    cursor = conn.cursor()
    # execute a query to get the account details
    cursor.execute("SELECT * FROM transactions WHERE account_number=?", (account_number,))
    # fetch the account details
    transaction_details = cursor.fetchall()
    # close the cursor
    cursor.close()
    # close the connection
    conn.close()
    # return the account details
    return transaction_details

def get_credit_card_details(credit_card_number):
    # connect to the sqlite database
    conn = get_db()
    # create a cursor object
    cursor = conn.cursor()
    # execute a query to get the account details
    cursor.execute("SELECT * FROM credit_card_details WHERE credit_card_number=?", (credit_card_number,))
    # fetch the account details
    credit_card_details = cursor.fetchone()
    # close the cursor
    cursor.close()
    # close the connection
    conn.close()
    # return the account details
    return credit_card_details
