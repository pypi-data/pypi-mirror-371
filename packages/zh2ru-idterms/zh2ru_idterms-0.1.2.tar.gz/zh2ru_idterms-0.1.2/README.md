
# zh2ru-idterms

中文证件（护照 / 驾驶证）用名词的中俄对照库（SQLite 版）。  
内置 `terms.db` 数据库，开箱即用：**地理名词、机构名称（按证件类型区分）、中文姓名拼音转俄文（帕拉第乌斯转写）**。

> 0.1.2 版本特性：
> - 全部存入数据库，不再额外提供Palladius转写，之前版本有错误。

---

## 安装

```bash
pip install zh2ru-idterms
```

无需任何 CLI、无需传入数据库路径，包内已自带 `terms.db`。

---

## 快速使用

```python
from zh2ru_idterms import (
    get_place_path,
    find_surname_pinyin,
    to_palladius_given,
    translate_person_name,
    find_org,
)

# 1) 地理名词：支持简称或全称
print(get_place_path(province_zh="浙江省"))      # {'province': 'Чжэцзян'}
print(get_place_path(province_zh="浙江"))        # {'province': 'Чжэцзян'}
print(get_place_path(city_zh="宁波市"))          # {'province': 'Чжэцзян', 'city': 'Нинбо'}
print(get_place_path(city_zh="宁波", district_zh="鄞州区"))
# -> {'province': 'Чжэцзян', 'city': 'Нинбо', 'district': 'Иньчжоу'}

# 2) 姓氏：拼音 → 俄文
print(find_surname_pinyin("zhang"))              # чжан

# 3) 名（给定拼音 → Palladius 转写）
print(to_palladius_given("xiaoming"))            # сяомин

# 4) 中文姓名（拼音形式） → 俄文全名
print(translate_person_name("zhang", "xiaoming"))# Чжан Сяомин

# 5) 机构名称（按证件类型）
print(find_org("国家移民管理局", doc_type="passport"))
# {'name_zh': '国家移民管理局', 'name_ru': 'Государственное управление по делам иммиграции КНР', ...}
```

### `get_place_path` 参数说明

- `province_zh`: 省/自治区/直辖市（**全称或简称**都可，如“浙江省”/“浙江”，“广西壮族自治区”/“广西”）
- `city_zh`: 地级市（可写“宁波市”或“宁波”）
- `district_zh`: 区/县（如“鄞州区”“鄞州”）

支持**部分层级**：
- 只给 `province_zh`：返回 `{province: ...}`
- 给 `city_zh` 不给 `province_zh`：全库搜索城市，若唯一命中，返回省市
- 只给 `district_zh`：全库搜索区县，若唯一命中，返回省市区

> 若同名多地命中（模糊情况），将返回 `None`，请提供更精确的上级以消歧。

---

## API 一览（保持兼容旧用法）

- `get_place_path(province_zh=None, city_zh=None, district_zh=None) -> Optional[dict]`
- `find_surname_pinyin(pinyin: str) -> Optional[str]`
- `to_palladius_given(pinyin_text: str) -> str`
- `translate_person_name(surname_pinyin: str, given_pinyin: str) -> str`
- `find_org(name_zh: str, doc_type: str = "passport", region_zh: Optional[str] = None) -> Optional[dict]`

> 机构：`doc_type` 建议使用 `"passport"` 或 `"driving_licence"`。

---

## 数据库说明

包内置 `data/terms.db`，结构包含：

- `geo_province / geo_city / geo_district`
- `authority_org`（机构，按 `doc_type` 区分）
- `surname_pinyin_rule`（姓：拼音→俄文）
- （可选）`surname_rule / givenname_rule / name_exception`（未必在你的数据集中启用）

> 运行时会检测 `aliases_zh` 列是否存在；不存在时**不影响使用**，仅降级为 `name_zh LIKE` 模糊匹配。

---

## 扩展与自定义数据

如果你有自己的数据导入，请**在外部工具中**导入同名表到你的 SQLite，再替换包内 `terms.db` 即可。  
（或在你的程序中通过 `importlib.resources.files('zh2ru_idterms')/'data/terms.db'` 找到路径，进行覆盖。）

---

## 版本记录

- **0.1.1**
  - 省份/自治区简称支持（浙江/广西等）
  - 兼容无 `aliases_zh` 列的数据库（自动降级匹配）
- 0.1.0
  - 初始版本，内置 `terms.db` 与核心 API

---

## 许可证

MIT
