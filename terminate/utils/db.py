import os
import sqlite3

PROMPTDB = 'prompt.db'

def remove_promptdb_if_exists():
    if os.path.exists(PROMPTDB):
        os.remove(PROMPTDB)

def open_prompt_db():
    # 解决 sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 12896 and this is thread id 21372.
    conn = sqlite3.connect(PROMPTDB, check_same_thread = False)
    cursor = conn.cursor()
    return conn, cursor

def close_prompt_db(conn, cursor):
    try:
        conn.close()
        cursor.close()
    except:
        print("close_prompt_db failed...")


remove_promptdb_if_exists()
CONN, CURSOR = open_prompt_db()


# ----------------
def open_dictionary_db():
    # 解决 sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 12896 and this is thread id 21372.
    conn = sqlite3.connect('dictionary.db', check_same_thread = False)
    cursor = conn.cursor()
    return conn, cursor

DICTIONARY_DB_CONN, DICTIONARY_DB_CURSOR = open_dictionary_db()