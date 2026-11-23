# -*- coding: utf-8 -*-
"""面试作品集 PPT V2：杂志编辑风。
去模板化：非对称版式、超大数字锚点、赤陶橙+墨绿+深墨蓝配色、
图表统一装进"证据卡"、去掉圆角卡片与"所以呢"模板条。
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "茶饮门店竞争格局与选址分析.pptx")
ASSETS = os.path.join(HERE, "assets")

PX = 914400 / 96  # 96dpi 下 1px = 9525 EMU
def px(v): return Emu(int(v * PX))

# ---- 配色：编辑杂志风（暖纸底 + 深墨蓝 + 赤陶橙 + 墨绿）----
PAPER  = RGBColor(0xF7, 0xF5, 0xF0)   # 暖纸底
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
INK    = RGBColor(0x1C, 0x20, 0x26)   # 近黑正文
INK2   = RGBColor(0x4A, 0x4E, 0x55)   # 次要正文
MUTED  = RGBColor(0x8A, 0x8D, 0x91)   # 弱化
NAVY   = RGBColor(0x14, 0x2A, 0x3D)   # 深墨蓝（深色页底）
NAVY2  = RGBColor(0x1E, 0x3C, 0x54)
CLAY   = RGBColor(0xC0, 0x5A, 0x3C)   # 赤陶橙（强调/警示/推翻）
CLAY_L = RGBColor(0xF2, 0xE2, 0xDA)
PINE   = RGBColor(0x2E, 0x6E, 0x56)   # 墨绿（幸存/正面）
PINE_L = RGBColor(0xDF, 0xEC, 0xE5)
GOLD   = RGBColor(0xC8, 0x92, 0x3E)   # 芥末金（点缀）
LINE   = RGBColor(0xDC, 0xD8, 0xCE)   # 暖灰分隔线
CARD   = RGBColor(0xFF, 0xFF, 0xFF)
SHADE  = RGBColor(0xEE, 0xEB, 0xE3)   # 浅灰底
FONT   = "微软雅黑"
FONT_NUM = "Arial"

prs = Presentation()
prs.slide_width = px(1280)
prs.slide_height = px(720)
BLANK = prs.slide_layouts[6]
N = 14


def slide(bg=PAPER):
    s = prs.slides.add_slide(BLANK)
    f = s.background.fill; f.solid(); f.fore_color.rgb = bg
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


def _set_run(r, size, color, bold, font, italic=False):
    r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color
    r.font.name = font; r.font.italic = italic
    rPr = r._r.get_or_add_rPr()
    ea = rPr.find(qn('a:ea'))
    if ea is None:
        ea = rPr.makeelement(qn('a:ea'), {}); rPr.append(ea)
    ea.set('typeface', font)


def text(s, x, y, w, h, runs, size=18, color=INK, bold=False, align=PP_ALIGN.LEFT,
         font=FONT, spacing=1.25, anchor=MSO_ANCHOR.TOP, italic=False):
    """runs: str 或 [(text,{size,color,bold,font,italic}),...]（同一段落）"""
    tb = s.shapes.add_textbox(px(x), px(y), px(w), px(h))
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]; p.alignment = align; p.line_spacing = spacing
    if isinstance(runs, str): runs = [(runs, {})]
    for t, st in runs:
        r = p.add_run(); r.text = t
        _set_run(r, st.get('size', size), st.get('color', color),
                 st.get('bold', bold), st.get('font', font), st.get('italic', italic))
    return tb


def paras(s, x, y, w, h, lines, size=17, color=INK2, gap=8, spacing=1.3, align=PP_ALIGN.LEFT):
    """lines: [(runs, styledict), ...] 多段落"""
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
    """章节小标：色块 + 字距感"""
    box(s, x, y + 4, 22, 3, color)
    text(s, x + 32, y, w, 24, label, size=13, color=color, bold=True, font=FONT_NUM, spacing=1.0)


def head(s, title, y=58, size=33, w=1120, color=INK):
    text(s, 60, y, w, 52, title, size=size, color=color, bold=True, spacing=1.18)


def footer(s, page, note="数据来源：Yelp Open Dataset（2018/2022 快照）"):
    rule(s, 60, 668, 1160, 1, LINE)
    text(s, 60, 678, 900, 20, note, size=11.5, color=MUTED)
    text(s, 1080, 678, 140, 20, f"{page:02d} / {N}", size=11.5, color=MUTED,
         align=PP_ALIGN.RIGHT, font=FONT_NUM)


def evcard(s, name, x, y, w, tag, bar=NAVY):
    """证据卡：白底细框 + 顶部色条 + 角标 + 真实图表"""
    from PIL import Image
    p = os.path.join(ASSETS, name)
    iw, ih = Image.open(p).size
    ch = round(w * ih / iw)
    box(s, x - 10, y - 10, w + 20, ch + 34, CARD, line=LINE, lw=0.75)
    rule(s, x - 10, y - 10, w + 20, 4, bar)
    text(s, x + 4, y - 6, w - 8, 22, tag, size=11.5, color=MUTED, font=FONT_NUM, spacing=1.0)
    s.shapes.add_picture(p, px(x), px(y + 18), px(w), px(ch))
    return ch + 34


def bignum(s, x, y, w, num, label, num_color=CLAY, num_size=66, label_size=15, label_color=INK2, align=PP_ALIGN.LEFT):
    text(s, x, y, w, num_size * 1.5, num, size=num_size, color=num_color,
         bold=True, font=FONT_NUM, spacing=1.0, align=align)
    text(s, x, y + num_size * 1.42, w, 28, label, size=label_size, color=label_color, align=align)


def verdict(s, y, lead, body, accent=CLAY, h=50):
    """底部判断条：左侧粗色条 + 深色纸底（非圆角）"""
    box(s, 60, y, 1160, h, SHADE)
    box(s, 60, y, 6, h, accent)
    text(s, 82, y + 4, 150, h - 8, lead, size=15, color=accent, bold=True,
         anchor=MSO_ANCHOR.MIDDLE)
    text(s, 214, y + 2, 990, h - 4, body, size=16, color=INK,
         anchor=MSO_ANCHOR.MIDDLE, spacing=1.2)


def section(s, num, name, desc, page):
    box(s, 0, 0, 1280, 720, NAVY)
    box(s, 0, 0, 1280, 9, CLAY)
    # 超大装饰数字，压在右下角
    text(s, 760, 150, 500, 460, num, size=300, color=NAVY2, bold=True,
         font=FONT_NUM, align=PP_ALIGN.RIGHT, spacing=1.0)
    text(s, 84, 236, 120, 40, "CHAPTER", size=13, color=GOLD, bold=True, font=FONT_NUM)
    rule(s, 84, 286, 120, 3, CLAY)
    text(s, 80, 312, 720, 96, name, size=58, color=WHITE, bold=True, spacing=1.1)
    text(s, 84, 432, 660, 56, desc, size=21, color=RGBColor(0xC2, 0xCF, 0xD8), spacing=1.35)
    text(s, 84, 654, 400, 24, "tea-market-analysis  ·  面试作品集", size=12.5,
         color=RGBColor(0x8F, 0xA3, 0xB2))
    text(s, 1080, 654, 140, 24, f"{page:02d} / {N}", size=12.5,
         color=RGBColor(0x8F, 0xA3, 0xB2), align=PP_ALIGN.RIGHT, font=FONT_NUM)


# ================= P1 封面 =================
s = slide(PAPER)
box(s, 0, 0, 452, 720, NAVY)
box(s, 452, 0, 5, 720, CLAY)
text(s, 52, 62, 360, 26, "DATA ANALYTICS  /  PORTFOLIO", size=12.5,
     color=RGBColor(0xB9, 0xC8, 0xD4), bold=True, font=FONT_NUM)
# 左侧主标：三行，行距紧
text(s, 48, 176, 380, 300,
     [("茶饮门店", {}), ("\n竞争格局与", {}), ("\n选址分析", {})],
     size=47, color=WHITE, bold=True, spacing=1.16)
rule(s, 52, 498, 96, 3, CLAY)
text(s, 52, 520, 360, 84,
     "真实数据 · 自建特征 · 自我推翻", size=16,
     color=RGBColor(0xD7, 0xE0, 0xE7), spacing=1.4)
text(s, 52, 650, 360, 24, "潘约翰  |  2026", size=13,
     color=RGBColor(0x9F, 0xB2, 0xC0), font=FONT_NUM)
# 右侧：主张 + 三条证据 + 大号引文标记
text(s, 512, 96, 700, 280, "“", size=190, color=CLAY_L, bold=True,
     font="Georgia", spacing=1.0)
text(s, 560, 210, 660, 150,
     [("竞品数量是优质商圈的", {}), ("\n症状，不是病因", {"color": CLAY})],
     size=37, color=INK, bold=True, spacing=1.3)
rule(s, 560, 392, 660, 1, LINE)
para_items = [
    ("150,346", "家真实商户样本", NAVY),
    ("477", "家奶茶门店为分析主体", NAVY),
    ("11", "个蓝海候选城市", PINE),
]
y = 424
for n, lab, c in para_items:
    text(s, 560, y, 210, 46, n, size=33, color=c, bold=True, font=FONT_NUM)
    text(s, 782, y + 7, 436, 34, lab, size=17, color=INK2)
    y += 66

# ================= P2 目录 =================
s = slide(PAPER)
kicker(s, 60, 58, "CONTENTS")
head(s, "四个部分，讲清一个决策问题", y=92, size=34)
rule(s, 60, 158, 1160, 1, LINE)
toc = [
    ("01", "背景与数据", "真实商户替代模拟数据，竞品密度用经纬度自建", CLAY),
    ("02", "核心发现", "市场集中、竞争两极分化，一个漂亮结论被推翻", NAVY),
    ("03", "稳健性与边界", "换半径、做 bootstrap，检验结论是否站得住", PINE),
    ("04", "结论", "先选市场、再选商圈，不把竞品数量当信号", GOLD),
]
y = 196
for num, name, desc, c in toc:
    text(s, 60, y, 110, 64, num, size=46, color=c, bold=True, font=FONT_NUM, spacing=1.0)
    text(s, 186, y + 2, 330, 42, name, size=27, color=INK, bold=True)
    text(s, 186, y + 46, 900, 32, desc, size=16.5, color=INK2)
    rule(s, 60, y + 92, 1160, 1, LINE)
    y += 116
footer(s, 2)

# ================= P3 章节 01 =================
s = slide()
section(s, "01", "背景与数据", "真实数据、自建特征，以及天然缺失的那一块", 3)

# ================= P4 数据底座 =================
s = slide()
kicker(s, 60, 52, "01  /  DATA FOUNDATION")
head(s, "用真实商户数据回答选址问题，而不是模拟数据", y=88, size=31)
rule(s, 60, 152, 1160, 1, LINE)
# 左：三个问题
text(s, 60, 178, 520, 30, "要回答的三个问题", size=16, color=MUTED, bold=True)
qs = [("Q1", "市场格局", "茶饮门店集中在哪些城市"),
      ("Q2", "竞争效应", "周边竞品越多，生意越差吗"),
      ("Q3", "选址决策", "哪些市场需求已验证、供给未饱和")]
y = 216
for tag, t, d in qs:
    text(s, 60, y, 74, 40, tag, size=24, color=CLAY, bold=True, font=FONT_NUM)
    text(s, 142, y - 1, 430, 34, t, size=20, color=INK, bold=True)
    text(s, 142, y + 32, 430, 30, d, size=15.5, color=INK2)
    rule(s, 60, y + 72, 540, 1, LINE)
    y += 90
# 右：数据底座——横向阶梯（非圆角）
text(s, 660, 178, 560, 30, "数据底座 / Yelp Open Dataset", size=16, color=MUTED, bold=True)
funnel = [("150,346", "商户总数", 560, NAVY),
          ("7,069", "茶饮门店（三类业态）", 470, NAVY2),
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
     size=15.5, color=INK2, spacing=1.4)
verdict(s, 606,
    [("关键前提", {"color": CLAY})],
    "竞品密度数据里没有，必须用经纬度自己算；需求是代理变量，结论要讲边界。")

# ================= P5 Q1 市场集中 =================
s = slide()
kicker(s, 60, 50, "02  /  FINDING 01")
head(s, "市场高度集中：前 5 城占 34%", y=84, size=32)
rule(s, 60, 148, 1160, 1, LINE)
evcard(s, "q1_city_distribution.png", 60, 182, 690, "EVIDENCE  /  茶饮门店 TOP10 城市", bar=NAVY)
# 右侧：超大数字锚点
bignum(s, 806, 200, 400, "956", "家茶饮门店 · 费城（最大单一市场）", num_color=CLAY, num_size=82)
rule(s, 806, 384, 400, 1, LINE)
paras(s, 806, 398, 400, 168, [
    ([("前 5 城占 34%", {"bold": True, "color": NAVY, "size": 19})], {}),
    ([("头部市场值得优先进入。但城市字段由用户填写，同一都市圈可能被拆成多个城市（费城 / Cherry Hill）。", {})], {"size": 15, "color": INK2}),
    ([("集中度数字受口径影响，非精确市占率。", {"color": MUTED})], {"size": 14.5}),
], gap=9, spacing=1.25)
verdict(s, 608, [("判断", {"color": CLAY})], "先锁定头部市场，但不把这个百分比当成精确市占率。")
footer(s, 5)

# ================= P6 Q2 两极分化 =================
s = slide()
kicker(s, 60, 50, "02  /  FINDING 02")
head(s, "竞争呈两极分化，不能用“平均竞品数”描述", y=84, size=31)
rule(s, 60, 148, 1160, 1, LINE)
evcard(s, "q2_competitor_density.png", 60, 180, 632, "EVIDENCE  /  1km 内竞品数分布", bar=NAVY)
# 右侧：两个超大数字
bignum(s, 748, 186, 460, "38%", "门店 1km 内零竞品 · 独立区隔市场", num_color=PINE, num_size=76)
rule(s, 748, 348, 460, 1, LINE)
bignum(s, 748, 366, 460, "30%", "门店 1km 内 ≥3 家 · 贴身竞争", num_color=CLAY, num_size=76)
rule(s, 748, 528, 460, 1, LINE)
text(s, 748, 544, 460, 56,
     "密度用 Haversine 球面距离自建：0.5 / 1 / 2 / 3km 四档，同州掩码避免跨界误计。1km≈步行 10 分钟商圈。",
     size=14.5, color=INK2, spacing=1.35)
verdict(s, 608, [("判断", {"color": CLAY})], "市场不是均匀的，必须分组看——这是后面所有分析的起点。")
footer(s, 6)

# ================= P7 章节 02 =================
s = slide()
section(s, "02", "核心发现", "一个被推翻的漂亮结论，和它背后的真正机制", 7)

# ================= P8 伪重复（核心页） =================
s = slide()
kicker(s, 60, 46, "02  /  THE TURNING POINT")
head(s, "初版结论“竞品越多越火”是假的", y=74, size=32, color=CLAY)
text(s, 60, 132, 1120, 26, "细粒度曲线非单调；23 家高密度店全部挤在费城唐人街一个街区。",
     size=15, color=INK2)
evcard(s, "q8_threshold.png", 60, 180, 1080, "EVIDENCE  /  全样本曲线 · 剔除簇后 · 费城内对照", bar=CLAY)
# 三个变化数字（非卡片）
tri = [
    ("相关系数 r", "0.19 → 0.016", NAVY),
    ("分组差异 p", "0.049 → 0.76", NAVY),
    ("高密度店来源", "19107 · 23 家", CLAY),
]
y = 528
for i, (lab, val, c) in enumerate(tri):
    x = 60 + i * 392
    rule(s, x, y, 360, 2, c)
    text(s, x, y + 10, 360, 24, lab, size=13, color=MUTED)
    text(s, x, y + 36, 368, 40, val, size=25, color=c, bold=True, font=FONT_NUM)
verdict(s, 618,
    [("关键", {"color": CLAY})],
    "23 家本质是 1 个观测（均评论 186 vs 费城其他 56）。竞品数量是优质商圈的症状，不是病因。",
    accent=CLAY, h=46)
footer(s, 8, "口径：剔除 competitors_1km ≥ 20 的伪重复簇后重算；Mann-Whitney p<0.001")

# ================= P9 评分梯度幸存 =================
s = slide()
kicker(s, 60, 50, "02  /  FINDING 03")
head(s, "同一个检验，一个被推翻、一个幸存", y=84, size=32)
rule(s, 60, 148, 1160, 1, LINE)
# 左：被推翻
box(s, 60, 178, 548, 328, SHADE)
box(s, 60, 178, 548, 5, CLAY)
text(s, 88, 200, 490, 34, "被推翻  ·  热度结论", size=22, color=CLAY, bold=True)
text(s, 88, 248, 490, 58, "r  0.19 → 0.016", size=36, color=INK, bold=True, font=FONT_NUM)
paras(s, 88, 326, 492, 168, [
    ([("剔除唐人街簇后相关性归零，分组差异 p 从 0.049 升到 0.76。", {})], {"size": 16}),
    ([("密度不提升需求——初版判断被自己的检验推翻。", {"bold": True, "color": INK})], {"size": 16}),
], gap=14)
# 右：幸存
box(s, 620, 178, 600, 328, SHADE)
box(s, 620, 178, 600, 5, PINE)
text(s, 648, 200, 544, 34, "幸存  ·  评分结论", size=22, color=PINE, bold=True)
text(s, 648, 248, 544, 58, "p  0.0001 → 0.0017", size=34, color=INK, bold=True, font=FONT_NUM)
paras(s, 648, 326, 544, 168, [
    ([("独占区 4.18 → 最卷区 3.86，剔除簇后仍显著（H=15.19）。", {})], {"size": 16}),
    ([("评分分化是全样本现象，不是单一街区伪造的。", {"bold": True, "color": INK})], {"size": 16}),
], gap=14)
verdict(s, 528,
    [("诚实的价值", {"color": PINE})],
    "同样的样本、同样的检验流程，一个被推翻、一个幸存——说明检验不是走过场。",
    accent=PINE, h=48)
text(s, 60, 596, 1160, 44,
     "评分下降的两种机制（低质店在无竞争区存活 / 高竞争区评分更分化）单期截面无法区分，属后续研究方向。",
     size=14.5, color=MUTED, spacing=1.3)
footer(s, 9)

# ================= P10 蓝海 =================
s = slide()
kicker(s, 60, 50, "02  /  FINDING 04")
head(s, "蓝海候选池 11 城：前三名排序稳定", y=84, size=32)
rule(s, 60, 148, 1160, 1, LINE)
evcard(s, "q5_blue_ocean.png", 60, 174, 560, "EVIDENCE  /  需求 × 供给气泡图", bar=NAVY)
# 右侧：口径 + 排名
text(s, 648, 178, 572, 30, "蓝海指数（口径已统一）", size=15, color=MUTED, bold=True)
text(s, 648, 212, 572, 60, "需求强度 ×（1 − 奶茶渗透率）", size=19, color=NAVY, bold=True, spacing=1.3)
rule(s, 648, 288, 572, 1, LINE)
text(s, 648, 302, 572, 28, "bootstrap 1000 次 · 进前三概率", size=14.5, color=MUTED)
ranks = [("01", "Reno", "87%", CLAY), ("02", "New Orleans", "82%", NAVY), ("03", "Indianapolis", "79%", NAVY)]
y = 338
for num, city, pct, c in ranks:
    text(s, 648, y, 60, 34, num, size=22, color=c, bold=True, font=FONT_NUM)
    text(s, 712, y, 360, 34, city, size=19, color=INK, bold=True)
    text(s, 1118, y, 102, 34, pct, size=20, color=c, bold=True,
         font=FONT_NUM, align=PP_ALIGN.RIGHT)
    rule(s, 648, y + 42, 572, 1, LINE)
    y += 56
text(s, 648, 520, 572, 60,
     "入选门槛：奶茶店≥5、茶饮店≥50。口径修正后候选池从 18 城收敛到 11 城。",
     size=14.5, color=INK2, spacing=1.35)
verdict(s, 608, [("边界", {"color": CLAY})], "只能讲“候选池排名”，不能讲“第一名绝对最好”。")
footer(s, 10)

# ================= P11 街区粒度 =================
s = slide()
kicker(s, 60, 50, "02  /  FINDING 05")
head(s, "城市内部差异巨大，选址必须下沉到街区", y=84, size=31)
rule(s, 60, 148, 1160, 1, LINE)
evcard(s, "q6_philadelphia_map.png", 60, 174, 400, "EVIDENCE  /  费城奶茶店地理分布", bar=NAVY)
# 右侧判断
text(s, 512, 180, 706, 36, "费城 19107：需求被验证的样本", size=21, color=NAVY, bold=True)
rule(s, 512, 228, 706, 2, CLAY)
paras(s, 512, 248, 706, 300, [
    ([("23 家奶茶店聚集，均评论 186 条——城市内部的热度差异远大于城市之间。", {})], {"size": 17}),
    ([("但这批店与 Q8 的伪重复簇是同一批：热度高说明需求存在，也可能意味着市场接近饱和。", {})], {"size": 17}),
    ([("正确用法", {"bold": True, "color": NAVY}),
      ("：先确认“这里有被验证的需求”，再叠加竞品间距、租金、铺位可得性做二次筛选。", {})], {"size": 17}),
], gap=18, spacing=1.4)
verdict(s, 600, [("不推荐", {"color": CLAY})], "数据给方向，不给最终答案——不直接推荐在 19107 开店。")
footer(s, 11, "口径：费城奶茶店经纬度散点，颜色越深表示累计评论数越高")

# ================= P12 章节 03 =================
s = slide()
section(s, "03", "稳健性与边界", "结论能不能对外讲，取决于它经不经得起折腾", 12)

# ================= P13 稳健性 =================
s = slide()
kicker(s, 60, 50, "03  /  ROBUSTNESS")
head(s, "结论不依赖参数选择，也不依赖单一城市排名", y=84, size=30)
rule(s, 60, 148, 1160, 1, LINE)
evcard(s, "q9_robustness.png", 60, 168, 900, "EVIDENCE  /  半径敏感性 · bootstrap 稳定性", bar=NAVY)
# 两组数字
rule(s, 60, 530, 560, 2, NAVY)
text(s, 60, 540, 560, 24, "半径敏感性 · 剔除簇后 r", size=13, color=MUTED)
text(s, 60, 564, 560, 42, "0.046  /  0.016  /  −0.028", size=24, color=NAVY, bold=True, font=FONT_NUM)
rule(s, 660, 530, 560, 2, PINE)
text(s, 660, 540, 560, 24, "bootstrap 进前三概率", size=13, color=MUTED)
text(s, 660, 564, 560, 42, "Reno 87%  ·  NOLA 82%", size=24, color=PINE, bold=True, font=FONT_NUM)
text(s, 60, 620, 1160, 38,
     "三档半径（0.5/1/2km）下 p 均 >0.05，“密度不提升需求”稳健；但评论数是累计值，含资历偏差——老店天然占优，这是 V2 首要待办。",
     size=13.5, color=MUTED, spacing=1.25)
footer(s, 13)

# ================= P14 结尾 =================
s = slide(NAVY)
box(s, 0, 0, 1280, 9, CLAY)
text(s, 76, 78, 1120, 86, "别怕竞品，别信竞品", size=62, color=WHITE, bold=True, spacing=1.1)
rule(s, 76, 182, 132, 4, CLAY)
text(s, 76, 206, 1100, 44, "先选市场，再选商圈，不把竞品数量当信号", size=24,
     color=RGBColor(0xB9, 0xC8, 0xD4))
steps = [("01", "选市场", "优先进入需求旺、奶茶店少的蓝海候选池"),
         ("02", "选商圈", "进入需求已被验证的成熟商圈，但不追竞品数量"),
         ("03", "筛铺位", "下沉到街区粒度，叠加租金与铺位可得性")]
y = 306
for num, t, d in steps:
    text(s, 78, y, 90, 52, num, size=34, color=CLAY, bold=True, font=FONT_NUM)
    text(s, 176, y + 2, 200, 44, t, size=24, color=WHITE, bold=True)
    text(s, 392, y + 8, 800, 38, d, size=17, color=RGBColor(0xC2, 0xCF, 0xD8))
    rule(s, 78, y + 58, 1120, 1, NAVY2)
    y += 84
text(s, 78, 654, 900, 26,
     "限制：缺租金与开店成本，结论只谈需求侧，落地需实地验证。",
     size=13, color=RGBColor(0x8F, 0xA3, 0xB2))
text(s, 1080, 654, 140, 26, f"{N:02d} / {N}", size=13,
     color=RGBColor(0x8F, 0xA3, 0xB2), align=PP_ALIGN.RIGHT, font=FONT_NUM)

prs.save(OUT)
print("已生成:", OUT)
print("页数:", len(prs.slides._sldIdLst))
