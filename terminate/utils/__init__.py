import os
import keyboard
import subprocess

import win32gui
from collections import Counter
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
from copy import deepcopy

import win32gui


from settings import DEBUG


VISIABLE_CHARS = [_ for _ in string.ascii_lowercase + string.digits + string.punctuation] 


def random_str():
    random.shuffle(string.ascii_lowercase.split())
    selected = random.choices([ x for x in string.ascii_lowercase], k=15)
    return ''.join(selected)


def debug_print(x):
    if DEBUG:
        print(x)

def clear_screen():
    if not DEBUG:
        os.system('cls')

def sort_keys(keys):
    high_keys = ['ctrl', 'alt', 'shift']
    return [k for k in keys if k in high_keys] + [k for k in keys if k not in high_keys]


def highlight_matched_substr(targetline, substr):
    result_chars = []
    current_targetline_index = 0

    for index, char in enumerate(targetline):
        if index < current_targetline_index:
            continue
        if targetline[index: index + len(substr)].lower() == substr.lower():
            result_chars.append(f'\033[92m{targetline[current_targetline_index: current_targetline_index + len(substr)]}\033[0m')
            current_targetline_index += len(substr)
        else:
            result_chars.append(char)
            current_targetline_index += 1
        
    return ''.join(result_chars)

class KeyEventRecorder:
    def __init__(self):
        # [('enter', 'down', 1714657760.6398544), ('enter', 'up', 1714657760.7244155), ...]
        self.key_events = []           # 记录按键历史
        self.meme_time = 1              # 1 second

    def reset_key_events(self):
        self.key_events = []

    def remove_outdated_events(self):
        result = []
        now = time.time()
        events = deepcopy(self.key_events)
        for _event in events:
            if now - _event[2] > self.meme_time and not keyboard.is_pressed(_event[0]):
                self.key_events.remove(_event)

    def get_keys(self):
        self.remove_outdated_events()

        downed_keys = Counter([_[0] for _ in self.key_events if _[1] == 'down'])
        uped_keys = Counter([_[0] for _ in self.key_events if _[1] == 'up'])

        return {
            # 连按了2次的键
            "continuous_twice_pressed_keys": [_ for _ in set(downed_keys.keys()).intersection(set(uped_keys.keys())) if downed_keys[_] == 2 and uped_keys[_] == 2],
            # 正在被按着的键
            "being_pressed_keys": [_ for _ in downed_keys.keys() if keyboard.is_pressed(_)]
        }


class ClipBoardRecorder:
    def __init__(self):
        self.history = []

    def get_latest_one(self):
        return self.history[-1] if self.history else None
