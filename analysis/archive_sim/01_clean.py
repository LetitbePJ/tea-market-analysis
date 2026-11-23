"""
01_clean.py — 奶茶门店数据清洗与画像
输入: data/milk_tea_raw.csv（课程实训模拟数据集）
输出: data/clean_milk_tea.csv + 控制台数据画像
"""
import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

RAW = "data/milk_tea_raw.csv"
OUT = "data/clean_milk_tea.csv"

df = pd.read_csv(RAW, encoding="utf-8-sig")
print(f"[0] 原始数据：{df.shape[0]:,} 行 × {df.shape[1]} 列")
print("字段：", list(df.columns))

# ---------- 1. 关键字段缺失处理 ----------
# 日销量 / 客流密度是全部分析的因变量与核心自变量，缺失即无分析价值 → 删行
before = len(df)
df = df.dropna(subset=["日销量(元)", "周边客流密度(人次/天)"])
print(f"[1] 关键字段缺失：删除 {before - len(df):,} 行")

# ---------- 2. 温度缺失：用同季节均值填充 ----------
# 理由：温度缺失多为零星缺失，同季节均值是比整体均值更合理的估计；在报告中披露该方法
n_temp_na = df["日均温度(℃)"].isnull().sum()
season_mean = df.groupby("季节(编码)")["日均温度(℃)"].mean()
df["日均温度(℃)"] = df["日均温度(℃)"].fillna(
    df["季节(编码)"].map(season_mean)
)
print(f"[2] 温度缺失：按同季节均值填充 {n_temp_na:,} 行")

# ---------- 3. 去重：门店+日期 唯一 ----------
before = len(df)
df = df.drop_duplicates(subset=["门店ID", "日期"], keep="first")
print(f"[3] 去重：删除 {before - len(df):,} 行（同店同日重复记录）")

# ---------- 4. 编码 → 中文标签 ----------
df["门店位置类型"] = df["门店位置类型(编码)"].map({1: "商场店", 2: "街边店", 3: "校园店", 4: "社区店"})
df["日期类型"] = df["日期类型(编码)"].map({1: "工作日", 2: "周末", 3: "法定节假日"})
df["季节"] = df["季节(编码)"].map({1: "春季", 2: "夏季", 3: "秋季", 4: "冬季"})

# ---------- 5. 数据画像 ----------
profile = {
    "清洗后行数": f"{len(df):,}",
    "门店数": df["门店ID"].nunique(),
    "城市数": df["城市"].nunique() if "城市" in df.columns else "字段不存在，以实际为准",
    "时间范围": f"{df['日期'].min()} ~ {df['日期'].max()}",
    "日销量均值": f"{df['日销量(元)'].mean():,.0f} 元",
    "日销量中位数": f"{df['日销量(元)'].median():,.0f} 元",
    "客流密度均值": f"{df['周边客流密度(人次/天)'].mean():,.0f} 人次/天",
    "竞品数量分布": df["3公里内竞品数量(家)"].describe().round(1).to_dict(),
}
print("\n[5] 数据画像")
for k, v in profile.items():
    print(f"    {k}: {v}")

df.to_csv(OUT, index=False, encoding="utf-8-sig")
print(f"\n已输出：{OUT}")
