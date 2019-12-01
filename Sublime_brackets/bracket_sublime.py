# coding: utf8
import re
# from functools import cmp_to_key

import sublime
import sublime_plugin
from sublime import Region

# for detecting "real" brackets in BracketeerCommand, and bracket matching in BracketeerBracketMatcher
OPENING_BRACKETS = ['{', '[', '(']
OPENING_BRACKET_LIKE = ['{', '[', '(', '"', "'", u'“', '‘', '«', '$', '‹']
# OPENING_BRACKET_LIKE = ['{', '[', '(', '"', "'", u'“', '‘', '«', '‹']
CLOSING_BRACKETS = ['}', ']', ')']
CLOSING_BRACKET_LIKE = ['}', ']', ')', '"', "'", u'”', '’', '»', '$', '›']
# CLOSING_BRACKET_LIKE = ['}', ']', ')', '"', "'", u'”', '’', '»', '›']
QUOTING_BRACKETS = ['\'', "\""]


class Bracket_sublimeCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        # check that whether regions are all empty, if true ctrl+shift+m
        original_region_all_empty = True
        for region in list(self.view.sel())[::-1]:
            original_region_all_empty = original_region_all_empty and region.empty()
            # print(original_region_all_empty)
        if original_region_all_empty:
            self.view.run_command("expand_selection",{"to": "brackets"})

        for region in list(self.view.sel())[::-1]:
            if region.empty():
                # print("region is empty")
                continue
            self.view.sel().subtract(region)
            self.run_each(edit, region, original_region_all_empty, **kwargs)

    def run_each(self, edit, region, original_region_all_empty, braces='{}', pressed=None, unindent=False, select=False, replace=False):
        '''
        Options:
            braces    a list of matching braces or a string containing the pair
            pressed   the key pressed; used for closing vs opening logic
            unindent  removes one "tab" from a newline.  true for braces that handle indent, like {}
            select    whether to select the region inside the braces
            replace   whether to insert new braces where the old braces were
        '''
        ####################### split_region_to_two_side #########################
        if braces[0] == "s":
            self.view.sel().add(region.begin())
            self.view.sel().add(region.end())
            return
        ####################### split_region_to_two_side #########################
        if self.view.settings().get('translate_tabs_to_spaces'):
            tab = ' ' * self.view.settings().get('tab_size')
        else:
            tab = "\t"

        row, col = self.view.rowcol(region.begin())
        indent_point = self.view.text_point(row, 0)
        if indent_point < region.begin():
            indent = self.view.substr(Region(indent_point, region.begin()))
            indent = re.match('[ \t]*', indent).group(0)
        else:
            indent = ''
        line = self.view.substr(self.view.line(region.a))
        selection = self.view.substr(region)

        # for braces that have newlines ("""), insert the current line's indent
        if isinstance(braces, list):
            l_brace = braces[0]
            r_brace = braces[1]
            braces = ''.join(braces)
            braces = braces.replace("\n", "\n" + indent)
            length = len(l_brace)
        else:
            braces = braces.replace("\n", "\n" + indent)
            length = len(braces) // 2
            l_brace = braces[:length]
            r_brace = braces[length:]

        if not region.empty():
        # else:
            substitute = self.view.substr(region)
            replacement = l_brace + substitute + r_brace
            # print(replacement)
            # if we're inserting "real" brackets, not quotes:
            real_brackets = l_brace in OPENING_BRACKETS and r_brace in CLOSING_BRACKETS

            # check to see if entire lines are selected, and if so do some smart indenting
            # bol_is_nl => allman style {}
            # bol_at_nl => kernigan&ritchie
            if region.begin() == 0:
                bol_is_nl = True
                bol_at_nl = False
            elif len(self.view) == region.begin() + 1:
                bol_is_nl = False
                bol_at_nl = False
            else:
                bol_is_nl = self.view.substr(region.begin() - 1) == "\n"
                bol_at_nl = l_brace == '{' and self.view.substr(region.begin()) == "\n" and self.view.substr(region.begin() - 1) != "\n"
            eol_is_nl = region.end() == self.view.size() or self.view.substr(region.end()) == "\n"
            eol_at_nl = self.view.substr(region.end() - 1) == "\n"
            if eol_is_nl:
                eol_is_nl = self.view.line(region.begin()) != self.view.line(region.end())

            if real_brackets and (bol_is_nl or bol_at_nl) and (eol_is_nl or eol_at_nl):
                indent = ''
                if bol_at_nl and substitute:
                    substitute = substitute[1:]
                m = re.match('([ \t]*)' + tab, substitute)
                if m:
                    indent = m.group(1)
                else:
                    substitute = tab + substitute
                output_end_point = region.begin() - len("\n" + indent + r_brace)

                if bol_at_nl:
                    replacement = l_brace + "\n" + substitute
                    if eol_at_nl:
                        replacement += indent + r_brace + "\n"
                        output_end_point -= 1
                    else:
                        replacement += r_brace + "\n"
                        output_end_point += len[indent]

                    if not self.view.substr[region.begin() - 1] == ' ':
                        replacement = ' ' + replacement
                else:
                    replacement = indent + l_brace + "\n" + substitute + indent + r_brace + "\n"
                    output_end_point -= 1
                output_end_point += len(replacement)
            else:
                output_end_point = region.begin() + len(replacement)

            original_region_all_empty_empty_in_brackets=False
            if original_region_all_empty and region.b-region.a == 2 and replace and self.view.substr(region.begin()) in OPENING_BRACKET_LIKE and self.view.substr(region.end() - 1) in CLOSING_BRACKET_LIKE:
                if not (l_brace == '' and r_brace == ''):
                    original_region_all_empty_empty_in_brackets=True
                replacement = l_brace
                replacement += replacement[(len(l_brace)+1):-(len(l_brace)+1)]
                replacement += r_brace
                output_end_point -= 2
                # print(l_brace, r_brace)
                self.view.replace(edit, region, replacement)
                l_brace = r_brace = ''
            elif replace and self.view.substr(region.begin() - 1) in OPENING_BRACKET_LIKE and self.view.substr(region.end()) in CLOSING_BRACKET_LIKE:
                output_end_point -= 1
                self.view.replace(edit, Region(region.begin() - 1, region.end() + 1), replacement)
            # elif replace and self.view.substr(region.begin()) in OPENING_BRACKET_LIKE and self.view.substr(region.end() - 1) in CLOSING_BRACKET_LIKE:
            #     if l_brace == '' and r_brace == '':
            #         replacement = l_brace + replacement[1:-1] + r_brace
            #     else:
            #         replacement = l_brace + replacement[2:-2] + r_brace
            #     output_end_point -= 2
            #     # print(l_brace, r_brace)
            #     self.view.replace(edit, region, replacement)
            #     l_brace = r_brace = ''
            else:
                self.view.replace(edit, region, replacement)

            if original_region_all_empty_empty_in_brackets:
                self.view.sel().add(output_end_point-1)
            elif select:
                self.view.sel().add(
                                    Region(
                                        output_end_point - len(replacement) + len(l_brace), 
                                        output_end_point - len(r_brace)
                                    )
                                )
            else:
                self.view.sel().add(output_end_point)


