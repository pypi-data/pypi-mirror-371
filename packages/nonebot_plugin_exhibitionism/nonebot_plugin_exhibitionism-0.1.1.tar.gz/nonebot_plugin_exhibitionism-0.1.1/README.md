<div align="center">

# nonebot-plugin-exhibitionism

_✨ 让我看看！！赛博露阴癖，将你的代码展示到群聊 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/hlfzsi/nonebot-plugin-exhibitionism.svg" alt="license">
</a>
<a href="https://pypi.org/project/nonebot-plugin-exhibitionism/">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-exhibitionism.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">

</div>

## 📖 介绍

这是一个让你的代码被群友看光光的 NoneBot2 插件！🔍

当你想要展示某个指令的源码实现时，只需要使用 `/see` 命令，插件会自动找到对应的处理器并将其源码以精美的代码图片形式展示出来。非常适合：

- 代码学习和交流
- 调试和问题排查
- 向群友炫耀你的代码（雾）
- 满足赛博露阴癖

## 💿 安装

### 使用 nb-cli 安装

在 NoneBot2 项目的根目录下打开命令行，输入以下指令即可安装：

```bash
nb plugin install nonebot-plugin-exhibitionism
```

### 使用包管理器安装

```bash
pip install nonebot-plugin-exhibitionism
```

### 使用 uv 安装

```bash
uv add nonebot-plugin-exhibitionism
```

然后在 NoneBot2 项目的 `pyproject.toml` 文件中的 `[tool.nonebot]` 部分添加：

```toml
plugins = ["nonebot_plugin_exhibitionism"]
```

## 🎉 使用

### 指令表


|       指令       |  权限  | 需要@ |   范围   |        说明        |
| :---------------: | :----: | :---: | :-------: | :----------------: |
| `/see [目标指令]` | 所有人 |  否  | 群聊/私聊 | 查看指定指令的源码 |

### 效果预览

发送指令：

```
/see /帮助
```

插件会：

1. 自动匹配到对应的处理器
2. 获取处理器的源码
3. 使用 Pygments 进行语法高亮
4. 生成精美的代码图片并发送

## ⚙️ 配置

本插件无需额外配置，安装即可使用。

### 配置项

- 代码风格：使用 `one-dark` 主题
- 字体大小：22px
- 包含行号显示
- 自动背景色处理

## 🔧 工作原理

1. **命令解析**：支持通过 Alconna 和传统 Matcher 两种方式匹配指令
2. **处理器查找**：模仿 Nonebot 事件处理流程，找到匹配的目标
3. **源码提取**：使用 `inspect` 模块获取处理器函数的源码
4. **代码渲染**：使用 Pygments 进行语法高亮，生成高质量代码图片
5. **图片发送**：将生成的图片通过 UniMessage 发送到群聊

## 🤝 贡献

欢迎提交 issue 和 pull request！

## 📄 许可证

本项目采用 AGPL-3 许可证。
