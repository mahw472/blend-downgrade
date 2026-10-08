# -*- coding: utf-8 -*-
"""高版本 .blend 的版本探测，以及调用 mxmodel 转换器做降级转换。

本模块只依赖 bpy 与 Python 标准库，不涉及界面，便于独立测试。
"""

import gzip
import os
import subprocess
import sys

import bpy

# .blend 文件头：'BLENDER'(7) + 指针宽度(1) + 字节序(1) + 版本号(3)
HEADER_SIZE = 12
GZIP_MAGIC = b"\x1f\x8b"
ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"

# 转换器可执行文件名
_CONVERTER_NAMES = ("mxmodelopt.exe",)

# 输出格式固定为 2.83
TARGET_VERSION = 283

# Windows：不为子进程创建控制台窗口
_CREATE_NO_WINDOW = 0x08000000


def current_version_code():
    """本机 Blender 版本 -> 三位数字，例如 2.83 -> 283、4.5 -> 405。"""
    version = bpy.app.version
    return version[0] * 100 + version[1]


def find_converter(explicit_path=""):
    """定位转换器可执行文件，找不到返回 None。

    查找顺序：偏好设置中的显式路径 -> 插件 bin 目录 -> 环境变量
    ``MXPAI_MXMODELOPT_DIR``。
    """
    if explicit_path:
        path = bpy.path.abspath(explicit_path)
        return path if os.path.isfile(path) else None

    here = os.path.dirname(__file__)
    directories = [os.path.join(here, "bin")]
    env_dir = os.environ.get("MXPAI_MXMODELOPT_DIR")
    if env_dir:
        directories.append(env_dir)

    for directory in directories:
        for name in _CONVERTER_NAMES:
            path = os.path.join(directory, name)
            if os.path.isfile(path):
                return path
    return None


def _parse_version(raw):
    """b'283' -> 283；非法值返回 None。"""
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError:
        return None
    if not text.isdigit():
        return None
    value = int(text)
    # 合理区间 2.50 ~ 9.99，超出视为解析失败
    if value < 250 or value > 999:
        return None
    return value


def read_blend_version(path):
    """读取 .blend 的版本号，返回 ``(version_code, compressed)``。

    ``version_code`` 为 int（如 283），无法判定时为 None；``compressed`` 表示文件是否被压缩。

    说明：gzip 可直接解压出文件头用于判定；zstd 在 Python 标准库中无法解压，
    版本未知；Blender 5.0 起文件头变为变长，此处同样可能判定失败。
    判定失败一律按「需要转换」处理，不会误判为可直接打开。
    """
    try:
        with open(path, "rb") as fp:
            head = fp.read(HEADER_SIZE)
            if head[:7] == b"BLENDER":
                return _parse_version(head[9:12]), False
            if head[:2] == GZIP_MAGIC:
                with gzip.open(path, "rb") as gz:
                    inner = gz.read(HEADER_SIZE)
                if inner[:7] == b"BLENDER":
                    return _parse_version(inner[9:12]), True
                return None, True
            if head[:4] == ZSTD_MAGIC:
                return None, True
    except (IOError, OSError):
        pass
    return None, None


def _run(converter, args):
    """执行转换器，返回 ``(returncode, 合并后的输出文本)``。"""
    command = [converter] + list(args)
    kwargs = {}
    if sys.platform == "win32":
        kwargs["creationflags"] = _CREATE_NO_WINDOW
    try:
        completed = subprocess.run(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, **kwargs)
    except OSError as error:
        return -1, str(error)
    output = completed.stdout.decode("utf-8", "replace") if completed.stdout else ""
    return completed.returncode, output


def _parse_info_count(text, key):
    """从 ``info`` 命令输出中取形如 ``meshes    = 1`` 的计数值，取不到返回 None。"""
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith(key):
            continue
        parts = line.split("=")
        if len(parts) != 2:
            continue
        try:
            return int(parts[1].strip())
        except ValueError:
            return None
    return None


def count_meshes(converter, path):
    """用转换器的 ``info`` 命令预检源文件可读性，返回网格数量；失败返回 None。

    转换器在无法解析的输入上会「成功」地输出空模型，因此转换前必须先做这项预检。
    """
    code, output = _run(converter, ("info", "-i", path))
    if code != 0:
        return None
    return _parse_info_count(output, "meshes")


def _tail(text, limit=300):
    text = (text or "").strip()
    return text[-limit:] if len(text) > limit else text


def convert(converter, source, target):
    """把 ``source`` 转换为 ``target``，返回 ``(是否成功, 失败信息)``。"""
    code, output = _run(converter, ("convert", "-i", source, "-o", target))
    if code != 0:
        return False, "转换器返回 %d：%s" % (code, _tail(output))
    if not os.path.isfile(target) or os.path.getsize(target) == 0:
        return False, "转换器未生成有效文件：%s" % _tail(output)
    return True, ""
