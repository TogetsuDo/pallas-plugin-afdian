# Afdian community plugin (`pallas-afdian`)

- 保持 L1：仅导入 `pallas.api.*`、NoneBot、FastAPI 与 Pydantic。
- 所有持久化数据使用 `plugin_data_dir("afdian")`。
- 安装目录名必须是 `afdian/`；本仓可 rsync / clone 到 `local/plugins/afdian`。
