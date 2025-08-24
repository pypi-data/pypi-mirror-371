#!../venv/bin/pytest

from collections.abc import Callable

import pytest
import urwid

from git_viewer.main import App, __version__
from git_viewer.log import run as gitl
from git_viewer.diff import run as gitd
from git_viewer.show import run as gits

class MockScreen:

	cols_rows: 'tuple[int, int]' = (0, 0)

	def start(self) -> None:
		pass

	def get_cols_rows(self) -> 'tuple[int, int]':
		return self.cols_rows

class AbstractMockLoop:

	def __init__(self,
		widget: urwid.Widget, palette: object, *,
		screen: MockScreen,
		handle_mouse: bool,
		input_filter: 'Callable[[list[str], list[int]], list[str]]|None' = None,
		unhandled_input: 'Callable[[str], bool]',
	) -> None:
		if input_filter is None:
			input_filter = lambda keys, raws: keys
		self.screen = screen
		self.widget = widget
		self.palette = palette
		self.input_filter = input_filter
		self.unhandled_input = unhandled_input

	def run(self) -> None:
		raise NotImplementedError()

	def simulate_key_press(self, key: str) -> bool:
		'''
		The urwid documentation says "The unhandled_input function should return True if it handled the input." [description of MainLoop.unhandled_input]
		But the return value is not checked and none of the official examples returns something from unhandled_input.
		Therefore I am not returning anything from the unhandled_input function either, making the return value of this method mean:
		True if it has been handled by widget or the input filter, None if it has been passed to unhandled_input.
		'''
		keys = self.input_filter([key], [-1])
		if not keys:
			return True
		assert len(keys) == 1
		key = keys[0]
		k = self.widget.keypress(self.screen.get_cols_rows(), key)
		if k:
			return self.unhandled_input(key)
		return True


# ---------- gitl ----------

def test_gitl(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(MockScreen, 'cols_rows', (80, 5))
	class MockLoop(AbstractMockLoop):

		# this test will need to be updated as the repo grows because the lengths of short hashes will increase
		expected_widget = [
			"| * 0923586 - tox.ini bugfix: don't ignore mypy.ini (10 months ago) <erzo>      ".encode(),
			"| * d387b76 - added passing tests for gits (10 months ago) <erzo>               ".encode(),
			"| * 050a057 - set version to 1.24.0-dev (10 months ago) <erzo>                  ".encode(),
			"|/                                                                              ".encode(),
			"* d5d3918 - (tag: v1.24.0) Merge branch 'dev' (10 months ago) <erzo>            ".encode(),
		]

		def run(self) -> None:
			# move view to the bottom so that stashes and uncommitted changes do not disturb the test
			self.simulate_key_press('G')
			assert self.widget.render(self.screen.get_cols_rows()).text == self.expected_widget

	monkeypatch.setattr(urwid, 'MainLoop', MockLoop)
	monkeypatch.setattr(App, 'create_screen', MockScreen)
	gitl(["59b91732a394692c3d3eff1d2bc5be2e7c1fa83f..8bef292eec831a6b2d761ee741d0d97be8937ae1"])


# ---------- gitd ----------

def test_gitd(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(MockScreen, 'cols_rows', (80, 5))
	class MockLoop(AbstractMockLoop):

		# this test will need to be updated as the repo grows because the lengths of short hashes will increase
		expected_widget = [
			"────────────────────────────────────────────────────────────────────────────────".encode(),
			"diff --git mypy.ini mypy.ini                                                    ".encode(),
			"index ee9e326..bda06ec 100644                                                   ".encode(),
			"--- mypy.ini (before commit)                                                    ".encode(),
			"+++ mypy.ini (after commit)                                                     ".encode(),
		]

		def run(self) -> None:
			assert self.widget.render(self.screen.get_cols_rows()).text == self.expected_widget

	monkeypatch.setattr(urwid, 'MainLoop', MockLoop)
	monkeypatch.setattr(App, 'create_screen', MockScreen)
	gitd(["59b91732a394692c3d3eff1d2bc5be2e7c1fa83f..8bef292eec831a6b2d761ee741d0d97be8937ae1"])


# ---------- gits ----------

def test_gits_commit(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(MockScreen, 'cols_rows', (61, 5))
	class MockLoop(AbstractMockLoop):

		expected_widget = [
			"commit 3795423b04a206b1c35b112468fb93409fc45671              ".encode(),
			"Author/Committer: erzo <erzo@posteo.de>                      ".encode(),
			"Date:             Fri Feb 7 17:47:39 2020 +0100              ".encode(),
			"Released in:      v0.2.0                                     ".encode(),
			"                                                             ".encode(),
		]

		def run(self) -> None:
			assert self.widget.render(self.screen.get_cols_rows()).text == self.expected_widget

	monkeypatch.setattr(urwid, 'MainLoop', MockLoop)
	monkeypatch.setattr(App, 'create_screen', MockScreen)
	gits(["3795423b04a206b1c35b112468fb93409fc45671"])

def test_gits_blob(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(MockScreen, 'cols_rows', (80, 5))
	class MockLoop(AbstractMockLoop):

		expected_widget = [
			"#!/usr/bin/env python3                                                          ".encode(),
			"                                                                                ".encode(),
			"# Copyright © 2020 erzo <erzo@posteo.de>                                        ".encode(),
			"# This work is free. You can redistribute it and/or modify it under the         ".encode(),
			"# terms of the Do What The Fuck You Want To Public License, Version 2,          ".encode(),
		]

		def run(self) -> None:
			assert self.widget.render(self.screen.get_cols_rows()).text == self.expected_widget

	monkeypatch.setattr(urwid, 'MainLoop', MockLoop)
	monkeypatch.setattr(App, 'create_screen', MockScreen)
	gits(["7637819c03e082471e85c2c8cb06133b8dbfc853"])


# ---------- help ----------

def test_help_general(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(MockScreen, 'cols_rows', (61, 5))
	class MockLoop(AbstractMockLoop):

		expected_widget = [
			"help                                                         ".encode(),
			("git-viewer version %s" % __version__).ljust(MockScreen.cols_rows[0]).encode(),
			"                                                             ".encode(),
			"Three Executables                                            ".encode(),
			"  `gitl` is the main program, a wrapper around `git log` from".encode(),
		]

		def run(self) -> None:
			self.simulate_key_press('f1')
			assert self.widget.render(self.screen.get_cols_rows()).text == self.expected_widget

	monkeypatch.setattr(urwid, 'MainLoop', MockLoop)
	monkeypatch.setattr(App, 'create_screen', MockScreen)
	gitl([])

def test_help_keyboard_shortcuts(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(MockScreen, 'cols_rows', (80, 5))
	class MockLoop(AbstractMockLoop):

		expected_widget = [
			"list of keyboard shortcuts                                                      ".encode(),
			"use <down>/j (`cursor down`) and <up>/k (`cursor up`) to select a shortcut      ".encode(),
			"use <right>/l (`go details`) or <space>/<enter> (`activate`) to show details    ".encode(),
			"use <left>/h/H (`go left`) to return                                            ".encode(),
			"                                                                                ".encode(),
		]

		def run(self) -> None:
			self.simulate_key_press('f2')
			# view does not start at top because window is too small to show selected line (the first shortcut) => move view to top
			self.simulate_key_press('V')
			self.simulate_key_press('g')
			self.simulate_key_press('g')
			assert self.widget.render(self.screen.get_cols_rows()).text == self.expected_widget

	monkeypatch.setattr(urwid, 'MainLoop', MockLoop)
	monkeypatch.setattr(App, 'create_screen', MockScreen)
	gitl([])

def test_help_available_commands(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(MockScreen, 'cols_rows', (80, 5))
	class MockLoop(AbstractMockLoop):

		# view does not start at top because window is too small to show selected line (the first command, i.e. add-editor)
		expected_widget = [
			"                                                                                ".encode(),
			"programmable commands:                                                          ".encode(),
			"add-editor                                                                      ".encode(),
			"config.edit                                                                     ".encode(),
			"config.export                                                                   ".encode(),
		]

		def run(self) -> None:
			self.simulate_key_press('f3')
			assert self.widget.render(self.screen.get_cols_rows()).text == self.expected_widget

	monkeypatch.setattr(urwid, 'MainLoop', MockLoop)
	monkeypatch.setattr(App, 'create_screen', MockScreen)
	gitl([])

def test_help_available_settings(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(MockScreen, 'cols_rows', (80, 5))
	class MockLoop(AbstractMockLoop):

		expected_widget = [
			"available settings:                                                             ".encode(),
			"  app.align                                       Allowed values:               ".encode(),
			"                                                  left-indentation, left,       ".encode(),
			"                                                  center, right                 ".encode(),
			"                                                  How to align lines, see also  ".encode(),
		]

		def run(self) -> None:
			self.simulate_key_press('f4')
			assert self.widget.render(self.screen.get_cols_rows()).text == self.expected_widget

	monkeypatch.setattr(urwid, 'MainLoop', MockLoop)
	monkeypatch.setattr(App, 'create_screen', MockScreen)
	gitl([])


# ---------- search ----------

def test_search_log(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(MockScreen, 'cols_rows', (80, 5))
	class MockLoop(AbstractMockLoop):

		# this test will need to be updated as the repo grows because the lengths of short hashes will increase
		expected_widget = [
			'              <erzo>                                                            '.encode(),
			'| * 2f76e47 - added failing test: test_show_dont_crash_when_passing_a_file (10  '.encode(),
			'              months ago) <erzo>                                                '.encode(),
			'| * a647639 - silence mypy errors  Module has no attribute "util" (10 months    '.encode(),
			'searching for "failing"                                                         '.encode(),
		]

		def run(self) -> None:
			for key in '/failing':
				self.simulate_key_press(key)
			self.simulate_key_press('enter')
			assert self.widget.render(self.screen.get_cols_rows()).text == self.expected_widget

	monkeypatch.setattr(urwid, 'MainLoop', MockLoop)
	monkeypatch.setattr(App, 'create_screen', MockScreen)
	gitl(["59b91732a394692c3d3eff1d2bc5be2e7c1fa83f..8bef292eec831a6b2d761ee741d0d97be8937ae1"])

def test_search_diff_via_g(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(MockScreen, 'cols_rows', (80, 5))
	class MockLoop(AbstractMockLoop):

		expected_widget = [
			"949 +                elif self.hash_id.startswith(':'):                         ".encode(),
			'950 +                    # ":./model.py" (equivalent to ":0:./model.py") is the '.encode(),
			"     added version of the file                                                  ".encode(),
			"951 +                    self.object_type = OBJECT_TYPE_BLOB                    ".encode(),
			"952 +                elif re.match('^[0-9a-f]+:', self.hash_id, re.I):          ".encode(),
		]

		def run(self) -> None:
			# select first commit
			self.simulate_key_press('^')
			# open commit
			self.simulate_key_press('l')
			# search for first modified line continaing model => select line 950
			self.simulate_key_press('n')
			assert self.widget.render(self.screen.get_cols_rows()).text == self.expected_widget

	monkeypatch.setattr(urwid, 'MainLoop', MockLoop)
	monkeypatch.setattr(App, 'create_screen', MockScreen)
	gitl(["-G", "model", "59b91732a394692c3d3eff1d2bc5be2e7c1fa83f..8bef292eec831a6b2d761ee741d0d97be8937ae1"])

def test_search_diff_title(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(MockScreen, 'cols_rows', (80, 5))
	class MockLoop(AbstractMockLoop):

		expected_widget_1 = [
			"────────────────────────────────────────────────────────────────────────────────".encode(),
			"diff --git src/git_viewer/model.py src/git_viewer/model.py                      ".encode(),
			"index 0e6e933..31d507b 100644                                                   ".encode(),
			"--- src/git_viewer/model.py (before commit)                                     ".encode(),
			'searching for "model"                                                           '.encode(),
		]

		expected_widget_2 = [
			"────────────────────────────────────────────────────────────────────────────────".encode(),
			"diff --git src/git_viewer/model.py src/git_viewer/model.py                      ".encode(),
			"index 0e6e933..31d507b 100644                                                   ".encode(),
			"--- src/git_viewer/model.py (before commit)                                     ".encode(),
			'end reached, starting at top                                                    '.encode(),
		]

		def run(self) -> None:
			# select first commit
			self.simulate_key_press('^')
			# open commit
			self.simulate_key_press('l')
			for key in "/model/t":
				self.simulate_key_press(key)
			self.simulate_key_press('enter')
			assert self.widget.render(self.screen.get_cols_rows()).text == self.expected_widget_1
			self.simulate_key_press('n')
			assert self.widget.render(self.screen.get_cols_rows()).text == self.expected_widget_2

	monkeypatch.setattr(urwid, 'MainLoop', MockLoop)
	monkeypatch.setattr(App, 'create_screen', MockScreen)
	gitl(["-G", "model", "59b91732a394692c3d3eff1d2bc5be2e7c1fa83f..8bef292eec831a6b2d761ee741d0d97be8937ae1"])

def test_search_in_help(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.setattr(MockScreen, 'cols_rows', (80, 5))
	class MockLoop(AbstractMockLoop):

		expected_widget = [
			"command search                                                                  ".encode(),
			"usage: search [--open | --next | --prev | --edit] [--reverse]                   ".encode(),
			"                                                                                ".encode(),
			"Search for a text.                                                              ".encode(),
			"                                                                                ".encode(),
		]

		def run(self) -> None:
			self.simulate_key_press('f3')
			for key in "/search":
				self.simulate_key_press(key)
			self.simulate_key_press('enter')
			self.simulate_key_press('right')
			assert self.widget.render(self.screen.get_cols_rows()).text == self.expected_widget

	monkeypatch.setattr(urwid, 'MainLoop', MockLoop)
	monkeypatch.setattr(App, 'create_screen', MockScreen)
	gitd([])
