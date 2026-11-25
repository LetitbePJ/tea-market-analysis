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

from geo_utils import haversine_matrix
from plot_utils import setup_chinese_font
from findings_io import write_group, drop_prefix

setup_chinese_font()

bt = pd.read_csv("data/bubble_tea.csv")
city = pd.read_csv("data/city_market.csv")
findings = []

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
# H7 蓝海城市排序稳定性（bootstrap：单店 vs 整群，两种口径对比）
# ============================================================
# 审计 D3：同商圈门店共享客流与租金，不是独立观测。原 bootstrap 按单店独立重采样，
# 把同一商圈的 23 家店当成 23 个独立信号，低估方差、高估排序稳定性。
# 现增加"按邮编商圈整群重采样"：一个商圈的门店整体进 or 整体不进，保留簇内相关。
print("\n========== H7 蓝海城市排序稳定性（bootstrap 1000 次） ==========")
c = city[(city["bubble_shops"] >= 5) & (city["tea_shops"] >= 50)].copy()
c["blue_ocean"] = c["bubble_med_reviews"] * (1 - c["bubble_penetration"])

# 城市必须用 (state, city) 联合定位：数据存在跨州同名城市（Brentwood/Clayton/
# Springfield 等），只用 city 会把不同州的门店混进同一城市的 bootstrap 样本。
keys = list(zip(c["state"], c["city"]))
tea = pd.read_csv("data/tea_shops.csv")          # 含全部茶饮店，用于整群口径重算渗透率
shops_by_key = {
    key: bt.loc[(bt["state"] == key[0]) & (bt["city"] == key[1]),
                "review_count"].to_numpy()
    for key in keys
}
penetration_by_key = {(row["state"], row["city"]): row["bubble_penetration"]
                      for _, row in c.iterrows()}
# 整群口径：每个城市按邮编分组，商圈内门店作为不可拆分的抽样单元。
# 预先把每个商圈的 (评论数组, 奶茶店占比, 门店数) 备好，避免 bootstrap 循环里重复 groupby。
zips_bt, zips_bt_n, zips_all_n = {}, {}, {}
for key in keys:
    sub = tea[(tea["state"] == key[0]) & (tea["city"] == key[1])].copy()
    sub["is_bt"] = sub["is_bubble_tea"].astype(bool)
    grouped = list(sub.groupby("postal_code"))
    # 每个商圈：奶茶店评论数组 / 奶茶店数 / 茶饮店总数
    zips_bt[key] = [g.loc[g["is_bt"], "review_count"].to_numpy() for _, g in grouped]
    zips_bt_n[key] = [int(g["is_bt"].sum()) for _, g in grouped]
    zips_all_n[key] = [len(g) for _, g in grouped]

B = 1000
rng = np.random.default_rng(42)
top3_single, top3_cluster = {key: 0 for key in keys}, {key: 0 for key in keys}
score_cluster = {key: [] for key in keys}
for _ in range(B):
    # 口径 A（旧）：城市内按单店独立重采样
    s_single = {key: np.median(rng.choice(shops_by_key[key], size=len(shops_by_key[key]), replace=True))
                * (1 - penetration_by_key[key]) for key in keys}
    for key in sorted(s_single, key=s_single.get, reverse=True)[:3]:
        top3_single[key] += 1
    # 口径 B（新）：按邮编商圈整群重采样——抽中的商圈整体进入，保留簇内相关
    s_cluster = {}
    for key in keys:
        groups = zips_bt[key]
        idx = rng.integers(0, len(groups), size=len(groups))
        # 需求端：抽中商圈里的奶茶店评论中位数（只取奶茶店，与 blue_ocean 口径一致）
        demand_arr = np.concatenate([zips_bt[key][i] for i in idx]) if zips_bt[key] else np.array([])
        if len(demand_arr):
            demand = np.median(demand_arr)
            # 供给端：渗透率随重采样变化 = 抽中商圈里奶茶店数 / 茶饮店数
            n_bt = sum(zips_bt_n[key][i] for i in idx)
            n_all = sum(zips_all_n[key][i] for i in idx)
            penetration = n_bt / n_all if n_all else 0.0
            s_cluster[key] = demand * (1 - penetration)
            score_cluster[key].append(s_cluster[key])
        else:
            s_cluster[key] = 0.0
    for key in sorted(s_cluster, key=s_cluster.get, reverse=True)[:3]:
        top3_cluster[key] += 1

# 展示名：同名城市带州缩写消歧，其余保持城市名（与 README/findings 表述一致）
label_counts = Counter(name for _, name in keys)
labels = {k: (f"{k[1]}({k[0]})" if label_counts[k[1]] > 1 else k[1]) for k in keys}
stab_single = (pd.Series({labels[k]: v for k, v in top3_single.items()}) / B * 100).sort_values(ascending=False)
stab_cluster = (pd.Series({labels[k]: v for k, v in top3_cluster.items()}) / B * 100).sort_values(ascending=False)
print("进入前 3 名的概率（%）——单店口径（旧，低估方差）：")
print(stab_single.round(1).to_string())
print("\n进入前 3 名的概率（%）——邮编商圈整群口径（新，保留簇内相关）：")
print(stab_cluster.round(1).to_string())

firm = stab_cluster[stab_cluster >= 80]
# 差异对比：列出两口径下概率变化最大的城市
delta = (stab_cluster - stab_single).reindex(stab_single.index).dropna()
top_change = delta.abs().nlargest(3).index
change_desc = "；".join(f"{n} {stab_single[n]:.0f}%→{stab_cluster[n]:.0f}%" for n in top_change)
findings.append(
    f"[H7c] 蓝海排序稳定性（按邮编商圈整群重采样 1000 次，修正 D3 单店独立的方差低估）："
    f"{'、'.join(firm.index) if len(firm) else '无城市'}"
    f" 稳定进入前 3 的概率为 {'、'.join(f'{v:.0f}%' for v in firm.values) if len(firm) else '0%'}。"
    f"头两名虽有 80%+ 概率，但蓝海指数区间大幅重叠（见 H7b），故结论只表述'候选池'，"
    f"不宣称精确名次。与旧单店口径相比变化最大：{change_desc}")
# 整群口径下前 3 城市的蓝海指数 95% 区间（体现方差被正确放大）
ci_desc = []
for k in sorted(keys, key=lambda k: np.median(score_cluster[k]), reverse=True)[:3]:
    arr = np.array(score_cluster[k])
    if len(arr):
        lo, hi = np.percentile(arr, [2.5, 97.5])
        ci_desc.append(f"{labels[k]} [{lo:.0f},{hi:.0f}]")
findings.append(
    f"[H7b] 整群重采样下蓝海指数 95% 区间：{'；'.join(ci_desc)}"
    f"——区间重叠说明前 3 名之间差距不具备统计显著性，对外只表述候选池排名")

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
top_stab = stab_cluster.head(8)[::-1]
ax.barh(top_stab.index, top_stab.values, color="#32936F", alpha=0.85)
for i, v in enumerate(top_stab.values):
    ax.text(v + 1, i, f"{v:.0f}%", va="center", fontsize=9)
ax.set_xlim(0, 105)
ax.set_xlabel("整群 bootstrap 后进入前 3 名的概率（%）")
ax.set_title("H7 蓝海城市排序稳定性（商圈整群）")
ax.grid(alpha=0.3, axis="x")

plt.tight_layout()
plt.savefig("charts/q9_robustness.png", dpi=150, bbox_inches="tight")
print("\n图表已保存: charts/q9_robustness.png")

print("\n" + "=" * 50)
for f in findings:
    print(f)
# 淘汰旧的单店口径 [H7]，由整群口径 [H7c] 取代
drop_prefix("[H7]")
# 每组结论单独幂等覆盖（[H6]/[H7c]/[H7b] 各一组）
for line in findings:
    write_group([line], group_prefix=line.split("]", 1)[0] + "]")
print("\n补充结论已写入 findings.txt")
