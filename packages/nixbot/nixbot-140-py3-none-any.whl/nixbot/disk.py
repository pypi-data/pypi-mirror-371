# This file is placed in the Public Domain.


"cache"


import json
import pathlib
import threading


from .object import update
from .paths  import fqn, store
from .serial import dump, load


lock = threading.RLock()


class Cache:

    disk = True
    objs = {}
    types = []

    @staticmethod
    def add(path, obj):
        Cache.objs[path] = obj
        typ = fqn(obj)
        if typ not in Cache.types:
            Cache.types.append(typ)

    @staticmethod
    def get(path):
        return Cache.objs.get(path, None)

    @staticmethod
    def typed(typ):
        return [x for x in Cache.objs if typ in x]

    @staticmethod
    def update(path, obj):
        if not obj:
            return
        if path in Cache.objs:
            update(Cache.objs[path], obj)
        else:
            Cache.add(path, obj)


def cdir(path):
    pth = pathlib.Path(path)
    pth.parent.mkdir(parents=True, exist_ok=True)


def read(obj, path, disk=False):
    with lock:
        if disk or Cache.disk:
            ppath = store(path)
            with open(ppath, "r", encoding="utf-8") as fpt:
                try:
                    update(obj, load(fpt))
                except json.decoder.JSONDecodeError as ex:
                    ex.add_note(path)
                    raise ex
            Cache.update(path, obj)
        else:
            update(obj, Cache.get(path))

 
def skel():
    pth = pathlib.Path(store())
    pth.mkdir(parents=True, exist_ok=True)
    return str(pth)


def write(obj, path, disk=False):
    with lock:
        if disk or Cache.disk:
            ppath = store(path)
            cdir(ppath)
            with open(ppath, "w", encoding="utf-8") as fpt:
                dump(obj, fpt, indent=4)
        Cache.update(path, obj)
        return path


def __dir__():
    return (
        'Cache',
        'find',
        'last',
        'read',
        'write'
    )
