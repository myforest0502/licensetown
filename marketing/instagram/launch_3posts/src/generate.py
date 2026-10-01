"""Render the launch carousels without touching application code.

Python 3.10+, Pillow 12.3.0; Windows Yu Gothic fonts (override with --fonts).
Run: python src/generate.py
"""
from pathlib import Path
import argparse
import json
import hashlib
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
GREEN, DEEP, INK, MUTED = '#16833b', '#075c31', '#171b18', '#58625b'
PALE, LINE = '#f2f8f2', '#d9e1da'
parser = argparse.ArgumentParser()
parser.add_argument('--fonts', type=Path, default=Path('C:/Windows/Fonts'))
args = parser.parse_args()
fonts = args.fonts
report = []

def font(size, bold=False):
    return ImageFont.truetype(str(fonts / ('YuGothB.ttc' if bold else 'YuGothM.ttc')), size)

def wrap(text, size, maxwidth=920, bold=False):
    f = font(size, bold)
    lines = []
    for raw in text.split('\n'):
        line = ''
        for ch in raw:
            if f.getlength(line + ch) > maxwidth:
                if ch in '。、？！）」』：':
                    tail = line[-1:]
                    lines.append(line[:-1])
                    line = tail + ch
                else:
                    lines.append(line)
                    line = ch
            else:
                line += ch
        lines.append(line)
    return lines

def height(text, size, bold=False, width=920):
    return len(wrap(text, size, width, bold)) * int(size * 1.42)

def write(text, x, y, size, color=INK, bold=False, width=920):
    for line in wrap(text, size, width, bold):
        bounds = draw.textbbox((x, y), line, font=font(size, bold), anchor='lt')
        assert bounds[0] >= 0 and bounds[2] <= 1080 and bounds[3] < 1230, (key, line, bounds)
        draw.text((x, y), line, font=font(size, bold), fill=color, anchor='lt')
        y += int(size * 1.42)
    return y

def portrait(x, y, size):
    pic = Image.open(ROOT / 'src/assets/gensan_main.png').convert('RGB')
    pic = ImageOps.fit(pic, (size, size))
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size-1, size-1), radius=36, fill=255)
    canvas.paste(pic, (x, y), mask)

posts = json.loads((ROOT / 'src/content.json').read_text(encoding='utf-8'))
for pi, post in enumerate(posts, 1):
    out = ROOT / post['folder']
    out.mkdir(parents=True, exist_ok=True)
    (out / 'caption.txt').write_text(post['caption'].strip() + '\n', encoding='utf-8')
    for si, slide in enumerate(post['slides'], 1):
        key = f'{post["folder"]}/{si:02}.png'
        canvas = Image.new('RGB', (1080, 1350), 'white')
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((0, 0, 1080, 16), fill=GREEN)
        write('LicenseTown', 80, 65, 34, GREEN, True)
        write('国家試験対策', 775, 72, 25, MUTED)
        draw.line((80, 135, 1000, 135), fill=LINE, width=2)
        write(f'0{pi}  /  {post["label"]}', 80, 171, 27, GREEN, True)
        heading, paragraphs = slide['heading'], slide['paragraphs']
        cover = si == 1
        hs = 76 if cover else 62
        if pi == 3 and cover:
            hs = 64
        if pi == 2 and cover:
            hs = 84
        y = write(heading, 80, 259, hs, DEEP, True) + 48
        bs = 43 if (pi, si) in [(1, 2), (1, 3)] else 46
        gap = 25
        total = sum(height(p, bs) for p in paragraphs) + gap * max(0, len(paragraphs)-1)
        assert y + total <= 1190, (key, y, total)
        for p in paragraphs:
            emphasis = p.startswith(('「', '次にやる問題', 'プロフィール'))
            y = write(p, 80, y, bs, DEEP if emphasis else INK, emphasis) + gap
        if cover and pi == 1:
            portrait(666, 875, 330)
            draw.line((80, 1010, 130, 1010), fill=GREEN, width=5)
            write('迷う時間を、\n次の一歩に。', 80, 1040, 42, DEEP, True, 550)
        elif cover and pi == 2:
            portrait(470, 685, 520)
            write('まずは、ここから。', 80, 1010, 33, MUTED, False, 370)
        elif cover and pi == 3:
            draw.rounded_rectangle((80, 765, 1000, 1160), radius=28, fill=PALE)
            write('学習塾じゃない、寺子屋だ。', 122, 820, 44, DEEP, True, 840)
            write('家族に勧められる道具を。\nその思いから、始まりました。', 122, 925, 40, INK, False, 840)
        elif (pi, si) in [(1, 5), (2, 3), (2, 4), (2, 5)]:
            available = 1200 - y
            if available >= 240:
                size = min(330, int(available)-10)
                portrait(1000-size, int(y), size)
        if si == 6:
            # A consistent, comfortably separated CTA strip.
            if y < 1040:
                draw.rounded_rectangle((80, 1080, 1000, 1187), radius=22, fill=GREEN)
                draw.text((126, 1110), 'プロフィールのリンクへ  →', font=font(43, True), fill='white', anchor='lt')
        draw.line((80, 1240, 1000, 1240), fill=LINE, width=2)
        draw.text((80, 1270), '@licensetown', font=font(27), fill=MUTED, anchor='lt')
        for n in range(6):
            draw.ellipse((465+n*25, 1280, 474+n*25, 1289), fill=GREEN if n == si-1 else LINE)
        draw.text((927, 1270), f'{si}/6', font=font(27), fill=MUTED, anchor='lt')
        canvas.save(out / f'{si:02}.png', optimize=True)
        report.append({'file': key, 'size': list(canvas.size), 'body_font_px': bs, 'heading_font_px': hs, 'text_bounds': 'PASS'})
    # A 360px-wide mobile-size overview, separate from upload files.
    sheet = Image.new('RGB', (1080, 900), '#e8ede8')
    for j in range(6):
        im = Image.open(out / f'{j+1:02}.png')
        im.thumbnail((360, 450), Image.Resampling.LANCZOS)
        sheet.paste(im, ((j % 3)*360, (j // 3)*450))
    (ROOT / 'preview').mkdir(exist_ok=True)
    sheet.save(ROOT / 'preview' / f'post{pi:02}_overview.jpg', quality=95)

assert len(report) == 18
for row in report:
    im = Image.open(ROOT / row['file'])
    assert im.size == (1080, 1350) and im.format == 'PNG'
    row['sha256'] = hashlib.sha256((ROOT / row['file']).read_bytes()).hexdigest()
(ROOT / 'src/validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('PASS: 18 PNGs, 1080x1350, RGB; text bounds checked; 3 captions and previews generated.')
