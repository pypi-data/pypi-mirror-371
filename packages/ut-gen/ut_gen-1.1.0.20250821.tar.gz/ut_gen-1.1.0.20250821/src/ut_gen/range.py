# coding=utf-8
"""
Koskya Utilities Module
contains the Kosakya Utilitiy Classes
"""
from typing import Any

TyArr = list[Any]
TyDic = dict[Any, Any]


class Range:
    """Range Dictionary Class

    Definition:
        Range Dictionary is a Dictionary which contains the range fields:
        count, start, step
    """

    @classmethod
    def get_next(cls, dic: TyDic):
        """get next suffix of range dictionary
        get next numerical or alpha suffix if start value of range
        dictionary is numeric or alpha

        Args:
            dic (dict): range dictionary
        Returns:
            list: next suffix
        """
        if dic['start'].isdigit():
            return cls.get_next_digit(dic)
        else:
            return cls.get_next_nodigit(dic)

    @staticmethod
    def get_next_digit(dic: TyDic):
        """get next numerical suffix from suffix generator of range dictionary

        Args:
            dic (dict): range dictionary
        Yields:
            str: next numerical suffix
        """
        len_count = len(dic['count'])
        count = int(dic['count'])
        start = int(dic['start'])
        step = int(dic['step'])
        for ii in range(0, count):
            if ii == 0:
                next = start
            else:
                next = next + step
            len_count = len(str(next))
            next_str = f'%{len_count}s' % next
            yield next_str

    def get_lexicographically_next_word(s):
        # If string is empty.
        if (s == " " or s == ""):
            return "a"
        # Find first character from right which is not z.
        i = len(s) - 1
        while (s[i] == 'z' and i >= 0):
            i -= 1
        # If all characters are 'z', append an 'a' at the end.
        if (i == -1):
            s = s + 'a'
        # If there are some non-z characters
        else:
            s = s.replace(s[i], chr(ord(s[i]) + 1), 1)
        return s

    @classmethod
    def get_next_nodigit(cls, dic: TyDic):
        """get next numerical suffix generator of range dictionary

        Args:
            dic (dict): range dictionary
        Yields:
            str: next numerical suffix
        """
        count = int(dic['count'])
        start = dic['start']
        step = int(dic['step'])
        for ii in range(0, count):
            if ii == 0:
                _next = start
            else:
                for jj in range(0, step):
                    _next = cls.get_lexicographically_next_word(_next)
            yield _next

    def get_arr(value: Any, range_dic: TyDic) -> TyArr:
        """
        get array of values defined by start value and range dictionary.
        create array items by adding all next suffixes from range dictionary
        to the value.

        Args:
            value (str): start value
            range_dic (dict): range dictionary
        Returns:
            list: array of values
        """
        if range_dic:
            arr = []
            for suffix in Range.get_next(range_dic):
                value_new = f"{value}{suffix}"
                arr.append(value_new)
            return arr
        return [value]

    @classmethod
    def get_values(cls, **kwargs):
        try:
            value = kwargs.get('values')[0]
            range_dic = kwargs.get('range_dic')
            return cls.get_arr(value, range_dic)
        except Exception:
            raise
