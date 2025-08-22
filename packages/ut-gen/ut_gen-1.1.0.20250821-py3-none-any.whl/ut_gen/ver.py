# coding=utf-8

import os
import re

from ut_log.log import Log


class Ver:
    """ Manage Verifcation
    """
    msg_path = "Given path: {zpath} has a wrong format or not existing"
    msg_email = "Wrong email address: {email}"
    msg_module = "Given module: {module} is not defined"

    @staticmethod
    def is_none(obj) -> bool:
        if obj is None:
            return True
        return False

    @staticmethod
    def is_not_none(obj) -> bool:
        if obj is None:
            return False
        return True

    @classmethod
    def path(cls, zpath) -> bool:
        if os.path.exists(zpath):
            return True
        Log.error(cls.msg_path.format(zpath))
        return False

    @classmethod
    def email(cls, email) -> bool:
        match = re.search(r'[\w.-]+@[\w.-]+.\w+', email)
        if match:
            return True
        Log.error(cls.msg_email.format(email))
        return False

    @staticmethod
    def name(name) -> bool:
        if len(name) > 1:
            return True
        return False

    @classmethod
    def module(cls, module, a_module) -> bool:
        if module in a_module:
            return True
        Log.error(cls.msg_module.format(module))
        return False
