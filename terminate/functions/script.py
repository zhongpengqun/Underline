import sqlite3
import os
import yaml


# if os.environ.get("settings.yml"):
#     SETTINGS_FILE_PATH = os.environ.get("settings.yml")
#     print("-------------------SETTINGS_FILE_PATH------------------")
#     print(SETTINGS_FILE_PATH)
# else:
#     SETTINGS_FILE_PATH = os.path.abspath(os.path.join(os.getcwd(), "settings.yml"))

# SETTINGS_FILE_PATH = os.path.abspath(os.path.join(os.getcwd(), "settings.yml"))

# DB = "notePrompter.db"
# DB = SETTINGS_FILE_PATH + ".db"
# DB_FILE = os.path.abspath(os.path.join(os.getcwd(), DB))
# TABLE = "note_lines"


# files_modifytime = {}


# def init_db():
#     try:
#         if os.path.exists(DB_FILE):
#             os.remove(DB_FILE)

#         connection = sqlite3.connect(DB)
#         cursor = connection.cursor()

#         cursor.execute(f"create table {TABLE} (id integer PRIMARY KEY AUTOINCREMENT, file VARCHAR, content VARCHAR);")
#         connection.commit()

#         cursor.close()
#         connection.close()

#         print("Done!")
#     except Exception as e:
#         print("-----------------Exception in init_db--------------------")
#         print(str(e))

# def init_table():
#     print('init_table....')

#     with open(SETTINGS_FILE_PATH, "r") as f:
#         settings = yaml.full_load(f)

#     connection = sqlite3.connect(DB)
#     cursor = connection.cursor()

#     cursor.execute(f"delete from {TABLE};")
#     connection.commit()

#     for document_dir in settings.get('document_dirs'):
#         for path, subdirs, files in os.walk(document_dir):
#             for name in files:
#                 if not name.endswith(tuple(settings.get('extensions'))):
#                     continue
#                 with open(f'{path}/{name}', encoding='UTF-8') as f:
#                     # 便于监控文件变化
#                     files_modifytime.update({f'{path}/{name}': os.stat(f'{path}/{name}').st_mtime})
#                     for _line in f.readlines():
#                         # print(f'Inserting {_line}')
#                         cursor.execute(f"insert into {TABLE}(file, content) values(?, ?)", (f"{path}/{name}", _line))

#     connection.commit()

#     cursor.close()
#     connection.close()
