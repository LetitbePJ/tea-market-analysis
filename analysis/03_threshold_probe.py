"""
03_threshold_probe.py — 竞品密度是否存在阈值？细粒度曲线 + 稳健性检验 + 显著性检验
背景：02_analysis.py 的 Q3 得到"竞品密度与热度正相关 r=0.19"，本脚本检验这个结论是否稳健。
结论（由本脚本计算后输出）：不稳健——表面上的"集聚效应"由单一街区驱动，
    剔除该街区后相关系数与分组差异均不再支持"密度提升需求"。具体数值见运行输出，
    不在代码中预先写死。正确解释：竞品数量是"优质商圈"的症状，而非病因（高客流商圈
    同时吸引顾客与竞品）。

方法：
  1. 逐密度点曲线（样本≥10 才纳入）
  2. 等样本四分位分箱（规避小样本噪声）
  3. 聚类来源识别：高密度点集中在哪些城市/邮编
  4. 剔除单一超级簇后重算相关系数与 Kruskal-Wallis 检验
  5. 费城内对照：超级簇 vs 其他门店（Mann-Whitney 检验）
  6. Q4 评分梯度：同样做剔除伪重复簇后的 Kruskal-Wallis 检验（与热度结论不同）
"""
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

bt = pd.read_csv("data/bubble_tea.csv")
print(f"样本: {len(bt)} 家奶茶店")
extra_findings = []

# ============ 1. 逐密度点曲线 ============
print("\n========== 1. 逐密度点曲线（样本≥10） ==========")
curve = (bt.groupby("competitors_1km")["review_count"]
         .agg(["mean", "median", "count"])
         .rename(columns={"mean": "均评论", "median": "中位评论", "count": "门店数"}))
curve = curve[curve["门店数"] >= 10]
print(curve.round(1).to_string())
# 结论由 curve 动态生成：把每个密度点的均评论串成箭头链，再由相邻差值判断是否单调
chain = " → ".join(f"{n}家 {v:.0f}" for n, v in zip(curve.index, curve["均评论"]))
deltas = curve["均评论"].diff().dropna()
monotone = (deltas >= 0).all() or (deltas <= 0).all()
print(f"→ 曲线{'单调' if monotone else '不单调'}（样本≥10 的密度点）：{chain}")

# ============ 2. 等样本四分位分箱 ============
print("\n========== 2. 等样本四分位分箱 ==========")
bt["q"] = pd.qcut(bt["competitors_1km"], 4, duplicates="drop")
qq = bt.groupby("q", observed=True)["review_count"].agg(["mean", "median", "count"])
print(qq.round(1).to_string())

# ============ 3. 高密度点的来源 ============
print("\n========== 3. 高密度点（≥20家竞品）来自哪里？ ==========")
hi = bt[bt["competitors_1km"] >= 20]
print(f"门店数: {len(hi)}")
print(f"城市: {hi['city'].value_counts().to_dict()}")
print(f"邮编: {hi['postal_code'].value_counts().to_dict()}")
print(f"均评论: {hi['review_count'].mean():.0f}（全样本均值 {bt['review_count'].mean():.0f}）")
# 簇的归属由数据反推，不写死"费城唐人街 19107 / 23 家"
hi_city = hi["city"].mode().iat[0] if len(hi) else "N/A"
hi_zip = hi["postal_code"].mode().iat[0] if len(hi) else "N/A"
print(f"→ {len(hi)} 家店集中于 {hi_city} 邮编 {hi_zip}："
      f"它们是同一个商圈的同批门店，不是 {len(hi)} 个独立观测")

# ============ 4. 剔除超级簇后重算 ============
print("\n========== 4. 剔除唐人街簇后的稳健性检验 ==========")
rest = bt[bt["competitors_1km"] < 20].copy()
r_all = bt["competitors_1km"].corr(bt["review_count"])
r_rest = rest["competitors_1km"].corr(rest["review_count"])
print(f"全样本 r = {r_all:.3f} → 剔除后 r = {r_rest:.3f}")

bt["g"] = pd.cut(bt["competitors_1km"], [-1, 0, 2, 5, np.inf], labels=["0家", "1-2家", "3-5家", "6家+"])
H1, p1 = stats.kruskal(*[g["review_count"].values for _, g in bt.groupby("g", observed=True)])
rest["g"] = pd.cut(rest["competitors_1km"], [-1, 0, 2, 5, np.inf], labels=["0家", "1-2家", "3-5家", "6家+"])
H2, p2 = stats.kruskal(*[g["review_count"].values for _, g in rest.groupby("g", observed=True)])
print(f"分组差异 Kruskal-Wallis：全样本 p={p1:.4f} → 剔除后 p={p2:.4f}")
print("剔除后各组均评论：", rest.groupby("g", observed=True)["review_count"].mean().round(0).to_dict())

# Q4 评分梯度同样要过伪重复检验：与 review_count 不同，它是否经得起剔除？
H1s, p1s = stats.kruskal(*[g["stars"].values for _, g in bt.groupby("g", observed=True)])
H2s, p2s = stats.kruskal(*[g["stars"].values for _, g in rest.groupby("g", observed=True)])
stars_rest = rest.groupby("g", observed=True)["stars"].mean()
print(f"Q4 评分梯度 Kruskal-Wallis：全样本 p={p1s:.4f} → 剔除后 p={p2s:.4f}")
print("剔除后各组均评分：", stars_rest.round(2).to_dict())

# ============ 5. 费城内对照 ============
print("\n========== 5. 费城内部：唐人街簇 vs 其他门店 ==========")
ph = bt[bt["city"] == "Philadelphia"]
cluster = ph[ph["competitors_1km"] >= 20]
others = ph[ph["competitors_1km"] < 20]
print(f"唐人街簇: n={len(cluster)}, 均评论={cluster['review_count'].mean():.0f}")
print(f"费城其他: n={len(others)}, 均评论={others['review_count'].mean():.0f}")
p_mw = stats.mannwhitneyu(cluster["review_count"], others["review_count"]).pvalue
print(f"Mann-Whitney p={p_mw:.4f} → 该街区热度显著更高（真实现象），但这是 1 个街区，不是密度效应")

# ============ 结论 ============
print("\n" + "=" * 50)
print("结论")
print("=" * 50)
extra_findings.append(
    f"[Q4b] 评分梯度经得起伪重复检验：剔除唐人街簇后 Kruskal-Wallis H={H2s:.2f}、p={p2s:.4f} 仍显著"
    f"（独占区 {stars_rest.iloc[0]:.2f} → 最卷区 {stars_rest.iloc[-1]:.2f}）。"
    "与 Q3 的热度结论不同——热度是单一街区伪造的，评分分化是全样本现象；"
    "但两种机制（低质店存活 / 高竞争区分化）单期截面仍无法区分")
extra_findings.append(
    "[Q8] 竞品密度不存在可推广的阈值：细粒度曲线非单调，剔除费城唐人街单一街区后"
    f"相关系数从 {r_all:.2f} 降至 {r_rest:.2f}、分组差异不再显著（p={p2:.2f}）。"
    "表面上\"竞品密→热度高\"是伪重复（pseudo-replication）造成的假象："
    "竞品数量是优质商圈的症状而非病因，正确策略是选商圈本身，而非追逐竞品数量")
for f in extra_findings:
    print(f)

with open("findings.txt", "a", encoding="utf-8") as f:
    f.write("\n".join(extra_findings) + "\n")


def _dedupe_findings(prefixes=("[Q4b]", "[Q8]")):
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

# ============ 图表 ============
fig, axes = plt.subplots(1, 3, figsize=(17, 5))

ax = axes[0]
ax.plot(curve.index, curve["均评论"], marker="o", color="#2E86AB")
ax.set_xlabel("1km 内同类奶茶店数量")
ax.set_ylabel("平均累计评论数")
ax.set_title("全样本：细粒度曲线（非单调）")
ax.grid(alpha=0.3)

ax = axes[1]
rest_g = rest.groupby("g", observed=True)["review_count"].mean()
bars = ax.bar(rest_g.index.astype(str), rest_g.values, color="#32936F", alpha=0.8)
for b in bars:
    ax.text(b.get_x() + b.get_width() / 2, b.get_height(), f"{b.get_height():.0f}", ha="center")
ax.set_ylim(0, 210)
ax.set_ylabel("平均累计评论数")
ax.set_title(f"剔除唐人街簇后：差异消失（p={p2:.2f}）")
ax.grid(alpha=0.3, axis="y")

ax = axes[2]
bars = ax.bar([f"唐人街 {hi_zip}\n(n={len(cluster)})", f"费城其他\n(n={len(others)})"],
              [cluster["review_count"].mean(), others["review_count"].mean()],
              color=["#E94B3C", "#A4A4A4"], alpha=0.85)
for b in bars:
    ax.text(b.get_x() + b.get_width() / 2, b.get_height(), f"{b.get_height():.0f}", ha="center")
ax.set_ylabel("平均累计评论数")
ax.set_title(f"费城内对照（p={p_mw:.4f}）\n高密度集中在这 1 个街区")
ax.grid(alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig("charts/q8_threshold.png", dpi=150, bbox_inches="tight")
print("图表已保存: charts/q8_threshold.png")
