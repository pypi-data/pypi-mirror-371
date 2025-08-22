from typing import Any

import subprocess

from ut_log.log import Log

TyArr = list[Any]


class Cmd:

    @staticmethod
    def ex(cmd: str, **kwargs) -> None:
        # universal_newlines = kwargs.get('universal_newlines', False)
        check = kwargs.get('check', False)
        shell = kwargs.get('shell', True)

        Log.Eq.debug("cmd", cmd)

        proc = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)
        subprocess.CompletedProcess(
                cmd, proc.returncode, proc.stdout, proc.stderr)
        if check and (proc.returncode != 0):
            raise subprocess.CalledProcessError(
                    proc.returncode, cmd, proc.stdout, proc.stderr)
        Log.Eq.debug("proc.stdout.decode()", proc.stdout.decode())
        Log.Eq.debug("proc.stderr.decode()", proc.stderr.decode())


class ArrCmd:

    @staticmethod
    def ex(a_cmd: TyArr, **kwargs) -> None:
        for cmd in a_cmd:
            Log.Eq.debug("cmd", cmd)
            Cmd.ex(cmd, **kwargs)
