# -*- coding: utf-8 -*-
"""面试作品集 PPT V3：克制的商业咨询数据分析风。
硬性配色：茶青灰蓝 #2C4447 / 浅茶棕橙 #D48B5C / 浅米茶白 #F6F5F0 /
正文 #444444 / 注释 #777777。茶饮线稿仅作暗纹与角落点缀，不遮挡信息。
所有分析文字与结论与 V2 完全一致，一字未改。
"""
from pptx import Presentation
from pptx.util import Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from PIL import Image
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "茶饮门店竞争格局与选址分析.pptx")
V3 = os.path.join(HERE, "assets_v3")

PX = 914400 / 96
def px(v): return Emu(int(v * PX))

# ---- 硬性规范配色（禁止新增高饱和色）----
DARK  = RGBColor(0x2C, 0x44, 0x47)   # 主深色：茶青灰蓝
CLAY  = RGBColor(0xD4, 0x8B, 0x5C)   # 强调色：浅茶棕橙
PAPER = RGBColor(0xF6, 0xF5, 0xF0)   # 页面基底：浅米茶白
INK   = RGBColor(0x44, 0x44, 0x44)   # 正文
NOTE  = RGBColor(0x77, 0x77, 0x77)   # 注释
WHITE = RGBColor(0xFF, 0xFF, 0xFF)   # 深色板块上的文字（蒙版保证锐利）
LINE  = RGBColor(0xDC, 0xD8, 0xCE)   # 中性浅灰分隔线（无彩色）
SHADE = RGBColor(0xEF, 0xED, 0xE7)   # 米白底色上的极浅块
# 深色板块上的次要文字：规范主色向白色的低对比过渡（同色系，非新饱和色）
ON_DARK = RGBColor(0xB7, 0xC2, 0xC1)
ON_DARK2 = RGBColor(0x94, 0xA4, 0xA3)
FONT = "微软雅黑"
FONT_NUM = "Arial"

prs = Presentation()
prs.slide_width = px(1280)
prs.slide_height = px(720)
BLANK = prs.slide_layouts[6]
N = 14


def slide(bg=PAPER, bgimg=None):
    s = prs.slides.add_slide(BLANK)
    f = s.background.fill; f.solid(); f.fore_color.rgb = bg
    if bgimg:
        s.shapes.add_picture(os.path.join(V3, bgimg), 0, 0, prs.slide_width, prs.slide_height)
    return s


def box(s, x, y, w, h, fill=None, line=None, lw=0.75):
    shp = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, px(x), px(y), px(w), px(h))
    if fill is None: shp.fill.background()
    else: shp.fill.solid(); shp.fill.fore_color.rgb = fill
    if line is None: shp.line.fill.background()
    else: shp.line.color.rgb = line; shp.line.width = Pt(lw)
    shp.shadow.inherit = False
    return shp


def rule(s, x, y, w, h=1, color=LINE):
    return box(s, x, y, w, max(h, 1), color)


def _set_run(r, size, color, bold, font):
    r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color
    r.font.name = font
    rPr = r._r.get_or_add_rPr()
    ea = rPr.find(qn('a:ea'))
    if ea is None:
        ea = rPr.makeelement(qn('a:ea'), {}); rPr.append(ea)
    ea.set('typeface', font)


def text(s, x, y, w, h, runs, size=18, color=INK, bold=False, align=PP_ALIGN.LEFT,
         font=FONT, spacing=1.25, anchor=MSO_ANCHOR.TOP):
    tb = s.shapes.add_textbox(px(x), px(y), px(w), px(h))
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]; p.alignment = align; p.line_spacing = spacing
    if isinstance(runs, str): runs = [(runs, {})]
    for t, st in runs:
        r = p.add_run(); r.text = t
        _set_run(r, st.get('size', size), st.get('color', color),
                 st.get('bold', bold), st.get('font', font))
    return tb


def paras(s, x, y, w, h, lines, size=17, color=INK, gap=8, spacing=1.3, align=PP_ALIGN.LEFT):
    tb = s.shapes.add_textbox(px(x), px(y), px(w), px(h))
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, (runs, st) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(st.get('gap', gap)); p.line_spacing = st.get('spacing', spacing)
        p.alignment = st.get('align', align)
        if isinstance(runs, str): runs = [(runs, {})]
        for t, rs in runs:
            r = p.add_run(); r.text = t
            _set_run(r, rs.get('size', st.get('size', size)),
                     rs.get('color', st.get('color', color)),
                     rs.get('bold', st.get('bold', False)),
                     rs.get('font', st.get('font', FONT)))
    return tb


def kicker(s, x, y, label, color=CLAY, w=560):
    text(s, x, y, w, 24, label, size=12.5, color=color, bold=True, font=FONT_NUM, spacing=1.0)


def head(s, title, y=58, size=33, w=1120, color=DARK):
    text(s, 60, y, w, 52, title, size=size, color=color, bold=True, spacing=1.18)


def footer(s, page, note="数据来源：Yelp Open Dataset（2018/2022 快照）"):
    rule(s, 60, 668, 1160, 1, LINE)
    text(s, 60, 678, 900, 20, note, size=11.5, color=NOTE)
    text(s, 1080, 678, 140, 20, f"{page:02d} / {N}", size=11.5, color=NOTE,
         align=PP_ALIGN.RIGHT, font=FONT_NUM)


def motif(s, name, x, y, w):
    """角落线稿点缀：极淡、不遮挡任何信息。"""
    p = os.path.join(V3, name)
    iw, ih = Image.open(p).size
    s.shapes.add_picture(p, px(x), px(y), px(w), px(round(w * ih / iw)))


def evcard(s, name, x, y, w, tag):
    """证据区：无边框、无色条、无阴影——只有角标 + 图，突出数据本身。"""
    p = os.path.join(V3, name)
    iw, ih = Image.open(p).size
    ch = round(w * ih / iw)
    text(s, x, y, w, 20, tag, size=10.5, color=NOTE, font=FONT_NUM, spacing=1.0)
    s.shapes.add_picture(p, px(x), px(y + 30), px(w), px(ch))
    return ch + 30


def bignum(s, x, y, w, num, label, num_color=CLAY, num_size=66, label_size=15, align=PP_ALIGN.LEFT):
    text(s, x, y, w, num_size * 1.5, num, size=num_size, color=num_color,
         bold=True, font=FONT_NUM, spacing=1.0, align=align)
    text(s, x, y + num_size * 1.42, w, 28, label, size=label_size, color=NOTE, align=align)


def verdict(s, y, lead, body, accent=CLAY, h=50):
    """判断条：去掉底色块与阴影，仅留左侧色线 + 文字。"""
    box(s, 60, y, 4, h, accent)
    text(s, 80, y + 4, 150, h - 8, lead, size=15, color=accent, bold=True,
         anchor=MSO_ANCHOR.MIDDLE)
    text(s, 212, y + 2, 992, h - 4, body, size=15.5, color=INK,
         anchor=MSO_ANCHOR.MIDDLE, spacing=1.2)


def section(s, num, name, desc, page):
    # 背景已由 slide(bgimg="bg_section.png") 提供：茶青灰蓝 + 同色系线稿暗纹 + 蒙版
    text(s, 80, 236, 150, 34, "CHAPTER", size=12, color=CLAY, bold=True, font=FONT_NUM)
    rule(s, 80, 282, 92, 2, CLAY)
    text(s, 76, 306, 720, 96, name, size=54, color=WHITE, bold=True, spacing=1.1)
    text(s, 80, 426, 660, 56, desc, size=20, color=ON_DARK, spacing=1.35)
    # 超大数字：同色系暗纹的一部分，极低对比，不抢标题
    text(s, 830, 120, 380, 480, num, size=250, color=RGBColor(0x35, 0x4F, 0x52),
         bold=True, font=FONT_NUM, align=PP_ALIGN.RIGHT, spacing=1.0)
    text(s, 80, 654, 400, 24, "tea-market-analysis  ·  面试作品集", size=12,
         color=ON_DARK2)
    text(s, 1080, 654, 140, 24, f"{page:02d} / {N}", size=12,
         color=ON_DARK2, align=PP_ALIGN.RIGHT, font=FONT_NUM)


# ================= P1 封面 =================
s = slide(PAPER)
# 左栏：茶青灰蓝底 + 同色系线稿暗纹 + 蒙版（背景图已合成，白色标题锐利）
s.shapes.add_picture(os.path.join(V3, "bg_cover_left.png"), 0, 0, px(452), px(720))
box(s, 452, 0, 2, 720, CLAY)
text(s, 52, 62, 360, 26, "DATA ANALYTICS  /  PORTFOLIO", size=12,
     color=ON_DARK, bold=True, font=FONT_NUM)
text(s, 48, 176, 380, 300,
     [("茶饮门店", {}), ("\n竞争格局与", {}), ("\n选址分析", {})],
     size=46, color=WHITE, bold=True, spacing=1.16)
rule(s, 52, 498, 80, 2, CLAY)
text(s, 52, 520, 360, 84,
     "真实数据 · 自建特征 · 自我推翻", size=15,
     color=ON_DARK, spacing=1.4)
text(s, 52, 650, 360, 24, "潘约翰  |  2026", size=12.5,
     color=ON_DARK2, font=FONT_NUM)
# 右栏
text(s, 560, 210, 660, 150,
     [("竞品数量是优质商圈的", {}), ("\n症状，不是病因", {"color": CLAY})],
     size=36, color=DARK, bold=True, spacing=1.3)
rule(s, 560, 392, 660, 1, LINE)
para_items = [
    ("150,346", "家真实商户样本", DARK),
    ("477", "家奶茶门店为分析主体", DARK),
    ("11", "个蓝海候选城市", CLAY),
]
y = 424
for n, lab, c in para_items:
    text(s, 560, y, 210, 46, n, size=32, color=c, bold=True, font=FONT_NUM)
    text(s, 782, y + 7, 436, 34, lab, size=16, color=INK)
    y += 66
# 右下角极淡线稿点缀（不遮挡信息）
motif(s, "motif_cup.png", 1130, 596, 110)

# ================= P2 目录 =================
s = slide(PAPER)
kicker(s, 60, 58, "CONTENTS")
head(s, "四个部分，讲清一个决策问题", y=92, size=34)
rule(s, 60, 158, 1160, 1, LINE)
toc = [
    ("01", "背景与数据", "真实商户替代模拟数据，竞品密度用经纬度自建", CLAY),
    ("02", "核心发现", "市场集中、竞争两极分化，一个漂亮结论被推翻", DARK),
    ("03", "稳健性与边界", "换半径、做 bootstrap，检验结论是否站得住", DARK),
    ("04", "结论", "先选市场、再选商圈，不把竞品数量当信号", CLAY),
]
y = 196
for num, name, desc, c in toc:
    text(s, 60, y, 110, 64, num, size=44, color=c, bold=True, font=FONT_NUM, spacing=1.0)
    text(s, 186, y + 2, 330, 42, name, size=26, color=DARK, bold=True)
    text(s, 186, y + 46, 900, 32, desc, size=16, color=INK)
    rule(s, 60, y + 92, 1160, 1, LINE)
    y += 116
motif(s, "motif_leaf.png", 1100, 596, 120)
footer(s, 2)

# ================= P3 章节 01 =================
s = slide(bgimg="bg_section.png")
section(s, "01", "背景与数据", "真实数据、自建特征，以及天然缺失的那一块", 3)

# ================= P4 数据底座 =================
s = slide()
kicker(s, 60, 52, "01  /  DATA FOUNDATION")
head(s, "用真实商户数据回答选址问题，而不是模拟数据", y=88, size=31)
rule(s, 60, 152, 1160, 1, LINE)
text(s, 60, 178, 520, 30, "要回答的三个问题", size=15, color=NOTE, bold=True)
qs = [("Q1", "市场格局", "茶饮门店集中在哪些城市"),
      ("Q2", "竞争效应", "周边竞品越多，生意越差吗"),
      ("Q3", "选址决策", "哪些市场需求已验证、供给未饱和")]
y = 216
for tag, t, d in qs:
    text(s, 60, y, 74, 40, tag, size=23, color=CLAY, bold=True, font=FONT_NUM)
    text(s, 142, y - 1, 430, 34, t, size=20, color=DARK, bold=True)
    text(s, 142, y + 32, 430, 30, d, size=15, color=INK)
    rule(s, 60, y + 72, 540, 1, LINE)
    y += 90
text(s, 660, 178, 560, 30, "数据底座 / Yelp Open Dataset", size=15, color=NOTE, bold=True)
funnel = [("150,346", "商户总数", 560, DARK),
          ("7,069", "茶饮门店（三类业态）", 470, RGBColor(0x3A, 0x56, 0x59)),
          ("477", "奶茶店 · 分析主体", 380, CLAY)]
y = 218
for i, (n, lab, w, c) in enumerate(funnel):
    x = 660 + (560 - w) / 2
    box(s, x, y, w, 84, c)
    text(s, x, y + 7, w, 44, n, size=35, color=WHITE, bold=True,
         font=FONT_NUM, align=PP_ALIGN.CENTER, spacing=1.0)
    text(s, x, y + 54, w, 24, lab, size=14, color=WHITE, align=PP_ALIGN.CENTER)
    y += 95
text(s, 660, 500, 560, 72,
     "覆盖 8 个都市圈、15 州/省。无销量、无开店日期——需求只能用累计评论数代理。",
     size=15, color=INK, spacing=1.4)
verdict(s, 606, "关键前提",
        "竞品密度数据里没有，必须用经纬度自己算；需求是代理变量，结论要讲边界。")

# ================= P5 Q1 市场集中 =================
s = slide()
kicker(s, 60, 50, "02  /  FINDING 01")
head(s, "市场高度集中：前 5 城占 34%", y=84, size=32)
rule(s, 60, 148, 1160, 1, LINE)
evcard(s, "q1_city_distribution.png", 60, 182, 690, "EVIDENCE  /  茶饮门店 TOP10 城市")
bignum(s, 806, 200, 400, "956", "家茶饮门店 · 费城（最大单一市场）", num_color=CLAY, num_size=82)
rule(s, 806, 384, 400, 1, LINE)
paras(s, 806, 398, 400, 168, [
    ([("前 5 城占 34%", {"bold": True, "color": DARK, "size": 19})], {}),
    ([("头部市场值得优先进入。但城市字段由用户填写，同一都市圈可能被拆成多个城市（费城 / Cherry Hill）。", {})], {"size": 15, "color": INK}),
    ([("集中度数字受口径影响，非精确市占率。", {"color": NOTE})], {"size": 14.5}),
], gap=9, spacing=1.25)
verdict(s, 608, "判断", "先锁定头部市场，但不把这个百分比当成精确市占率。")
footer(s, 5)

# ================= P6 Q2 两极分化 =================
s = slide()
kicker(s, 60, 50, "02  /  FINDING 02")
head(s, "竞争呈两极分化，不能用“平均竞品数”描述", y=84, size=31)
rule(s, 60, 148, 1160, 1, LINE)
evcard(s, "q2_competitor_density.png", 60, 180, 632, "EVIDENCE  /  1km 内竞品数分布")
bignum(s, 748, 186, 460, "38%", "门店 1km 内零竞品 · 独立区隔市场", num_color=DARK, num_size=76)
rule(s, 748, 348, 460, 1, LINE)
bignum(s, 748, 366, 460, "30%", "门店 1km 内 ≥3 家 · 贴身竞争", num_color=CLAY, num_size=76)
rule(s, 748, 528, 460, 1, LINE)
text(s, 748, 544, 460, 56,
     "密度用 Haversine 球面距离自建：0.5 / 1 / 2 / 3km 四档，同州掩码避免跨界误计。1km≈步行 10 分钟商圈。",
     size=14.5, color=INK, spacing=1.35)
verdict(s, 608, "判断", "市场不是均匀的，必须分组看——这是后面所有分析的起点。")
footer(s, 6)

# ================= P7 章节 02 =================
s = slide(bgimg="bg_section.png")
section(s, "02", "核心发现", "一个被推翻的漂亮结论，和它背后的真正机制", 7)

# ================= P8 伪重复（核心页） =================
s = slide()
kicker(s, 60, 46, "02  /  THE TURNING POINT")
head(s, "初版结论“竞品越多越火”是假的", y=74, size=32, color=CLAY)
text(s, 60, 132, 1120, 26, "细粒度曲线非单调；23 家高密度店全部挤在费城唐人街一个街区。",
     size=15, color=INK)
evcard(s, "q8_threshold.png", 60, 180, 1080, "EVIDENCE  /  全样本曲线 · 剔除簇后 · 费城内对照")
tri = [
    ("相关系数 r", "0.19 → 0.016", DARK),
    ("分组差异 p", "0.049 → 0.76", DARK),
    ("高密度店来源", "19107 · 23 家", CLAY),
]
y = 528
for i, (lab, val, c) in enumerate(tri):
    x = 60 + i * 392
    rule(s, x, y, 360, 2, c)
    text(s, x, y + 10, 360, 24, lab, size=13, color=NOTE)
    text(s, x, y + 36, 368, 40, val, size=25, color=c, bold=True, font=FONT_NUM)
verdict(s, 618, "关键",
        "23 家本质是 1 个观测（均评论 186 vs 费城其他 56）。竞品数量是优质商圈的症状，不是病因。",
        accent=CLAY, h=46)
footer(s, 8, "口径：剔除 competitors_1km ≥ 20 的伪重复簇后重算；Mann-Whitney p<0.001")

# ================= P9 评分梯度幸存 =================
s = slide()
kicker(s, 60, 50, "02  /  FINDING 03")
head(s, "同一个检验，一个被推翻、一个幸存", y=84, size=32)
rule(s, 60, 148, 1160, 1, LINE)
box(s, 60, 178, 548, 328, SHADE)
box(s, 60, 178, 548, 4, CLAY)
text(s, 88, 200, 490, 34, "被推翻  ·  热度结论", size=21, color=CLAY, bold=True)
text(s, 88, 248, 490, 58, "r  0.19 → 0.016", size=35, color=DARK, bold=True, font=FONT_NUM)
paras(s, 88, 326, 492, 168, [
    ([("剔除唐人街簇后相关性归零，分组差异 p 从 0.049 升到 0.76。", {})], {"size": 16}),
    ([("密度不提升需求——初版判断被自己的检验推翻。", {"bold": True, "color": DARK})], {"size": 16}),
], gap=14)
box(s, 620, 178, 600, 328, SHADE)
box(s, 620, 178, 600, 4, DARK)
text(s, 648, 200, 544, 34, "幸存  ·  评分结论", size=21, color=DARK, bold=True)
text(s, 648, 248, 544, 58, "p  0.0001 → 0.0017", size=34, color=DARK, bold=True, font=FONT_NUM)
paras(s, 648, 326, 544, 168, [
    ([("独占区 4.18 → 最卷区 3.86，剔除簇后仍显著（H=15.19）。", {})], {"size": 16}),
    ([("评分分化是全样本现象，不是单一街区伪造的。", {"bold": True, "color": DARK})], {"size": 16}),
], gap=14)
verdict(s, 528, "诚实的价值",
        "同样的样本、同样的检验流程，一个被推翻、一个幸存——说明检验不是走过场。",
        accent=DARK, h=48)
text(s, 60, 596, 1160, 44,
     "评分下降的两种机制（低质店在无竞争区存活 / 高竞争区评分更分化）单期截面无法区分，属后续研究方向。",
     size=14, color=NOTE, spacing=1.3)
footer(s, 9)

# ================= P10 蓝海 =================
s = slide()
kicker(s, 60, 50, "02  /  FINDING 04")
head(s, "蓝海候选池 11 城：前三名排序稳定", y=84, size=32)
rule(s, 60, 148, 1160, 1, LINE)
evcard(s, "q5_blue_ocean.png", 60, 174, 560, "EVIDENCE  /  需求 × 供给气泡图")
text(s, 648, 178, 572, 30, "蓝海指数（口径已统一）", size=15, color=NOTE, bold=True)
text(s, 648, 212, 572, 60, "需求强度 ×（1 − 奶茶渗透率）", size=19, color=DARK, bold=True, spacing=1.3)
rule(s, 648, 288, 572, 1, LINE)
text(s, 648, 302, 572, 28, "bootstrap 1000 次 · 进前三概率", size=14.5, color=NOTE)
ranks = [("01", "Reno", "87%", CLAY), ("02", "New Orleans", "82%", DARK), ("03", "Indianapolis", "79%", DARK)]
y = 338
for num, city, pct, c in ranks:
    text(s, 648, y, 60, 34, num, size=22, color=c, bold=True, font=FONT_NUM)
    text(s, 712, y, 360, 34, city, size=19, color=DARK, bold=True)
    text(s, 1118, y, 102, 34, pct, size=20, color=c, bold=True,
         font=FONT_NUM, align=PP_ALIGN.RIGHT)
    rule(s, 648, y + 42, 572, 1, LINE)
    y += 56
text(s, 648, 520, 572, 60,
     "入选门槛：奶茶店≥5、茶饮店≥50。口径修正后候选池从 18 城收敛到 11 城。",
     size=14.5, color=INK, spacing=1.35)
verdict(s, 608, "边界", "只能讲“候选池排名”，不能讲“第一名绝对最好”。")
footer(s, 10)

# ================= P11 街区粒度 =================
s = slide()
kicker(s, 60, 50, "02  /  FINDING 05")
head(s, "城市内部差异巨大，选址必须下沉到街区", y=84, size=31)
rule(s, 60, 148, 1160, 1, LINE)
evcard(s, "q6_philadelphia_map.png", 60, 174, 400, "EVIDENCE  /  费城奶茶店地理分布")
text(s, 512, 180, 706, 36, "费城 19107：需求被验证的样本", size=21, color=DARK, bold=True)
rule(s, 512, 228, 706, 2, CLAY)
paras(s, 512, 248, 706, 300, [
    ([("23 家奶茶店聚集，均评论 186 条——城市内部的热度差异远大于城市之间。", {})], {"size": 17}),
    ([("但这批店与 Q8 的伪重复簇是同一批：热度高说明需求存在，也可能意味着市场接近饱和。", {})], {"size": 17}),
    ([("正确用法", {"bold": True, "color": DARK}),
      ("：先确认“这里有被验证的需求”，再叠加竞品间距、租金、铺位可得性做二次筛选。", {})], {"size": 17}),
], gap=18, spacing=1.4)
verdict(s, 600, "不推荐", "数据给方向，不给最终答案——不直接推荐在 19107 开店。")
footer(s, 11, "口径：费城奶茶店经纬度散点，颜色越深表示累计评论数越高")

# ================= P12 章节 03 =================
s = slide(bgimg="bg_section.png")
section(s, "03", "稳健性与边界", "结论能不能对外讲，取决于它经不经得起折腾", 12)

# ================= P13 稳健性 =================
s = slide()
kicker(s, 60, 50, "03  /  ROBUSTNESS")
head(s, "结论不依赖参数选择，也不依赖单一城市排名", y=84, size=30)
rule(s, 60, 148, 1160, 1, LINE)
evcard(s, "q9_robustness.png", 60, 168, 900, "EVIDENCE  /  半径敏感性 · bootstrap 稳定性")
rule(s, 60, 530, 560, 2, DARK)
text(s, 60, 540, 560, 24, "半径敏感性 · 剔除簇后 r", size=13, color=NOTE)
text(s, 60, 564, 560, 42, "0.046  /  0.016  /  −0.028", size=24, color=DARK, bold=True, font=FONT_NUM)
rule(s, 660, 530, 560, 2, CLAY)
text(s, 660, 540, 560, 24, "bootstrap 进前三概率", size=13, color=NOTE)
text(s, 660, 564, 560, 42, "Reno 87%  ·  NOLA 82%", size=24, color=CLAY, bold=True, font=FONT_NUM)
text(s, 60, 620, 1160, 38,
     "三档半径（0.5/1/2km）下 p 均 >0.05，“密度不提升需求”稳健；但评论数是累计值，含资历偏差——老店天然占优，这是 V2 首要待办。",
     size=13.5, color=NOTE, spacing=1.25)
footer(s, 13)

# ================= P14 结尾 =================
s = slide(bgimg="bg_ending.png")
box(s, 0, 0, 1280, 6, CLAY)
text(s, 76, 78, 1120, 86, "别怕竞品，别信竞品", size=60, color=WHITE, bold=True, spacing=1.1)
rule(s, 76, 182, 110, 3, CLAY)
text(s, 76, 206, 1100, 44, "先选市场，再选商圈，不把竞品数量当信号", size=23,
     color=ON_DARK)
steps = [("01", "选市场", "优先进入需求旺、奶茶店少的蓝海候选池"),
         ("02", "选商圈", "进入需求已被验证的成熟商圈，但不追竞品数量"),
         ("03", "筛铺位", "下沉到街区粒度，叠加租金与铺位可得性")]
y = 306
for num, t, d in steps:
    text(s, 78, y, 90, 52, num, size=33, color=CLAY, bold=True, font=FONT_NUM)
    text(s, 176, y + 2, 200, 44, t, size=24, color=WHITE, bold=True)
    text(s, 392, y + 8, 800, 38, d, size=17, color=ON_DARK)
    rule(s, 78, y + 58, 1120, 1, RGBColor(0x3A, 0x56, 0x59))
    y += 84
text(s, 78, 654, 900, 26,
     "限制：缺租金与开店成本，结论只谈需求侧，落地需实地验证。",
     size=13, color=ON_DARK2)
text(s, 1080, 654, 140, 26, f"{N:02d} / {N}", size=13,
     color=ON_DARK2, align=PP_ALIGN.RIGHT, font=FONT_NUM)

prs.save(OUT)
print("已生成:", OUT)
print("页数:", len(prs.slides._sldIdLst))
