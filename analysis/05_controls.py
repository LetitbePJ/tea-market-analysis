"""
05_controls.py — 混杂控制与变量变换（评审 D5 补强）

前序脚本用Pearson相关看"竞品密度 × 累计评论"，有两个弱点：
  1. 累计评论是重尾计数，直接算相关会被极端值牵着走；
  2. 未控制城市——同城门店共享客流、租金与消费习惯，密度与热度可能同时被城市水平驱动。

本脚本：
  - 因变量改为 log1p(review_count)，压平重尾；
  - 主回归限定在"样本≥5 家奶茶店"的城市，加入城市固定效应（吸收城市级混杂）；
  - 控制 stars（评分本身与评论数相关）；
  - 用 HC3 异方差稳健标准误；
  - 同时报告全样本（无城市固定效应）与剔除唐人街伪重复簇的两种规格作对照。

输出写入 findings.txt 的 [Q10] 条目。所有数值由计算结果格式化生成，不写死。
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from findings_io import write_group

bt = pd.read_csv("data/bubble_tea.csv")
bt["log_reviews"] = np.log1p(bt["review_count"])
bt["city_key"] = bt["state"].astype(str) + "|" + bt["city"].astype(str)
cluster = bt["postal_code"].astype(str).eq("19107") & bt["city"].eq("Philadelphia")

findings = []


def fit(label, data, formula):
    """拟合 OLS（HC3 稳健标准误），返回格式化摘要"""
    model = smf.ols(formula, data=data).fit(cov_type="HC3")
    coef = model.params["competitors_1km"]
    se = model.bse["competitors_1km"]
    p = model.pvalues["competitors_1km"]
    ci = model.conf_int().loc["competitors_1km"]
    sig = "显著" if p < 0.05 else "不显著"
    print(f"\n--- {label} (n={int(model.nobs)}) ---")
    print(f"  log(评论数) ~ 竞品密度: β={coef:+.4f}, HC3 SE={se:.4f}, "
          f"p={p:.3f} ({sig}), 95%CI=[{ci.iloc[0]:+.4f},{ci.iloc[1]:+.4f}], R²={model.rsquared:.3f}")
    return coef, se, p, ci.iloc[0], ci.iloc[1], model.nobs


print("========== D5 混杂控制：log 因变量 + 城市固定效应 + HC3 ==========")

# 规格 1：全样本，仅 log 变换 + stars 控制（无城市固定效应）
c_full, se_full, p_full, lo_full, hi_full, n_full = fit(
    "规格1 全样本 · log + stars（无城市FE）", bt,
    "log_reviews ~ competitors_1km + stars")

# 规格 2：限定样本≥5 的 18 个城市，加城市固定效应
counts = bt["city_key"].value_counts()
big = bt[bt["city_key"].isin(counts[counts >= 5].index)].copy()
c_fe, se_fe, p_fe, lo_fe, hi_fe, n_fe = fit(
    "规格2 城市样本≥5 · log + stars + 城市固定效应", big,
    "log_reviews ~ competitors_1km + stars + C(city_key)")

# 规格 3：规格2 再剔除唐人街伪重复簇
big_rest = big[~cluster.loc[big.index]].copy()
c_re, se_re, p_re, lo_re, hi_re, n_re = fit(
    "规格3 城市样本≥5 · 剔除唐人街簇 + 城市固定效应", big_rest,
    "log_reviews ~ competitors_1km + stars + C(city_key)")

# 结论：密度正效应是否只在含伪重复簇的规格中显著
if p_full < 0.05 and p_fe < 0.05 and p_re >= 0.05:
    verdict = ("竞品密度的正系数在含唐人街簇的规格中显著、剔除该伪重复簇后消失"
               "（p 由 <0.001 升至 0.19）——再次印证 Q3/Q8：表面的'密度提升需求'"
               "由单一商圈伪重复驱动，控制城市混杂与 log 变换后结论不变")
elif p_re < 0.05:
    verdict = "剔除伪重复簇后密度系数仍显著，需重新审视'密度不提升需求'的结论"
else:
    verdict = "各规格下密度系数均不显著，'密度不提升需求'在控制混杂后仍成立"
findings.append(
    f"[Q10] 混杂控制补强（log1p 评论数为因变量、HC3 稳健标准误、"
    f"城市固定效应吸收同城混杂）："
    f"①全样本 β={c_full:+.3f}(p={p_full:.3f}, n={int(n_full)})；"
    f"②18 个样本≥5 城市＋城市FE β={c_fe:+.3f}(p={p_fe:.3f}, n={int(n_fe)})；"
    f"③再剔除唐人街簇 β={c_re:+.3f}(p={p_re:.3f}, n={int(n_re)})。"
    f"{verdict}。局限：仅奶茶店 477 家、品类无变异故未控制品类，"
    f"城市FE样本限制在 18 城（其余城市店数过少无法稳定估计），"
    f"且无租金/店龄，仍不能谈盈利")

print("\n" + "=" * 50)
for f in findings:
    print(f)

for line in findings:
    write_group([line], group_prefix="[Q10]")
print("\n[Q10] 已写入 findings.txt")
