# coding=utf-8
from typing import Any

TyDic = dict[Any, Any]
TyAoD = list[TyDic]
TyExc = type[Exception]
TyDic_Str = TyDic | str


class ArgumentError(Exception):
    """ Argument Error Exception Class
    """
    pass


class Exc:
    """ Manage Exception
    """
    @staticmethod
    def sh_aod_trace(tb, sw_traceback: bool = True) -> TyAoD:
        """ Show Exception type, message and traceback
        """
        _aod_trace = []
        while tb is not None:
            _d_trace: TyDic = {
                    'filename': tb.tb_frame.f_code.co_filename,
                    'name': tb.tb_frame.f_code.co_name,
                    'lineno': tb.tb_lineno
            }
            _aod_trace.append(_d_trace)
            if not sw_traceback:
                break
            tb = tb.tb_next
        return _aod_trace

    @classmethod
    def sh_d_trace(cls, exc: TyExc, sw_traceback: bool = True) -> TyDic:
        """ Show Exception type, message and traceback
        """
        _aod_trace = cls.sh_aod_trace(exc.__traceback__)
        _d_trace = {
                'type': type(exc).__name__,
                'exc': str(exc),
                'trace': _aod_trace
        }
        return _d_trace

    @classmethod
    def sh_exc(
            cls, exc: TyExc, sw_traceback: bool = True, sw_json: bool = True
    ) -> TyDic_Str:
        """
        Show Exception type, message and traceback
        """
        d_trace: TyDic = cls.sh_d_trace(exc, sw_traceback)
        if sw_json:
            return d_trace
        return (f"type: {d_trace['type']}, "
                f"message: {d_trace['message']}, "
                f"trace: {d_trace['trace']}")

    @staticmethod
    def get_exc(exc: TyExc) -> str:
        _exc_arr = list(exc.args)
        _exc_msg: str = _exc_arr.pop(0)
        return _exc_msg % tuple(_exc_arr)


class ExcNo(Exception):
    pass


class ExcStop(Exception):
    pass
