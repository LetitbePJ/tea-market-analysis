# -*- coding: utf-8 -*-
"""V4 展示资源：
1) 图表保结构重着色——只替换高饱和数据色到新规范茶色系，文字/网格/背景保持原样；
2) 铺满整页的低透明度茶饮线稿肌理——茶叶轮廓 + 柔和茶汤波纹，透明度 8%-14%。

新硬性规范配色：#F5F3EE 底 / #384A48 茶灰绿 / #947C6B 哑光浅茶棕。
不改动任何数据、数值、文字。输出到 assets_v4，旧资源目录不覆盖。
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "assets_v4")
os.makedirs(OUT, exist_ok=True)

# ---- 新硬性规范色 ----
DARK = (0x38, 0x4A, 0x48)   # 低饱和茶灰绿
CLAY = (0x94, 0x7C, 0x6B)   # 哑光浅茶棕
PAPER = (0xF5, 0xF3, 0xEE)  # 浅茶米白

# 同色系派生（非新增色相）：用于图表内的次级数据系列
SAGE = tuple(int(DARK[i] * 0.46 + PAPER[i] * 0.54) for i in range(3))
SAND = tuple(int(CLAY[i] * 0.52 + PAPER[i] * 0.48) for i in range(3))


def remap_rgb(arr):
    """HSV 色相分类重映射；近灰/近白像素（文字、网格、背景）保持不变。"""
    rgb = arr[..., :3].astype(np.float32) / 255.0
    mx = rgb.max(axis=2)
    mn = rgb.min(axis=2)
    v = mx
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)

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

    # 保留深浅层次，但不过度压暗哑光色
    f = (0.88 + 0.12 * v)[..., None]
    out = np.clip(base * f, 0, 255).astype(np.uint8)

    neutral = (s < 0.16) | (v > 0.965)
    out[neutral] = arr[..., :3][neutral]
    return out


def recolor_charts():
    for p in sorted(os.listdir(SRC)):
        if not p.lower().endswith(".png"):
            continue
        im = Image.open(os.path.join(SRC, p)).convert("RGBA")
        a = np.array(im)
        a[..., :3] = remap_rgb(a)
        Image.fromarray(a).save(os.path.join(OUT, p))
        print("图表重着色:", p)


# ---------- 茶饮线稿（舒展贝塞尔，单色） ----------
def bezier(p0, p1, p2, p3, n=64):
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        pts.append((
            u**3 * p0[0] + 3 * u*u*t * p1[0] + 3 * u*t*t * p2[0] + t**3 * p3[0],
            u**3 * p0[1] + 3 * u*u*t * p1[1] + 3 * u*t*t * p2[1] + t**3 * p3[1],
        ))
    return pts


def leaf_tile(S, color, alpha):
    """一片舒展茶叶线稿（透明底），用于平铺肌理。"""
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = (*color, alpha)
    top = bezier((S*0.04, S*0.62), (S*0.16, S*0.18), (S*0.70, S*0.10), (S*0.94, S*0.40))
    bot = bezier((S*0.94, S*0.40), (S*0.76, S*0.86), (S*0.22, S*0.90), (S*0.04, S*0.62))
    d.line(top + bot + [top[0]], fill=c, width=max(1, S // 150), joint="curve")
    mid = bezier((S*0.06, S*0.62), (S*0.36, S*0.55), (S*0.64, S*0.48), (S*0.92, S*0.40))
    d.line(mid, fill=c, width=max(1, S // 200))
    spine = bezier((S*0.06, S*0.62), (S*0.36, S*0.55), (S*0.64, S*0.48), (S*0.92, S*0.40), 80)
    for t in (0.22, 0.40, 0.58, 0.76):
        x, y = spine[int(80 * t)]
        d.line([(x, y), (x - S*0.03, y - S*0.16)], fill=c, width=max(1, S // 240))
        d.line([(x, y), (x + S*0.01, y + S*0.15)], fill=c, width=max(1, S // 240))
    return im


def wave_tile(S, color, alpha):
    """柔和茶汤波纹（透明底）。"""
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = (*color, alpha)
    for k in range(3):
        y0 = S * (0.30 + 0.16 * k)
        pts = [(x, y0 + S * 0.035 * math.sin(x / S * 3.5 * math.pi + k * 0.8))
               for x in range(int(S*0.04), int(S*0.96), 3)]
        d.line(pts, fill=c, width=max(1, S // 260))
    return im


def pearl_tile(S, color, alpha):
    """珍珠（波霸）：一组小圆圈，疏密不一地散在杯底。"""
    rnd = random.Random(int(S) + 7)
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = (*color, alpha)
    w = max(1, S // 150)
    for _ in range(11):
        r = rnd.uniform(S * 0.028, S * 0.05)
        x = rnd.uniform(S * 0.12, S * 0.88)
        y = rnd.uniform(S * 0.55, S * 0.9)
        d.ellipse([x - r, y - r, x + r, y + r], outline=c, width=w)
    return im


def jelly_tile(S, color, alpha):
    """椰果：几颗圆角方块，零散漂着。"""
    rnd = random.Random(int(S) + 13)
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = (*color, alpha)
    w = max(1, S // 170)
    for _ in range(7):
        s = rnd.uniform(S * 0.07, S * 0.11)
        x = rnd.uniform(S * 0.12, S * 0.82)
        y = rnd.uniform(S * 0.15, S * 0.82)
        d.rounded_rectangle([x, y, x + s, y + s * 0.82], radius=s * 0.18,
                            outline=c, width=w)
    return im


def bean_tile(S, color, alpha):
    """咖啡豆：椭圆轮廓 + 中间一道弧线（中缝）。"""
    rnd = random.Random(int(S) + 29)
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = (*color, alpha)
    w = max(1, S // 160)
    for _ in range(4):
        cx = rnd.uniform(S * 0.2, S * 0.8)
        cy = rnd.uniform(S * 0.2, S * 0.8)
        rw = rnd.uniform(S * 0.07, S * 0.1)
        rh = rw * 0.68
        ang = rnd.uniform(-1.2, 1.2)
        dx, dy = math.cos(ang) * rw, math.sin(ang) * rw * 0.5
        pts = []
        for t in range(25):
            a = 2 * math.pi * t / 24
            px = cx + dx * math.cos(a) - dy * 0.5 * math.sin(a)
            py = cy + dy * math.sin(a) + dx * 0.5 * math.cos(a)
            pts.append((px, py))
        d.line(pts + [pts[0]], fill=c, width=w, joint="curve")
        d.line([(cx - dx * 0.72, cy - dy * 0.72), (cx, cy),
                (cx + dx * 0.72, cy + dy * 0.72)], fill=c, width=w)
    return im


def texture(name, seed, alpha, leaf_size, wave_size, leaf_n, wave_n):
    """生成铺满整页的淡肌理底图（1280x720，米白底 + 低对比线稿）。"""
    W, H = 1280, 720
    rnd = random.Random(seed)
    base = Image.new("RGBA", (W, H), (*PAPER, 255))

    leaf = leaf_tile(leaf_size, DARK, alpha)
    wave = wave_tile(wave_size, CLAY, max(1, int(alpha * 0.8)))

    # 茶叶：随机散点（非网格），尺寸/角度各异，疏密随参数变化
    for _ in range(leaf_n * 3):
        sc = rnd.uniform(0.62, 1.32)
        m0 = leaf.resize((int(leaf_size * sc), int(leaf_size * sc)))
        m = m0.rotate(rnd.uniform(-170, 170), resample=Image.BICUBIC, expand=True)
        x = int(rnd.uniform(-m.width * 0.35, W - m.width * 0.45))
        y = int(rnd.uniform(-m.height * 0.35, H - m.height * 0.45))
        base.alpha_composite(m, (x, y))

    # 水波：横向柔和曲线，铺在若干高度
    for k in range(wave_n):
        m = wave.rotate(rnd.uniform(-8, 8), resample=Image.BICUBIC, expand=True)
        x = int(rnd.uniform(-120, W - wave_size * 0.5))
        y = int(rnd.uniform(-40, H - wave_size * 0.4))
        base.alpha_composite(m, (x, y))

    # 点缀小料：珍珠 / 椰果 / 咖啡豆——数量更少、透明度再压一档，只作肌理里的轻点缀
    dot_alpha = max(1, int(alpha * 0.8))
    accents = [
        (pearl_tile(150, CLAY, dot_alpha), 2),
        (jelly_tile(150, DARK, dot_alpha), 2),
        (bean_tile(150, CLAY, dot_alpha), 1),
    ]
    for tile, cnt in accents:
        for _ in range(cnt):
            m = tile.rotate(rnd.uniform(-45, 45), resample=Image.BICUBIC, expand=True)
            x = int(rnd.uniform(-30, W - m.width * 0.6))
            y = int(rnd.uniform(-30, H - m.height * 0.6))
            base.alpha_composite(m, (x, y))

    base.convert("RGB").save(os.path.join(OUT, name))
    print("肌理底图:", name, "alpha=", alpha)


def generate_textures():
    # 封面稍明显、图表页更淡、章节与结尾居中；seed 不同 → 疏密与角度各异
    texture("bg_cover.png",  seed=11, alpha=34, leaf_size=300, wave_size=520, leaf_n=5, wave_n=3)
    texture("bg_text.png",   seed=23, alpha=26, leaf_size=260, wave_size=460, leaf_n=4, wave_n=2)
    texture("bg_chart.png",  seed=37, alpha=21, leaf_size=240, wave_size=440, leaf_n=3, wave_n=2)
    texture("bg_section.png",seed=41, alpha=30, leaf_size=320, wave_size=560, leaf_n=5, wave_n=3)
    texture("bg_end.png",    seed=53, alpha=28, leaf_size=300, wave_size=520, leaf_n=4, wave_n=3)


if __name__ == "__main__":
    recolor_charts()
    generate_textures()
    print("资源目录:", OUT)
