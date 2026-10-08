# -*- coding: utf-8 -*-
"""Blend 版本转换器 —— 让低版本 Blender 打开高版本 .blend。

低版本 Blender 无法直接打开高版本 .blend：文件头中的版本号高于本机版本会被拒绝，
且新增的数据结构无法解析。本插件先用 mxmodelopt 转换器把源文件转成低版本可用的副本，
再打开该副本。

注意：转换只搬运「模型资产」（网格 / 材质 / 贴图 / 骨架 / 动画 / 变换），
相机、灯光、曲线、修改器、渲染设置等不会保留。
"""

bl_info = {
    "name": "Blend 版本转换器",
    "author": "模型派 (MXPai)",
    "version": (1, 0, 0),
    "blender": (2, 83, 0),
    "location": "3D 视图标题栏右上角（按钮）",
    "description": "把高版本 .blend 转为低版本可用的副本后打开（仅保留模型资产）",
    "warning": "仅保留模型资产：网格 / 材质 / 贴图 / 骨架 / 动画",
    "doc_url": "https://mxpai.net",
    "support": "COMMUNITY",
    "category": "Import-Export",
}

import bpy

from . import icons
from . import operators
from . import preferences

_classes = (
    preferences.BlendDowngradePreferences,
    operators.OpenDowngradedBlend,
)

_register_classes, _unregister_classes = bpy.utils.register_classes_factory(_classes)


def register():
    icons.register()
    _register_classes()
    bpy.types.VIEW3D_HT_header.append(operators.draw_toolbar_button)


def unregister():
    bpy.types.VIEW3D_HT_header.remove(operators.draw_toolbar_button)
    _unregister_classes()
    icons.unregister()


if __name__ == "__main__":
    register()
