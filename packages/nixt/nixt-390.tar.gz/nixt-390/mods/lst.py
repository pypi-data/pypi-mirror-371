# This file is been placed in the Public Domain.


"available types"


from nixt.disk import Cache


def ls(event):
    event.reply(",".join([x.split(".")[-1].lower() for x in Cache.types]))
