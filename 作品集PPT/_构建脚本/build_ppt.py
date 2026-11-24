# -*- coding: utf-8 -*-
"""生成面试作品集 PPT：茶饮门店竞争格局与选址分析。
不依赖 slidep 引擎，用 python-pptx 直接生成可编辑的 .pptx。
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "茶饮门店竞争格局与选址分析.pptx")
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# 画布 1280x720 px -> 13.333 x 7.5 in (16:9)
PX = 914400 / 96  # 1px in EMU (96 dpi)
def px(v): return Emu(int(v * PX))

# 深海商务蓝色板
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
INK = RGBColor(0x26, 0x28, 0x2E)
PRIMARY = RGBColor(0x23, 0x4B, 0x80)
SECOND = RGBColor(0x4A, 0x73, 0xA8)
ACCENT = RGBColor(0x1A, 0x33, 0x58)
LIGHT = RGBColor(0x82, 0xA1, 0xC4)
PALE = RGBColor(0xEE, 0xF3, 0xF9)
PALE2 = RGBColor(0xF6, 0xF8, 0xFB)
LINE = RGBColor(0xD3, 0xDB, 0xE5)
GREY = RGBColor(0x66, 0x66, 0x66)
RED = RGBColor(0xBA, 0x3A, 0x2B)
GREEN = RGBColor(0x2A, 0x7A, 0x5E)
FONT = "微软雅黑"
FONT_NUM = "Arial"

prs = Presentation()
prs.slide_width = px(1280)
prs.slide_height = px(720)
BLANK = prs.slide_layouts[6]

CHAPTERS = ["01 背景与数据", "02 核心发现", "03 稳健性与边界", "04 结论"]
N = 14


def add_slide():
    s = prs.slides.add_slide(BLANK)
    bg = s.background.fill
    bg.solid()
    bg.fore_color.rgb = WHITE
    return s


def rect(s, x, y, w, h, fill=None, line=None, lw=0.75, radius=False):
    shp = s.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
        px(x), px(y), px(w), px(h))
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid(); shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line; shp.line.width = Pt(lw)
    if radius:
        try: shp.adjustments[0] = 0.08
        except Exception: pass
    shp.shadow.inherit = False
    return shp


def line(s, x, y, w, h=1, color=LINE, lw=0.75):
    shp = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, px(x), px(y), px(w), px(max(h, 1)))
    shp.fill.solid(); shp.fill.fore_color.rgb = color
    shp.line.fill.background(); shp.shadow.inherit = False
    return shp


def text(s, x, y, w, h, runs, size=20, color=INK, bold=False, align=PP_ALIGN.LEFT,
         font=FONT, line_spacing=1.35, anchor=MSO_ANCHOR.TOP, margin=0):
    """runs: str 或 [(text, {size,color,bold,font}), ...]"""
    box = s.shapes.add_textbox(px(x), px(y), px(w), px(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = px(margin); tf.margin_right = px(margin)
    tf.margin_top = px(margin); tf.margin_bottom = px(margin)
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = line_spacing
    if isinstance(runs, str):
        runs = [(runs, {})]
    for t, st in runs:
        r = p.add_run(); r.text = t
        r.font.size = Pt(st.get("size", size))
        r.font.bold = st.get("bold", bold)
        r.font.color.rgb = st.get("color", color)
        r.font.name = st.get("font", font)
        # 东亚字体
        rPr = r._r.get_or_add_rPr()
        ea = rPr.find(qn('a:ea'))
        if ea is None:
            ea = rPr.makeelement(qn('a:ea'), {}); rPr.append(ea)
        ea.set('typeface', st.get("font", font))
    return box


def para(s, x, y, w, h, lines, size=20, color=INK, gap=6, line_spacing=1.3):
    """多段文本：lines = [(runs, style_dict), ...]"""
    box = s.shapes.add_textbox(px(x), px(y), px(w), px(h))
    tf = box.text_frame; tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    for i, (runs, st) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap); p.line_spacing = st.get("line_spacing", line_spacing)
        p.alignment = st.get("align", PP_ALIGN.LEFT)
        if isinstance(runs, str): runs = [(runs, {})]
        for t, rs in runs:
            r = p.add_run(); r.text = t
            r.font.size = Pt(rs.get("size", st.get("size", size)))
            r.font.bold = rs.get("bold", st.get("bold", False))
            r.font.color.rgb = rs.get("color", st.get("color", color))
            r.font.name = rs.get("font", st.get("font", FONT))
            rPr = r._r.get_or_add_rPr()
            ea = rPr.find(qn('a:ea'))
            if ea is None:
                ea = rPr.makeelement(qn('a:ea'), {}); rPr.append(ea)
            ea.set('typeface', rs.get("font", st.get("font", FONT)))
    return box


def content_header(s, title, chapter_idx):
    text(s, 60, 62, 1000, 48, title, size=33, color=INK, bold=True, line_spacing=1.15)
    line(s, 60, 144, 1160, 1, LINE)
    text(s, 60, 150, 300, 22, " tea-market-analysis · 面试作品集", size=13, color=GREY)
    text(s, 960, 150, 260, 22, CHAPTERS[chapter_idx], size=13,
         color=PRIMARY, bold=True, align=PP_ALIGN.RIGHT)


def footer(s, page, source="数据来源：Yelp Open Dataset"):
    line(s, 60, 666, 1160, 1, LINE)
    text(s, 60, 674, 800, 22, source, size=13, color=GREY)
    text(s, 1050, 674, 170, 22, f"{page:02d} / {N}", size=13, color=GREY, align=PP_ALIGN.RIGHT)


def conclusion_bar(s, y, runs, h=46):
    rect(s, 60, y, 1160, h, PALE, line=LIGHT, lw=0.75)
    rect(s, 60, y, 5, h, PRIMARY)
    text(s, 78, y + 3, 1120, h - 6, runs, size=19, color=INK,
         anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.25)


def pic(s, name, x, y, w, h=None):
    p = os.path.join(ASSETS, name)
    if h is None:
        from PIL import Image
        iw, ih = Image.open(p).size
        h = w * ih / iw
    return s.shapes.add_picture(p, px(x), px(y), px(w), px(h))


def section_page(s, num, name, desc, page):
    rect(s, 0, 0, 1280, 720, PRIMARY)
    text(s, 90, 150, 520, 240, num, size=200, color=LIGHT, bold=True, font=FONT_NUM)
    text(s, 92, 390, 900, 70, name, size=48, color=WHITE, bold=True)
    line(s, 92, 480, 420, 2, LIGHT)
    text(s, 92, 500, 900, 60, desc, size=22, color=WHITE)
    text(s, 92, 650, 400, 30, "tea-market-analysis · 面试作品集", size=14,
         color=RGBColor(0xC7, 0xD6, 0xE8))
    text(s, 1050, 650, 150, 30, f"{page:02d} / {N}", size=14,
         color=RGBColor(0xC7, 0xD6, 0xE8), align=PP_ALIGN.RIGHT)


# ===== P1 封面 =====
s = add_slide()
rect(s, 0, 0, 1280, 720, WHITE)
rect(s, 0, 0, 470, 720, PRIMARY)
rect(s, 470, 0, 6, 720, ACCENT)
text(s, 62, 70, 360, 40, "DATA ANALYTICS · PORTFOLIO", size=16, color=LIGHT, font=FONT_NUM)
text(s, 62, 200, 360, 220,
     [("茶饮门店", {}), ("\n竞争格局与", {}), ("\n选址分析", {})],
     size=52, color=WHITE, bold=True, line_spacing=1.18)
line(s, 62, 470, 300, 2, LIGHT)
para(s, 62, 492, 360, 110,
     [("基于 Yelp 开放数据的真实商户分析", {"size": 19, "color": WHITE}),
      ("含伪重复识别、稳健性检验与自我推翻", {"size": 16, "color": LIGHT})],
     line_spacing=1.6, gap=8)
text(s, 540, 250, 660, 60, "竞品数量是优质商圈的症状，不是病因", size=30, color=PRIMARY, bold=True)
line(s, 540, 330, 640, 1, LINE)
para(s, 540, 360, 640, 220, [
    ([("真实商户数据", {"bold": True, "color": PRIMARY}), ("　150,346 家", {})], {}),
    ([("自建竞品密度特征", {"bold": True, "color": PRIMARY}), ("　Haversine 四档半径", {})], {}),
    ([("结论经检验与修正", {"bold": True, "color": PRIMARY}), ("　推翻初版错误结论", {})], {}),
], size=21, gap=18)
text(s, 540, 640, 640, 30, "汇报人：潘约翰　|　2026", size=16, color=GREY)

# ===== P2 目录 =====
s = add_slide()
content_header(s, "四个部分，讲清一个决策问题", 0)
items = [
    ("01", "背景与数据", "用真实商户数据替代模拟数据，自建竞品密度特征"),
    ("02", "核心发现", "市场集中、密度两极分化，以及一个被推翻的漂亮结论"),
    ("03", "稳健性与边界", "换半径、做 bootstrap，检验结论是否站得住"),
    ("04", "结论", "先选市场，再选商圈，不把竞品数量当信号"),
]
y = 200
for num, name, desc in items:
    text(s, 80, y, 110, 70, num, size=54, color=PRIMARY, bold=True, font=FONT_NUM)
    text(s, 210, y + 2, 360, 44, name, size=29, color=INK, bold=True)
    text(s, 210, y + 48, 780, 32, desc, size=18, color=GREY)
    y += 122
    if num != "04": line(s, 80, y - 18, 1120, 1, LINE)
footer(s, 2)

# ===== P3 章节 01 =====
s = add_slide(); section_page(s, "01", "背景与数据", "真实数据、自建特征，以及天然缺失的那一块", 3)

# ===== P4 数据底座 =====
s = add_slide()
content_header(s, "用真实商户数据回答选址问题，而不是模拟数据", 0)
# 左侧问题编号块
text(s, 60, 180, 540, 36, "要回答的三个问题", size=22, color=PRIMARY, bold=True)
qs = [
    ("Q1", "市场格局", "茶饮门店集中在哪些城市"),
    ("Q2", "竞争效应", "周边竞品越多，生意越差吗"),
    ("Q3", "选址决策", "哪些市场需求已验证、供给未饱和"),
]
y = 228
for tag, t, d in qs:
    rect(s, 60, y, 540, 104, PALE2, line=LINE, lw=0.75, radius=True)
    rect(s, 60, y, 5, 104, PRIMARY)
    text(s, 82, y + 12, 60, 34, tag, size=22, color=PRIMARY, bold=True, font=FONT_NUM)
    text(s, 145, y + 12, 430, 34, t, size=22, color=INK, bold=True)
    text(s, 145, y + 52, 430, 34, d, size=17, color=GREY)
    y += 120
# 右侧数据漏斗
text(s, 650, 180, 560, 36, "数据底座（Yelp Open Dataset）", size=22, color=PRIMARY, bold=True)
funnel = [("150,346", "商户总数", 530), ("7,069", "茶饮门店（三类业态）", 420), ("477", "奶茶店（分析主体）", 310)]
y = 232
for i, (n, label, w) in enumerate(funnel):
    x = 650 + (530 - w) / 2
    rect(s, x, y, w, 86, [PRIMARY, SECOND, LIGHT][i], radius=True)
    text(s, x, y + 6, w, 46, n, size=38 if i == 0 else 34, color=WHITE if i < 2 else ACCENT,
         bold=True, align=PP_ALIGN.CENTER, font=FONT_NUM)
    text(s, x, y + 50, w, 30, label, size=16, color=WHITE if i < 2 else ACCENT, align=PP_ALIGN.CENTER)
    y += 100
text(s, 650, 542, 560, 70,
     "覆盖 Yelp 的 8 个都市圈、15 州/省；无销量、无开店日期，需求只能用累计评论数代理。",
     size=18, color=GREY, line_spacing=1.4)
conclusion_bar(s, 622,
    [("所以呢：", {"bold": True, "color": PRIMARY}),
     ("竞品密度数据里没有，必须用经纬度自己算；需求是代理变量，结论要讲边界。", {})], h=38)
footer(s, 4)

# ===== P5 Q1 市场集中 =====
s = add_slide()
content_header(s, "市场高度集中：前 5 城占 34%，费城是最大单一市场", 0)
pic(s, "q1_city_distribution.png", 60, 176, 700)
rect(s, 800, 176, 420, 400, PALE2, line=LINE, lw=0.75, radius=True)
text(s, 824, 200, 372, 40, "最大单一市场", size=21, color=PRIMARY, bold=True)
text(s, 824, 250, 372, 60, "956", size=54, color=ACCENT, bold=True, font=FONT_NUM)
text(s, 900, 278, 280, 34, "家茶饮门店 · 费城", size=18, color=INK)
line(s, 824, 330, 372, 1, LINE)
para(s, 824, 350, 372, 210, [
    ([("前 5 城占 34%", {"bold": True, "color": PRIMARY})], {}),
    ([("头部市场值得优先进入，但城市字段是用户填写的。", {})], {"size": 18}),
    ([("同一都市圈可能被拆成多个城市（如费城与 Cherry Hill），集中度数字受口径影响。", {})], {"size": 18}),
], size=19, gap=12)
conclusion_bar(s, 600,
    [("所以呢：", {"bold": True, "color": PRIMARY}),
     ("先锁定头部市场，但不要把这个百分比当成精确的市占率。", {})], h=48)
footer(s, 5)

# ===== P6 Q2 两极分化 =====
s = add_slide()
content_header(s, "竞争呈两极分化：38% 零竞品，30% 贴身竞争", 0)
pic(s, "q2_competitor_density.png", 60, 180, 640)
rect(s, 740, 180, 240, 180, PALE2, line=LINE, lw=0.75, radius=True)
text(s, 760, 200, 200, 34, "独立区隔市场", size=19, color=GREEN, bold=True)
text(s, 760, 240, 200, 60, "38%", size=48, color=GREEN, bold=True, font=FONT_NUM)
text(s, 760, 306, 200, 40, "1km 内零竞品", size=17, color=GREY)
rect(s, 1000, 180, 220, 180, PALE2, line=LINE, lw=0.75, radius=True)
text(s, 1020, 200, 180, 34, "贴身竞争", size=19, color=RED, bold=True)
text(s, 1020, 240, 180, 60, "30%", size=48, color=RED, bold=True, font=FONT_NUM)
text(s, 1020, 306, 180, 40, "1km 内 ≥3 家", size=17, color=GREY)
para(s, 740, 390, 480, 170, [
    ([("密度用 Haversine 球面距离自建：", {"bold": True, "color": PRIMARY})], {}),
    ([("0.5 / 1 / 2 / 3km 四档半径，同州掩码避免跨界误计。1km 约等于步行 10 分钟商圈。", {})], {"size": 18}),
    ([("用经纬度自己造字段——这是真实数据和模拟数据最大的区别。", {"size": 18, "color": GREY})], {"size": 18}),
], size=19, gap=10)
conclusion_bar(s, 600,
    [("所以呢：", {"bold": True, "color": PRIMARY}),
     ("市场不是均匀的，不能用“平均竞品数”描述，必须分组看。", {})], h=48)
footer(s, 6)

# ===== P7 章节 02 =====
s = add_slide(); section_page(s, "02", "核心发现", "一个被推翻的漂亮结论，和它背后的真正机制", 7)

# ===== P8 伪重复（核心页） =====
s = add_slide()
content_header(s, "初版结论“竞品越多越火”是假的：23 家高密度店全在一个街区", 2)
pic(s, "q8_threshold.png", 60, 176, 1160)
# 图下方两个关键数字
rect(s, 60, 512, 360, 82, PALE2, line=LINE, lw=0.75, radius=True)
text(s, 80, 522, 320, 30, "相关系数 r", size=16, color=GREY)
text(s, 80, 550, 320, 40, "0.19  →  0.016", size=28, color=PRIMARY, bold=True, font=FONT_NUM)
rect(s, 440, 512, 360, 82, PALE2, line=LINE, lw=0.75, radius=True)
text(s, 460, 522, 320, 30, "分组差异 p", size=16, color=GREY)
text(s, 460, 550, 320, 40, "0.049  →  0.76", size=28, color=PRIMARY, bold=True, font=FONT_NUM)
rect(s, 820, 512, 400, 82, PALE2, line=LINE, lw=0.75, radius=True)
text(s, 840, 522, 360, 30, "高密度门店来源", size=16, color=GREY)
text(s, 840, 548, 360, 42, "费城唐人街 19107 · 23 家", size=22, color=RED, bold=True)
conclusion_bar(s, 616,
    [("所以呢：", {"bold": True, "color": PRIMARY}),
     ("这 23 家本质是 1 个观测（均评论 186 vs 费城其他 56）。竞品数量是优质商圈的症状，不是病因。", {})], h=42)
footer(s, 8, "口径：剔除 competitors_1km ≥ 20 的伪重复簇后重算；Mann-Whitney p<0.001")

# ===== P9 评分梯度幸存 =====
s = add_slide()
content_header(s, "评分梯度是真实现象：剔除伪重复簇后 p=0.0017 仍显著", 2)
# 左右对照
rect(s, 60, 180, 555, 330, PALE2, line=LINE, lw=0.75, radius=True)
text(s, 84, 200, 510, 40, "被推翻：热度结论", size=24, color=RED, bold=True)
text(s, 84, 258, 510, 50, "r  0.19 → 0.016", size=34, color=RED, bold=True, font=FONT_NUM)
para(s, 84, 330, 505, 160, [
    ([("剔除唐人街簇后相关性归零，分组差异 p 从 0.049 升到 0.76。", {})], {"size": 18}),
    ([("结论：密度不提升需求——初版判断被自己的检验推翻。", {"bold": True, "color": INK})], {"size": 18}),
], size=18, gap=12)
rect(s, 665, 180, 555, 330, PALE2, line=LINE, lw=0.75, radius=True)
text(s, 689, 200, 510, 40, "幸存：评分结论", size=24, color=GREEN, bold=True)
text(s, 689, 258, 510, 50, "p  0.0001 → 0.0017", size=34, color=GREEN, bold=True, font=FONT_NUM)
para(s, 689, 330, 505, 160, [
    ([("独占区 4.18 → 最卷区 3.86，剔除簇后仍显著（H=15.19）。", {})], {"size": 18}),
    ([("结论：评分分化是全样本现象，不是单一街区伪造的。", {"bold": True, "color": INK})], {"size": 18}),
], size=18, gap=12)
conclusion_bar(s, 540,
    [("关键的诚实：", {"bold": True, "color": PRIMARY}),
     ("同样的样本、同样的检验流程，一个被推翻、一个幸存——说明检验不是走过场。", {})], h=48)
text(s, 60, 606, 1160, 40,
     "评分下降的两种机制（低质店在无竞争区存活 / 高竞争区评分更分化）单期截面无法区分，屬后续研究方向。",
     size=17, color=GREY)
footer(s, 9)

# ===== P10 蓝海 =====
s = add_slide()
content_header(s, "蓝海候选池 11 城：Reno、Indianapolis、New Orleans 排序稳定", 2)
pic(s, "q5_blue_ocean.png", 60, 172, 700)
rect(s, 790, 172, 430, 420, PALE2, line=LINE, lw=0.75, radius=True)
text(s, 814, 192, 382, 36, "蓝海指数口径（已统一）", size=20, color=PRIMARY, bold=True)
text(s, 814, 234, 382, 60, "需求强度 ×（1 − 奶茶渗透率）", size=19, color=INK, bold=True, line_spacing=1.3)
line(s, 814, 306, 382, 1, LINE)
text(s, 814, 320, 382, 34, "入选门槛：奶茶店≥5、茶饮店≥50", size=17, color=GREY)
text(s, 814, 366, 382, 40, "bootstrap 1000 次", size=18, color=PRIMARY, bold=True)
para(s, 814, 404, 382, 180, [
    ([("Reno", {"bold": True, "color": PRIMARY}), ("　87% 进前三", {})], {"size": 19}),
    ([("New Orleans", {"bold": True, "color": PRIMARY}), ("　82% 进前三", {})], {"size": 19}),
    ([("Indianapolis", {"bold": True, "color": PRIMARY}), ("　79% 进前三", {})], {"size": 19}),
    ([("口径修正后候选池从 18 城收敛到 11 城。", {"color": GREY})], {"size": 17}),
], size=19, gap=10)
conclusion_bar(s, 608,
    [("所以呢：", {"bold": True, "color": PRIMARY}),
     ("只能讲“候选池排名”，不能讲“第一名绝对最好”；指数只是进入优先级参考。", {})], h=46)
footer(s, 10)

# ===== P11 街区粒度 =====
s = add_slide()
content_header(s, "城市内部差异巨大：选址必须下沉到街区", 2)
pic(s, "q6_philadelphia_map.png", 60, 174, 480)
rect(s, 580, 174, 640, 400, PALE2, line=LINE, lw=0.75, radius=True)
text(s, 606, 196, 590, 40, "费城 19107：需求被验证的样本", size=22, color=PRIMARY, bold=True)
para(s, 606, 254, 590, 230, [
    ([("23 家奶茶店聚集，均评论 186 条——城市内部的热度差异远大于城市之间。", {})], {"size": 19}),
    ([("但这批店与 Q8 的伪重复簇是同一批门店：热度高说明需求存在，也可能意味着市场接近饱和。", {})], {"size": 19}),
    ([("正确用法：先确认“这里有被验证的需求”，再叠加竞品间距、租金、铺位可得性做二次筛选。", {"bold": True, "color": INK})], {"size": 19}),
], size=19, gap=16)
conclusion_bar(s, 600,
    [("所以呢：", {"bold": True, "color": PRIMARY}),
     ("数据给方向，不给最终答案——不直接推荐在 19107 开店。", {})], h=48)
footer(s, 11, "口径：费城奶茶店经度/纬度散点，颜色越深表示累计评论数越高")

# ===== P12 章节 03 =====
s = add_slide(); section_page(s, "03", "稳健性与边界", "结论能不能对外讲，取决于它经不经得起折腾", 12)

# ===== P13 稳健性 =====
s = add_slide()
content_header(s, "结论不依赖参数选择，也不依赖单一城市排名", 2)
pic(s, "q9_robustness.png", 60, 176, 1160)
rect(s, 60, 500, 560, 108, PALE2, line=LINE, lw=0.75, radius=True)
text(s, 82, 514, 516, 32, "半径敏感性 · 剔除簇后", size=17, color=PRIMARY, bold=True)
text(s, 82, 550, 516, 46, "0.046  /  0.016  /  −0.028", size=25, color=ACCENT, bold=True, font=FONT_NUM)
rect(s, 660, 500, 560, 108, PALE2, line=LINE, lw=0.75, radius=True)
text(s, 682, 514, 516, 32, "bootstrap 排序稳定性", size=17, color=PRIMARY, bold=True)
text(s, 682, 550, 516, 46, "Reno 87% · NOLA 82%", size=25, color=ACCENT, bold=True, font=FONT_NUM)
text(s, 60, 624, 1160, 36,
     "三档半径（0.5/1/2km）下 p 均 >0.05，“密度不提升需求”稳健；但评论数是累计值，含资历偏差（老店天然占优），这是 V2 要解决的第一件事。",
     size=17, color=GREY)
footer(s, 13)

# ===== P14 结尾 =====
s = add_slide()
rect(s, 0, 0, 1280, 720, ACCENT)
text(s, 80, 90, 1120, 70, "别怕竞品，别信竞品", size=56, color=WHITE, bold=True)
line(s, 80, 184, 500, 2, LIGHT)
text(s, 80, 210, 1100, 50, "先选市场，再选商圈，不把竞品数量当信号", size=26, color=LIGHT)
steps = [
    ("01", "选市场", "优先进入需求旺、奶茶店少的蓝海候选池"),
    ("02", "选商圈", "进入需求已被验证的成熟商圈，但不追竞品数量"),
    ("03", "筛铺位", "下沉到街区粒度，叠加租金与铺位可得性"),
]
y = 320
for num, t, d in steps:
    rect(s, 80, y, 1120, 92, RGBColor(0x25, 0x40, 0x66), line=SECOND, lw=0.5, radius=True)
    text(s, 104, y + 12, 90, 60, num, size=36, color=LIGHT, bold=True, font=FONT_NUM)
    text(s, 210, y + 14, 220, 44, t, size=26, color=WHITE, bold=True)
    text(s, 210, y + 54, 900, 32, d, size=18, color=RGBColor(0xC7, 0xD6, 0xE8))
    y += 108
text(s, 80, 660, 700, 30, "限制：缺租金与开店成本，结论只谈需求侧，落地需实地验证。", size=15, color=RGBColor(0xA8, 0xBC, 0xD4))
text(s, 1100, 660, 100, 30, "14 / 14", size=15, color=RGBColor(0xA8, 0xBC, 0xD4), align=PP_ALIGN.RIGHT)

prs.save(OUT)
print("已生成:", OUT)
print("页数:", len(prs.slides._sldIdLst))
