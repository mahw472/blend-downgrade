# -*- coding: utf-8 -*-
"""插件的自定义图标：预加载 icons 目录下的图片，用 get_icon() 取 icon_id。

替换 icons 目录下的同名 PNG 即可换图标，文件名即图标名。
"""

import os

import bpy
import bpy.utils.previews

_IMAGE_EXTS = (".png", ".jpg", ".jpeg")

_preview_collection = None

# icon_id 仍为 0 时补一次 reload（启用插件时可能还没有 GPU 上下文）
_reload_pending = False


def load_icons():
    """扫描本目录下所有图片并预加载；重复调用会先清掉旧的集合。"""
    global _preview_collection, _reload_pending
    clear_icons()
    _preview_collection = bpy.utils.previews.new()
    directory = os.path.dirname(__file__)
    for entry in sorted(os.listdir(directory)):
        path = os.path.join(directory, entry)
        name, ext = os.path.splitext(entry)
        if ext.lower() in _IMAGE_EXTS and os.path.isfile(path):
            _preview_collection.load(name.lower(), path, "IMAGE")
    _reload_pending = True


def clear_icons():
    global _preview_collection
    if _preview_collection is not None:
        _preview_collection.clear()
        bpy.utils.previews.remove(_preview_collection)
        _preview_collection = None


def get_icon(name) -> int:
    """取图标的 icon_id；尚未加载或图标不存在时返回 0。"""
    global _reload_pending
    if _preview_collection is None:
        load_icons()
    icon = _preview_collection.get(name.lower()) if _preview_collection is not None else None
    if icon is None:
        return 0
    if icon.icon_id == 0 and _reload_pending:
        _reload_pending = False
        icon.reload()
    return icon.icon_id


def register():
    load_icons()


def unregister():
    clear_icons()
