# This file is placed in the Public Domain.


"find"


import time


from nixt.disk  import Cache
from nixt.find  import find, fntime
from nixt.func  import fmt
from nixt.utils import elapsed


def fnd(event):
    if not event.rest:
        res = sorted([x.split('.')[-1].lower() for x in Cache.types])
        if res:
            event.reply(",".join(res))
        return
    clz = event.args[0]
    nmr = 0
    for fnm, obj in list(find(clz, event.gets)):
        event.reply(f"{nmr} {fmt(obj)} {elapsed(time.time()-fntime(fnm))}")
        nmr += 1
    if not nmr:
        event.reply("no result")
