import sys
import traceback
import time
import datetime
import os
import re
import yaml
import pyperclip
import sqlite3
from utils.clipboard import read_from_clipboard, write_to_clipboard
from utils.file import append_clipboard_content_to_specified_text_file, transfer_docx_as_lines, transfer_pdf_as_lines
from utils.ui import green, blue
from utils.db import remove_promptdb_if_exists, open_prompt_db, close_prompt_db, CONN, CURSOR, DICTIONARY_DB_CONN, DICTIONARY_DB_CURSOR
from utils import random_str, highlight_matched_substr
from pprint import pformat

from IPython import embed

from settings import MARK


class Overviewpy:
    @staticmethod
    def print_var():
        c = f"print({read_from_clipboard()})"
        s = random_str()
        text = f"print('---------{read_from_clipboard()}---------↓-{s}') # {MARK}"
        text += '\n'
        text += c + f"# {MARK}"
        text += '\n'
        text += f"print('------------------↑-{s}') # {MARK}"
        pyperclip.copy(text)

    def remove_print(self):
        removeds = []
        result = []
        text = read_from_clipboard()
        for line in text.split('\n'):
            print(line)
            if MARK in line:
                removeds.append(line)
            else:
                result.append(line)
        pyperclip.copy('\n'.join(result))
        self.ui_function_result = green(f'REMOVED {len(removeds)} LINES:') + '\n' + '\n'.join(removeds)

    def file_structure(self):
        def line_num_ui(line_index):
            chars_count = 8
            num = f'[{line_index + 1}]:'
            result = num + ' ' * (chars_count - len(num))
            return result

        text = read_from_clipboard()

        result = ''
        lines = text.split('\n')
        keywords = ['class ', 'def ', '@staticmethod']

        for index, line in enumerate(lines):
            for _kw in keywords:
                if line.strip(' ').lower().startswith(_kw):
                    result += f'{line_num_ui(index)} {line}' + '\n'

        self.ui_function_result = result

    def list_docs(self):
        documents_dir = os.path.abspath(os.path.join(os.getcwd(), "documents"))
        os.listdir(documents_dir)
        # todo

    def guidance(self):
        result = 'todo'
        self.ui_function_result = result

    # @staticmethod
    def ipythoner(self):
        a = "I will be accessible in IPython shell!"
        embed()
        # todo test
        # from PIL import Image
        # image = Image.open(r'C:\Users\zlzk\Documents\GitHub\prompt\笔记生成器\1711699160.png')
        # image.show()
        # self.ui_function_result = 'test'


class ClipBoardFunctions:
    def __init__(self):
        self.cursor = 0
        self.limit = 20
        self.items = None

    def cb_history_list(self):
        items = self.clipboard_recorder.history[-self.limit:]
        items.reverse()

        self.items = items

        result = ''
        for index, text in enumerate(items):
            if index == self.cursor:
                result += green(f'{index}:  {text[:100]}')
            else:
                result += f'{index}:  {text[:100]}'
            result += '\n'
        self.ui_function_result = result

    def cb_item_down(self):
        # 到底了就不需要往下了
        if self.cursor >= len(self.items) - 1:
            self.cursor = len(self.items) - 1
        else:
            self.cursor += 1

        self.cb_history_list()

    def cb_item_up(self):
        # 到顶了就不需要往上了
        if self.cursor <= 0:
            self.cursor = 0
        else:
            self.cursor -= 1

        self.cb_history_list()

    def cb_item_confirm(self):
        write_to_clipboard(self.items[self.cursor])


class CharsFunctions:
    def __init__(self):
        self.cursor = 0
        self.limit = 20

    @staticmethod
    def extract_cn():
        chinese_text = ','.join(re.findall(r'[\u4e00-\u9fa5]+', read_from_clipboard()))
        pyperclip.copy(chinese_text)

    @staticmethod
    def upper():
        pyperclip.copy(read_from_clipboard().upper())


class PromptFunctions:
    def __init__(self):
        self.current_dir = os.path.abspath(os.path.join(os.getcwd(), "functions"))
        self.table_name = "note_lines"
        self.files_modifytime = {}

        self.public_note_path = os.path.join(self.current_dir, "note", f"public-note-{datetime.datetime.now().strftime('%Y-%m-%d')}.txt")
        self.private_note_path = os.path.join(self.current_dir, "note", f"private-note-{datetime.datetime.now().strftime('%Y-%m-%d')}.txt")
        self.storehouse_note_path = os.path.join(self.current_dir, "storehouse-note", f"{datetime.datetime.now().strftime('%Y-%m-%d')}.txt")

        self.submodes = [None, 'SwitchNoteSettingYaml', 'Test']
        self.activate_submode = None
        self.setting_files = [os.path.join(self.current_dir, "settings-public.yml"),
                              os.path.join(self.current_dir, "settings-private.yml"),
                              os.path.join(self.current_dir, "settings-official-documents.yml")]
        self.activate_setting_file = self.setting_files[0]

        self.db_conn = CONN
        self.db_cursor = CURSOR
        self.init_db()

        self.dictionary_db_conn = DICTIONARY_DB_CONN
        self.dictionary_db_cursor = DICTIONARY_DB_CURSOR

        self.query_input_flag = False

    def init_db(self):
        with open(self.activate_setting_file, "r", encoding='UTF-8') as f:
            settings = yaml.full_load(f)
        self.settings = settings

        # sys.exit()


        try:
            self.db_cursor.execute(f"create table IF NOT EXISTS {self.table_name} (id integer PRIMARY KEY AUTOINCREMENT, file VARCHAR, content VARCHAR);")
            self.db_conn.commit()

            print('init_table....')
            with open(self.activate_setting_file, "r") as f:
                settings = yaml.full_load(f)

            self.db_cursor.execute(f"delete from {self.table_name};")
            self.db_conn.commit()

            for document_dir in settings.get('document_dirs'):
                for path, subdirs, files in os.walk(document_dir):
                    for name in files:
                        file_lines = []       

                        if not name.endswith(tuple(settings.get('extensions'))):
                            continue

                        # todo vzhong
                        if name.endswith('.docx'):
                            file_lines = transfer_docx_as_lines(f'{path}/{name}')
                        elif name.endswith('.pdf'):
                            file_lines = transfer_pdf_as_lines(f'{path}/{name}')
                        else:
                            # with open(f'{path}/{name}', encoding='UTF-8') as f:
                            with open(f'{path}/{name}', 'rb') as f:
                                # 便于监控文件变化
                                self.files_modifytime.update({f'{path}/{name}': os.stat(f'{path}/{name}').st_mtime})
                                file_lines = f.readlines()

                        for _line in file_lines:
                            self.db_cursor.execute(f"insert into {self.table_name}(file, content) values(?, ?)", (f"{path}/{name}", _line))

            self.db_conn.commit()

            # close_prompt_db(self.db_conn, self.db_cursor)
            print("Done!")
        except Exception as e:
            traceback.print_exc()
            print("-----------------Exception in init_db--------------------")
            print(str(e))

    def update_ui_submode_result(self):
        self.ui_submode_result = ''
        if self.activate_submode != 'SwitchNoteSettingYaml':
            return

        for _f in self.setting_files:
            with open(os.path.join(self.current_dir, _f), 'r', encoding='utf-8') as f:
                self.ui_submode_result += green(_f) + '\n' if _f == self.activate_setting_file else blue(_f) + '\n'
                self.ui_submode_result += ''.join(f.readlines())

    def switch_submode(self):
        self.activate_submode = self.submodes[(self.submodes.index(self.activate_submode) + 1) % len(self.submodes)]
        self.ui_submode = ''

        # if self.activate_submode == 'SwitchNoteSettingYaml':
        self.update_ui_submode_result()

    # def get_note_setting_path(self): 
    #     self.ui_function_result = pformat(self.settings, width=50)

    def append_to_public_note(self):
        append_clipboard_content_to_specified_text_file(self.public_note_path)
        # 确认写入成功
        with open(self.public_note_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            self.ui_function_result = '\n'.join(lines[-10:])

    def append_to_private_note(self):
        append_clipboard_content_to_specified_text_file(self.private_note_path)
        # 确认写入成功
        with open(self.private_note_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            self.ui_function_result = '\n'.join(lines[-10:])

    def append_to_storehouse_note(self):
        append_clipboard_content_to_specified_text_file(self.storehouse_note_path)
        # 确认写入成功
        with open(self.storehouse_note_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            self.ui_function_result = '\n'.join(lines[-10:])

    def refresh_db(self):
        # for f, modifytime in self.files_modifytime.items():
        #     if os.stat(f).st_mtime != modifytime:
        #         self.ui_function_result = 'Refreshing DB due to files changed...'
        #         self.init_table()
        #         time.sleep(3)
        #         break
        self.ui_function_result = 'Refreshing DB due to files changed...'
        self.init_db()
        self.ui_function_result = 'Done.'

    def switch_settings(self):
        if self.activate_submode == 'SwitchNoteSettingYaml':
            self.activate_setting_file = self.setting_files[(self.setting_files.index(self.activate_setting_file) + 1) % len(self.setting_files)]
            self.refresh_db()
            self.update_ui_submode_result()
        else:
            self.ui_function_result = 'SubMode should be `SwitchNoteSettingYaml` at first!'

    def query(self, input=None):
        RELATED_LINES_UP_COUNT = 8
        RELATED_LINES_DOWN_COUNT = 15

        result = []
        if not input:
            keyword = read_from_clipboard()
        else:
            keyword = input

        try:
            # conn, cursor = open_prompt_db()
            try:
                self.db_cursor.execute(f"select id, file, content from {self.table_name} where LOWER(content) like ?;", ("%" + keyword.lower() + "%",))
                matched_records = self.db_cursor.fetchall()
            # sqlite3.OperationalError: no such table: note_lines
            except sqlite3.OperationalError:
                self.init_db()
                self.db_cursor.execute(f"select id, file, content from {self.table_name} where LOWER(content) like ?;", ("%" + keyword.lower() + "%",))
                matched_records = self.db_cursor.fetchall()

            for _matched_record in matched_records:
                _id, _file, _content = _matched_record
                result.append(green(f"Found in file: {_file} ↓↓↓"))

                # 匹配行的上下行也将被选中显示出来
                selected_lines_ids = list(range(max(1,_id - RELATED_LINES_UP_COUNT), _id + RELATED_LINES_DOWN_COUNT))
                self.db_cursor.execute("select content from %s where id in (%s);" % (self.table_name, ','.join([str(_) for _ in selected_lines_ids])))
                selected_lines = self.db_cursor.fetchall()
                for _selected_line in selected_lines:
                    line_content = _selected_line[0]

                    if type(line_content) == type(b''):
                        line_content = line_content.decode("utf-8")

                    highlighted_line = highlight_matched_substr(line_content, keyword)
                    result.append(highlighted_line)

            if len(result) > 2000:
                self.ui_function_result = 'Aborted! Too much returns'
            elif not result:
                self.ui_function_result = 'No result.'
            else:
                self.ui_function_result = '\n'.join(result)
        # except sqlite3.OperationalError as e:
        except Exception as e:
            traceback.print_exc()
            print(f'发生错误, {str(e)}')
            raise

    def query_input(self):
        self.query_input_flag = not self.query_input_flag
        self.ui_query_input = ''
        self.ui_function_result = ''

    def query_dictionary(self):
        text = read_from_clipboard()
        if text:
            # self.dictionary_db_cursor.execute(f"select * from word where LOWER(english) like ?;", ("%" + text.lower() + "%",))
            self.dictionary_db_cursor.execute(f"select * from word where LOWER(english)=?;", (text.lower(),))
            matched_records = self.dictionary_db_cursor.fetchall()

        self.ui_function_result = ''
        if not matched_records:
            self.dictionary_db_cursor.execute(f"select * from word where chinese like ?;", ("%" + text.lower() + "%",))
            matched_records = self.dictionary_db_cursor.fetchall()

        if matched_records:
            self.ui_function_result = '\n\n'.join([_[0] + '\n' + _[1] for _ in matched_records])


class DocumentsFunctions:
    def list_docs(self):
        pass

    def next_doc(self):
        pass

    def open_doc(self):
        pass
