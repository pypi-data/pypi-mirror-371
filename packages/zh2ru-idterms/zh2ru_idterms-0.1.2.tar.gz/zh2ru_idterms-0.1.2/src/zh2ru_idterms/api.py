# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
import sqlite3
from functools import lru_cache
from importlib.resources import files


# =========================
# 基础：获取连接 / 小工具
# =========================

@lru_cache(maxsize=1)
def _conn() -> sqlite3.Connection:
    db_path = files("zh2ru_idterms") / "data" / "terms.db"
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def _one(sql: str, *args):
    return _conn().execute(sql, args).fetchone()

def _all(sql: str, *args):
    return _conn().execute(sql, args).fetchall()

# 去后缀（用于兼容简称/全称）
_SUFFIX_PAT = re.compile(
    r"(省|市|区|县|特别行政区|自治州|自治县|自治区|回族|维吾尔|壮族)$"
)

def _short_cn(name: str | None) -> str:
    if not name:
        return ""
    s = name.strip()
    # 多次剔除直到剔不动
    prev = None
    while s and s != prev:
        prev = s
        s = _SUFFIX_PAT.sub("", s)
    return s

def _like_token(name: str | None) -> str:
    s = _short_cn(name)
    return f"%{s}%" if s else "%"


# ==================================
# 1) 地理名词：get_place_path（不变）
# ==================================

def get_place_path(
        province_zh: str | None = None,
        city_zh: str | None = None,
        district_zh: str | None = None,
) -> dict | None:
    """
    兼容老版本：
    - 仅省：返回 {'province': '...'}
    - 仅市：返回 {'province': '...', 'city': '...'}
    - 市+区 或 仅区：返回 {'province': '...', 'city': '...', 'district': '...'}
    - 兼容简称（浙江/宁波/鄞州）或全称（浙江省/宁波市/鄞州区）
    """
    # 仅省
    if province_zh and not city_zh and not district_zh:
        row = _one(
            "SELECT name_ru FROM geo_province "
            "WHERE name_zh = ? OR name_zh LIKE ? LIMIT 1",
            province_zh, _like_token(province_zh),
        )
        return {"province": row["name_ru"]} if row else None

    # 仅市（自动带出省）
    if city_zh and not district_zh:
        row = _one(
            "SELECT p.name_ru AS prov_ru, c.name_ru AS city_ru "
            "FROM geo_city c JOIN geo_province p ON p.id=c.province_id "
            "WHERE c.name_zh = ? OR c.name_zh LIKE ? LIMIT 1",
            city_zh, _like_token(city_zh),
        )
        return {"province": row["prov_ru"], "city": row["city_ru"]} if row else None

    # 区（带不带市都行）
    if district_zh:
        if city_zh:
            row = _one(
                "SELECT p.name_ru AS prov_ru, c.name_ru AS city_ru, d.name_ru AS dist_ru "
                "FROM geo_district d "
                "JOIN geo_city c ON c.id=d.city_id "
                "JOIN geo_province p ON p.id=c.province_id "
                "WHERE (c.name_zh = ? OR c.name_zh LIKE ?) "
                "  AND (d.name_zh = ? OR d.name_zh LIKE ?) "
                "LIMIT 1",
                city_zh, _like_token(city_zh), district_zh, _like_token(district_zh),
            )
        else:
            row = _one(
                "SELECT p.name_ru AS prov_ru, c.name_ru AS city_ru, d.name_ru AS dist_ru "
                "FROM geo_district d "
                "JOIN geo_city c ON c.id=d.city_id "
                "JOIN geo_province p ON p.id=c.province_id "
                "WHERE d.name_zh = ? OR d.name_zh LIKE ? "
                "LIMIT 1",
                district_zh, _like_token(district_zh),
            )
        return (
            {"province": row["prov_ru"], "city": row["city_ru"], "district": row["dist_ru"]}
            if row else None
        )

    return None


# ==================================
# 2) 姓氏：拼音 → 俄文（不变）
# ==================================

def find_surname_pinyin(pinyin: str) -> str | None:
    if not pinyin:
        return None
    row = _one(
        "SELECT ru_map FROM surname_pinyin_rule WHERE LOWER(pinyin)=LOWER(?)",
        pinyin.strip(),
    )
    return row["ru_map"] if row else None


# ==================================
# 3) 名：拼音 →（完全从 DB 规则）→ 俄文（不变名）
# ==================================

@lru_cache(maxsize=1)
def _load_given_rules() -> list[tuple[str, str, int]]:
    """
    从 givenname_rule 载入：[(pattern, ru, priority)]
    - 仅使用 DB，不内置任何字典
    - pattern 用于最长匹配（lowercase）
    """
    rows = _all(
        "SELECT pattern, ru_map, COALESCE(priority, 100) AS pr "
        "FROM givenname_rule"
    )
    rules: list[tuple[str, str, int]] = []
    for r in rows:
        pat = (r["pattern"] or "").strip().lower()
        ru_raw = (r["ru_map"] or "").strip()
        if not pat or not ru_raw:
            continue
        # 兼容 JSON 或 纯文本
        ru = None
        if ru_raw.startswith("{") and ru_raw.endswith("}"):
            try:
                obj = json.loads(ru_raw)
                for k in ("ru", "name_ru", "map", "value"):
                    if isinstance(obj.get(k), str):
                        ru = obj[k]
                        break
            except Exception:
                pass
        if ru is None:
            ru = ru_raw
        rules.append((pat, ru, int(r["pr"])))
    # 排序：长度降序、优先级升序、pattern 词典序
    rules.sort(key=lambda x: (-len(x[0]), x[2], x[0]))
    return rules

def _norm_given_text(s: str) -> str:
    return (s or "").strip().lower()

def to_palladius_given(pinyin_text: str) -> str:
    """
    名的转写：完全从 DB 的 givenname_rule 做“从左到右的最长匹配”。
    未命中的字符将原样输出（避免空结果）。
    示例：'xiaoming' -> 'сяомин'（前提：DB 里有 xiao→сяо, ming→мин 等规则）
    """
    text = _norm_given_text(pinyin_text)
    if not text:
        return ""

    rules = _load_given_rules()
    if not rules:
        # 若 DB 中没有规则，直接原样返回
        return pinyin_text

    # 预分词：保留空白/连字符为分隔符
    tokens = re.split(r"(\s+|-+)", text)
    out: list[str] = []

    # 将规则按长度分桶，加速匹配
    buckets: dict[int, list[tuple[str, str, int]]] = {}
    lens: set[int] = set()
    for pat, ru, pr in rules:
        L = len(pat)
        buckets.setdefault(L, []).append((pat, ru, pr))
        lens.add(L)
    lens_desc = sorted(lens, reverse=True)

    for tok in tokens:
        # 分隔符原样输出
        if re.fullmatch(r"\s+|-+", tok):
            out.append(tok)
            continue

        i = 0
        n = len(tok)
        buf = []
        while i < n:
            matched = False
            for L in lens_desc:
                if i + L > n:
                    continue
                sub = tok[i:i+L]
                # 同长度桶内遍历（已按 priority 排好）
                for pat, ru, _pr in buckets[L]:
                    if sub == pat:
                        buf.append(ru)
                        i += L
                        matched = True
                        break
                if matched:
                    break
            if not matched:
                # 不在规则内的字符，保留
                buf.append(tok[i])
                i += 1
        out.append("".join(buf))

    return "".join(out)


# ==================================
# 4) 全名：拼音姓 + 拼名 → 俄文（不变名）
# ==================================

def translate_person_name(surname_pinyin: str, given_pinyin: str) -> str:
    sur = find_surname_pinyin(surname_pinyin) or surname_pinyin
    given = to_palladius_given(given_pinyin)

    def cap_ru(s: str) -> str:
        return s[:1].upper() + s[1:] if s else s

    return f"{cap_ru(sur)} {cap_ru(given)}".strip()


# ==================================
# 5) 机构名称：查库（不变名）
# ==================================

def find_org(name_zh: str, doc_type: str = "passport", region_zh: str | None = None) -> dict | None:
    """
    在 authority_org 中查找：
    - 先 exact，再 LIKE（兼容简称）
    - 必须匹配 doc_type（'passport' / 'driving_licence'）
    - 若提供 region_zh，会限制 region_zh 相等或 LIKE
    返回：{'name_zh':..., 'name_ru':..., 'doc_type':..., 'region_zh':...} 或 None
    """
    name_zh = (name_zh or "").strip()
    if not name_zh:
        return None

    params = [doc_type, name_zh]
    sql_exact = (
        "SELECT name_zh, name_ru, doc_type, region_zh "
        "FROM authority_org WHERE doc_type=? AND name_zh=? LIMIT 1"
    )

    row = _one(sql_exact, *params)
    if row:
        return dict(row)

    # LIKE 查询（兼容简称）
    like = _like_token(name_zh)
    params2 = [doc_type, like]
    sql_like = (
        "SELECT name_zh, name_ru, doc_type, region_zh "
        "FROM authority_org WHERE doc_type=? AND name_zh LIKE ? "
    )

    if region_zh:
        sql_like += "AND (region_zh = ? OR region_zh LIKE ?) "
        params2.extend([region_zh, _like_token(region_zh)])

    sql_like += "LIMIT 1"
    row = _one(sql_like, *params2)
    return dict(row) if row else None