#!/usr/bin/env python3

import enum
import typing

ID_UNTRACKED = "<untracked>"
ID_UNSTAGED = "<unstaged>"
ID_STAGED = "<staged>"
ID_STASHES_GROUP = "<stashed>"
ID_TODO = "<todo>"
SPECIAL_DETAILS_IDS = (ID_UNTRACKED, ID_UNSTAGED, ID_STAGED, ID_TODO)
SPECIAL_IDS = SPECIAL_DETAILS_IDS + (ID_STASHES_GROUP,)

VIRTUAL_ID_OTHER = "<other>"

TYPE_STASHED = "stashed"
TYPE_OTHER = "other"
TYPE_ERROR = "error"
TYPE_TAG = "tag"
TYPE_BLOB = "blob"
TYPE_START_OF_FILE = "sof"
TYPE_NUMBERED_LINE = "numbered-line"
TYPE_UNTRACKED = "untracked"
TYPE_TODO = "todo"

class SearchLines(enum.Enum):
	ALL = 'all'
	ADDED = '+'
	REMOVED = '-'
	MODIFIED = '+-'
	CONTEXT = 'context'
	META = 'meta'
	TITLE = 'title'

if typing.TYPE_CHECKING:
	class SearchFlags(typing.TypedDict, total=False):
		#: None: case sensitive if search text contains upper case letters, case insensitive otherwise
		case_sensitive: 'bool|None'
		is_regex: bool
		lines: 'SearchLines'
