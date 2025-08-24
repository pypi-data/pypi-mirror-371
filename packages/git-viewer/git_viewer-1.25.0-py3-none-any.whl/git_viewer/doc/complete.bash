#!/usr/bin/env bash

# Basics about writing bash completion functions as explained in
# https://www.gnu.org/software/bash/manual/html_node/Programmable-Completion.html
# do not fully apply because the function is wrapped with __git_func_wrap
# $1, $2 and $3 are not passed
# _get_comp_words_by_ref provides the variables cur, prev, words, cword
# __gitcomp can be used to complete a list of options
# see /usr/share/bash-completion/completions/git

__gitviewer_load_git_completion ()
{
	local path oldifs
	paths="$(pkg-config --variable=completionsdir bash-completion 2>/dev/null || true)"
	paths="${paths:-/usr/share/bash-completion/completions}"
	oldifs="$IFS"
	IFS=:
	for path in $paths; do
		path="${path%/}/git"
		if [ -f "$path" ]; then
			. "$path"
			IFS="$oldifs"
			return
		fi
	done
	IFS="$oldifs"
	echo "Failed to find git completion script"
}

__gitviewer_has_option ()
{
	local c=1
	local option="$1"
	while [ $c -lt $cword ]; do
		if [ "$option" = "${words[c]}" ]; then
			return 0
		fi
		((c++))
	done
	return 1
}

__gitviewer_gitl ()
{
	__git_has_doubledash && return
	if __gitviewer_has_option '-d' || __gitviewer_has_option '--diff-options'; then
		_git_diff
	else
		_git_log
		__gitcomp '--unreachable --diff-options --version --help'
	fi
}

__gitviewer_load_git_completion
__git_complete gitl __gitviewer_gitl
__git_complete gitd git_diff
__git_complete gits git_show
