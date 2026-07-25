# 牛牛爱发电（afdian）

可选社区插件：通过爱发电订单为画画等功能提供**额外额度**与可选**群共享额度**。

安装目录须为 `local/plugins/afdian/`（与 `PLUGIN_ID` 一致）。

```bash
# 推荐：克隆到插件目录
git clone https://github.com/TogetsuDo/pallas-afdian.git local/plugins/afdian

# 或从本仓同步到站点
rsync -a --delete --exclude .git/ /path/to/pallas-afdian/ /path/to/Pallas-Bot/local/plugins/afdian/
```

装好后重启 Bot（或热加载社区插件）。未启用时，画画只走免费日限，**不会**出现付费引导文案。

包内 `assets/icon.png`（及 cover / avatar）供控制台商店与插件列表展示。

---

## 怎么配置（推荐走 WebUI）

打开控制台 → **插件** → **牛牛爱发电**，按分组填写后保存。

### 1. 基础（必做）

| 界面项 | 作用 |
| --- | --- |
| **启用爱发电额度** | 打开总开关 |
| **Webhook Token** | 自定一串校验口令（不要用空）；须与爱发电后台回调 URL 里的 `token` **完全一致** |

两项都配好后插件才算「就绪」，画画才可能扣额外额度。

### 2. 爱发电开发者入口与 Webhook

官方文档与后台（域名 `afdian` / `ifdian` 通常互通，打不开可换一个）：

| 用途 | URL |
| --- | --- |
| 开发者文档（API / Webhook） | https://guide.afdian.com/creator/developer |
| 开发者后台（填 Webhook、查 user_id / API Token） | https://afdian.net/dashboard/dev |

Bot 需能被公网访问（或经反代）。在开发者后台配置通知地址，二选一（`TOKEN` 换成你在 WebUI 填的口令）：

```text
https://你的域名/afdian/webhook?token=TOKEN
https://你的域名/pallas-image/afdian/webhook?token=TOKEN
```

第二条是旧路径，继续用也行。

**订单留言**里要能解析出 QQ，例如：`QQ:123456789`（赞助人填留言；解析失败则无法入账）。

入账数据默认在 `data/afdian/`。若以前只有 `data/draw/pallas_afdian_*.json`，启动时会自动迁到新目录。

### 3. 额度方案（按需）

每次成功回调会给对应用户加「额外次数」。匹配顺序：

1. **方案金额额度**（方案 ID + 实付金额）→ 最精确  
2. **方案额度**（只按方案 ID）  
3. **默认发放额度**（上面都没命中时用，默认 10）

| 界面项 | 说明 |
| --- | --- |
| **默认发放额度** | 兜底次数，例如 `65` |
| **方案额度 JSON** | 例：`{"方案ID": 30}` |
| **方案金额额度 JSON** | 直接贴嵌套 JSON；或改用下方「文件」 |
| **方案金额额度文件** | 文件名或相对路径，如 `1.json` |

文件查找顺序：绝对路径 → 仓库根相对路径 → `data/afdian/` → `data/draw/` → `data/pallas_image/`。  
以前放在 `data/draw/1.json` 的映射可以继续写 `1.json`，不必搬文件。

#### 方案 ID（`plan_id`）怎么拿

插件按订单里的 **`plan_id`** 做映射（见[官方字段说明](https://guide.afdian.com/creator/developer)）。**自选金额**订单该字段常为空，只能走「默认发放额度」。

爱发电后台**不一定**有「复制方案 ID」的显眼入口；社区里常见、也较稳妥的做法是：

1. **先配好 Webhook，下一笔真实订单（可用小额），从回调里抄**（推荐）  
   看 Bot 日志或抓包 JSON：`data.order.plan_id`，以及 `total_amount`（用来填金额档）。  
   很多站点就是这样拿到 ID 再写进额度映射的；不必猜 URL。

2. **下单页地址栏里的查询参数**  
   若打开赞助档后跳到类似  
   `https://afdian.net/order/create?plan_id=……&product_type=…`  
   则 `plan_id=` 后面那一段就是。  
   （部分分享链接也会带这个参数。）

3. **开放 API 查历史订单**  
   在[开发者后台](https://afdian.net/dashboard/dev)拿到 `user_id` 与 API Token，按[文档](https://guide.afdian.com/creator/developer)调用「查订单」；已有订单的 `plan_id` 可直接复用。  
   注意：文档里的「查看方案」接口需要**已经知道** `plan_id`，不能用来从零枚举。

`/item/<一段 id>` 这类商品页路径，**有时**与 `plan_id` 相同，但爱发电未把它写成通用规则；**若与 Webhook 不一致，一律以回调 / 查订单结果为准。**

嵌套 JSON 示例（外层为订单里的 `plan_id`，内层为金额 → 次数）：

```json
{
  "0d42421849bf11f180df52540025c377": {
    "1.20": 15,
    "5.00": 65,
    "10.00": 150
  }
}
```

金额键建议写成两位小数（与订单字段 `total_amount` 一致）。

### 4. 宣传（「牛牛爱发电」回复）

用户发 `牛牛爱发电` / `画画额度说明` 时回复支持页与配图。

| 界面项 | 说明 |
| --- | --- |
| **支持页链接** | 爱发电商品/主页 URL |
| **宣传图本地路径** | 如 `aifadian.jpg`（优先）；查找目录同「额度文件」 |
| **宣传图 URL** | 本地图找不到时可用 http(s) 图床地址 |

本地图与 URL **有本地用本地**；两者都空则只回链接或提示未配置。

### 5. 群共享额度（可选）

| 界面项 | 说明 |
| --- | --- |
| **启用群共享额度** | 打开后，群内可把额度绑到某个 QQ 池 |
| **共享额度群号列表** | JSON 数组，如 `[123456]`；**留空 `[]` 表示所有群都可绑** |

群内流程：有额外额度的用户发 `绑定画画共享额度` → 同群成员画画可走该共享池；绑定人可 `解绑画画共享额度`。

---

## 配置项一览（环境变量）

WebUI 保存后写入 `data/pallas_config/webui.json`（优先级最高）。键名如下，也可手写进 `pallas.toml` / `.env`（不推荐与 WebUI 重复维护）。

| 键 | 对应界面 |
| --- | --- |
| `PALLAS_AFDIAN_ENABLED` | 启用爱发电额度 |
| `PALLAS_AFDIAN_WEBHOOK_TOKEN` | Webhook Token |
| `PALLAS_AFDIAN_DEFAULT_CREDITS` | 默认发放额度 |
| `PALLAS_AFDIAN_PLAN_CREDITS_JSON` | 方案额度 JSON |
| `PALLAS_AFDIAN_PLAN_AMOUNT_CREDITS_JSON` | 方案金额额度 JSON |
| `PALLAS_AFDIAN_PLAN_AMOUNT_CREDITS_JSON_PATH` | 方案金额额度文件 |
| `PALLAS_AFDIAN_PROMO_PAGE_URL` | 支持页链接 |
| `PALLAS_AFDIAN_PROMO_IMAGE_PATH` | 宣传图本地路径 |
| `PALLAS_AFDIAN_PROMO_IMAGE_URL` | 宣传图 URL |
| `PALLAS_AFDIAN_GROUP_BILLING_ENABLED` | 启用群共享额度 |
| `PALLAS_AFDIAN_GROUP_BILLING_GROUP_IDS` | 共享额度群号列表 |

旧键 `PALLAS_IMAGE_AFDIAN_*`、`DRAW_AFDIAN_WEBHOOK_TOKEN`：仅当对应**新键为空**时仍兼容读取。新装站点请只用 `PALLAS_AFDIAN_*`。

---

## 口令

| 口令 | 说明 |
| --- | --- |
| `牛牛爱发电` / `画画额度说明` | 支持页 + 配图 |
| `画画额度` | 查看额外额度 / 共享池 |
| `绑定画画共享额度` / `解绑画画共享额度` | 群共享绑定 |
| `用户额度` / `用户额度设置` | 超管查看/设置余额（私聊） |

拒画文案只用「免费次数 / 额外额度 / 共享额度」等中性说法，**不会**在拒画时硬推「爱发电」广告。

---

## 自检清单

1. WebUI 已开「启用」且 Token 非空  
2. 爱发电后台 Webhook URL 含同一 `token`，公网能打到 Bot  
3. 测一笔订单，留言带 `QQ:…`，再发 `画画额度` 看余额是否增加  
4. （可选）`牛牛爱发电` 能出图/链接；免费次数用尽后画画会扣额外额度  

---

## 给其他插件

```python
from afdian import api
if api.is_ready():
    ...
```

路径加载时模块名可能是 `local.plugins.afdian`；官方画画等通过软依赖按接口特征查找，不依赖短包名。

## 单测

在已安装 Pallas 依赖的环境中：

```bash
python tests/run_unit.py
```
