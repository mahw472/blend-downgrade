# -*- coding: utf-8 -*-
"""插件偏好设置。"""

import bpy

BRAND_NAME = "模型派"
BRAND_URL = "https://mxpai.net"


class BlendDowngradePreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    converter_path: bpy.props.StringProperty(
        name="转换器路径",
        description="mxmodelopt.exe 的完整路径。留空则自动在插件 bin 目录、"
                    "环境变量 MXPAI_MXMODELOPT_DIR 与开发目录中查找",
        subtype="FILE_PATH",
        default="",
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "converter_path")

        layout.separator()
        box = layout.box()
        box.label(text="%s (MXPai)" % BRAND_NAME, icon="URL")
        box.label(text="更多模型素材与三维工具：")
        button = box.operator("wm.url_open", text=BRAND_URL, icon="URL")
        button.url = BRAND_URL
