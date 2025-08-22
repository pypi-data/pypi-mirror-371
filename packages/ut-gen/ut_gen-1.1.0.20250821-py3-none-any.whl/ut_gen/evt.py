# coding=utf-8
from typing import Any

TyDic = dict[Any, Any]


class EvtHandle:
    """Event Handler Class
    """
    @staticmethod
    def sh_evargs(env, evt_type, action) -> TyDic:
        return {'env': env, 'type': evt_type, 'action': action}
