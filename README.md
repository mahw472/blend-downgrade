# Blend 版本转换器

**让低版本 Blender 打开高版本 `.blend` 文件。**

同事/客户发来一个 Blender 4.5 存的 `.blend`，而你机器上只有 2.83、3.3 这类老版本 —— 直接打开会被拒绝。这个插件把源文件转成低版本可用的副本，然后自动打开它，**网格、材质、贴图、骨架、蒙皮权重、动画全部保留**。

由 [模型派 MXPai](https://mxpai.net) 开发并开源。

---

## 它解决什么问题

高版本 Blender 保存的 `.blend` 无法被低版本打开：文件头里的版本号高于本机版本会被直接拒绝，而且新增的数据结构低版本根本解析不了。这个插件不做完整工程迁移，只把**模型资产**搬过去 —— 这恰好是「拿到别人的模型想用起来」时真正需要的部分。

## 保留与丢失

| 保留 | 不保留 |
|---|---|
| 网格（含多边形，不强制三角化） | 相机、灯光 |
| 材质与节点树 | 曲线、文本、融球 |
| 贴图（含打包贴图） | 修改器、约束 |
| 骨架与蒙皮权重 | 渲染/世界设置 |
| 动画（动作、关键帧、NLA） | 场景、集合层级 |
| 物体变换层级 | 粒子、物理 |

## 环境要求

- **Windows x64** —— 内置的转换器是 Windows 程序（`bin/mxmodelopt.exe`）
- **Blender 2.83 LTS 及以上**，装在**低版本的那一侧**（用 2.83 打开 4.5 的文件，插件就装在 2.83 里）

## 安装

1. 到 [Releases](../../releases) 下载 `blend_downgrade-<版本>.zip`（**不要**下载 Source code）
2. Blender → `Edit` → `Preferences` → `Add-ons`
3. `Install from File...`，选中刚下载的 zip，勾选启用
4. 使用入口：**3D 视图标题栏右上角的图标按钮**

## 使用

点按钮 → 选一个高版本 `.blend` → 转换完成后自动打开。

- 转换结果输出在源文件同目录，命名为 `<原名>_283.blend`，原文件不会被改动
- 如果源文件版本**不高于**本机版本，插件会跳过转换直接打开（不做多余的有损转换）
- 转换器找不到时，可在插件偏好设置里手动指定 `mxmodelopt.exe` 路径

## 常见问题

**Q：转换后怎么少了相机和灯光？**
A：这是设计如此。插件只搬运模型资产，见上方「保留与丢失」。完整工程迁移不在目标范围内。

**Q：提示「源文件无法解析」？**
A：转换器读不出网格时会提前中止，避免产出一个空的 `.blend`。常见原因是文件结构属于尚未支持的范围。

**Q：能转成别的版本吗？**
A：目前输出固定为 2.83 格式（2.83 是 2.8x 系列里最新的 LTS，兼容面最广）。

**Q：macOS / Linux 能用吗？**
A：暂时不行，内置转换器是 Windows 程序。理论上可以用 WINE 或被其他平台的原生构建替换，欢迎 PR。

## 开发调试

把插件源码目录放进 Blender 的 addons 目录即可（用软链接更方便，改完重载插件就生效）：

```bash
git clone https://github.com/mahw472/blend-downgrade.git
# <Blender>/<版本>/scripts/addons/blend_downgrade  ->  本仓库的 src/blend_downgrade
```

转换器是**专有二进制**，不随本仓库发布，只随官方安装包分发。调试时用环境变量
`MXPAI_MXMODELOPT_DIR` 指向它所在的目录，或在插件偏好设置里直接指定
`mxmodelopt.exe` 的路径。

## 许可

插件源码（`src/`、`tools/`）以 **GPL-3.0-or-later** 发布，见 [LICENSE](LICENSE) ——
这与 Blender 插件生态保持一致。

`bin/` 下的转换器（`mxmodelopt.exe` 及其 DLL）是**专有组件**，不属于本仓库源码，
仅随官方发布的安装包分发，不适用 GPL。

「Blender」是 Blender Foundation 的商标。本项目的名称与图标均未使用 Blender
官方品牌元素，也不代表获得 Blender Foundation 的背书。

---

## English

**Blend Downgrader** — open newer `.blend` files in older Blender versions.

A colleague sends you a `.blend` saved in Blender 4.5, but you are stuck on 2.83 or 3.3.
This add-on converts the file into a copy your old Blender can open, **keeping meshes,
materials, textures, armatures, skin weights and animation**.

> **Preserved:** meshes (polygons kept), materials, textures, armatures, skin weights,
> animation, object transforms.
> **Not preserved:** cameras, lights, curves, modifiers, constraints, render settings.

**Requirements:** Windows x64 (the bundled converter is a Windows binary) and Blender 2.83 LTS
or newer — installed in the **older** Blender you want to open the file with.

**Install:** grab `blend_downgrade-<version>.zip` from [Releases](../../releases), then
`Edit → Preferences → Add-ons → Install from File...`. The button shows up at the top-right
of the 3D Viewport header.

**Development:** drop `src/blend_downgrade` into Blender's `scripts/addons/`. The converter is a
proprietary binary shipped only with official packages; point `MXPAI_MXMODELOPT_DIR` at it to test.

**License:** GPL-3.0-or-later for the add-on source. The converter binaries in `bin/` are
proprietary and distributed only with official release packages. "Blender" is a trademark of
the Blender Foundation; this project uses no official Blender branding and is not endorsed by
the Blender Foundation.

Made by [MXPai](https://mxpai.net).
