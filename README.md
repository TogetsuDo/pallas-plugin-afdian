<p align="center">
  <img src="./assets/brand-avatar.png" width="220" height="220" alt="牛牛爱发电">
</p>

<h1 align="center">牛牛爱发电 afdian</h1>

<p align="center">通过爱发电为画画等功能提供可选额外额度与群共享额度。</p>

<p align="center">
  <img alt="社区插件" src="https://img.shields.io/badge/%E7%A4%BE%E5%8C%BA%E6%8F%92%E4%BB%B6-4B5563">
  <img alt="版本" src="https://img.shields.io/badge/%E7%89%88%E6%9C%AC-v0.1.1-2563EB">
</p>

## 安装方式

可在控制台插件商店安装，也可按社区插件目录放入 `local/plugins/afdian/`（目录名须与插件 ID `afdian` 一致，与仓库名无关）。

```bash
git clone https://github.com/TogetsuDo/pallas-plugin-afdian.git local/plugins/afdian
```

装好后重启 Bot（或热加载社区插件）。未启用时，画画等只走免费日限，**不会**出现付费引导文案。

## 怎么使用

- `牛牛爱发电` / `画画额度说明`：回复支持页链接与宣传图。
- `画画额度`：查看个人额外额度或本群共享额度。
- `绑定画画共享额度` / `解绑画画共享额度`：在群内绑定或解除共享额度池。
- `用户额度` / `用户额度设置`：超管私聊查看或设置余额。

> 详细用法、限制条件和可用范围以帮助为主。拒画文案只用「免费次数 / 额外额度 / 共享额度」等中性说法，不会在拒画时硬推爱发电口令。

## 命令权限

| 功能 | 默认等级 |
| --- | --- |
| `牛牛爱发电` / `画画额度说明` | 所有人 |
| `画画额度` | 所有人 |
| `绑定画画共享额度` / `解绑画画共享额度` | 所有人 |
| `用户额度` / `用户额度设置` | 超级用户 |

## 配置项

> 可在控制台 **插件 → 牛牛爱发电** 中修改；落盘键前缀为 `PALLAS_AFDIAN_*`。旧键 `PALLAS_IMAGE_AFDIAN_*` / `DRAW_AFDIAN_WEBHOOK_TOKEN` 仅在新键为空时兼容读取。

### 基础（必做）

| 配置项 | 说明 |
| --- | --- |
| `pallas_afdian_enabled` | 是否启用爱发电额外额度 |
| `pallas_afdian_webhook_token` | Webhook 校验 token；须与回调 URL 中的 `token` 完全一致 |

两项都配好后插件才算就绪，画画等才可能扣额外额度。

### Webhook

开发者文档与后台（`afdian` / `ifdian` 域名通常互通）：

| 用途 | URL |
| --- | --- |
| 开发者文档（API / Webhook） | https://guide.afdian.com/creator/developer |
| 开发者后台 | https://afdian.net/dashboard/dev |

Bot 需公网可访问（或经反代）。在开发者后台配置通知地址（`TOKEN` 换成 WebUI 中的口令）：

```text
https://你的域名/afdian/webhook?token=TOKEN
https://你的域名/pallas-image/afdian/webhook?token=TOKEN
```

第二条为旧路径，可继续使用。订单留言需能解析 QQ（如 `QQ:123456789`），否则无法入账。数据默认在 `data/afdian/`；若仅有旧 `data/draw/pallas_afdian_*.json`，启动时会自动迁移。

### 额度方案

匹配顺序：方案金额额度 → 方案额度 → 默认发放额度。

| 配置项 | 说明 |
| --- | --- |
| `pallas_afdian_default_credits` | 未命中方案映射时的默认次数 |
| `pallas_afdian_plan_credits_json` | 按方案 ID 发放，如 `{"方案ID": 30}` |
| `pallas_afdian_plan_amount_credits_json` | 按方案 ID + 金额的嵌套 JSON |
| `pallas_afdian_plan_amount_credits_json_path` | 同上内容的文件路径（如 `1.json`） |

文件查找：绝对路径 → 仓库根相对路径 → `data/afdian/` → `data/draw/` → `data/pallas_image/`。

**方案 ID（`plan_id`）怎么拿**：以订单字段为准（见[官方说明](https://guide.afdian.com/creator/developer)）；自选金额订单常为空，只能走默认额度。后台不一定有显眼的「复制方案 ID」，较稳妥的做法：

1. 配好 Webhook 后下一笔真实订单（可用小额），从回调 JSON 抄 `data.order.plan_id` 与 `total_amount`（推荐）。
2. 若下单页形如 `…/order/create?plan_id=…`，可从查询参数抄。
3. 用开发者后台的 API Token 调「查订单」看历史订单里的 `plan_id`。「查看方案」接口需要已经知道 ID，不能从零枚举。

`/item/<一段 id>` 有时碰巧等于 `plan_id`，但并非官方保证；**与 Webhook 不一致时以回调 / 查订单为准。**

金额键建议两位小数，与订单 `total_amount` 一致，例如：

```json
{
  "0d42421849bf11f180df52540025c377": {
    "1.20": 15,
    "5.00": 65,
    "10.00": 150
  }
}
```

### 宣传与群共享

| 配置项 | 说明 |
| --- | --- |
| `pallas_afdian_promo_page_url` | 「牛牛爱发电」回复中的支持页链接 |
| `pallas_afdian_promo_image_path` | 宣传图本地路径/文件名（优先；查找目录同额度文件） |
| `pallas_afdian_promo_image_url` | 宣传图 http(s) 地址（无本地图时用） |
| `pallas_afdian_group_billing_enabled` | 是否启用群共享额度 |
| `pallas_afdian_group_billing_group_ids` | 启用共享的群号列表；空列表表示全部群可绑 |

## 排障

| 现象 | 处理 |
| --- | --- |
| 画画次数用尽仍无额外额度路径 | 检查是否启用、Token 是否非空；未就绪时只会提示明天再来。 |
| 下单后额度不加 | 看 Webhook 是否打到 Bot、URL 中 `token` 是否一致；留言是否含可解析 QQ。 |
| 方案映射不生效 | 用回调里的 `plan_id` / `total_amount` 核对 JSON；自选金额可能无 `plan_id`。 |
| `牛牛爱发电` 无图无链接 | 配置支持页或宣传图路径/URL；确认本地文件能在查找目录中找到。 |
| 群共享绑不上 | 开启群共享；绑定人需已有额外额度（或曾有过额度）。 |

## 实现

源码位置：

- 插件入口：[`__init__.py`](./__init__.py)
- 配置定义：[`config.py`](./config.py)
- 命令处理：[`handlers.py`](./handlers.py)
- 订单回调：[`webhook.py`](./webhook.py)
- 额度存储：[`store.py`](./store.py)
- 对外接口：[`api.py`](./api.py)

实现要点：

- 对画画等插件为软依赖；未安装或未启用时对方不得出现付费文案。
- Webhook 做订单幂等入账；群共享将计费 QQ 解析到绑定人。
- 路径加载时模块名可能是 `local.plugins.afdian`，软依赖按接口特征查找。

## 更新日志

版本变更见 [`CHANGELOG.md`](./CHANGELOG.md)；也可在控制台插件商店弹窗的「更新日志」分栏查看。

## 相关链接

- [社区插件索引](https://github.com/PallasBot/community-plugin-index)
- [社区插件商店说明](https://github.com/PallasBot/Pallas-Bot/blob/dev/docs/guide/community-plugin-store.md)
- [爱发电开发者文档](https://guide.afdian.com/creator/developer)
- [爱发电开发者后台](https://afdian.net/dashboard/dev)
