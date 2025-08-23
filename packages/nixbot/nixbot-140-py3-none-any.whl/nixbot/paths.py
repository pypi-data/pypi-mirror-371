# This file is placed in the Public Domain.


"cache"


import datetime
import os


class Workdir:

    name = __file__.rsplit(os.sep, maxsplit=2)[-2]
    wdr = os.path.expanduser(f"~/.{name}")


def fqn(obj):
    kin = str(type(obj)).split()[-1][1:-2]
    if kin == "type":
        kin = f"{obj.__module__}.{obj.__name__}"
    return kin


def getpath(obj):
    return ident(obj)


def ident(obj):
    return os.path.join(fqn(obj), *str(datetime.datetime.now()).split())


def long(name):
    split = name.split(".")[-1].lower()
    res = name
    for names in types():
        if split == names.split(".")[-1].lower():
            res = names
            break
    return res


def store(pth=""):
    return os.path.join(Workdir.wdr, "store", pth)


def strip(pth, nmr=3):
    return os.sep.join(pth.split(os.sep)[-nmr:])


def types():
    return os.listdir(store())


def __dir__():
    return (
        'Cache',
        'read',
        'write'
    )
