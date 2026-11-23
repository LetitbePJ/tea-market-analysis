"""
01_extract_tea.py — 从 Yelp 开放数据中提取茶饮门店并构建竞品密度特征
数据来源: Yelp Open Dataset (官方公开数据集, https://www.yelp.com/dataset)
说明: 原始数据不提供"周边竞品数量"字段，本脚本用经纬度 + Haversine 公式
      自行计算每家门店周边竞品密度——这是真实数据分析工作中的特征构建环节。

输入: data/yelp_business.parquet (150,346 家真实商户)
输出: data/tea_shops.csv          (清洗后的茶饮门店表，含竞品密度特征)
"""
import numpy as np
import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

RAW = "data/yelp_business.parquet"
OUT = "data/tea_shops.csv"

df = pd.read_parquet(RAW)
print(f"[0] Yelp 原始商户: {len(df):,} 家")
print("    字段:", list(df.columns))

# ---------- 1. 提取茶饮相关门店 ----------
# 三类茶饮业态：Bubble Tea(奶茶) / Coffee & Tea(咖啡茶饮综合) / Tea Rooms(茶室)
mask = df["categories"].astype(str).str.contains(
    "Bubble Tea|Coffee & Tea|Tea Rooms", na=False)
tea = df[mask].copy()
print(f"[1] 茶饮相关门店: {len(tea):,} 家")
tea["is_bubble_tea"] = tea["categories"].astype(str).str.contains("Bubble Tea")
print(f"    其中奶茶店(Bubble Tea): {tea['is_bubble_tea'].sum()} 家")

# ---------- 2. 清洗 ----------
before = len(tea)
tea = tea.drop_duplicates(subset=["business_id"])
print(f"[2] 按 business_id 去重: 删除 {before - len(tea)} 行")

# 经纬度缺失无法计算地理特征 → 删行并披露
n_no_geo = tea[["latitude", "longitude"]].isnull().any(axis=1).sum()
tea = tea.dropna(subset=["latitude", "longitude"])
print(f"    经纬度缺失删行: {n_no_geo}")

# review_count=0 的门店无需求信号（可能是新店/歇业店），保留但单独标记
tea["has_reviews"] = tea["review_count"] > 0

# 城市/州字段规范化（Yelp 用户填写，有大小写混杂）
tea["city"] = tea["city"].str.strip().str.title()
tea["state"] = tea["state"].str.strip().str.upper()

# ---------- 3. 特征构建: Haversine 竞品密度 ----------
# 定义: 对每家奶茶店，统计同州其他奶茶店中距离 ≤1km / ≤3km 的数量。
# 注: 1km ≈ 步行 10 分钟商圈, 3km ≈ 原项目定义的直接竞品商圈
def haversine_matrix(lat1, lon1, lat2, lon2):
    """向量化的 Haversine 球面距离（公里）"""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))

bt = tea[tea["is_bubble_tea"]].reset_index(drop=True)
lat = bt["latitude"].to_numpy(dtype=float)
lon = bt["longitude"].to_numpy(dtype=float)
states = bt["state"].astype(str).to_numpy()
same_state = states[:, None] == states[None, :]

# 477x477 距离矩阵，一次算完（内存 < 2MB）
dist = haversine_matrix(lat[:, None], lon[:, None], lat[None, :], lon[None, :])
np.fill_diagonal(dist, np.inf)          # 排除自己
# 多档半径：0.5km≈社区级、1km≈步行商圈、2km≈片区级、3km≈城市级
for r_km, col in [(0.5, "competitors_500m"), (1, "competitors_1km"),
                  (2, "competitors_2km"), (3, "competitors_3km")]:
    bt[col] = ((dist <= r_km) & same_state).sum(axis=1)

print(f"[3] 竞品密度特征构建完成（0.5/1/2/3km 四档）")
print("    1km 内竞品数分布:", bt["competitors_1km"].describe().round(1).to_dict())
print("    2km 内竞品数分布:", bt["competitors_2km"].describe().round(1).to_dict())
print("    3km 内竞品数分布:", bt["competitors_3km"].describe().round(1).to_dict())

# ---------- 4. 城市/州级市场表（供蓝海分析用） ----------
# 注意口径：茶饮口径(tea_*)与奶茶口径(bubble_*)必须分开统计，
# 蓝海指数必须用同一口径的分子分母（详见 04_robustness.py 说明）
city_all = (tea.groupby(["state", "city"])
            .agg(tea_shops=("business_id", "count"),
                 tea_med_reviews=("review_count", "median"))
            .reset_index())
city_bt = (bt.groupby(["state", "city"])
           .agg(bubble_shops=("business_id", "count"),
                bubble_med_reviews=("review_count", "median"),
                bubble_avg_stars=("stars", "mean"),
                bubble_mean_comp=("competitors_1km", "mean"))
           .reset_index())
city_mkt = city_all.merge(city_bt, on=["state", "city"], how="left")
city_mkt[["bubble_shops"]] = city_mkt[["bubble_shops"]].fillna(0)
city_mkt["bubble_shops"] = city_mkt["bubble_shops"].astype(int)
# 奶茶渗透率 = 奶茶店 / 茶饮店（衡量"该市奶茶供给相对市场规模是否饱和"）
city_mkt["bubble_penetration"] = (city_mkt["bubble_shops"]
                                  / city_mkt["tea_shops"]).round(3)
city_mkt = city_mkt.sort_values("tea_shops", ascending=False)
print(f"[4] 城市-州市场表: {len(city_mkt)} 个城市")

# ---------- 5. 输出 ----------
tea.to_csv(OUT, index=False, encoding="utf-8-sig")
city_mkt.to_csv("data/city_market.csv", index=False, encoding="utf-8-sig")
bt.to_csv("data/bubble_tea.csv", index=False, encoding="utf-8-sig")
print("\n已输出: data/tea_shops.csv, data/bubble_tea.csv, data/city_market.csv")

print("\n=== 数据画像 ===")
print(f"茶饮门店总数: {len(tea):,} | 奶茶店: {len(bt)}")
print(f"覆盖州数: {tea['state'].nunique()} | 覆盖城市: {tea['city'].nunique()}")
print(f"奶茶店评分均值: {bt['stars'].mean():.2f} | 中位评论数: {bt['review_count'].median():.0f}")
print(f"奶茶店最多的城市: {bt['city'].value_counts().head(5).to_dict()}")
