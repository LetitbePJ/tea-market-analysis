# -*- coding: utf-8 -*-
"""面试作品集 PPT V4：清爽松弛的商业分析报告风。
新硬性配色：浅茶米白 #F5F3EE / 低饱和茶灰绿 #384A48（仅小范围）/
哑光浅茶棕 #947C6B（少量）/ 正文 #424242 / 注释 #757575。
全页铺满低透明茶饮线稿肌理；文字框与图表区叠加半透米白蒙版托出前景。
深色只用于窄条、编号块、标题小色块、重点指标；无大面积深色、无橙色、无阴影边框。
所有分析文字与结论与 V3 完全一致，一字未改。
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
A = os.path.join(HERE, "assets_v4")

PX = 914400 / 96
def px(v): return Emu(int(v * PX))

# ---- 新硬性规范配色 ----
DARK  = RGBColor(0x38, 0x4A, 0x48)   # 茶灰绿：仅小范围（窄条/编号块/标题小色块）
CLAY  = RGBColor(0x94, 0x7C, 0x6B)   # 哑光浅茶棕：少量强调
PAPER = RGBColor(0xF5, 0xF3, 0xEE)   # 页面底色
INK   = RGBColor(0x42, 0x42, 0x42)   # 正文
NOTE  = RGBColor(0x75, 0x75, 0x75)   # 注释
WHITE = RGBColor(0xFF, 0xFF, 0xFF)   # 蒙版/浅色块上的字
LINE  = RGBColor(0xDD, 0xD9, 0xD0)   # 中性浅分隔线
SHADE = RGBColor(0xFC, 0xFA, 0xF6)   # 极浅米白内容块
FONT = "微软雅黑"
FONT_NUM = "Arial"

prs = Presentation()
prs.slide_width = px(1280)
prs.slide_height = px(720)
BLANK = prs.slide_layouts[6]
N = 14


def slide(bgimg):
    """浅米白底 + 铺满整页的茶饮肌理。"""
    s = prs.slides.add_slide(BLANK)
    f = s.background.fill; f.solid(); f.fore_color.rgb = PAPER
    s.shapes.add_picture(os.path.join(A, bgimg), 0, 0, prs.slide_width, prs.slide_height)
    return s


def box(s, x, y, w, h, fill=None, line=None, lw=0.75):
    shp = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, px(x), px(y), px(w), px(h))
    if fill is None: shp.fill.background()
    else: shp.fill.solid(); shp.fill.fore_color.rgb = fill
    if line is None: shp.line.fill.background()
    else: shp.line.color.rgb = line; shp.line.width = Pt(lw)
    shp.shadow.inherit = False
    return shp


def veil(s, x, y, w, h, op=0.90):
    """半透米白蒙版：压淡底下肌理，把文字/图表托出来。无边框、无阴影。"""
    shp = box(s, x, y, w, h, WHITE)
    srgbClr = shp.fill._xPr.solidFill.srgbClr
    alpha = srgbClr.makeelement(qn('a:alpha'), {'val': str(int(op * 100000))})
    srgbClr.append(alpha)
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


def head(s, title, y=76, size=32, w=1120, color=DARK):
    text(s, 64, y, w, 52, title, size=size, color=color, bold=True, spacing=1.18)


def footer(s, page, note="数据来源：Yelp Open Dataset（2018/2022 快照）"):
    rule(s, 64, 666, 1152, 1, LINE)
    text(s, 64, 676, 900, 20, note, size=11.5, color=NOTE)
    text(s, 1070, 676, 146, 20, f"{page:02d} / {N}", size=11.5, color=NOTE,
         align=PP_ALIGN.RIGHT, font=FONT_NUM)


def evcard(s, name, x, y, w, tag):
    """证据区：图表白底铺在米白蒙版上，无边框/色条/阴影，图表上不叠任何纹理。"""
    p = os.path.join(A, name)
    iw, ih = Image.open(p).size
    ch = round(w * ih / iw)
    veil(s, x - 8, y - 8, w + 16, ch + 42, op=0.94)
    text(s, x, y, w, 20, tag, size=10.5, color=NOTE, font=FONT_NUM, spacing=1.0)
    s.shapes.add_picture(p, px(x), px(y + 30), px(w), px(ch))
    return ch + 30


def bignum(s, x, y, w, num, label, num_color=DARK, num_size=66, label_size=15, align=PP_ALIGN.LEFT):
    text(s, x, y, w, num_size * 1.5, num, size=num_size, color=num_color,
         bold=True, font=FONT_NUM, spacing=1.0, align=align)
    text(s, x, y + num_size * 1.42, w, 28, label, size=label_size, color=NOTE, align=align)


def verdict(s, y, lead, body, accent=CLAY, h=50):
    """判断条：左侧短色线 + 文字，无底色块、无阴影。"""
    box(s, 64, y, 3, h, accent)
    text(s, 84, y + 4, 150, h - 8, lead, size=15, color=accent, bold=True,
         anchor=MSO_ANCHOR.MIDDLE)
    text(s, 212, y + 2, 992, h - 4, body, size=15.5, color=INK,
         anchor=MSO_ANCHOR.MIDDLE, spacing=1.2)


def numblock(s, x, y, num, color=DARK, size=44, w=74, h=58):
    """编号块：小范围深色，白字编号。"""
    box(s, x, y, w, h, color)
    text(s, x, y + 4, w, h - 4, num, size=size, color=WHITE, bold=True,
         font=FONT_NUM, align=PP_ALIGN.CENTER, spacing=1.0)


def section(s, num, name, desc, page):
    # 浅底 + 肌理（背景图已铺），左侧小色块编号，深色仅限编号块与章节名
    numblock(s, 80, 214, num, color=DARK, size=40, w=96, h=70)
    rule(s, 80, 306, 74, 2, CLAY)
    text(s, 76, 330, 780, 96, name, size=52, color=DARK, bold=True, spacing=1.1)
    text(s, 80, 448, 700, 56, desc, size=20, color=INK, spacing=1.35)
    # 超大编号：极淡茶棕线稿感，低对比，不抢章节名
    text(s, 900, 150, 320, 460, num, size=210, color=RGBColor(0xE4, 0xDD, 0xD4),
         bold=True, font=FONT_NUM, align=PP_ALIGN.RIGHT, spacing=1.0)
    text(s, 80, 654, 400, 24, "tea-market-analysis  ·  面试作品集", size=12, color=NOTE)
    text(s, 1070, 654, 146, 24, f"{page:02d} / {N}", size=12, color=NOTE,
         align=PP_ALIGN.RIGHT, font=FONT_NUM)


# ================= P1 封面（全浅底，窄条点缀） =================
s = slide("bg_cover.png")
# 左侧内容：大面积米白蒙版托出，窄茶灰绿竖条点缀（非半页深色）
veil(s, 56, 118, 470, 520, op=0.90)
box(s, 68, 178, 7, 306, DARK)
text(s, 100, 148, 380, 26, "DATA ANALYTICS  /  PORTFOLIO", size=12,
     color=CLAY, bold=True, font=FONT_NUM)
text(s, 96, 200, 410, 300,
     [("茶饮门店", {}), ("\n竞争格局与", {}), ("\n选址分析", {})],
     size=44, color=DARK, bold=True, spacing=1.18)
rule(s, 100, 520, 62, 2, CLAY)
text(s, 100, 540, 380, 40, "真实数据 · 自建特征 · 自我推翻", size=15, color=INK, spacing=1.4)
text(s, 100, 600, 380, 24, "潘约翰  |  2026", size=12.5, color=NOTE, font=FONT_NUM)
# 右侧内容：金句 + 三组数据
veil(s, 560, 168, 664, 470, op=0.88)
text(s, 588, 196, 620, 150,
     [("竞品数量是优质商圈的", {}), ("\n症状，不是病因", {"color": CLAY})],
     size=35, color=DARK, bold=True, spacing=1.32)
rule(s, 588, 372, 620, 1, LINE)
para_items = [
    ("150,346", "家真实商户样本", DARK),
    ("477", "家奶茶门店为分析主体", DARK),
    ("11", "个蓝海候选城市", CLAY),
]
y = 400
for n, lab, c in para_items:
    text(s, 588, y, 196, 46, n, size=31, color=c, bold=True, font=FONT_NUM)
    text(s, 800, y + 7, 400, 34, lab, size=16, color=INK)
    y += 64

# ================= P2 目录 =================
s = slide("bg_text.png")
veil(s, 56, 46, 1168, 612, op=0.90)
kicker(s, 64, 54, "CONTENTS")
head(s, "四个部分，讲清一个决策问题", y=90, size=34)
rule(s, 64, 156, 1152, 1, LINE)
toc = [
    ("01", "背景与数据", "真实商户替代模拟数据，竞品密度用经纬度自建", DARK),
    ("02", "核心发现", "市场集中、竞争两极分化，一个漂亮结论被推翻", CLAY),
    ("03", "稳健性与边界", "换半径、做 bootstrap，检验结论是否站得住", DARK),
    ("04", "结论", "先选市场、再选商圈，不把竞品数量当信号", CLAY),
]
y = 192
for num, name, desc, c in toc:
    numblock(s, 64, y, num, color=c, size=27, w=62, h=54)
    text(s, 150, y - 2, 360, 42, name, size=25, color=DARK, bold=True)
    text(s, 150, y + 42, 960, 32, desc, size=16, color=INK)
    rule(s, 64, y + 92, 1152, 1, LINE)
    y += 114
footer(s, 2)

# ================= P3 章节 01 =================
s = slide("bg_section.png")
section(s, "01", "背景与数据", "真实数据、自建特征，以及天然缺失的那一块", 3)

# ================= P4 数据底座 =================
s = slide("bg_chart.png")
kicker(s, 64, 48, "01  /  DATA FOUNDATION")
head(s, "用真实商户数据回答选址问题，而不是模拟数据", y=84, size=31)
rule(s, 64, 148, 1152, 1, LINE)
veil(s, 56, 170, 545, 430, op=0.90)
text(s, 64, 176, 520, 30, "要回答的三个问题", size=15, color=NOTE, bold=True)
qs = [("Q1", "市场格局", "茶饮门店集中在哪些城市"),
      ("Q2", "竞争效应", "周边竞品越多，生意越差吗"),
      ("Q3", "选址决策", "哪些市场需求已验证、供给未饱和")]
y = 212
for tag, t, d in qs:
    text(s, 64, y, 74, 40, tag, size=23, color=CLAY, bold=True, font=FONT_NUM)
    text(s, 146, y - 1, 430, 34, t, size=20, color=DARK, bold=True)
    text(s, 146, y + 32, 430, 30, d, size=15, color=INK)
    rule(s, 64, y + 72, 526, 1, LINE)
    y += 90
veil(s, 636, 170, 588, 430, op=0.90)
text(s, 660, 176, 540, 30, "数据底座 / Yelp Open Dataset", size=15, color=NOTE, bold=True)
funnel = [("150,346", "商户总数", 520),
          ("7,069", "茶饮门店（三类业态）", 440),
          ("477", "奶茶店 · 分析主体", 360)]
y = 212
for i, (n, lab, w) in enumerate(funnel):
    x = 660 + (520 - w) / 2
    box(s, x, y, w, 80, SHADE)
    box(s, x, y, 4, 80, DARK if i < 2 else CLAY)
    text(s, x + 16, y + 8, w - 24, 42, n, size=33, color=DARK if i < 2 else CLAY,
         bold=True, font=FONT_NUM, align=PP_ALIGN.CENTER, spacing=1.0)
    text(s, x + 16, y + 52, w - 24, 22, lab, size=14, color=INK, align=PP_ALIGN.CENTER)
    y += 90
text(s, 660, 492, 540, 66,
     "覆盖 8 个都市圈、15 州/省。无销量、无开店日期——需求只能用累计评论数代理。",
     size=15, color=INK, spacing=1.4)
verdict(s, 606, "关键前提",
        "竞品密度数据里没有，必须用经纬度自己算；需求是代理变量，结论要讲边界。")

# ================= P5 Q1 市场集中 =================
s = slide("bg_chart.png")
kicker(s, 64, 48, "02  /  FINDING 01")
head(s, "市场高度集中：前 5 城占 34%", y=82, size=32)
evcard(s, "q1_city_distribution.png", 64, 176, 682, "EVIDENCE  /  茶饮门店 TOP10 城市")
veil(s, 790, 176, 434, 420, op=0.90)
bignum(s, 806, 196, 400, "956", "家茶饮门店 · 费城（最大单一市场）", num_color=CLAY, num_size=78)
rule(s, 806, 374, 400, 1, LINE)
paras(s, 806, 388, 400, 168, [
    ([("前 5 城占 34%", {"bold": True, "color": DARK, "size": 19})], {}),
    ([("头部市场值得优先进入。但城市字段由用户填写，同一都市圈可能被拆成多个城市（费城 / Cherry Hill）。", {})], {"size": 15, "color": INK}),
    ([("集中度数字受口径影响，非精确市占率。", {"color": NOTE})], {"size": 14.5}),
], gap=9, spacing=1.25)
verdict(s, 606, "判断", "先锁定头部市场，但不把这个百分比当成精确市占率。")
footer(s, 5)

# ================= P6 Q2 两极分化 =================
s = slide("bg_chart.png")
kicker(s, 64, 48, "02  /  FINDING 02")
head(s, "竞争呈两极分化，不能用“平均竞品数”描述", y=82, size=31)
evcard(s, "q2_competitor_density.png", 64, 174, 626, "EVIDENCE  /  1km 内竞品数分布")
veil(s, 738, 174, 486, 420, op=0.90)
bignum(s, 752, 182, 456, "38%", "门店 1km 内零竞品 · 独立区隔市场", num_color=DARK, num_size=72)
rule(s, 752, 340, 456, 1, LINE)
bignum(s, 752, 356, 456, "30%", "门店 1km 内 ≥3 家 · 贴身竞争", num_color=CLAY, num_size=72)
rule(s, 752, 514, 456, 1, LINE)
text(s, 752, 528, 456, 60,
     "密度用 Haversine 球面距离自建：0.5 / 1 / 2 / 3km 四档，同州掩码避免跨界误计。1km≈步行 10 分钟商圈。",
     size=14, color=INK, spacing=1.32)
verdict(s, 606, "判断", "市场不是均匀的，必须分组看——这是后面所有分析的起点。")
footer(s, 6)

# ================= P7 章节 02 =================
s = slide("bg_section.png")
section(s, "02", "核心发现", "一个被推翻的漂亮结论，和它背后的真正机制", 7)

# ================= P8 伪重复（核心页） =================
s = slide("bg_chart.png")
kicker(s, 64, 44, "02  /  THE TURNING POINT")
head(s, "初版结论“竞品越多越火”是假的", y=72, size=32, color=CLAY)
veil(s, 56, 126, 1168, 40, op=0.86)
text(s, 64, 130, 1140, 28, "细粒度曲线非单调；23 家高密度店全部挤在费城唐人街一个街区。",
     size=15, color=INK)
evcard(s, "q8_threshold.png", 64, 176, 1152, "EVIDENCE  /  全样本曲线 · 剔除簇后 · 费城内对照")
veil(s, 56, 520, 1168, 80, op=0.90)
tri = [
    ("相关系数 r", "0.19 → 0.016", DARK),
    ("分组差异 p", "0.049 → 0.76", DARK),
    ("高密度店来源", "19107 · 23 家", CLAY),
]
y = 526
for i, (lab, val, c) in enumerate(tri):
    x = 64 + i * 388
    rule(s, x, y, 350, 2, c)
    text(s, x, y + 8, 350, 24, lab, size=13, color=NOTE)
    text(s, x, y + 34, 356, 40, val, size=24, color=c, bold=True, font=FONT_NUM)
verdict(s, 622, "关键",
        "23 家本质是 1 个观测（均评论 186 vs 费城其他 56）。竞品数量是优质商圈的症状，不是病因。",
        accent=CLAY, h=42)
footer(s, 8, "口径：剔除 competitors_1km ≥ 20 的伪重复簇后重算；Mann-Whitney p<0.001")

# ================= P9 评分梯度幸存 =================
s = slide("bg_text.png")
kicker(s, 64, 48, "02  /  FINDING 03")
head(s, "同一个检验，一个被推翻、一个幸存", y=82, size=32)
veil(s, 56, 172, 552, 340, op=0.92)
box(s, 64, 176, 536, 4, CLAY)
text(s, 88, 196, 490, 34, "被推翻  ·  热度结论", size=21, color=CLAY, bold=True)
text(s, 88, 244, 490, 58, "r  0.19 → 0.016", size=34, color=DARK, bold=True, font=FONT_NUM)
paras(s, 88, 320, 492, 168, [
    ([("剔除唐人街簇后相关性归零，分组差异 p 从 0.049 升到 0.76。", {})], {"size": 16}),
    ([("密度不提升需求——初版判断被自己的检验推翻。", {"bold": True, "color": DARK})], {"size": 16}),
], gap=14)
veil(s, 620, 172, 604, 340, op=0.92)
box(s, 628, 176, 588, 4, DARK)
text(s, 652, 196, 544, 34, "幸存  ·  评分结论", size=21, color=DARK, bold=True)
text(s, 652, 244, 544, 58, "p  0.0001 → 0.0017", size=33, color=DARK, bold=True, font=FONT_NUM)
paras(s, 652, 320, 544, 168, [
    ([("独占区 4.18 → 最卷区 3.86，剔除簇后仍显著（H=15.19）。", {})], {"size": 16}),
    ([("评分分化是全样本现象，不是单一街区伪造的。", {"bold": True, "color": DARK})], {"size": 16}),
], gap=14)
verdict(s, 528, "诚实的价值",
        "同样的样本、同样的检验流程，一个被推翻、一个幸存——说明检验不是走过场。",
        accent=DARK, h=48)
veil(s, 56, 592, 1168, 48, op=0.86)
text(s, 64, 596, 1140, 42,
     "评分下降的两种机制（低质店在无竞争区存活 / 高竞争区评分更分化）单期截面无法区分，属后续研究方向。",
     size=14, color=NOTE, spacing=1.3)
footer(s, 9)

# ================= P10 蓝海 =================
s = slide("bg_chart.png")
kicker(s, 64, 48, "02  /  FINDING 04")
head(s, "蓝海候选池 11 城：前三名排序稳定", y=82, size=32)
evcard(s, "q5_blue_ocean.png", 64, 172, 552, "EVIDENCE  /  需求 × 供给气泡图")
veil(s, 640, 172, 584, 424, op=0.90)
text(s, 652, 176, 560, 30, "蓝海指数（口径已统一）", size=15, color=NOTE, bold=True)
text(s, 652, 210, 560, 60, "需求强度 ×（1 − 奶茶渗透率）", size=19, color=DARK, bold=True, spacing=1.3)
rule(s, 652, 284, 560, 1, LINE)
text(s, 652, 298, 560, 28, "bootstrap 1000 次 · 进前三概率", size=14.5, color=NOTE)
ranks = [("01", "Reno", "87%", CLAY), ("02", "New Orleans", "82%", DARK), ("03", "Indianapolis", "79%", DARK)]
y = 334
for num, city, pct, c in ranks:
    text(s, 652, y, 60, 34, num, size=22, color=c, bold=True, font=FONT_NUM)
    text(s, 716, y, 350, 34, city, size=19, color=DARK, bold=True)
    text(s, 1110, y, 100, 34, pct, size=20, color=c, bold=True,
         font=FONT_NUM, align=PP_ALIGN.RIGHT)
    rule(s, 652, y + 42, 560, 1, LINE)
    y += 56
text(s, 652, 516, 560, 60,
     "入选门槛：奶茶店≥5、茶饮店≥50。口径修正后候选池从 18 城收敛到 11 城。",
     size=14.5, color=INK, spacing=1.35)
verdict(s, 606, "边界", "只能讲“候选池排名”，不能讲“第一名绝对最好”。")
footer(s, 10)

# ================= P11 街区粒度 =================
s = slide("bg_chart.png")
kicker(s, 64, 48, "02  /  FINDING 05")
head(s, "城市内部差异巨大，选址必须下沉到街区", y=82, size=31)
evcard(s, "q6_philadelphia_map.png", 64, 172, 394, "EVIDENCE  /  费城奶茶店地理分布")
veil(s, 494, 172, 730, 424, op=0.90)
text(s, 512, 178, 690, 36, "费城 19107：需求被验证的样本", size=21, color=DARK, bold=True)
rule(s, 512, 226, 690, 2, CLAY)
paras(s, 512, 246, 690, 320, [
    ([("23 家奶茶店聚集，均评论 186 条——城市内部的热度差异远大于城市之间。", {})], {"size": 17}),
    ([("但这批店与 Q8 的伪重复簇是同一批：热度高说明需求存在，也可能意味着市场接近饱和。", {})], {"size": 17}),
    ([("正确用法", {"bold": True, "color": DARK}),
      ("：先确认“这里有被验证的需求”，再叠加竞品间距、租金、铺位可得性做二次筛选。", {})], {"size": 17}),
], gap=18, spacing=1.4)
verdict(s, 606, "不推荐", "数据给方向，不给最终答案——不直接推荐在 19107 开店。")
footer(s, 11, "口径：费城奶茶店经纬度散点，颜色越深表示累计评论数越高")

# ================= P12 章节 03 =================
s = slide("bg_section.png")
section(s, "03", "稳健性与边界", "结论能不能对外讲，取决于它经不经得起折腾", 12)

# ================= P13 稳健性 =================
s = slide("bg_chart.png")
kicker(s, 64, 48, "03  /  ROBUSTNESS")
head(s, "结论不依赖参数选择，也不依赖单一城市排名", y=82, size=30)
evcard(s, "q9_robustness.png", 64, 164, 868, "EVIDENCE  /  半径敏感性 · bootstrap 稳定性")
veil(s, 56, 524, 1168, 122, op=0.90)
rule(s, 64, 530, 550, 2, DARK)
text(s, 64, 540, 550, 24, "半径敏感性 · 剔除簇后 r", size=13, color=NOTE)
text(s, 64, 562, 550, 42, "0.046  /  0.016  /  −0.028", size=23, color=DARK, bold=True, font=FONT_NUM)
rule(s, 660, 530, 550, 2, CLAY)
text(s, 660, 540, 550, 24, "bootstrap 进前三概率", size=13, color=NOTE)
text(s, 660, 562, 550, 42, "Reno 87%  ·  NOLA 82%", size=23, color=CLAY, bold=True, font=FONT_NUM)
text(s, 64, 616, 1140, 34,
     "三档半径（0.5/1/2km）下 p 均 >0.05，“密度不提升需求”稳健；但评论数是累计值，含资历偏差——老店天然占优，这是 V2 首要待办。",
     size=13, color=NOTE, spacing=1.24)
footer(s, 13)

# ================= P14 结尾（浅底） =================
s = slide("bg_end.png")
veil(s, 56, 46, 1168, 612, op=0.90)
box(s, 76, 78, 7, 74, CLAY)
text(s, 100, 76, 1120, 86, "别怕竞品，别信竞品", size=56, color=DARK, bold=True, spacing=1.1)
rule(s, 100, 176, 92, 2, CLAY)
text(s, 100, 196, 1100, 44, "先选市场，再选商圈，不把竞品数量当信号", size=23, color=INK)
steps = [("01", "选市场", "优先进入需求旺、奶茶店少的蓝海候选池"),
         ("02", "选商圈", "进入需求已被验证的成熟商圈，但不追竞品数量"),
         ("03", "筛铺位", "下沉到街区粒度，叠加租金与铺位可得性")]
y = 292
for num, t, d in steps:
    numblock(s, 80, y, num, color=DARK, size=26, w=58, h=48)
    text(s, 160, y + 2, 200, 44, t, size=23, color=DARK, bold=True)
    text(s, 380, y + 8, 800, 38, d, size=17, color=INK)
    rule(s, 80, y + 58, 1120, 1, LINE)
    y += 82
veil(s, 56, 642, 1168, 40, op=0.86)
text(s, 80, 648, 900, 26,
     "限制：缺租金与开店成本，结论只谈需求侧，落地需实地验证。",
     size=13, color=NOTE)
text(s, 1070, 648, 146, 26, f"{N:02d} / {N}", size=13,
     color=NOTE, align=PP_ALIGN.RIGHT, font=FONT_NUM)

prs.save(OUT)
print("已生成:", OUT)
print("页数:", len(prs.slides._sldIdLst))
