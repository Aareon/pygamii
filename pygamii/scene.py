# coding: utf-8
from __future__ import unicode_literals
from pygamii.utils import init_colors, get_color_pair
import time
import platform
import os
import curses

stdscr = curses.initscr()
curses.start_color()
curses.noecho()
curses.cbreak()
stdscr.keypad(True)
stdscr.nodelay(True)
curses.flushinp()
curses.cbreak()
curses.curs_set(0)
current_os = platform.system()

init_colors()


class BaseScene(object):
    # prints per seconds
    pps = 1200
    rows = 23
    cols = 80
    blank_char = ' '
    char = ' '
    color = 'white'
    bg_color = 'black'
    playing = False
    objects = []
    actions = []

    def __init__(self, **kwargs):
        self.objects = []
        self.actions = []

        for key, value in kwargs.items():
            if key not in ('objects', 'actions') and hasattr(self, key):
                setattr(self, key, value)
            else:
                raise Exception('Key "{}" not found'.format(key))

    def add_object(self, obj):
        obj.scene = self
        self.objects.append(obj)
        obj.on_create()

    def remove_object(self, obj):
        self.objects.remove(obj)
        obj.on_destroy()

    def add_action(self, action, auto_start=True):
        self.actions.append(action)
        action.scene = self

        action.on_create()

        if auto_start:
            action.start()

    def remove_action(self, action):
        self.actions.remove(action)
        action.on_destroy()

    def clean(self):
        stdscr.clear()

    def get_terminal_size(self):
        x, y = stdscr.getmaxyx()
        x, y = y, x
        return x, y

    def render(self):
        self.clean()

        for i in range(self.rows - 1):
            stdscr.addstr(i, 0, ' ' * self.cols)

        for obj in self.objects:
            lines = str(obj).split('\n')
            for i, text in enumerate(lines):
                y = obj.y + i
                for j, char in enumerate(text):
                    x = obj.x + j

                    bg_none = obj.bg_color is None
                    color = obj.color or self.color
                    bg_color = obj.bg_color or self.bg_color

                    pair = get_color_pair(color, bg_color)

                    if x >= 0 and y >= 0 and x <= self.cols and y <= self.rows:
                        if char != ' ' or not bg_none:
                            stdscr.addstr(y, x, char, pair)

        stdscr.addstr(self.rows, 0, ' ' * (self.cols - 1))
        stdscr.refresh()

    def start(self):
        if current_os == 'Windows':
            os.system('cls')
        else:
            os.system('clear')
        first = True
        self.playing = True
        while self.playing:
            if not first:
                time.sleep(0.05)
            else:
                first = False
            if self.playing:
                self.render()

    def stop(self):
        self.playing = False

        for action in self.actions:
            action.stop()
