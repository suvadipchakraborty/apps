"""Generate the OG image and app icons for The Shelf (Suva's app store)."""
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

random.seed(7)

INK = (17, 18, 24)          # #111218
INK_2 = (24, 26, 36)        # #181A24
PAPER = (243, 241, 236)     # #F3F1EC
MUTED = (150, 152, 171)     # #9698AB

ACCENTS = [
    (232, 164, 74),   # amber   - rankings & signals
    (47, 155, 224),   # sky     - discover
    (124, 111, 240),  # violet  - culture
    (34, 166, 160),   # teal    - utility
    (233, 78, 119),   # coral   - games
]

DEJAVU_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def vertical_gradient(size, top, bottom):
    w, h = size
    base = Image.new("RGB", (1, h), color=0)
    for y in range(h):
        t = y / max(h - 1, 1)
        r = round(top[0] + (bottom[0] - top[0]) * t)
        g = round(top[1] + (bottom[1] - top[1]) * t)
        b = round(top[2] + (bottom[2] - top[2]) * t)
        base.putpixel((0, y), (r, g, b))
    return base.resize((w, h))


def rounded_tile(draw, xy, radius, fill, alpha=255):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill)


def make_og_image(path, w=1200, h=630):
    img = vertical_gradient((w, h), INK, INK_2).convert("RGBA")

    # Soft glow behind the tile cluster (bottom-right)
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([w - 620, h - 560, w + 220, h + 260], fill=(124, 111, 240, 40))
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    img = Image.alpha_composite(img, glow)

    draw = ImageDraw.Draw(img)

    # Mosaic of small rounded tiles -> abstract stand-in for "many small apps"
    tile = 30
    gap = 10
    cols, rows = 9, 6
    start_x = w - (cols * (tile + gap)) + 40
    start_y = h - (rows * (tile + gap)) - 40
    for r in range(rows):
        for c in range(cols):
            # sparse, irregular placement rather than a solid grid
            if random.random() < 0.62:
                continue
            x = start_x + c * (tile + gap)
            y = start_y + r * (tile + gap)
            color = random.choice(ACCENTS)
            fade = random.uniform(0.55, 1.0)
            rgba = (color[0], color[1], color[2], int(255 * fade))
            rounded_tile(draw, [x, y, x + tile, y + tile], radius=8, fill=rgba)

    # Kicker
    kicker_font = ImageFont.truetype(DEJAVU_BOLD, 26)
    draw.text((80, 130), "Built by Suva", font=kicker_font, fill=MUTED + (255,))

    # Title
    title_font = ImageFont.truetype(DEJAVU_BOLD, 96)
    draw.text((78, 168), "The Shelf", font=title_font, fill=PAPER + (255,))

    # Subtitle
    sub_font = ImageFont.truetype(DEJAVU, 34)
    draw.text((80, 300), "Small, sharp apps. One link.", font=sub_font, fill=(206, 207, 220, 255))

    # A row of accent dots as a simple wordmark flourish under the subtitle
    dot_y = 372
    dot_x = 80
    for color in ACCENTS:
        draw.ellipse([dot_x, dot_y, dot_x + 16, dot_y + 16], fill=color + (255,))
        dot_x += 30

    img.convert("RGB").save(path, "PNG")


def make_icon(path, size, bg=INK, fg=PAPER, maskable=False):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pad = int(size * (0.18 if maskable else 0.0))
    draw.rounded_rectangle(
        [pad, pad, size - pad, size - pad],
        radius=int(size * 0.22),
        fill=bg + (255,),
    )

    # Simple mark: three stacked "shelf" bars in accent colors
    bar_w = int(size * 0.46)
    bar_h = int(size * 0.07)
    x0 = (size - bar_w) // 2
    ys = [size * 0.36, size * 0.50, size * 0.64]
    for y, color in zip(ys, ACCENTS[:3]):
        draw.rounded_rectangle(
            [x0, y, x0 + bar_w, y + bar_h], radius=bar_h // 2, fill=color + (255,)
        )

    img.save(path, "PNG")


def make_favicon(path):
    sizes = [16, 32, 48]
    imgs = []
    for s in sizes:
        im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, s - 1, s - 1], radius=max(2, s // 5), fill=INK + (255,))
        bar_w = int(s * 0.5)
        bar_h = max(1, int(s * 0.09))
        x0 = (s - bar_w) // 2
        ys = [s * 0.32, s * 0.48, s * 0.64]
        for y, color in zip(ys, ACCENTS[:3]):
            d.rectangle([x0, y, x0 + bar_w, y + bar_h], fill=color + (255,))
        imgs.append(im)
    imgs[0].save(path, format="ICO", sizes=[(s, s) for s in sizes], append_images=imgs[1:])


if __name__ == "__main__":
    import os
    out = "/home/claude/work/appstore/public/assets"
    os.makedirs(out, exist_ok=True)
    make_og_image(f"{out}/og-image.png")
    make_icon(f"{out}/icon-192.png", 192)
    make_icon(f"{out}/icon-512.png", 512)
    make_icon(f"{out}/apple-touch-icon.png", 180)
    make_icon(f"{out}/icon-maskable-512.png", 512, maskable=True)
    make_favicon(f"{out}/../favicon.ico")
    print("done")
