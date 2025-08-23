# This file is placed in the Public Domain.


"commands"


import inspect
import logging
import _thread


from .event  import Event
from .fleet  import Fleet
from .parse  import parse
from .pkg    import Mods, mod, sums
from .thread import launch
from .utils  import spl


class Commands:

    cmds  = {}
    names = {}

    @staticmethod
    def add(func, mod=None) -> None:
        Commands.cmds[func.__name__] = func
        if mod:
            Commands.names[func.__name__] = mod.__name__.split(".")[-1]

    @staticmethod
    def get(cmd):
        func = Commands.cmds.get(cmd, None)
        if not func:
            name = Commands.names.get(cmd, None)
            if not name:
                return
            module = mod(name)
            if module:
                scan(module)
                func = Commands.cmds.get(cmd)
        return func


def cmnd(clt, txt):
    evt = Event()
    evt.orig = repr(clt)
    evt.type = "command"
    evt.txt = txt
    command(evt)
    evt.wait()
    return evt


def command(evt):
    parse(evt)
    func = Commands.get(evt.cmd)
    if func:
        func(evt)
        Fleet.display(evt)
    evt.ready()


def inits(names):
    modz = []
    for name in spl(names):
        try:
            module = mod(name)
            if not module:
                continue
            if "init" in dir(module):
                thr = launch(module.init)
                modz.append((module, thr))
        except Exception as ex:
            logging.exception(ex)
            _thread.interrupt_main()
    return modz


def scan(mod):
    for key, cmdz in inspect.getmembers(mod, inspect.isfunction):
        if key.startswith("cb"):
            continue
        if 'event' in cmdz.__code__.co_varnames:
            Commands.add(cmdz, mod)


def table():
    if Mods.checksum and not sums():
        logging.error("checksums don't match")
        return
    tbl = mod("tbl")
    names = getattr(tbl, "NAMES", None)
    if names:
        Commands.names.update(names)


def __dir__():
    return (
        'Commands',
        'cmnd',
        'command',
        'inits',
        'scan',
        'table'
    )
