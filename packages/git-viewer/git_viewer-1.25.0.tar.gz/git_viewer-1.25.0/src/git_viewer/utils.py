#!/usr/bin/env python3

import re
import gettext
import typing
from collections.abc import Callable, Iterable, Iterator, Sequence
_ = gettext.gettext

from . import urwid_constants

# None is an allowed value for attributes:
# "None will typically be rendered with the terminal’s default foreground and background colors."
# http://urwid.org/manual/displayattributes.html#using-display-attributes

UrwidTextType: 'typing.TypeAlias' = 'str'
UrwidAttributeType: 'typing.TypeAlias' = 'str|None'
UrwidMarkupType: 'typing.TypeAlias' = 'UrwidTextType | tuple[UrwidAttributeType, UrwidMarkupType] | list[UrwidMarkupType]'
UrwidSimplifiedMarkupType: 'typing.TypeAlias' = 'UrwidTextType | tuple[UrwidAttributeType, UrwidTextType] | list[tuple[UrwidAttributeType, UrwidTextType]]'

UrwidColorType: 'typing.TypeAlias' = 'str'
MyColorType: 'typing.TypeAlias' = 'str'
# There is also a two-tuple variant to copy a style and 4- and 6-tuple variants including mono and high colors. But I am using only the 3-tuple version consisting of name, foreground, background.
UrwidPaletteThreeTuple: 'typing.TypeAlias' = 'tuple[UrwidAttributeType, UrwidColorType, UrwidColorType]'

T = typing.TypeVar('T')


# ------- create table -------

def format_table(rows: 'Sequence[Sequence[object]]', *, fmt: 'str|list[str]' = '%s', col_sep: str = " ") -> 'list[str]':
	if not rows:
		return []

	num_cols = len(rows[0])
	num_rows = len(rows)
	if not isinstance(fmt, list):
		fmt = [fmt] * num_cols
	else:
		while len(fmt) < num_cols:
			fmt.append('%s')

	formatted_rows = [[f%cell for cell,f in zip(row,fmt)] for row in rows]
	col_widths = [len(max((formatted_rows[row][col] for row in range(num_rows)), key=len)) for col in range(num_cols)]
	return [col_sep.join(cell.ljust(w) for cell,w in zip(row,col_widths)) for row in formatted_rows]


# ------- lists -------

def replace_to_markup(ln: str, old: str, new: UrwidMarkupType, *, count: int = -1, markup_function: 'Callable[[UrwidMarkupType], UrwidMarkupType] | None' = None) -> UrwidMarkupType:
	if not isinstance(new, list):
		new = [new]

	out: 'list[UrwidMarkupType]' = []
	first = True
	for word in ln.split(old, count):
		if first:
			first = False
		else:
			out.extend(new)

		if not word:
			continue

		if markup_function:
			word_markup = markup_function(word)
		else:
			word_markup = word

		if isinstance(word_markup, list):
			out.extend(word_markup)
		else:
			out.append(word_markup)

	return out

def iter_join(sep: 'T', iterable: 'Iterable[T]') -> 'Iterator[T]':
	iterable = iter(iterable)
	try:
		yield next(iterable)
		for item in iterable:
			yield sep
			yield item
	except StopIteration:
		pass

def list_join(sep: 'T', iterable: 'Iterator[T]') -> 'list[T]':
	return list(iter_join(sep, iterable))


# ------- replace in markup -------

def replace_in_markup(markup: UrwidMarkupType, old: 're.Pattern[str]', new: 'UrwidMarkupType | Callable[[re.Match[str]], UrwidMarkupType]') -> UrwidMarkupType:
	'''
	old: regular expression object
	new: markup or function which takes a match object and returns a markup
	in contrast to replace_attribute this replaces text, no attributes
	'''
	if isinstance(old, str):
		old = re.compile(re.escape(old))

	if isinstance(markup, str):
		return replace_in_str(markup, old, new)

	if isinstance(markup, tuple):
		assert len(markup) == 2
		return (markup[0], replace_in_markup(markup[1], old, new))

	out = []
	for w in markup:
		out.append(replace_in_markup(w, old, new))
	return out

def replace_in_str(markup: str, old: 're.Pattern[str]', new: 'UrwidMarkupType | Callable[[re.Match[str]], UrwidMarkupType]') -> UrwidMarkupType:
	out: 'list[UrwidMarkupType]' = []
	def append(w: UrwidMarkupType) -> None:
		if w is None:
			raise TypeError("new returns None")
		if not w:
			return
		if isinstance(w, str) and out and isinstance(out[-1], str):
			out[-1] += w
			return
		out.append(w)
	i = 0
	for m in old.finditer(markup):
		append(markup[i:m.start()])
		w: UrwidMarkupType
		try:
			w = new(m)  # type: ignore [operator]  # yes, str, tuple and list are not callable. That's what the try-except is there for.
		except TypeError:
			w = typing.cast(UrwidMarkupType, new)
		if isinstance(w, list):
			for wi in w: append(wi)
		else:
			append(w)
		i = m.end()
	append(markup[i:])

	if not out:
		return ""

	if isinstance(out, list) and len(out) == 1:
		return out[0]

	return out

# ------- simplify markup -------

def simplify_markup(markup: UrwidMarkupType) -> UrwidSimplifiedMarkupType:
	'''clean up the markup to avoid bugs in urwid'''
	if isinstance(markup, str):
		return markup
	
	out = list(_simplify_markup(None, markup))
	if not out:
		return ""
	
	if len(out) == 1:
		return out[0]
	
	return out

def _simplify_markup(default_attribute: UrwidAttributeType, markup: UrwidMarkupType) -> 'Iterator[tuple[UrwidAttributeType, UrwidTextType]]':
	if isinstance(markup, str):
		yield (default_attribute, markup)
	
	elif isinstance(markup, tuple):
		yield from _simplify_markup(markup[0], markup[1])
	
	else:
		last_attr = None
		last_markups: 'list[str]' = []
		for m in markup:
			for ia, im in _simplify_markup(default_attribute, m):
				if ia != last_attr:
					if last_markups:
						yield last_attr, "".join(last_markups)
					last_attr = ia
					last_markups = []
				last_markups.append(im)
		if last_markups:
			yield last_attr, "".join(last_markups)

# ------- replace attributes -------

def replace_attribute(markup: UrwidMarkupType, attr: UrwidAttributeType, newattr: UrwidAttributeType) -> 'tuple[UrwidMarkupType, int]':
	'''
	replace attr in markup with newattr, returns (newmarkup, number of replacements)
	in contrast to replace_in_markup this replaces attributes, no text
	'''
	assert isinstance(attr, str)
	assert isinstance(newattr, str)
	if isinstance(markup, str):
		return markup, 0
	if isinstance(markup, tuple):
		markup1, n = replace_attribute(markup[1], attr, newattr)
		if markup[0] == attr:
			return (newattr, markup1), n+1
		else:
			return (markup[0], markup1), n

	out = []
	n = 0
	for m in markup:
		_m, _n = replace_attribute(m, attr, newattr)
		out.append(_m)
		n += _n
	return out, n

# ------- palette tuples <-> color strings -------

SEP_COLOR = "/"
ALLOWED_EMPHASIS = {"bold", "underline", "standout", "italics", "blink", "strikethrough"}

def palette_tuple_to_color_str(palette_tuple: UrwidPaletteThreeTuple) -> MyColorType:
	name, fg, bg = palette_tuple
	fg = _convert_fg_to_user(fg)
	bg = _convert_bg_to_user(bg)
	return fg + SEP_COLOR + bg

def _convert_fg_to_user(fg: UrwidColorType) -> MyColorType:
	fg_list = fg.split(",")
	fg_color = fg_list[0]
	for name, value in urwid_constants.COLOR.__dict__.items():
		if name.startswith("FG_") and value == fg_color:
			fg_color = name[3:].lower().replace("_", " ")
			fg_list[0] = fg_color
			return ",".join(fg_list)

	assert False, "INTERNAL ERROR: invalid foreground color %r" % fg

def _convert_bg_to_user(bg: UrwidColorType) -> MyColorType:
	bg_list = bg.split(",")
	bg_color = bg_list[0]
	for name, value in urwid_constants.COLOR.__dict__.items():
		if name.startswith("FG_") and value == bg_color:
			bg_color = name[3:].lower().replace("_", " ")
			bg_list[0] = bg_color
			return ",".join(bg_list)

	assert False, "INTERNAL ERROR: invalid background color %r" % bg


def color_str_to_palette_tuple(name: UrwidAttributeType, color_str: MyColorType) -> UrwidPaletteThreeTuple:
	if SEP_COLOR in color_str:
		fg, bg = color_str.split(SEP_COLOR, 1)
	else:
		fg = color_str
		bg = urwid_constants.COLOR.BG_DEFAULT

	fg = _convert_fg_to_urwid(fg)
	bg = _convert_bg_to_urwid(bg)

	return (name, fg, bg)

def _convert_fg_to_urwid(fg: MyColorType) -> UrwidColorType:
	fg_list = fg.split(",")
	fg_color_name = "FG_" + fg_list[0].upper().replace(" ", "_")
	fg_color = getattr(urwid_constants.COLOR, fg_color_name, None)
	if fg_color is None:
		raise ValueError(_("invalid foreground color %r") % fg_list[0])
	assert isinstance(fg_color, str)
	for i in range(1, len(fg_list)):
		if fg_list[i] not in ALLOWED_EMPHASIS:
			raise ValueError(_("invalid emphasis %r") % fg_list[i])

	fg_list[0] = fg_color
	return ",".join(fg_list)

def _convert_bg_to_urwid(bg: MyColorType) -> UrwidColorType:
	bg_color_name = "BG_" + bg.upper().replace(" ", "_")
	bg_color = getattr(urwid_constants.COLOR, bg_color_name, None)
	if bg_color is None:
		raise ValueError(_("invalid background color %r") % bg)
	assert isinstance(bg_color, str)
	return bg_color


# ------- color markup -------

_reo_color_tag = re.compile(r'<color=([^>]*)>|</color>')
def colored_str_to_markup(coloredstr: str, define_color: 'Callable[[MyColorType], UrwidAttributeType]') -> UrwidMarkupType:
	# >>> colored_str_to_markup('hello <color=red>world</color>')
	# l = ['hello ', 'red', 'world', None, '']
	l = _reo_color_tag.split(coloredstr)
	n = len(l)
	out: 'list[UrwidMarkupType]' = []

	text = l[0]
	if text:
		out.append(text)

	i = 1
	while i < n:
		i = _colored_str_to_markup(l, i, n, out, define_color)
		assert i % 2 == 1

		if i >= n:
			break

		i += 1
		text = l[i]
		assert isinstance(text, str)

		if text:
			out.append(text)

		i += 1

	if not out:
		return ""

	if len(out) == 1:
		return out[0]

	return out

def _colored_str_to_markup(l: 'list[str]', i: int, n: int, out: 'list[UrwidMarkupType]', define_color: 'Callable[[MyColorType], UrwidAttributeType]') -> int:
	color = l[i]
	assert isinstance(color, str)
	subout: 'list[UrwidMarkupType]' = []

	while i < n:
		assert i % 2 == 1

		i += 1
		text = l[i]
		assert isinstance(text, str)

		if text:
			subout.append(text)

		i += 1
		if i >= n or l[i] is None:
			break
		else:
			i = _colored_str_to_markup(l, i, n, subout, define_color)

	if subout:
		attr = define_color(color)
		out.append((attr, subout[0] if len(subout) == 1 else subout))

	return i


# ------- mnemonics -------

class CommandWithMnemonic(str):

	__slots__ = ('mnemonic')
	mnemonic: str

	def __new__(cls, cmd: str, mnemonic: str) -> 'CommandWithMnemonic':
		cmd = super().__new__(cls, cmd)
		cmd.mnemonic = mnemonic
		return cmd

	def __repr__(self) -> str:
		return "%s(%s, %r)" % (type(self).__name__, super().__repr__(), self.mnemonic)

	def __add__(self, other: 'Mnemonic|str') -> 'CommandWithMnemonic|str':
		if isinstance(other, Mnemonic):
			return CommandWithMnemonic(self, self.mnemonic + Mnemonic.sep + other.mnemonic)
		return super().__add__(other)

class Mnemonic:

	__slots__ = ('mnemonic')
	sep = _(", ")

	def __init__(self, mnemonic: str) -> None:
		self.mnemonic = mnemonic

	def __rfloordiv__(self, cmd: str) -> CommandWithMnemonic:
		assert isinstance(cmd, str)
		return CommandWithMnemonic(cmd, self.mnemonic)

def like_in(*other_programs: str) -> Mnemonic:
	other_programs_formatted = join(other_programs, _(', '), _(' and '))
	mnemonic = _('like in {other_programs}').format(other_programs=other_programs_formatted)
	return Mnemonic(mnemonic)

def join(l: 'Sequence[str]', sep: str, last_sep: str) -> str:
	if not l:
		return ""
	last = l[-1]
	l = l[:-1]
	if not l:
		return last
	return last_sep.join((sep.join(l), last))
