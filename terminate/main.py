import keyboard
import subprocess
import re
import os

import win32gui
import win32con
import win32api
import time
import threading
import time
import platform
import pyperclip
import sys
import random
import string
import requests

import win32gui
import traceback

from utils.clipboard import read_from_clipboard, write_to_clipboard
from utils import random_str, debug_print, clear_screen, VISIABLE_CHARS

# from documents.vscode import SHORTCUTS
# from settings import GUIDANCE_DOC
from settings import DEBUG, U_HOLLOW_CIRCLE, U_LIGHT_SHADE, U_SOLID_CIRCLE, NOTE_PATHS, U_LEFT_HALF_BLOCK, U_FULL_BLOCK
from utils.ui import green, red, yellow, blue, key_visualize
from utils.file import append_clipboard_content_to_specified_text_file
from utils import KeyEventRecorder, ClipBoardRecorder, sort_keys
from functions import Overviewpy, ClipBoardFunctions, CharsFunctions, PromptFunctions, DocumentsFunctions
from utils.book import Book

def align_text(text):
    if len(text) >= 45:
        return text[:42] + "..."
    else:
        return text + ' ' * (45 - len(text))

hotkey_helptext = \
align_text('↓ →') + align_text('Show Books List') + '\n'
# align_text('←  ↑') + align_text('UnLock') + '\n' + \
# align_text('↓  →') + align_text('Switch Mode') + '\n' + \
# align_text('Right Alt') + align_text('Clear Result!') + '\n'


# 注意，键盘分了左边的alt和右边的alt，分别为alt和right alt
key_2_func = {
    'General': {
        'being_pressed_keys_func': [
            ({'alt', 'right'}, 'help', '帮助'),
            ({'alt', 'down'}, 'extract_cn', '提取中文字符'),
            #
            ({'alt', '1'}, 'append_to_english_note', 'Append to English note'),
            ({'alt', '2'}, 'append_to_python_note', 'Append to Python note'),
            ({'alt', '0'}, 'append_to_work_note', 'Append to work note'),
        ],
        'continuous_twice_pressed_key_func': [
            # ('right alt', 'guidance', '快捷键指南'),
        ]
    },
    # 'Overview.py':
    # {
    #     'being_pressed_keys_func': [
    #         ({'ctrl', 'left'}, 'file_structure', '查看结构'),
    #         ({'ctrl', '0'}, 'ipythoner', '打开Ipython (Ctrl D 退出)'),
            
    #     ],
    #     'continuous_twice_pressed_key_func': [
    #     ]
    # },
    # 'Chars':
    # {
    #     'being_pressed_keys_func': [
    #         ({'ctrl', 'down'}, 'extract_cn', '提取中文字符'),
    #         ({'ctrl', 'up'}, 'upper', '大写字母'),
    #     ],
    #     'continuous_twice_pressed_key_func': [
    #     ]
    # },
    # 'Documents':
    # {
    #     'being_pressed_keys_func': [
    #         ({'up'}, 'list_docs', '文档列表'),
    #         ({'right'}, 'next_doc', '下一个'),
    #         ({'right ctrl'}, 'open_doc', '打开'),
    #     ],
    #     'continuous_twice_pressed_key_func': [
    #     ]
    # },
    # 'Clipboard':
    # {
    #     'being_pressed_keys_func': [
    #         ({'right', }, 'cb_history_list', 'Show Clipboard history'),
    #         ({'shift', }, 'cb_item_confirm', 'Confirm item selected'),
    #         ({'alt', 'down'}, 'cb_item_down', 'Move down forward'),
    #         ({'alt', 'up'}, 'cb_item_up', 'Move up forward'),
    #     ],
    #     'continuous_twice_pressed_key_func': [
    #     ]
    # },
    # 'Prompt':
    # {
    #     'being_pressed_keys_func': [
    #         # ({'ctrl', 'left'}, 'get_note_setting_path', 'Show notes path'),
    #         ({'ctrl', 'right'}, 'refresh_db', 'Refresh DB'),
    #         ({'ctrl', 'up'}, 'append_to_public_note', 'Append to public note'),
    #         ({'ctrl', 'down'}, 'append_to_private_note', 'Append to private note'),
    #         # 
    #         ({'alt', 'right'}, 'append_to_storehouse_note', 'Append to storehouse note'),
    #         #
    #         ({'down'}, 'switch_settings', 'Switch settings'),
    #         ({'alt', 'up'}, 'print_var', 'PyDebug: 打印变量'),
    #         ({'alt', 'down'}, 'remove_print', 'PyDebug: 移除 Ubermensche'),
    #         #
    #         ({'shift'}, 'query', 'Query Note'),
    #         ({'right ctrl'}, 'switch_submode', 'Switch Sub Mode'),
    #         ({'f8'}, 'query_input', 'Query input matched (Open & Close)'),
    #         ({'f10'}, 'query_dictionary', 'Query 中/E Dictionary'),
    #     ],
    #     'continuous_twice_pressed_key_func': [
    #         # ('down', 'refresh_db', 'Refresh DB'),
    #     ]
    # }
}

def key_2_func_helptext(active_mode):
    result = ''
    for keys, func, help_text in key_2_func[active_mode]['being_pressed_keys_func']:
        keys_str = '  '.join([key_visualize(k) for k in sort_keys(list(keys))])
        result += align_text(keys_str) + align_text(help_text)
        result += '\n'

    if key_2_func[active_mode]['continuous_twice_pressed_key_func']:
        result += '\n'
    for key, func, help_text in key_2_func[active_mode]['continuous_twice_pressed_key_func']:
        keys_str = f'连按2次: {key}'
        result += align_text(keys_str) + align_text(help_text)
        result += '\n'

    return result


class Application(DocumentsFunctions, Overviewpy, ClipBoardFunctions, CharsFunctions, PromptFunctions):
    def __init__(self):
        super(Overviewpy, self).__init__()
        super(ClipBoardFunctions, self).__init__()
        super(CharsFunctions, self).__init__()
        super(PromptFunctions, self).__init__()
        self.locked = False
        self.modes = []
        self.key_event_recorder = KeyEventRecorder()
        self.clipboard_recorder = ClipBoardRecorder()
        #
        self.books = []
        self.current_selected_book = None

        self.init_ui()

    def init_ui(self):
        self.ui_locked = ''
        self.ui_modes_status = '   '.join(['%s %s' % (green(U_SOLID_CIRCLE) if active else U_HOLLOW_CIRCLE, mode) for mode, active in self.modes])
        self.ui_line_separator = '-' * (len(self.ui_modes_status) - 3)
        self.ui_current_clipboard_text = ''
        self.ui_shortcuts_help_text = ''
        self.ui_function_result = ''
        self.ui_query_input = ''
        #
        self.ui_submode = ''
        self.ui_submode_result = ''
        self.ui_notedbs = ''

        #
        self.ui_books_list = ''

    @property
    def current_active_mode(self):
        for _ in self.modes:
            if _[1] is True:
                return _, self.modes.index(_)

    def is_mode_active(self, mode):
        return mode in [_[0] for _ in self.modes if _[1] is True]

    def list_books(self):
        documents_dir = os.path.abspath(os.path.join(os.getcwd(), "books"))
        self.books = os.listdir(documents_dir)

    def switch_mode(self):
        """
        swith mode to next one
        """
        if self.locked:
            return

        self.init_ui()

        _current_active_mode_index = self.current_active_mode[1]

        # set all modes as non-active
        for index in range(0, len(self.modes)):
            self.modes[index][1] = False

        refreshed_active_mode_index = (_current_active_mode_index + 1) % len(self.modes)
        self.modes[refreshed_active_mode_index][1] = True

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False

    def draw_ui(self):
        # --------- Refresh help text ---------
        self.help_text = yellow(hotkey_helptext)

        # cb_text = read_from_clipboard()
        # ui_current_clipboard_text
        # self.ui_current_clipboard_text = ""
        # if len(cb_text + "...") > len(self.ui_line_separator):
        #     self.ui_current_clipboard_text += cb_text[:len(self.ui_line_separator) - 3] + "..."
        # else:
        #     self.ui_current_clipboard_text += cb_text

        # if self.ui_current_clipboard_text:
        #     self.ui_current_clipboard_text = blue(self.ui_current_clipboard_text)

        # self.ui_locked = red('!！LOCKED') if self.locked else ''

        # self.ui_modes_status = '   '.join(['%s %s' % (green(U_SOLID_CIRCLE) if active else U_HOLLOW_CIRCLE, mode) for mode, active in self.modes])

        # if self.activate_submode:
        #     self.ui_submode = '  '.join([yellow(_) if self.activate_submode and self.activate_submode == _ else {None: ''}.get(_, _) for _ in self.submodes])

        if self.books:
            self.ui_books_list = '\n'.join(self.books)

        result = [
            self.ui_locked,
            self.ui_modes_status,

            self.ui_submode,
            self.ui_submode_result,

            self.ui_current_clipboard_text,
            green(f'{U_FULL_BLOCK}  ') + self.ui_query_input if self.query_input_flag else '',
            self.help_text,
            self.ui_shortcuts_help_text,
            self.ui_function_result,

            #
            self.ui_books_list,
        ]

        clear_screen()
        for item in result:
            if item:
                print(self.ui_line_separator)
                print(item)

    def clear_result(self):
        self.ui_function_result = ''
        self.query_input_flag = False
        self.ui_query_input = ''


    # def netcoffee_push_note_to_remote():
    #     if current_active_mode[0] == 'NetCoffee':
    #         r = requests.get(API_NOTE_ADD)
    #         print(r.text)

application = Application()
# application.print_var()

def on_key_press(event):
    try:
        if application.locked:
            application.key_event_recorder.reset_key_events()
            application.draw_ui()
            return

        application.key_event_recorder.key_events.append((event.name, event.event_type, time.time()))
        keys = application.key_event_recorder.get_keys()

        # query input
        if application.query_input_flag and event.event_type == 'down' and event.name.lower() in VISIABLE_CHARS:
            application.ui_query_input += event.name
        if application.ui_query_input:
            application.query(input=application.ui_query_input)

        # func_name = None
        # for _func in key_2_func[application.current_active_mode[0][0]]['being_pressed_keys_func']:
        #     if _func[0] == set(keys['being_pressed_keys']):
        #         func_name =  _func[1]
        #         getattr(application, func_name)()
        #         # application.key_event_recorder.reset_key_events()
        #         break
        # for _func in key_2_func[application.current_active_mode[0][0]]['continuous_twice_pressed_key_func']:
        #     # todo, 不会执行到双击的
        #     if _func[0] in set(keys['continuous_twice_pressed_keys']):
        #         func_name =  _func[1]
        #         getattr(application, func_name)()
        #         # application.key_event_recorder.reset_key_events()
        #         break   

        application.draw_ui()
    except Exception as e:
        traceback.print_exc()
        print(f'System exit with unexcepted error: {str(e)}')
        sys.exit(1)

def on_clipboard_changes():
#     while True:
#         clipboard_text = read_from_clipboard()
#         if clipboard_text and clipboard_text != application.clipboard_recorder.get_latest_one():
#             application.clipboard_recorder.history.append(clipboard_text)
#             # Refresh UI
#             if application.current_active_mode[0][0] == 'Clipboard':
#                 application.cb_history_list()
#         time.sleep(0.2)
    pass

if __name__ == "__main__":
    # print("同时按下 `→` 和键盘这边的 alt 键，获取帮助。")
    thread_clipboard = threading.Thread(target=on_clipboard_changes, name='thread_clipboard')
    thread_clipboard.daemon = True
    thread_clipboard.start()

    keyboard.hook(on_key_press)
    keyboard.add_hotkey('down+right', lambda: application.list_books())
    # keyboard.add_hotkey('left+up', lambda: application.unlock())
    # keyboard.add_hotkey('down+right', lambda: application.switch_mode())
    # keyboard.add_hotkey('right alt', lambda: application.clear_result())
    application.draw_ui()
    keyboard.wait()

