<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-bfvgrouptools

_✨ NoneBot 插件简单描述 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/owner/nonebot-plugin-template.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-template">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-template.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">

</div>

## 📖 介绍

为 BFV 玩家提供状态查询、封禁记录查询，以及自动处理加群请求等功能的群管理插件

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-bfvgrouptools

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-bfvgrouptools

</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-bfvgrouptools

</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-bfvgrouptools

</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-bfvgrouptools

</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_template"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

|     配置项     | 必填 | 默认值 |           说明           |
| :------------: | :--: | :----: | :----------------------: |
| ALLOWED_GROUPS |  是  |   无   | 启用群申请自动通过的群号 |

## 🎉 使用

### 指令表

|  指令   | 权限 | 需要@ | 范围 |              说明               |
| :-----: | :--: | :---: | :--: | :-----------------------------: |
| player= |  无  |  否   | 群聊 | 查询玩家 bfban 和 bfvrobot 状态 |
|   pb=   |  无  |  否   | 群聊 |          查询屏蔽原因           |
