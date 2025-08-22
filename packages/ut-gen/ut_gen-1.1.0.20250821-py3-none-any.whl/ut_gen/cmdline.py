from typing import Any

import re
import sys

TyArr = list[Any]


class Cmdline:

    RE_CMD_LEX1 = r'''
      "((?:\\["\\]|[^"])*)"|'([^']*)'|(\\.)|(&&?|\|\|?|\d?\>|[<])|([^\s'"\\&|<>]+)|(\s+)|(.)
    '''
    RE_CMD_LEX0 = r'''
      "((?:""|\\["\\]|[^"])*)"?()|(\\\\(?=\\*")|\\")|(&&?|\|\|?|\d?>|[<])|([^\s"&|<>]+)|(\s+)|(.)
    '''
    FIELDS_PATTERN = re.compile(r"(?:\"(.*?)\"|(\S+))")

    @classmethod
    def sh_re_cmd_lex(cls, platform: int):
        match platform:
            case 1:
                return cls.RE_CMD_LEX1
            case 0:
                return cls.RE_CMD_LEX0
            case _:
                raise AssertionError(f'unkown platform {platform}')

    @staticmethod
    def sh_word_for_qs(qs: str, word: str, platform: int) -> str:
        word = qs.replace('\\"', '"').replace('\\\\', '\\')
        if platform == 0:
            word = word.replace('""', '"')
        return word

    @classmethod
    def split_by_re0(cls, s, platform: Any = 'this') -> TyArr:
        """
        Multi-platform variant of shlex.split() for command-line splitting.
        For use with subprocess, for argv injection etc. Using fast REGEX.

        platform: 'this' = auto from current platform;
                  1 = POSIX;
                  0 = Windows/CMD
                  (other values reserved)
        """
        if platform == 'this':
            _platform = int(sys.platform != 'win32')
        else:
            _platform = int(platform)
        RE_CMD_LEX = cls.sh_re_cmd_lex(_platform)
        args = []
        accu = None   # collects pieces of one arg
        for qs, qss, esc, pipe, word, white, fail in re.findall(RE_CMD_LEX, s):
            if word:
                pass   # most frequent
            elif esc:
                word = esc[1]
            elif white or pipe:
                if accu is not None:
                    args.append(accu)
                if pipe:
                    args.append(pipe)
                accu = None
                continue
            elif fail:
                msg = f"invalid or incomplete shell string: {s}"
                raise ValueError(msg)
            elif qs:
                word = cls.sh_word_for_qs(qs, word, platform)
            else:
                word = qss   # may be even empty; must be last
            accu = (accu or '') + word
        if accu is not None:
            args.append(accu)
        return args

    @classmethod
    def split_by_re1(cls, string: str) -> TyArr:
        """
        Given an argument string this attempts to split it into small parts.
        """
        rv = []
        for match in re.finditer(r"('([^'\\]*(?:\\.[^'\\]*)*)'"
                                 r'|"([^"\\]*(?:\\.[^"\\]*)*)"'
                                 r'|\S+)\s*', string, re.S):
            arg = match.group().strip()
            if arg[:1] == arg[-1:] and arg[:1] in '"\'':
                arg = arg[1:-1].encode('ascii', 'backslashreplace') \
                    .decode('unicode-escape')
            try:
                arg = type(string)(arg)
            except UnicodeError:
                pass
            rv.append(arg)
        return rv

    @classmethod
    def split_by_re2(cls, data: str) -> TyArr:
        return [x[0] or x[1] for x in cls.FIELDS_PATTERN.findall(data)]
