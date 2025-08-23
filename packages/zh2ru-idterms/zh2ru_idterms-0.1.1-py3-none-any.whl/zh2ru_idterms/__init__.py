from .api import (
    # 原用法要求的名字（保持不变）
    get_place_path,
    find_surname_pinyin,
    to_palladius_given,
    translate_person_name,
    find_org,
)

# 额外导出也可以保留（可选），但你原来的代码只依赖上面这五个
__all__ = [
    "get_place_path",
    "find_surname_pinyin",
    "to_palladius_given",
    "translate_person_name",
    "find_org",
]