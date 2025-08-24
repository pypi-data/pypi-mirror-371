#!../venv/bin/pytest

import os
import pytest
import urwid
from mock_urwid import UrwidMock, urwid_mock, run


def test_show_blob(monkeypatch: pytest.MonkeyPatch, urwid_mock: UrwidMock) -> None:
	monkeypatch.chdir(os.path.join(os.path.split(__file__)[0], '..', 'src', 'git_viewer'))
	urwid_mock.set_size(60, 12)
	@urwid_mock.set_mock_loop
	def mainloop() -> None:
		window = [
			"#!/usr/bin/env python                                       ".encode(),
			"                                                            ".encode(),
			"import os                                                   ".encode(),
			"import stat                                                 ".encode(),
			"import tempfile                                             ".encode(),
			"import re                                                   ".encode(),
			"import shlex                                                ".encode(),
			"import shutil                                               ".encode(),
			"import gettext                                              ".encode(),
			"_ = gettext.gettext                                         ".encode(),
			"                                                            ".encode(),
			"from .api_subprocess import Runner, CommandError            ".encode(),
			"from .string_formatter import formatter                     ".encode(),
			"from .color_decoder import ColorDecoder                     ".encode(),
		]

		assert urwid_mock.get_lines() == window[0:12]
		urwid_mock.simulate_key_press('j')
		urwid_mock.simulate_key_press('j')
		assert urwid_mock.get_lines() == window[0+2:12+2]

	run('gits', 'e02d90235a201f25b8d845bb3a78c534d7d8120c:./model.py')


def test_show_commit(monkeypatch: pytest.MonkeyPatch, urwid_mock: UrwidMock) -> None:
	monkeypatch.chdir(os.path.join(os.path.split(__file__)[0], '..', 'src', 'git_viewer'))
	urwid_mock.set_size(74, 31)
	@urwid_mock.set_mock_loop
	def mainloop() -> None:
		window = [
			"commit 2bc77cf785abac95772b6cb5e0d604111b9a8875                           ".encode(),
			"Author/Committer: erzo <erzo@posteo.de>                                   ".encode(),
			"Author Date:      Sat Nov 2 08:17:11 2024 +0100                           ".encode(),
			"Committer Date:   Sat Nov 2 08:22:50 2024 +0100                           ".encode(),
			"Released in:      v1.24.0                                                 ".encode(),
			"                                                                          ".encode(),
			"    added new setting log-view.commit-number-auto-print                   ".encode(),
			"                                                                          ".encode(),
			"    add the following line to your config file in order to enable it      ".encode(),
			"    set log-view.commit-number-auto-print                                 ".encode(),
			"                                                                          ".encode(),
			"    or the following line in order to toggle it when pressing a key       ".encode(),
			"    map # 'set log-view.commit-number-auto-print!'                        ".encode(),
			"──────────────────────────────────────────────────────────────────────────".encode(),
			"diff --git src/git_viewer/main.py src/git_viewer/main.py                  ".encode(),
			"index e173976..5ea87d5 100644                                             ".encode(),
			"--- src/git_viewer/main.py (before commit)                                ".encode(),
			"+++ src/git_viewer/main.py (after commit)                                 ".encode(),
			"@@ -546,6 +546,8 @@ class LogView(SelectableListbox):                     ".encode(),
			"546      commit_number_enable = False                                     ".encode(),
			'547      commit_number_pattern = " {n}"                                   '.encode(),
			"548                                                                       ".encode(),
			"549 +    auto_print_commit_number = False                                 ".encode(),
			"550 +                                                                     ".encode(),
			"551      def __init__(self, log_model):                                   ".encode(),
			"552          self.model = log_model                                       ".encode(),
			"553          self.decoder = color_decoder.ColorDecoder()                  ".encode(),
			"@@ -740,6 +742,32 @@ class LogView(SelectableListbox):                    ".encode(),
			"742              return False                                             ".encode(),
			"743                                                                       ".encode(),
			"744                                                                       ".encode(),
			"745 +    # ------- print commit number -------                            ".encode(),
			"746 +                                                                     ".encode(),
			"747 +    def keypress(self, size, key):                                   ".encode(),
		]

		assert urwid_mock.get_lines() == window[0:31]
		urwid_mock.simulate_key_press('down')
		urwid_mock.simulate_key_press('down')
		urwid_mock.simulate_key_press('down')
		assert urwid_mock.get_lines() == window[0+3:31+3]

	run('gits', '2bc77cf785abac95772b6cb5e0d604111b9a8875')


def test_show_tag(monkeypatch: pytest.MonkeyPatch, urwid_mock: UrwidMock) -> None:
	monkeypatch.chdir(os.path.join(os.path.split(__file__)[0], '..', 'src', 'git_viewer'))
	urwid_mock.set_size(81, 18)
	@urwid_mock.set_mock_loop
	def mainloop() -> None:
		full_window = [
			"tag v1.24.0                                                                      ".encode(),
			"Tagger: erzo <erzo@posteo.de>                                                    ".encode(),
			"                                                                                 ".encode(),
			"v1.24.0                                                                          ".encode(),
			"                                                                                 ".encode(),
			"New features:                                                                    ".encode(),
			"- added new setting log-view.commit-number-auto-print                            ".encode(),
			"  commit 2bc77cf785abac95772b6cb5e0d604111b9a8875                                ".encode(),
			"                                                                                 ".encode(),
			"Bugfixes:                                                                        ".encode(),
			"- `yank --no-git url/file-on-current-branch` uses branch name of the remote      ".encode(),
			"  commit fa47e70250c1337bf31dd195b7b2cf0a0389ff6f                                ".encode(),
			"                                                                                 ".encode(),
			"commit d5d3918f320eaec0b955691f6be9f9811ff01dd1                                  ".encode(),
			"Sat Nov 2 08:28:01 2024 +0100                                                    ".encode(),
			"                                                                                 ".encode(),
			"                                                                                 ".encode(),
			"                                                                                 ".encode(),
		]

		assert urwid_mock.get_lines() == full_window
		urwid_mock.simulate_key_press('down')
		urwid_mock.simulate_key_press('down')
		urwid_mock.simulate_key_press('down')
		assert urwid_mock.get_lines() == full_window

	run('gits', 'v1.24.0')


def test_show_dont_crash_when_passing_a_file(monkeypatch: pytest.MonkeyPatch, urwid_mock: UrwidMock) -> None:
	monkeypatch.chdir(os.path.join(os.path.split(__file__)[0], '..', 'src', 'git_viewer'))
	urwid_mock.set_size(81, 18)
	@urwid_mock.set_mock_loop
	def mainloop() -> None:
		# The main loop may or may not be called and if it is the output of urwid_mock.get_lines() will change
		# but that is not important. The purpose of this test is to ensure that gits does not crash.
		pass

	run('gits', 'model.py')
