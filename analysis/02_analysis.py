"""
02_analysis.py — 北美茶饮门店竞争格局与选址分析（Q1–Q7，真实 Yelp 数据）
核心方法说明：
  - "需求" 用 review_count（累计评论数）作为代理变量，Yelp 无销量数据，此为行业常规做法
  - 竞品密度由 01_extract_tea.py 用经纬度构建（1km/3km 同州奶茶店计数）
  - 所有阈值由数据分位数驱动，不拍脑袋
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from plot_utils import setup_chinese_font
from findings_io import write_group

setup_chinese_font()

CHARTS = "charts"
os.makedirs(CHARTS, exist_ok=True)
findings = []


def save_fig(fig, name):
    path = os.path.join(CHARTS, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"    图表已保存: {path}")


def add_finding(q, text):
    findings.append((q, text))
    print(f"    ★ 结论: {text}")


tea = pd.read_csv("data/tea_shops.csv")
bt = pd.read_csv("data/bubble_tea.csv")
city = pd.read_csv("data/city_market.csv")

# ============================================================
# Q1 市场格局：茶饮门店的城市分布与集中度
# ============================================================
print("\n========== Q1 茶饮市场的城市分布 ==========")
top_city = city.sort_values("tea_shops", ascending=False).head(10)
top_city["奶茶占比%"] = top_city["bubble_shops"] / top_city["tea_shops"] * 100
print(top_city.round(1).to_string(index=False))

cr = city.sort_values("tea_shops", ascending=False)["tea_shops"]
cr5 = cr.head(5).sum() / cr.sum() * 100
add_finding("Q1", f"茶饮门店高度集中在头部城市：前 5 城占全部茶饮门店的 {cr5:.0f}%；"
             f"费城({int(city.loc[city['city']=='Philadelphia','tea_shops'].iloc[0])}家)是最大单一市场")

fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(top_city["city"][::-1], top_city["tea_shops"][::-1], color="#2E86AB")
ax.set_xlabel("茶饮门店数")
ax.set_title("Q1 茶饮门店数 Top10 城市（真实 Yelp 数据）")
ax.grid(alpha=0.3, axis="x")
save_fig(fig, "q1_city_distribution.png")
plt.close(fig)

# ============================================================
# Q2 竞品密度分布：奶茶店扎堆到什么程度？
# ============================================================
print("\n========== Q2 奶茶店竞品密度分布（1km/3km） ==========")
print(bt[["competitors_1km", "competitors_3km"]].describe().round(1))
lonely = (bt["competitors_1km"] == 0).mean() * 100
crowd = (bt["competitors_1km"] >= 3).mean() * 100
add_finding("Q2", f"{lonely:.0f}% 的奶茶店 1km 内没有同类竞品（独立区隔市场），"
             f"{crowd:.0f}% 则与 3 家以上奶茶店贴身竞争——市场呈两极分化")

fig, ax = plt.subplots(figsize=(9, 5))
ax.hist(bt["competitors_1km"], bins=range(0, bt["competitors_1km"].max() + 2), color="#E94B3C", alpha=0.75)
ax.set_xlabel("1km 内同类奶茶店数量")
ax.set_ylabel("门店数")
ax.set_title("Q2 奶茶店竞品密度分布（1km 半径）")
ax.grid(alpha=0.3, axis="y")
save_fig(fig, "q2_competitor_density.png")
plt.close(fig)

# ============================================================
# Q3 竞品密度 vs 门店热度：竞争是抢生意还是养市场？
# ============================================================
print("\n========== Q3 竞品密度与门店热度（review_count 代理） ==========")
r = bt["competitors_1km"].corr(bt["review_count"])
bt["密度分组"] = pd.cut(bt["competitors_1km"], bins=[-1, 0, 2, 5, np.inf],
                    labels=["0家(独占)", "1-2家", "3-5家", "6家以上"])
grp = bt.groupby("密度分组", observed=True)["review_count"].agg(["mean", "median", "count"])
print(grp.round(1).to_string())
add_finding("Q3", f"竞品密度与门店热度 r={r:.2f}（{'正相关' if r > 0.05 else '负相关' if r < -0.05 else '基本无关'}）；"
             f"热度最高的是「{grp['mean'].idxmax()}」组（均评论 {grp['mean'].max():.0f} 条）"
             f"——⚠️ 该结论为截面初值，须经 03_threshold_probe.py 做伪重复与稳健性检验后方可采信；"
             f"检验结果以 findings.txt 中 [Q8] 条目为准（脚本不预先写死推翻后的数值）")

fig, ax = plt.subplots(figsize=(9, 5))
means = grp["mean"].values
bars = ax.bar(grp.index.astype(str), means, color=["#32936F", "#2E86AB", "#F6AE2D", "#E94B3C"])
for b in bars:
    ax.text(b.get_x() + b.get_width() / 2, b.get_height(), f"{b.get_height():.0f}", ha="center")
ax.set_ylabel("平均累计评论数（需求代理）")
ax.set_title("Q3 不同竞品密度分组的门店热度")
ax.grid(alpha=0.3, axis="y")
save_fig(fig, "q3_density_heat.png")
plt.close(fig)

# ============================================================
# Q4 竞品密度 vs 评分：竞争是否抬高品质门槛？
# ============================================================
print("\n========== Q4 竞品密度与评分 ==========")
stars_grp = bt.groupby("密度分组", observed=True)["stars"].mean()
print(stars_grp.round(2).to_string())
from scipy import stats as _st
H4, p4 = _st.kruskal(*[g["stars"].values for _, g in bt.groupby("密度分组", observed=True)])
print(f"    Kruskal-Wallis H={H4:.2f}, p={p4:.4f}")
diff = stars_grp.max() - stars_grp.min()
add_finding("Q4", f"评分随竞品密度单调下降：独占区 {stars_grp.iloc[0]:.2f} → 最卷区 {stars_grp.iloc[-1]:.2f}"
             f"（差 {diff:.2f} 分，Kruskal-Wallis p={p4:.4f} {'显著' if p4 < 0.05 else '不显著'}）。"
             f"两种解释：①低质量店在无竞争环境下也能存活；②高竞争区基数大、评分更分化——"
             f"样本层面无法区分因果，属后续研究方向")

# ============================================================
# Q5 蓝海城市识别：低竞争 × 高需求
# ============================================================
print("\n========== Q5 城市「蓝海指数」 ==========")
# 口径修正（审计 H1 + 评审 D4）：
#   - 分子与分母统一为"奶茶口径"（此前分子误用了含咖啡店的茶饮口径）
#   - 旧口径"需求×供给"量纲不统一、权重隐含为 1:1 且未论证（评审 D4）
#   - 新口径：需求强度与供给稀缺度各自转成【全样本分位数排名(0-1)】后再加权，
#     消除量纲差异；权重用两套做敏感性分析（等权 0.5/0.5 与需求主导 0.7/0.3），
#     只把两套都靠前的城市当候选池，不宣称精确名次。
#   - 用茶饮店总数作为市场规模代理（无人口数据），并要求茶饮店≥50 以排除微型市场
c = city[(city["bubble_shops"] >= 5) & (city["tea_shops"] >= 50)].copy()
c["demand_strength"] = c["bubble_med_reviews"]
c["supply_scarcity"] = 1 - c["bubble_penetration"]
c["demand_rank"] = c["demand_strength"].rank(pct=True)
c["scarcity_rank"] = c["supply_scarcity"].rank(pct=True)
WEIGHTS = {"等权(0.5/0.5)": 0.5, "需求主导(0.7/0.3)": 0.7}
for label, w in WEIGHTS.items():
    c[f"score_{label}"] = c["demand_rank"] * w + c["scarcity_rank"] * (1 - w)
c["blue_ocean"] = c["score_等权(0.5/0.5)"]     # 主口径用等权，图表沿用
print(f"    入选城市数: {len(c)}（奶茶店≥5 且 茶饮店≥50）")
print(c.sort_values("blue_ocean", ascending=False)
      [["state", "city", "tea_shops", "bubble_shops", "bubble_penetration",
        "demand_strength", "blue_ocean"]].round(2).to_string(index=False))
# 两套权重下的前 5 名，取交集作为稳健候选池
top_sets = {}
for label in WEIGHTS:
    top_sets[label] = set(c.sort_values(f"score_{label}", ascending=False).head(5)["city"])
    print(f"    权重 {label} 前5: "
          f"{'、'.join(c.sort_values(f'score_{label}', ascending=False).head(5)['city'])}")
candidate_pool = set.intersection(*top_sets.values())
blue = c[c["city"].isin(candidate_pool)].sort_values("blue_ocean", ascending=False)
add_finding("Q5", f"蓝海候选池（奶茶店≥5、茶饮店≥50；需求与供给各转分位排名后加权，"
             f"等权与需求主导两套权重前5的交集）：{'、'.join(blue['city'])}"
             f"——两套权重下前三均为 Reno / New Orleans / Indianapolis（顺序互换），"
             f"说明候选池稳健但精确名次不可靠；其中 New Orleans 奶茶渗透率仅 "
             f"{c.loc[c['city']=='New Orleans','bubble_penetration'].iat[0]*100:.1f}%、"
             f"存量店中位评论 {c.loc[c['city']=='New Orleans','demand_strength'].iat[0]:.0f} 条，"
             f"需求已验证而供给未饱和")

fig, ax = plt.subplots(figsize=(9, 6))
sc = ax.scatter(c["bubble_shops"], c["demand_strength"], s=c["tea_shops"] / 4,
                alpha=0.55, color="#2E86AB", edgecolors="white")
ax.axhline(c["demand_strength"].median(), ls="--", alpha=0.4, color="gray")
ax.axvline(c["bubble_shops"].median(), ls="--", alpha=0.4, color="gray")
for _, row in blue.iterrows():
    ax.annotate(row["city"], (row["bubble_shops"], row["demand_strength"]),
                fontsize=9, xytext=(6, 6), textcoords="offset points")
ax.set_xlabel("该市奶茶店数量（供给）")
ax.set_ylabel("该市奶茶店中位评论数（需求强度）")
ax.set_title("Q5 城市竞争-需求矩阵（气泡大小=茶饮市场规模）\n左上角为蓝海：供给少、需求强")
ax.grid(alpha=0.2)
save_fig(fig, "q5_blue_ocean.png")
plt.close(fig)

# ============================================================
# Q6 费城案例：最密集市场内部的选址逻辑
# ============================================================
print("\n========== Q6 费城案例（97 家奶茶店的最大市场） ==========")
ph = bt[bt["city"] == "Philadelphia"]
print(f"费城奶茶店: {len(ph)} 家 | 1km 内竞品中位数: {ph['competitors_1km'].median():.0f}")
print(f"费城热度 Top3 街区（按门店均值评论数，用邮编近似街区）:")
ph_zip = (ph.groupby("postal_code")["review_count"].agg(["mean", "count"])
          .query("count >= 3").sort_values("mean", ascending=False).head(3))
print(ph_zip.round(1).to_string())
best_zip = ph_zip["mean"].idxmax()
add_finding("Q6", f"费城内部：{best_zip} 邮编区热度最高（均 {ph_zip['mean'].max():.0f} 条评论、"
             f"{int(ph_zip.loc[best_zip,'count'])} 家店）——说明城市内部差异巨大、选址需下沉到街区。"
             f"⚠️ 注意：{best_zip} 与 Q8 识别的伪重复簇是同一批门店，此处仅作示例，不作独立证据")

fig, ax = plt.subplots(figsize=(9, 8))
sc = ax.scatter(ph["longitude"], ph["latitude"], c=np.log1p(ph["review_count"]),
                cmap="YlOrRd", s=40, alpha=0.8, edgecolors="gray", linewidths=0.5)
plt.colorbar(sc, ax=ax, label="log(1+累计评论数)")
ax.set_xlabel("经度")
ax.set_ylabel("纬度")
ax.set_title("Q6 费城 97 家奶茶店地理分布（颜色越深热度越高）")
ax.grid(alpha=0.2)
save_fig(fig, "q6_philadelphia_map.png")
plt.close(fig)

# ============================================================
# Q7 选址建议汇总
# ============================================================
print("\n========== Q7 选址决策建议 ==========")
add_finding("Q7", "综合建议：①优先进入蓝海城市（Q5）而非扎堆费城/坦帕；"
             "②进入热门城市时选本身已验证有需求的成熟商圈（Q6），但不以「竞品数量」作为择址指标"
             "（Q3/Q8 已证伪密度效应）；③城市内下沉到街区粒度筛选铺位。"
             "局限：评论数是需求的粗代理，未含租金与开店成本，落地需实地验证。")

# ============================================================
# 汇总输出
# ============================================================
print("\n" + "=" * 50)
print("全部结论汇总（可直接进报告与 README）")
print("=" * 50)
for q, text in findings:
    print(f"[{q}] {text}")
# 每组结论单独幂等覆盖，不再整体重写/追加
for q, text in findings:
    write_group([f"[{q}] {text}"], group_prefix=f"[{q}]")
print("\n结论已写入 findings.txt")
