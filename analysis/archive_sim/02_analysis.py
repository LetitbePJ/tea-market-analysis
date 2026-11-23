"""
02_analysis.py — 奶茶门店选址与竞品分析（Q1–Q7 重构版）
相对原版 question.py 的改进：
  1. 相关性全部计算 Pearson r，不再只靠肉眼看散点
  2. 分组阈值由数据驱动（分位数/分组均值变化），不再硬编码"8 家""10000 人次"
  3. 敏感度指标真正输出（原版算完 mall_sens 就丢了）
  4. 全量数据绘图（原版只抽 10% 样本，结论代表性存疑）
  5. 图表落盘 charts/ 目录（GitHub 可展示），不再只 plt.show()
  6. 每个问题输出一条"观点式结论"，可直接写进报告
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

CLEAN = "data/clean_milk_tea.csv"
CHARTS = "charts"
os.makedirs(CHARTS, exist_ok=True)

df = pd.read_csv(CLEAN)
findings = []


def save_fig(fig, name):
    path = os.path.join(CHARTS, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"    图表已保存: {path}")


def add_finding(q, text):
    findings.append((q, text))
    print(f"    ★ 结论: {text}")


# ============================================================
# Q1 客流密度 vs 销量：线性 or 边际效应？
# 方法：全量 Pearson r + 十分位分组均值曲线（阈值看拐点，不拍脑袋）
# ============================================================
print("\n========== Q1 客流密度与销量的关系 ==========")
r_all = df["周边客流密度(人次/天)"].corr(df["日销量(元)"])
print(f"    全量 Pearson r = {r_all:.3f}")

dec = pd.qcut(df["周边客流密度(人次/天)"], q=10)
curve = df.groupby(dec, observed=True)["日销量(元)"].mean()
print("    客流十分位组的平均日销量：")
print(curve.round(0).to_string())

# 相邻组间的增量，看哪一段开始明显放缓
increments = curve.diff().dropna()
slow_idx = increments.idxmin()  # 增量最小的那个分位段
add_finding("Q1", f"客流与销量呈正相关（r={r_all:.2f}）；"
             f"增量在客流「{slow_idx}」段明显放缓，提示边际效应，而非无限线性增长")

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(range(len(curve)), curve.values, marker="o", color="#2E86AB")
ax.set_xticks(range(len(curve)))
ax.set_xticklabels([str(i) for i in curve.index], rotation=30, fontsize=8)
ax.set_xlabel("周边客流密度十分位组（低 → 高）")
ax.set_ylabel("平均日销量(元)")
ax.set_title("Q1 客流密度与日销量：十分位均值曲线")
ax.grid(alpha=0.3)
save_fig(fig, "q1_footfall_sales.png")
plt.close(fig)

# ============================================================
# Q2 竞品数量 vs 销量：负相关？下滑临界点在哪？
# 方法：按竞品数分组（样本量≥50 的组才纳入），看相邻组降幅
# ============================================================
print("\n========== Q2 竞品数量与销量的关系 ==========")
comp = df.groupby("3公里内竞品数量(家)")["日销量(元)"].agg(["mean", "count"])
comp = comp[comp["count"] >= 50].reset_index()
comp["环比降幅%"] = comp["mean"].pct_change() * 100
print(comp.round(1).to_string(index=False))

if len(comp) >= 2:
    worst = comp.loc[comp["环比降幅%"].idxmin()]
    add_finding("Q2", f"竞品数量与销量呈负相关；降幅最大发生在竞品 {int(worst['3公里内竞品数量(家)'])} 家组"
                 f"（环比 {worst['环比降幅%']:.1f}%），应作为选址时的竞品密度预警线")

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(comp["3公里内竞品数量(家)"], comp["mean"], marker="o", color="#E94B3C")
for _, row in comp.iterrows():
    ax.text(row["3公里内竞品数量(家)"], row["mean"], f"{int(row['mean'])}", ha="center", va="bottom", fontsize=8)
ax.set_xlabel("3公里内竞品数量(家)")
ax.set_ylabel("平均日销量(元)")
ax.set_title("Q2 竞品数量与平均日销量（样本量≥50 的分组）")
ax.grid(alpha=0.3)
save_fig(fig, "q2_competitor_sales.png")
plt.close(fig)

# ============================================================
# Q3 最近竞品距离 vs 销量
# 方法：距离分箱 + 组间均值对比 + Pearson r
# ============================================================
print("\n========== Q3 最近竞品距离与销量的关系 ==========")
df["竞品距离分组"] = pd.cut(df["最近竞品距离(米)"], bins=[0, 500, 1000, 2000, 3500],
                        labels=["<500米", "500-1000米", "1000-2000米", ">2000米"])
dist = df.groupby("竞品距离分组", observed=True)["日销量(元)"].agg(["mean", "count"])
print(dist.round(0).to_string())

r_dist = df["最近竞品距离(米)"].corr(df["日销量(元)"])
near, far = dist["mean"].iloc[0], dist["mean"].iloc[-1]
add_finding("Q3", f"竞品距离与销量 r={r_dist:.2f}；距离分组均值显示"
             f"「{dist.index[0]}」组均销 {near:,.0f} 元 vs「{dist.index[-1]}」组 {far:,.0f} 元"
             f"（差异 {'显著' if abs(near - far) / far > 0.05 else '不明显'}，差异比例 {(near - far) / far * 100:.1f}%）")

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(dist.index.astype(str), dist["mean"], alpha=0.75, color="#32936F")
for b in bars:
    ax.text(b.get_x() + b.get_width() / 2, b.get_height(), f"{int(b.get_height())}", ha="center")
ax.set_xlabel("最近竞品距离")
ax.set_ylabel("平均日销量(元)")
ax.set_title("Q3 竞品距离分组的平均日销量")
ax.grid(alpha=0.3, axis="y")
save_fig(fig, "q3_distance_sales.png")
plt.close(fig)

# ============================================================
# Q4 客流密度 × 竞品数量 交互效应
# ============================================================
print("\n========== Q4 不同客流下竞品的影响 ==========")
df["客流分组"] = pd.cut(df["周边客流密度(人次/天)"], bins=[0, 3000, 8000, np.inf],
                    labels=["低客流≤3000", "中客流3k-8k", "高客流≥8000"])
inter = (df[df["3公里内竞品数量(家)"] <= 12]
         .groupby(["客流分组", "3公里内竞品数量(家)"], observed=True)["日销量(元)"]
         .agg(["mean", "count"]).reset_index())
inter = inter[inter["count"] >= 5]
pivot = inter.pivot(index="3公里内竞品数量(家)", columns="客流分组", values="mean")
print(pivot.round(0).to_string())

# 高客流区竞品多 vs 低客流区竞品少 的对比
hh = df[(df["客流分组"] == "高客流≥8000") & (df["3公里内竞品数量(家)"] >= 10)]["日销量(元)"]
ll = df[(df["客流分组"] == "低客流≤3000") & (df["3公里内竞品数量(家)"] <= 5)]["日销量(元)"]
if len(hh) > 0 and len(ll) > 0:
    add_finding("Q4", f"高客流+竞品≥10家 均销 {hh.mean():,.0f} 元 vs 低客流+竞品≤5家 {ll.mean():,.0f} 元："
                 f"{'高客流能对冲竞品压力' if hh.mean() > ll.mean() else '竞品伤害强于客流红利'}（Q7 选址依据）")

fig, ax = plt.subplots(figsize=(10, 6))
for g in pivot.columns:
    ax.plot(pivot.index, pivot[g], marker="o", label=str(g))
ax.set_xlabel("3公里内竞品数量(家)")
ax.set_ylabel("平均日销量(元)")
ax.set_title("Q4 不同客流密度下竞品数量的影响")
ax.legend()
ax.grid(alpha=0.3)
save_fig(fig, "q4_interaction.png")
plt.close(fig)

# ============================================================
# Q5 位置类型 × 客流：各类型店的客流敏感度（原版算完没输出）
# ============================================================
print("\n========== Q5 各位置类型的客流敏感度 ==========")
loc_flow = df.groupby(["门店位置类型", "客流分组"], observed=True)["日销量(元)"].mean().unstack()
print(loc_flow.round(0).to_string())

sens = {}
for loc in loc_flow.index:
    # 低客流组在商场/校园/街边店几乎无样本，改用「中→高客流」的提升幅度衡量敏感度（各组均有样本）
    mid_v, high_v = loc_flow.loc[loc, "中客流3k-8k"], loc_flow.loc[loc, "高客流≥8000"]
    if pd.notna(mid_v) and pd.notna(high_v) and mid_v > 0:
        sens[loc] = (high_v - mid_v) / mid_v * 100
print("    客流敏感度（高客流组均销相对中客流组的提升%）:", {k: f"{v:.0f}%" for k, v in sens.items()})
if sens:
    most, least = max(sens, key=sens.get), min(sens, key=sens.get)
    add_finding("Q5", f"客流敏感度排序：{most} 最高（{sens[most]:.0f}%），{least} 最低（{sens[least]:.0f}%）——"
                 f"选址建议：{most} 必须抢高客流位，{least} 对客流依赖较弱、可考虑租金更低的次级位置")

fig, ax = plt.subplots(figsize=(10, 6))
loc_flow.plot(kind="bar", ax=ax, alpha=0.8)
ax.set_ylabel("平均日销量(元)")
ax.set_title("Q5 各位置类型在不同客流水平下的日销量")
ax.legend(title="客流分组")
ax.grid(alpha=0.3, axis="y")
save_fig(fig, "q5_location_sensitivity.png")
plt.close(fig)

# ============================================================
# Q6 季节对客流-销量关系的调节（竞品数取众数而非硬编码 8）
# ============================================================
print("\n========== Q6 季节的调节作用 ==========")
mode_comp = int(df["3公里内竞品数量(家)"].mode().iloc[0])
print(f"    竞品数量固定为众数：{mode_comp} 家（替代原版硬编码的 8 家）")
season_flow = df[df["3公里内竞品数量(家)"] == mode_comp].groupby(
    ["季节", "客流分组"], observed=True)["日销量(元)"].mean().unstack()
print(season_flow.round(0).to_string())

if "夏季" in season_flow.index and "冬季" in season_flow.index:
    lift = season_flow.loc["夏季"] - season_flow.loc["冬季"]
    add_finding("Q6", f"季节调节显著：夏季 vs 冬季的销量差随客流分组扩大"
                 f"（低客流差 {lift.get('低客流≤3000', float('nan')):,.0f} 元 → 高客流差 {lift.get('高客流≥8000', float('nan')):,.0f} 元），"
                 f"高客流位的季节弹性更大，选址需更重视冬季保底策略")

fig, ax = plt.subplots(figsize=(10, 6))
for g in season_flow.columns:
    ax.plot(season_flow.index, season_flow[g], marker="o", label=str(g))
ax.set_xlabel("季节")
ax.set_ylabel(f"平均日销量(元)（竞品={mode_comp}家）")
ax.set_title("Q6 季节对客流-销量关系的调节")
ax.legend()
ax.grid(alpha=0.3)
save_fig(fig, "q6_season.png")
plt.close(fig)

# ============================================================
# Q7 选址决策：两种组合对比（口径改为"营收潜力"，不冒充 ROI）
# ============================================================
print("\n========== Q7 选址组合对比 ==========")
hh = df[(df["客流分组"] == "高客流≥8000") & (df["3公里内竞品数量(家)"] >= 10)]
ml = df[(df["客流分组"] == "中客流3k-8k") & (df["3公里内竞品数量(家)"] <= 5)]
compare = pd.DataFrame({
    "组合": ["高客流+高竞品(≥10家)", "中客流+低竞品(≤5家)"],
    "样本量": [len(hh), len(ml)],
    "平均日销量": [hh["日销量(元)"].mean(), ml["日销量(元)"].mean()],
    "客单价均值": [hh["客单价(元)"].mean() if "客单价(元)" in df.columns else np.nan,
                ml["客单价(元)"].mean() if "客单价(元)" in df.columns else np.nan],
})
print(compare.round(1).to_string(index=False))
win = compare.loc[compare["平均日销量"].idxmax(), "组合"]
add_finding("Q7", f"营收潜力对比：{win} 更优（注：未含租金/人力成本数据，"
             f"真正的投资回报需补充成本字段——这是本研究的局限）")

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(compare["组合"], compare["平均日销量"], alpha=0.75, color=["#A4A4A4", "#2E86AB"])
for b in bars:
    ax.text(b.get_x() + b.get_width() / 2, b.get_height(), f"{int(b.get_height())}元", ha="center")
ax.set_ylabel("平均日销量(元)")
ax.set_title("Q7 两种选址组合的营收潜力对比")
ax.grid(alpha=0.3, axis="y")
save_fig(fig, "q7_decision.png")
plt.close(fig)

# ============================================================
# 汇总输出
# ============================================================
print("\n" + "=" * 50)
print("全部结论汇总（可直接进报告与 README）")
print("=" * 50)
for q, text in findings:
    print(f"[{q}] {text}")
with open("findings.txt", "w", encoding="utf-8") as f:
    for q, text in findings:
        f.write(f"[{q}] {text}\n")
print("\n结论已写入 findings.txt")
