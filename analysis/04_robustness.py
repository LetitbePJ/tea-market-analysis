"""
04_robustness.py — 稳健性检验（补齐审计发现的 H6 / H7）
  H6 半径敏感性：竞品半径 500m / 1km / 2km 下，Q3 的结论是否成立？
  H7 排序稳定性：蓝海城市排名经 bootstrap 重采样后是否稳定？

两个检验共用同一数据，输出结论用于判断"哪些结论可以对外讲"。
"""
from collections import Counter

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

bt = pd.read_csv("data/bubble_tea.csv")
city = pd.read_csv("data/city_market.csv")
findings = []

R = 6371.0


def haversine_matrix(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


lat = bt["latitude"].to_numpy(dtype=float)
lon = bt["longitude"].to_numpy(dtype=float)
st = bt["state"].astype(str).to_numpy()
same = st[:, None] == st[None, :]
D = haversine_matrix(lat[:, None], lon[:, None], lat[None, :], lon[None, :])
np.fill_diagonal(D, np.inf)

cluster = bt["postal_code"].astype(str).eq("19107") & bt["city"].eq("Philadelphia")

# ============================================================
# H6 半径敏感性
# ============================================================
print("========== H6 半径敏感性检验 ==========")
rows = []
for radius in [0.5, 1.0, 2.0]:
    cnt = ((D <= radius) & same).sum(axis=1)
    r_all = pd.Series(cnt).corr(bt["review_count"])
    # 分组：0 / 1-2 / 3+（按半径缩放）
    bins = [-1, 0, 2, np.inf]
    g = pd.cut(cnt, bins, labels=["0", "1-2", "3+"])
    p_all = stats.kruskal(*[bt.loc[g == k, "review_count"].values for k in ["0", "1-2", "3+"]
                            if (g == k).sum() > 5]).pvalue
    # 剔除唐人街簇后
    keep = ~cluster
    r_sub = pd.Series(cnt[keep.values]).corr(bt.loc[keep, "review_count"].reset_index(drop=True))
    g_sub = g[keep.values]
    p_sub = stats.kruskal(*[bt.loc[keep, "review_count"].values[g_sub == k]
                            for k in ["0", "1-2", "3+"] if (g_sub == k).sum() > 5]).pvalue
    rows.append({"半径km": radius, "均值竞品数": cnt.mean(),
                 "r(全样本)": r_all, "p(全样本)": p_all,
                 "r(剔除簇)": r_sub, "p(剔除簇)": p_sub})

sens = pd.DataFrame(rows)
print(sens.round(3).to_string(index=False))
print("\n判读：若三档半径下'剔除簇后 r≈0、p>0.05'都成立，则\"密度不提升需求\"这一结论对半径选择稳健")

stable = (sens["p(剔除簇)"] > 0.05).all() and (sens["r(剔除簇)"].abs() < 0.1).all()
findings.append(
    f"[H6] 半径敏感性：500m/1km/2km 三档下，剔除唐人街簇后相关系数分别为 "
    + "、".join(f"{v:.3f}" for v in sens["r(剔除簇)"])
    + f"，p 值均{'＞0.05（结论稳健）' if stable else '存在＜0.05 的档位（结论依赖半径）'}")

# ============================================================
# H7 蓝海城市排序稳定性（bootstrap）
# ============================================================
print("\n========== H7 蓝海城市排序稳定性（bootstrap 1000 次） ==========")
c = city[(city["bubble_shops"] >= 5) & (city["tea_shops"] >= 50)].copy()
c["blue_ocean"] = c["bubble_med_reviews"] * (1 - c["bubble_penetration"])

# 城市必须用 (state, city) 联合定位：数据存在跨州同名城市（Brentwood/Clayton/
# Springfield 等），只用 city 会把不同州的门店混进同一城市的 bootstrap 样本。
keys = list(zip(c["state"], c["city"]))
shops_by_key = {
    key: bt.loc[(bt["state"] == key[0]) & (bt["city"] == key[1]),
                "review_count"].to_numpy()
    for key in keys
}
penetration_by_key = {
    (row["state"], row["city"]): row["bubble_penetration"]
    for _, row in c.iterrows()
}
B = 1000
rng = np.random.default_rng(42)
top3 = {key: 0 for key in keys}
for _ in range(B):
    scores = {}
    for key, arr in shops_by_key.items():
        boot_med = np.median(rng.choice(arr, size=len(arr), replace=True))
        scores[key] = boot_med * (1 - penetration_by_key[key])
    for key in sorted(scores, key=scores.get, reverse=True)[:3]:
        top3[key] += 1

# 展示名：同名城市带州缩写消歧，其余保持城市名（与 README/findings 表述一致）
label_counts = Counter(name for _, name in keys)
labels = {k: (f"{k[1]}({k[0]})" if label_counts[k[1]] > 1 else k[1]) for k in keys}
stab = (pd.Series({labels[k]: v for k, v in top3.items()}) / B * 100).sort_values(ascending=False)
print("进入前 3 名的概率（%）：")
print(stab.round(1).to_string())
firm = stab[stab >= 80]
verdict = "排序可对外讲" if len(firm) >= 2 else "排序不稳定，只能讲候选池、不能讲排名"
findings.append(
    f"[H7] 蓝海排序稳定性：bootstrap 1000 次后，"
    f"{'、'.join(firm.index) if len(firm) else '无城市'}"
    f" 有 {'、'.join(f'{v:.0f}%' for v in firm.values) if len(firm) else '0%'} 的概率稳定进入前 3——{verdict}")

# ============================================================
# 图表 + 输出
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
x = np.arange(len(sens))
ax.plot(x, sens["r(全样本)"], marker="o", label="全样本", color="#E94B3C")
ax.plot(x, sens["r(剔除簇)"], marker="s", label="剔除唐人街簇", color="#2E86AB")
ax.set_xticks(x)
ax.set_xticklabels([f"{v}km" for v in sens["半径km"]])
ax.axhline(0, color="gray", lw=0.8)
ax.set_ylabel("竞品密度与热度的相关系数 r")
ax.set_title("H6 半径敏感性：剔除伪重复簇后关系消失")
ax.legend()
ax.grid(alpha=0.3)

ax = axes[1]
top_stab = stab.head(8)[::-1]
ax.barh(top_stab.index, top_stab.values, color="#32936F", alpha=0.85)
for i, v in enumerate(top_stab.values):
    ax.text(v + 1, i, f"{v:.0f}%", va="center", fontsize=9)
ax.set_xlim(0, 105)
ax.set_xlabel("bootstrap 后进入前 3 名的概率（%）")
ax.set_title("H7 蓝海城市排序稳定性")
ax.grid(alpha=0.3, axis="x")

plt.tight_layout()
plt.savefig("charts/q9_robustness.png", dpi=150, bbox_inches="tight")
print("\n图表已保存: charts/q9_robustness.png")

print("\n" + "=" * 50)
for f in findings:
    print(f)
with open("findings.txt", "a", encoding="utf-8") as f:
    f.write("\n".join(findings) + "\n")


def _dedupe_findings(prefixes=("[H6]", "[H7]")):
    """重复运行时避免同一结论被追加多次"""
    try:
        lines = open("findings.txt", encoding="utf-8").read().splitlines()
    except FileNotFoundError:
        return
    kept, seen = [], set()
    for ln in lines:
        if ln.startswith(prefixes):
            if ln in seen:
                continue
            seen.add(ln)
        kept.append(ln)
    open("findings.txt", "w", encoding="utf-8").write("\n".join(kept) + "\n")


_dedupe_findings()
print("\n补充结论已追加到 findings.txt")
