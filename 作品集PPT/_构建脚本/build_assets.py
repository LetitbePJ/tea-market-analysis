# -*- coding: utf-8 -*-
"""生成 V3 展示资源：
1) 图表保结构重着色——只替换高饱和数据色到茶色系，文字/网格/背景保持原样；
2) 茶饮单色线稿暗纹——茶叶、奶茶杯、水波纹，透明度 10%-18%。

不改动任何数据、数值、文字，只做视觉样式处理。
"""
import colorsys
import glob
import math
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "assets_v3")
os.makedirs(OUT, exist_ok=True)

# ---- 硬性规范色 ----
DARK = (0x2C, 0x44, 0x47)   # 茶青灰蓝
CLAY = (0xD4, 0x8B, 0x5C)   # 浅茶棕橙
PAPER = (0xF6, 0xF5, 0xF0)  # 浅米茶白

# 由规范色派生的同色系低饱和色（非新增色相）
SAGE = tuple(int(DARK[i] * 0.42 + PAPER[i] * 0.58) for i in range(3))   # 青灰浅
SAND = tuple(int(CLAY[i] * 0.48 + PAPER[i] * 0.52) for i in range(3))   # 茶棕浅


def remap_rgb(arr):
    """HSV 色相分类重映射；近灰/近白像素（文字、网格、背景）保持不变。"""
    rgb = arr[..., :3].astype(np.float32) / 255.0
    mx = rgb.max(axis=2)
    mn = rgb.min(axis=2)
    v = mx
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)

    # 色相（度）
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    h = np.zeros_like(mx)
    mask = (mx - mn) > 1e-6
    idx = mask & (mx == r)
    h[idx] = ((g[idx] - b[idx]) / (mx[idx] - mn[idx])) % 6
    idx = mask & (mx == g)
    h[idx] = ((b[idx] - r[idx]) / (mx[idx] - mn[idx])) + 2
    idx = mask & (mx == b)
    h[idx] = ((r[idx] - g[idx]) / (mx[idx] - mn[idx])) + 4
    h = (h * 60) % 360

    base = np.zeros((*mx.shape, 3), dtype=np.float32)
    blue = (h >= 175) & (h < 250)
    red = (h < 40) | (h >= 330)
    green = (h >= 90) & (h < 175)
    yellow = (h >= 40) & (h < 90)
    other = ~(blue | red | green | yellow)
    for m, col in ((blue, DARK), (red, CLAY), (green, SAGE),
                   (yellow, SAND), (other, DARK)):
        base[m] = col

    # 用原明度保留深浅层次（数据渐变语义不丢）
    f = (0.70 + 0.30 * v)[..., None]
    out = np.clip(base * f, 0, 255).astype(np.uint8)

    # 中性像素（文字/网格/白色背景）保持原样
    neutral = (s < 0.16) | (v > 0.965)
    out[neutral] = arr[..., :3][neutral]
    return out


def recolor_charts():
    for p in sorted(glob.glob(os.path.join(SRC, "*.png"))):
        im = Image.open(p).convert("RGBA")
        a = np.array(im)
        a[..., :3] = remap_rgb(a)
        dst = os.path.join(OUT, os.path.basename(p))
        Image.fromarray(a).save(dst)
        print("图表重着色:", os.path.basename(dst))


# ---------- 茶饮线稿 ----------
def bezier(p0, p1, p2, p3, n=48):
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        pts.append((
            u**3 * p0[0] + 3 * u*u*t * p1[0] + 3 * u*t*t * p2[0] + t**3 * p3[0],
            u**3 * p0[1] + 3 * u*u*t * p1[1] + 3 * u*t*t * p2[1] + t**3 * p3[1],
        ))
    return pts


def motif(size, color, alpha, drawer, name):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = (*color, alpha)
    drawer(d, size, c)
    im.save(os.path.join(OUT, name))
    print("线稿:", name)


def draw_leaf(d, S, c):
    top = bezier((S*0.06, S*0.60), (S*0.22, S*0.20), (S*0.70, S*0.14), (S*0.90, S*0.48))
    bot = bezier((S*0.90, S*0.48), (S*0.72, S*0.84), (S*0.24, S*0.88), (S*0.06, S*0.60))
    d.line(top + bot + [top[0]], fill=c, width=3, joint="curve")
    d.line(bezier((S*0.08, S*0.60), (S*0.36, S*0.56), (S*0.62, S*0.50), (S*0.88, S*0.48)),
           fill=c, width=2)
    for t in (0.25, 0.45, 0.65):
        x, y = bezier((S*0.08, S*0.60), (S*0.36, S*0.56), (S*0.62, S*0.50), (S*0.88, S*0.48), 60)[int(60*t)]
        d.line([(x, y), (x - S*0.02, y - S*0.13)], fill=c, width=2)


def draw_cup(d, S, c):
    d.line([(S*0.25, S*0.34), (S*0.33, S*0.84), (S*0.69, S*0.84), (S*0.77, S*0.34)],
           fill=c, width=3, joint="curve")
    d.line([(S*0.21, S*0.32), (S*0.81, S*0.32)], fill=c, width=3)
    d.line([(S*0.56, S*0.32), (S*0.64, S*0.09)], fill=c, width=3)
    d.line([(S*0.28, S*0.45), (S*0.74, S*0.45)], fill=c, width=2)
    d.arc([S*0.40, S*0.52, S*0.62, S*0.72], 20, 160, fill=c, width=2)


def draw_wave(d, S, c):
    for k in range(4):
        y0 = S * (0.28 + 0.13 * k)
        pts = [(x, y0 + S*0.028 * math.sin(x / S * 5 * math.pi + k * 0.7))
               for x in range(int(S*0.06), int(S*0.95), 4)]
        d.line(pts, fill=c, width=2)


def draw_ring(d, S, c):
    d.ellipse([S*0.12, S*0.12, S*0.88, S*0.88], outline=c, width=3)
    d.ellipse([S*0.24, S*0.24, S*0.76, S*0.76], outline=c, width=1)


def make_motifs():
    # 深色板块用：同色系青灰浅线稿（后续再叠纯色蒙版压低）
    motif(560, SAGE, 70, draw_leaf, "motif_leaf_light.png")
    motif(560, SAGE, 62, draw_cup, "motif_cup_light.png")
    motif(620, SAGE, 60, draw_wave, "motif_wave_light.png")
    motif(560, SAGE, 66, draw_ring, "motif_ring_light.png")
    # 浅色内页用：规范深色线稿，透明度 10%-18% → alpha 26-46
    motif(560, DARK, 34, draw_leaf, "motif_leaf.png")
    motif(560, DARK, 30, draw_cup, "motif_cup.png")
    motif(620, CLAY, 30, draw_wave, "motif_wave.png")


def generate_dark_bg():
    """深色板块背景：茶青灰蓝底 + 同色系线稿暗纹 + 纯色蒙版（保证白标题锐利）。"""
    def compose(W, H, layers, name):
        base = Image.new("RGBA", (W, H), (*DARK, 255))
        for fname, size, pos in layers:
            m = Image.open(os.path.join(OUT, fname)).resize(size)
            base.alpha_composite(m, pos)
        # 纯色蒙版：再压低暗纹，白标题区保持干净
        base = Image.alpha_composite(base, Image.new("RGBA", (W, H), (*DARK, 52)))
        base.convert("RGB").save(os.path.join(OUT, name))
        print("暗纹背景:", name)

    # 封面左栏：茶叶 + 水波，偏右下，避开左上标题区
    compose(452, 720, [
        ("motif_leaf_light.png", (500, 500), (-150, 300)),
        ("motif_wave_light.png", (560, 560), (-120, 520)),
    ], "bg_cover_left.png")
    # 章节页：右侧茶叶 + 底部水波，避开左侧标题
    compose(1280, 720, [
        ("motif_leaf_light.png", (620, 620), (720, 150)),
        ("motif_wave_light.png", (760, 760), (-100, 420)),
    ], "bg_section.png")
    # 结尾页：右下茶叶 + 左下水波
    compose(1280, 720, [
        ("motif_leaf_light.png", (560, 560), (820, 250)),
        ("motif_wave_light.png", (680, 680), (-160, 400)),
    ], "bg_ending.png")


if __name__ == "__main__":
    recolor_charts()
    make_motifs()
    generate_dark_bg()
    print("资源目录:", OUT)
