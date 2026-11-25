"""findings.txt 统一写入：按前缀分组的幂等覆盖（非追加）

每个脚本只负责自己那组前缀的结论。写入时：
  - 先删掉文件里所有属于本组前缀的旧行；
  - 再把新结论插入到该组在固定顺序中的位置；
  - 其他脚本的组原样保留，整体顺序固定，不随运行次序变化。

这样重复运行任何脚本，findings.txt 都是同一个结果（幂等），
不会出现"结论被追加多份"或"行顺序随运行顺序漂移"。
"""
import os

FINDINGS_PATH = "findings.txt"

# 各组前缀与固定输出顺序（长的放前面，避免 [H7] 误匹配 [H7c]/[H7b]）
GROUP_ORDER = ("[Q1]", "[Q2]", "[Q3]", "[Q4]", "[Q4b]", "[Q5]", "[Q6]", "[Q7]",
               "[Q8]", "[Q10]", "[H6]", "[H7]", "[H7c]", "[H7b]")


def _group_of(line):
    """返回该行所属的前缀组；不匹配返回 None。用最长前缀优先匹配。"""
    for p in sorted(GROUP_ORDER, key=len, reverse=True):
        if line.startswith(p):
            return p
    return None


def write_group(lines, group_prefix=None):
    """把 lines（字符串列表）写入其所属前缀组，幂等覆盖。

    group_prefix 可显式指定（如 "[Q5]"）；省略时从 lines[0] 推断。
    """
    if isinstance(lines, str):
        lines = [lines]
    if not lines:
        return
    prefix = group_prefix or _group_of(lines[0])
    if prefix is None:
        raise ValueError(f"无法从结论行推断前缀组，请显式传 group_prefix: {lines[0][:40]}")

    try:
        with open(FINDINGS_PATH, encoding="utf-8") as f:
            existing = [ln for ln in f.read().splitlines() if ln.strip()]
    except FileNotFoundError:
        existing = []

    # 移除本组所有旧行（整个文件范围），保留其他组
    kept = [ln for ln in existing if _group_of(ln) != prefix]
    # 把新行追加到末尾，再按固定组顺序重排
    all_lines = kept + list(lines)
    buckets = {p: [] for p in GROUP_ORDER}
    others = []
    for ln in all_lines:
        g = _group_of(ln)
        if g is None:
            others.append(ln)
        else:
            buckets[g].append(ln)
    ordered = [ln for p in GROUP_ORDER for ln in buckets[p]] + others
    with open(FINDINGS_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(ordered) + "\n")


def drop_prefix(prefix):
    """删除指定前缀组的所有行（用于淘汰旧口径结论，如单店 bootstrap 的 [H7]）。"""
    if not os.path.exists(FINDINGS_PATH):
        return
    with open(FINDINGS_PATH, encoding="utf-8") as f:
        lines = f.read().splitlines()
    kept = [ln for ln in lines if not ln.startswith(prefix)]
    with open(FINDINGS_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(kept) + "\n")
