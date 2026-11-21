# -*- coding: utf-8 -*-
"""用 Pillow 渲染 README 主视觉 hero.png（设计稿 1200x630，2x 超采样）。"""
import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "hero.png")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

DW, DH = 1200, 630
S = 2
W, H = DW * S, DH * S
FD = "C:/Windows/Fonts"


def font(name, size):
    return ImageFont.truetype(os.path.join(FD, name), int(size * S))


F_TITLE = font("segoeuib.ttf", 76)
F_TAG = font("msyhbd.ttc", 36)
F_BODY = font("msyh.ttc", 19)
F_EYE = font("segoeui.ttf", 13)
F_CHIP = font("msyh.ttc", 14)
F_QUOTE = font("segoeuii.ttf", 15)
F_SMALL = font("segoeui.ttf", 12)
F_BUBBLE = font("msyh.ttc", 19)
F_PILL = font("msyh.ttc", 20)
F_PILL_HI = font("msyhbd.ttc", 20)
F_AVATAR = font("msyh.ttc", 11)
F_BTN = font("msyh.ttc", 16)
F_SYM = font("seguisym.ttf", 17)
F_SEG = font("msyh.ttc", 12)

img = Image.new("RGBA", (W, H), (7, 11, 24, 255))
d = ImageDraw.Draw(img)


def P(*vals):
    return [v * S for v in vals]


def layer():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def compose(ly):
    img.alpha_composite(ly)


# ---------------------------------------------------------------- background
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
t = xx / (W - 1) * 0.55 + yy / (H - 1) * 0.45
c0, c1, c2 = (7, 11, 24), (13, 11, 36), (4, 18, 28)
arr = np.zeros((H, W, 3), np.float32)
for i in range(3):
    arr[:, :, i] = np.interp(t, [0, 0.55, 1], [c0[i], c1[i], c2[i]])

for cx, cy, rad, col, op in [
    (250, 110, 440, (124, 58, 237), 0.42),
    (1080, 580, 460, (6, 182, 212), 0.30),
    (980, 80, 320, (236, 72, 153), 0.18),
]:
    dd = np.sqrt((xx - cx * S) ** 2 + (yy - cy * S) ** 2) / (rad * S)
    a = np.clip(1.0 - dd, 0, 1) ** 2 * op
    for i in range(3):
        arr[:, :, i] += col[i] * a

arr = np.clip(arr, 0, 255).astype(np.uint8)
img = Image.fromarray(arr, "RGB").convert("RGBA")
d = ImageDraw.Draw(img)

# dot grid
dots = layer()
ddraw = ImageDraw.Draw(dots)
step = 26 * S
for x in range(0, W, step):
    for y in range(0, H, step):
        ddraw.ellipse([x - 1 * S, y - 1 * S, x + 1 * S, y + 1 * S], fill=(148, 163, 184, 28))
compose(dots)


# ---------------------------------------------------------------- helpers
def grad_image(c1, c2, x1, x2):
    tt = np.clip((np.arange(W, dtype=np.float32) - x1 * S) / max(1.0, (x2 - x1) * S), 0, 1)
    out = np.zeros((H, W, 4), np.uint8)
    for i in range(3):
        out[:, :, i] = (c1[i] + (c2[i] - c1[i]) * tt)[None, :].astype(np.uint8)
    out[:, :, 3] = 255
    return Image.fromarray(out, "RGBA")


def gradient_text(x, y, text, fnt, c1, c2, anchor="ls"):
    mask_layer = layer()
    ImageDraw.Draw(mask_layer).text((x * S, y * S), text, font=fnt, fill=(255, 255, 255, 255), anchor=anchor)
    bbox = mask_layer.getbbox()
    if not bbox:
        return
    grad = grad_image(c1, c2, bbox[0] / S, bbox[2] / S)
    out = layer()
    out.paste(grad, (0, 0), mask_layer.split()[3])
    compose(out)


def tracked(x, y, text, fnt, fill, tracking, draw_obj):
    cx = x * S
    for ch in text:
        draw_obj.text((cx, y * S), ch, font=fnt, fill=fill, anchor="ls")
        cx += draw_obj.textlength(ch, font=fnt) + tracking * S


def soft_glow(box, radius, color, blur, width=6):
    ly = layer()
    ImageDraw.Draw(ly).rounded_rectangle(P(*box), radius=radius * S, outline=color, width=width)
    ly = ly.filter(ImageFilter.GaussianBlur(blur * S))
    compose(ly)


# ---------------------------------------------------------------- left copy
eye = layer()
tracked(80, 92, "IDEA #013  ·  INPUT METHOD", F_EYE, (124, 137, 168, 255), 4, ImageDraw.Draw(eye))
compose(eye)

gradient_text(76, 184, "BubbleType", F_TITLE, (245, 208, 254), (103, 232, 249))
d.text((80 * S, 248 * S), "不敲键盘，只点词。", font=F_TAG, fill=(248, 250, 252, 255), anchor="ls")
d.text((80 * S, 302 * S), "识别对方最后一句，把字母键的位置铺满「下一词」；", font=F_BODY,
       fill=(148, 163, 184, 255), anchor="ls")
d.text((80 * S, 332 * S), "点一个，立刻以它为新起点，长出下一波。", font=F_BODY,
       fill=(148, 163, 184, 255), anchor="ls")

chips = ["零打字", "端侧推理", "一键回退"]
cx = 80
for c in chips:
    cw = d.textlength(c, font=F_CHIP) / S + 28
    box = (cx, 360, cx + cw, 392)
    ly = layer()
    ImageDraw.Draw(ly).rounded_rectangle(P(*box), radius=16 * S, fill=(255, 255, 255, 9),
                                         outline=(148, 163, 184, 56), width=2)
    compose(ly)
    d.text(((cx + cw / 2) * S, 376 * S), c, font=F_CHIP, fill=(203, 213, 225, 255), anchor="mm")
    cx += cw + 12

d.text((80 * S, 548 * S), "“The best keyboard is the one you never touch.”",
       font=F_QUOTE, fill=(100, 116, 139, 255), anchor="ls")

sm = layer()
tracked(80, 578, "BUBBLETYPE · CONCEPT 2026", F_SMALL, (71, 85, 105, 255), 1.5, ImageDraw.Draw(sm))
compose(sm)

# ---------------------------------------------------------------- phone
rot = layer()
ImageDraw.Draw(rot).rounded_rectangle(P(666, 38, 1134, 592), radius=64 * S,
                                      outline=(139, 92, 246, 40), width=2)
rot = rot.rotate(-4, center=(900 * S, 315 * S), resample=Image.BICUBIC)
compose(rot)

# shadow
sh = layer()
ImageDraw.Draw(sh).rounded_rectangle(P(690, 56, 1110, 574), radius=46 * S, fill=(34, 211, 238, 46))
sh = sh.filter(ImageFilter.GaussianBlur(34 * S))
compose(sh)
sh2 = layer()
ImageDraw.Draw(sh2).rounded_rectangle(P(690, 56, 1110, 574), radius=46 * S, fill=(0, 0, 0, 140))
sh2 = sh2.filter(ImageFilter.GaussianBlur(18 * S))
compose(sh2)

body = layer()
bd = ImageDraw.Draw(body)
bd.rounded_rectangle(P(690, 56, 1110, 574), radius=46 * S, fill=(10, 14, 26, 255),
                     outline=(139, 92, 246, 165), width=3)
bd.rounded_rectangle(P(694, 60, 1106, 570), radius=42 * S, outline=(34, 211, 238, 60), width=2)
compose(body)

screen = layer()
ImageDraw.Draw(screen).rounded_rectangle(P(702, 68, 1098, 562), radius=34 * S, fill=(12, 17, 32, 255))
compose(screen)

island = layer()
ImageDraw.Draw(island).rounded_rectangle(P(855, 78, 945, 100), radius=11 * S, fill=(5, 7, 14, 255))
compose(island)

# avatar
av = layer()
ImageDraw.Draw(av).ellipse(P(718, 136, 750, 168), fill=(244, 114, 182, 255))
compose(av)
av2 = layer()
ImageDraw.Draw(av2).ellipse(P(718, 136, 750, 168), fill=(139, 92, 246, 150))
compose(av2)
d.text((734 * S, 152 * S), "她", font=font("msyhbd.ttc", 12), fill=(255, 255, 255, 255), anchor="mm")

# chat bubble
chat = layer()
ImageDraw.Draw(chat).rounded_rectangle(P(758, 128, 996, 184), radius=18 * S,
                                       fill=(255, 255, 255, 12), outline=(255, 255, 255, 20), width=2)
compose(chat)
d.text((778 * S, 162 * S), "明天几点出发？", font=F_BUBBLE, fill=(226, 232, 240, 255), anchor="ls")

hint = layer()
tracked(718, 206, "为下一句，挑一个词", F_SEG, (100, 116, 139, 255), 1, ImageDraw.Draw(hint))
compose(hint)


# ---------------------------------------------------------------- pills
def pill(cx, cy, label, hi=False):
    fnt = F_PILL_HI if hi else F_PILL
    w = min(200, d.textlength(label, font=fnt) / S + 26)
    h = 42
    x, y = cx - w / 2, cy - h / 2
    box = (x, y, x + w, y + h)
    if hi:
        soft_glow((x - 2, y - 2, x + w + 2, y + h + 2), h / 2 + 2, (34, 211, 238, 170), 10, 4)
    ly = layer()
    ld = ImageDraw.Draw(ly)
    fill = (34, 211, 238, 58) if hi else (139, 92, 246, 40)
    stroke = (103, 232, 249, 255) if hi else (139, 92, 246, 145)
    ld.rounded_rectangle(P(*box), radius=h / 2 * S,
                         fill=fill, outline=stroke, width=2)
    compose(ly)
    d.text((cx * S, cy * S), label, font=fnt,
           fill=(236, 254, 255, 255) if hi else (221, 214, 254, 255), anchor="mm")
    return box


words = [
    [("六点", True), ("早点", False), ("七点半", False)],
    [("出发", False), ("都行", False), ("八点", False)],
    [("太早", False), ("你定", False), ("一起", False)],
]
rnd_state = [0]
jitters = [(-3, 2), (2, -2), (-2, -1), (3, 1), (-1, -2), (2, 2), (-3, -1), (1, 2), (3, -2)]
hi_box = None
colw, gap = 112, 12
for r, row in enumerate(words):
    cy = 247 + r * 68
    for c, (label, hi) in enumerate(row):
        jx, jy = jitters[r * 3 + c]
        ccx = 718 + colw / 2 + c * (colw + gap) + jx
        box = pill(ccx, cy + jy, label, hi)
        if hi:
            hi_box = box

if hi_box:
    x1, y1, x2, y2 = hi_box
    pulse = layer()
    pd = ImageDraw.Draw(pulse)
    pd.rounded_rectangle(P(x1 - 6, y1 - 6, x2 + 6, y2 + 6), radius=(42 / 2 + 6) * S,
                         outline=(34, 211, 238, 110), width=2)
    pd.rounded_rectangle(P(x1 - 14, y1 - 14, x2 + 14, y2 + 14), radius=(42 / 2 + 14) * S,
                         outline=(34, 211, 238, 45), width=2)
    compose(pulse)

# ---------------------------------------------------------------- bottom bar
d.line(P(718, 446, 1078, 446), fill=(255, 255, 255, 18), width=2)

btn = layer()
bdd = ImageDraw.Draw(btn)
for bcx in (740, 1020, 1064):
    bdd.ellipse(P(bcx - 20, 474, bcx + 20, 514), fill=(255, 255, 255, 10),
                outline=(71, 85, 105, 255), width=2)
compose(btn)

d.text((740 * S, 494 * S), "拼", font=F_BTN, fill=(203, 213, 225, 255), anchor="mm")
d.text((768 * S, 494 * S), "切回拼音", font=F_SEG, fill=(100, 116, 139, 255), anchor="lm")
d.text((1020 * S, 494 * S), "↻", font=F_SYM, fill=(203, 213, 225, 255), anchor="mm")
d.text((1064 * S, 494 * S), "⌫", font=F_SYM, fill=(203, 213, 225, 255), anchor="mm")
d.text((900 * S, 540 * S), "第 1 波 · 20 个词泡", font=F_SEG, fill=(71, 85, 105, 255), anchor="mm")

# ---------------------------------------------------------------- output
final = img.convert("RGB").resize((DW, DH), Image.LANCZOS)
final.save(OUT, "PNG", optimize=True)
print(OUT)
