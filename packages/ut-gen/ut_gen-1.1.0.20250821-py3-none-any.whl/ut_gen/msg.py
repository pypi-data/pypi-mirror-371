# coding=utf-8
"""
Koskya Utilities Module
contains the Kosakya Utilitiy Classes
"""

from ut_com.com import Com
from ut_gen.col import Col


class Level:
    """Log Level specific Text Formatting Class
    """
    @staticmethod
    def sh_color(level):
        match level:
            case 'CRITICAL':
                return Col.sh_bold_red(level)
            case 'ERROR':
                return Col.sh_bold_magenta(level)
            case 'WARNING':
                return Col.sh_bold_yellow(level)
            case 'DEBUG':
                return Col.sh_bold_light_green(level)
            case 'INFO':
                return Col.sh_bold_cyan(level)
            case _:
                return level


class Msg:
    """
    Message Class
    """
    @staticmethod
    def get(**kwargs):
        MSGS = kwargs.get('MSGS')
        if MSGS is None:
            MSGS = Com.MSGS
        env = kwargs.get('env')
        _type = kwargs.get('type')
        fnc = kwargs.get('fnc')
        action = kwargs.get('action')
        arr = kwargs.get('arr')

        msg = MSGS[env][_type][fnc][action]
        if not arr:
            return msg
        return msg.format(arr)

    @staticmethod
    def get_objs(**kwargs):
        MSGS = kwargs.get('MSGS')
        if MSGS is None:
            MSGS = Com.MSGS
        env = kwargs.get('env')
        _type = kwargs.get('type')
        fnc = kwargs.get('fnc')
        arr = kwargs.get('arr')
        if type.endswith('class'):
            _type = f'{_type}(es)'
        _type = f'{_type}(s)'
        action = kwargs.get('action')
        if arr:
            msg = MSGS[env]['objs'][fnc][action]
            return msg.format(_type, arr)
        if action == 'ver_sel':
            msg = MSGS[env]['objs'][fnc][action]
            return msg.format(_type)
        msg = MSGS[env]['objs'][fnc]['all']
        return msg.format(_type)


class MsgFmt:
    """
    Message Formatting Class
    """
    @staticmethod
    def out(out, caller, out_typ='MSG'):
        if caller:
            if out:
                return f'[{caller}] {out_typ}: {out}'
            return f'[{caller}] {out_typ}: '
        if out:
            return f'{out_typ}: {out}'
        return f'{out_typ}: '

    @classmethod
    def msg(cls, msg, caller):
        return cls.out(msg, caller, out_typ='MSG')

    @classmethod
    def exc(cls, exc, caller):
        return cls.out(exc, caller, out_typ='EXC')

    @staticmethod
    def prefix(msg, prefix=None, sw_short=False):
        if not prefix:
            return msg
        if sw_short:
            prefix = prefix.split('.')[0]
        if isinstance(msg, (list, tuple)):
            msg_arr = msg.splitlines()
            zmsg = [f"[{prefix}] {line}" for line in msg_arr]
            return '\n'.join(zmsg)
        return f"[{prefix}] {msg}"

    @classmethod
    def status(cls, msg, exit_code=None, exc=None):
        if exit_code == 0:
            return cls.success(msg, exit_code)
        return cls.failed(msg, exit_code, exc)

    @classmethod
    def status_host_cmd(cls, host, cmd, exit_code, exc=None):
        msg = f"Host: [{host}] Command: [{cmd}]"
        return cls.status(msg, exit_code, exc)

    @staticmethod
    def success(msg, exit_code=None):
        if isinstance(msg, (list, tuple)):
            msg = " ".join(msg)
        success = Col.sh_bold_green('SUCCESS')
        if exit_code == 0:
            return f"{msg} Exit-Code:[{exit_code}] [{success}]"
        return f"{msg} [{success}]"

    @staticmethod
    def failed(msg, exit_code=None, exc=None):
        if isinstance(msg, (list, tuple)):
            msg = " ".join(msg)
        failed = Col.sh_bold_red('FAILED')
        if exit_code is not None:
            if exc:
                return f"{msg} Exit-Code:[{exit_code}] [{failed}] error:{exc}"
            return f"{msg} Exit-Code:[{exit_code}] [{failed}]"
        if exc:
            return f"{msg} [{failed}] error:{exc}"
        return f"{msg} [{failed}] "
