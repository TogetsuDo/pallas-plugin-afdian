# Changelog

## 0.1.6

- 声明 `afdian.quota` / `afdian.promo` LLM 工具。

## 0.1.5

- `metadata.extra.help_tag`：帮助图分组为「工具」(tool)。

## 0.1.4

- 启动迁移：若 `data/draw` 中额度/绑定文件比 `data/afdian` 更新，则再同步一次，避免升级站点漏迁新订单。

## 0.1.3

- `画画额度` 增加别名 `画画次数`。
- 宣传图本地路径按文件字节发送（不再依赖 `file://`）；配置路径可解析绝对路径、仓库相对路径、文件名（在 `data/afdian` / `data/draw` / `data/pallas_image` 查找）。

## 0.1.2

- 修正商店作者角标：移除误用为作者头像的 `assets/avatar.png` 与索引 `avatar` 字段（角标改回 GitHub 作者头像）。
- 保留 `icon` / `cover` / `brand-avatar` 作为插件卡片与 README 配图。

## 0.1.1

- 仓库更名为 `pallas-plugin-afdian`。
- README 对齐社区插件模版；补充 Webhook / 方案 ID 获取说明与中文配置标签。
- 宣传图支持本地路径；包内 `assets` 图标。

## 0.1.0

- 从 Pallas Draw 插件拆分 Afdian 额外额度、订单回调与群共享额度功能。
- WebUI 中文标签与分组；兼容旧 `PALLAS_IMAGE_AFDIAN_*` 配置键。
