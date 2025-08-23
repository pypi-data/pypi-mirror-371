# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from functools import lru_cache
from importlib.resources import files, as_file
from typing import Any, Dict, Optional, Tuple

import zh2ru_idterms

# ============== DB 连接 ==============

def _db_path_in_package() -> str:
    res = files(zh2ru_idterms) / "data" / "terms.db"
    with as_file(res) as p:
        return str(p)

@lru_cache(maxsize=1)
def _get_conn() -> sqlite3.Connection:
    path = _db_path_in_package()
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# 探测列是否存在（缓存）
@lru_cache(maxsize=None)
def _has_col(table: str, col: str) -> bool:
    conn = _get_conn()
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    cols = {r["name"] for r in rows}
    return col in cols

def _row_any(conn: sqlite3.Connection, sql: str, args_list: Tuple[Tuple, ...]) -> Optional[sqlite3.Row]:
    for args in args_list:
        cur = conn.execute(sql, args)
        row = cur.fetchone()
        if row:
            return row
    return None

# ============== 名称归一化 ==============

_MUNICIPALITIES_FULL2SHORT = {"北京市": "北京", "天津市": "天津", "上海市": "上海", "重庆市": "重庆"}
_MUNICIPALITIES_SHORT = set(_MUNICIPALITIES_FULL2SHORT.values())

_PROVINCE_SPECIAL_FULL2SHORT = {
    "广西壮族自治区": "广西",
    "内蒙古自治区": "内蒙古",
    "西藏自治区": "西藏",
    "宁夏回族自治区": "宁夏",
    "新疆维吾尔自治区": "新疆",
    "香港特别行政区": "香港",
    "澳门特别行政区": "澳门",
}
_SUFFIXES_GENERAL = ("省", "市", "区", "县")

def normalize_region_zh(name: str) -> str:
    if not name:
        return name
    name = name.strip()
    if name in _MUNICIPALITIES_FULL2SHORT:
        return _MUNICIPALITIES_FULL2SHORT[name]
    if name in _MUNICIPALITIES_SHORT:
        return name
    if name in _PROVINCE_SPECIAL_FULL2SHORT:
        return _PROVINCE_SPECIAL_FULL2SHORT[name]
    if name in _PROVINCE_SPECIAL_FULL2SHORT.values():
        return name
    for suf in _SUFFIXES_GENERAL:
        if name.endswith(suf) and len(name) > len(suf):
            return name[: -len(suf)]
    return name

# ============== 地名查询 ==============

def find_province(name_zh: str) -> Optional[sqlite3.Row]:
    if not name_zh:
        return None
    conn = _get_conn()
    nm = name_zh.strip()
    nm_norm = normalize_region_zh(nm)

    # 精确中文名
    row = _row_any(conn, "SELECT * FROM geo_province WHERE name_zh = ?", ((nm,), (nm_norm,)))
    if row:
        return row

    # 别名列可用才查别名
    if _has_col("geo_province", "aliases_zh"):
        row = _row_any(
            conn,
            "SELECT * FROM geo_province WHERE aliases_zh LIKE ?",
            ((f'%\"{nm}\"%',), (f'%\"{nm_norm}\"%',)),
        )
        if row:
            return row

    # 最后退化为 name_zh LIKE
    return conn.execute(
        "SELECT * FROM geo_province WHERE name_zh LIKE ? ORDER BY LENGTH(name_zh) ASC LIMIT 1",
        (f"%{nm_norm}%",),
    ).fetchone()

def find_city(province_id: int, name_zh: str) -> Optional[sqlite3.Row]:
    if not name_zh:
        return None
    conn = _get_conn()
    nm = name_zh.strip()
    nm_norm = normalize_region_zh(nm)

    row = _row_any(
        conn,
        "SELECT * FROM geo_city WHERE province_id = ? AND name_zh = ?",
        ((province_id, nm), (province_id, nm_norm)),
    )
    if row:
        return row

    if _has_col("geo_city", "aliases_zh"):
        row = _row_any(
            conn,
            "SELECT * FROM geo_city WHERE province_id = ? AND aliases_zh LIKE ?",
            ((province_id, f'%\"{nm}\"%'), (province_id, f'%\"{nm_norm}\"%')),
        )
        if row:
            return row

    return conn.execute(
        "SELECT * FROM geo_city WHERE province_id = ? AND name_zh LIKE ? "
        "ORDER BY LENGTH(name_zh) ASC LIMIT 1",
        (province_id, f"%{nm_norm}%",),
    ).fetchone()

def find_district(city_id: int, name_zh: str) -> Optional[sqlite3.Row]:
    if not name_zh:
        return None
    conn = _get_conn()
    nm = name_zh.strip()
    nm_norm = normalize_region_zh(nm)

    row = _row_any(
        conn,
        "SELECT * FROM geo_district WHERE city_id = ? AND name_zh = ?",
        ((city_id, nm), (city_id, nm_norm)),
    )
    if row:
        return row

    if _has_col("geo_district", "aliases_zh"):
        row = _row_any(
            conn,
            "SELECT * FROM geo_district WHERE city_id = ? AND aliases_zh LIKE ?",
            ((city_id, f'%\"{nm}\"%'), (city_id, f'%\"{nm_norm}\"%')),
        )
        if row:
            return row

    return conn.execute(
        "SELECT * FROM geo_district WHERE city_id = ? AND name_zh LIKE ? "
        "ORDER BY LENGTH(name_zh) ASC LIMIT 1",
        (city_id, f"%{nm_norm}%",),
    ).fetchone()

def _find_city_globally(name_zh: str) -> Optional[sqlite3.Row]:
    if not name_zh:
        return None
    conn = _get_conn()
    nm = normalize_region_zh(name_zh.strip())

    rows = conn.execute("SELECT * FROM geo_city WHERE name_zh = ?", (nm,)).fetchall()
    if len(rows) == 1:
        return rows[0]
    if len(rows) > 1:
        return None

    if _has_col("geo_city", "aliases_zh"):
        rows = conn.execute("SELECT * FROM geo_city WHERE aliases_zh LIKE ?", (f'%\"{nm}\"%',)).fetchall()
        if len(rows) == 1:
            return rows[0]
        if len(rows) > 1:
            return None

    return conn.execute(
        "SELECT * FROM geo_city WHERE name_zh LIKE ? ORDER BY LENGTH(name_zh) ASC LIMIT 1",
        (f"%{nm}%",),
    ).fetchone()

def _find_district_globally(name_zh: str) -> Optional[sqlite3.Row]:
    if not name_zh:
        return None
    conn = _get_conn()
    nm = normalize_region_zh(name_zh.strip())

    rows = conn.execute("SELECT * FROM geo_district WHERE name_zh = ?", (nm,)).fetchall()
    if len(rows) == 1:
        return rows[0]
    if len(rows) > 1:
        return None

    if _has_col("geo_district", "aliases_zh"):
        rows = conn.execute("SELECT * FROM geo_district WHERE aliases_zh LIKE ?", (f'%\"{nm}\"%',)).fetchall()
        if len(rows) == 1:
            return rows[0]
        if len(rows) > 1:
            return None

    return conn.execute(
        "SELECT * FROM geo_district WHERE name_zh LIKE ? ORDER BY LENGTH(name_zh) ASC LIMIT 1",
        (f"%{nm}%",),
    ).fetchone()

def get_place_path(
        province_zh: Optional[str] = None,
        city_zh: Optional[str] = None,
        district_zh: Optional[str] = None,
) -> Optional[Dict[str, str]]:
    conn = _get_conn()
    prov = city = dist = None

    if province_zh:
        prov = find_province(province_zh)
        if not prov:
            return None

    if city_zh:
        if prov:
            city = find_city(prov["id"], city_zh)
            if not city:
                return None
        else:
            city = _find_city_globally(city_zh)
            if not city:
                return None

    if district_zh:
        if city:
            dist = find_district(city["id"], district_zh)
            if not dist:
                return None
        else:
            dist = _find_district_globally(district_zh)
            if not dist:
                return None
            city = conn.execute("SELECT * FROM geo_city WHERE id = ?", (dist["city_id"],)).fetchone()
            if not city:
                return None
            if not prov:
                prov = conn.execute("SELECT * FROM geo_province WHERE id = ?", (city["province_id"],)).fetchone()

    if city and not prov:
        prov = conn.execute("SELECT * FROM geo_province WHERE id = ?", (city["province_id"],)).fetchone()

    out: Dict[str, str] = {}
    if prov:
        out["province"] = prov["name_ru"] or prov["name_zh"]
    if city:
        out["city"] = city["name_ru"] or city["name_zh"]
    if dist:
        out["district"] = dist["name_ru"] or dist["name_zh"]
    return out or None

# ============== 机构 ==============

def find_authority_org(name_zh: str, doc_type: str = "passport", region_zh: Optional[str] = None) -> Optional[Dict[str, Any]]:
    conn = _get_conn()
    nm = (name_zh or "").strip()
    reg_norm = normalize_region_zh(region_zh.strip()) if region_zh else None

    if reg_norm:
        row = conn.execute(
            """SELECT * FROM authority_org
               WHERE doc_type = ? AND name_zh = ? AND IFNULL(region_zh,'') IN (?, ?)
               LIMIT 1""",
            (doc_type, nm, reg_norm, region_zh),
        ).fetchone()
        if row:
            return dict(row)

    row = conn.execute(
        "SELECT * FROM authority_org WHERE doc_type = ? AND name_zh = ? LIMIT 1",
        (doc_type, nm),
    ).fetchone()
    if row:
        return dict(row)

    if _has_col("authority_org", "aliases_zh"):
        row = conn.execute(
            "SELECT * FROM authority_org WHERE doc_type = ? AND aliases_zh LIKE ? LIMIT 1",
            (doc_type, f'%\"{nm}\"%'),
        ).fetchone()
        if row:
            return dict(row)

    row = conn.execute(
        "SELECT * FROM authority_org WHERE doc_type = ? AND name_zh LIKE ? ORDER BY length(name_zh) ASC LIMIT 1",
        (doc_type, f"%{nm}%"),
    ).fetchone()
    return dict(row) if row else None

# ============== 姓名 ==============

def surname_hanzi_to_ru(hanzi: str) -> Optional[str]:
    if not hanzi:
        return None
    conn = _get_conn()
    row = conn.execute("SELECT ru_pref FROM surname_rule WHERE hanzi = ?", (hanzi.strip(),)).fetchone()
    return row["ru_pref"] if row else None

def surname_pinyin_to_ru(pinyin: str) -> Optional[str]:
    if not pinyin:
        return None
    conn = _get_conn()
    row = conn.execute(
        "SELECT ru_map FROM surname_pinyin_rule WHERE pinyin = ? ORDER BY priority ASC LIMIT 1",
        (pinyin.lower().strip(),),
    ).fetchone()
    return row["ru_map"] if row else None

try:
    from .palladius_name import to_palladius_given  # type: ignore
except Exception:  # pragma: no cover
    def to_palladius_given(pinyin_text: str) -> str:
        return pinyin_text or ""

def compose_full_name_ru(
        *,
        surname_hanzi: Optional[str] = None,
        surname_pinyin: Optional[str] = None,
        given_pinyin: Optional[str] = None,
) -> str:
    sur_ru = ""
    if surname_hanzi:
        sur_ru = surname_hanzi_to_ru(surname_hanzi) or ""
    if not sur_ru and surname_pinyin:
        sur_ru = surname_pinyin_to_ru(surname_pinyin) or (surname_pinyin or "")
    given_ru = to_palladius_given(given_pinyin or "") if given_pinyin else ""
    return f"{sur_ru} {given_ru}".strip()

# ============== 兼容旧名 ==============

def find_surname_pinyin(pinyin: str) -> Optional[str]:
    return surname_pinyin_to_ru(pinyin)

def translate_person_name(surname_pinyin: str, given_pinyin: str) -> str:
    return compose_full_name_ru(surname_pinyin=surname_pinyin, given_pinyin=given_pinyin)

def find_org(name_zh: str, doc_type: str = "passport", region_zh: Optional[str] = None) -> Optional[Dict[str, Any]]:
    return find_authority_org(name_zh=name_zh, doc_type=doc_type, region_zh=region_zh)

__all__ = [
    "get_place_path",
    "find_surname_pinyin",
    "to_palladius_given",
    "translate_person_name",
    "find_org",
    "normalize_region_zh",
    "find_province",
    "find_city",
    "find_district",
    "find_authority_org",
    "surname_hanzi_to_ru",
    "surname_pinyin_to_ru",
    "compose_full_name_ru",
]