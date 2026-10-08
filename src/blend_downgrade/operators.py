# -*- coding: utf-8 -*-
"""「降级打开高版本 .blend」操作符。"""

import os

import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper

from . import blend_reader
from . import icons
from . import preferences


def _converter_path_preference(context):
    """取本插件偏好设置中的转换器路径；偏好未注册时返回空串。"""
    addon = context.preferences.addons.get(__package__)
    preferences = getattr(addon, "preferences", None)
    return getattr(preferences, "converter_path", "") if preferences else ""


class OpenDowngradedBlend(bpy.types.Operator, ImportHelper):
    """把高版本 .blend 转为低版本可用的副本，然后打开该副本"""

    bl_idname = "blend_downgrade.open_high_blend"
    bl_label = "转换并打开高版本 .blend"
    bl_options = {"REGISTER"}

    filename_ext = ".blend"
    filter_glob: StringProperty(default="*.blend", options={"HIDDEN"})

    def execute(self, context):
        source = bpy.path.abspath(self.filepath)
        if not os.path.isfile(source):
            self.report({"ERROR"}, "文件不存在: %s" % source)
            return {"CANCELLED"}

        current = blend_reader.current_version_code()
        version, _ = blend_reader.read_blend_version(source)

        # 源文件版本不高于本机时 Blender 自己就能打开，不做多余的有损转换
        # （压缩文件也适用，Blender 会自行解压）
        if version is not None and version <= current:
            self.report({"INFO"}, "文件版本 %d，本机可直接打开" % version)
            bpy.ops.wm.open_mainfile(filepath=source)
            return {"FINISHED"}

        converter = blend_reader.find_converter(_converter_path_preference(context))
        if converter is None:
            self.report({"ERROR"}, "找不到转换器 mxmodelopt.exe，请在插件偏好设置中指定路径")
            return {"CANCELLED"}

        # 预检：读不出网格说明无法解析，此时转换器会「成功」地产出空文件
        meshes = blend_reader.count_meshes(converter, source)
        if not meshes:
            self.report({"ERROR"}, "源文件无法解析（压缩格式或暂不支持的结构），已中止")
            return {"CANCELLED"}

        directory = os.path.dirname(source)
        stem = os.path.splitext(os.path.basename(source))[0]
        target = os.path.join(directory, "%s_%d.blend" % (stem, blend_reader.TARGET_VERSION))

        succeeded, message = blend_reader.convert(converter, source, target)
        if not succeeded:
            self.report({"ERROR"}, message)
            return {"CANCELLED"}

        self.report({"WARNING"}, "已转为低版本格式并打开：%s（仅保留模型资产）· 由 %s 提供"
                    % (os.path.basename(target), preferences.BRAND_NAME))
        bpy.ops.wm.open_mainfile(filepath=target)
        return {"FINISHED"}


def draw_toolbar_button(self, context):
    """在 3D 视图标题栏右上角绘制转换入口按钮（图标式，悬停显示提示）。"""
    icon_value = icons.get_icon("convert")
    if icon_value:
        self.layout.operator(OpenDowngradedBlend.bl_idname, text="", icon_value=icon_value)
    else:
        self.layout.operator(OpenDowngradedBlend.bl_idname, text="", icon="FILE_BLEND")
