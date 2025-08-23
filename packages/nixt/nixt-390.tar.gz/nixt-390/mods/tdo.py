# This file is placed in the Public Domain.


"todo list"


import time


from nixt.disk  import write
from nixt.find  import find, fntime
from nixt.paths import ident
from nixt.utils import elapsed


class Todo:

    def __init__(self):
        self.txt = ''


def dne(event):
    if not event.args:
        event.reply("dne <txt>")
        return
    selector = {'txt': event.args[0]}
    nmr = 0
    for fnm, obj in find('todo', selector, disk=True):
        nmr += 1
        obj.__deleted__ = True
        write(obj, fnm)
        event.done()
        break
    if not nmr:
        event.reply("nothing todo")


def tdo(event):
    if not event.rest:
        nmr = 0
        for fnm, obj in find('todo', disk=True):
            lap = elapsed(time.time()-fntime(fnm))
            event.reply(f'{nmr} {obj.txt} {lap}')
            nmr += 1
        if not nmr:
            event.reply("no todo")
        return
    obj = Todo()
    obj.txt = event.rest
    write(obj, ident(obj), disk=True)
    event.done()
