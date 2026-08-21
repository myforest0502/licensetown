from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageStat


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(r"C:\Users\M'sPC\OneDrive\Desktop2\HP作成用\元画像S.png")
PREVIEW = ROOT / "preview-724-final.png"

SECTIONS = [
    ("Header", 0, 62),
    ("01", 62, 458),
    ("02", 458, 666),
    ("03", 666, 866),
    ("04", 866, 1178),
    ("05", 1178, 1343),
    ("06", 1343, 1558),
    ("07", 1558, 1812),
    ("08", 1812, 2048),
    ("CTA", 2048, 2141),
    ("Footer", 2141, 2172),
]


def main() -> None:
    segment_y = [0, 600, 1200, 1572]
    if all((ROOT / f".segment-{y}.png").exists() for y in segment_y):
        stitched = Image.new("RGB", (724, 2172), "white")
        for y in segment_y:
            with Image.open(ROOT / f".segment-{y}.png").convert("RGB") as segment:
                if y < 1572:
                    stitched.paste(segment, (0, y))
                else:
                    stitched.paste(segment, (0, y))
        stitched.save(PREVIEW, optimize=True)

    with Image.open(SOURCE).convert("RGB") as source, Image.open(PREVIEW).convert("RGB") as preview:
        if source.size != preview.size:
            raise SystemExit(f"size mismatch: {source.size=} {preview.size=}")

        # Half-size side-by-side image for a full-page visual review.
        half = (source.width // 2, source.height // 2)
        left = source.resize(half, Image.Resampling.LANCZOS)
        right = preview.resize(half, Image.Resampling.LANCZOS)
        board = Image.new("RGB", (half[0] * 2, half[1] + 28), "white")
        board.paste(left, (0, 28))
        board.paste(right, (half[0], 28))
        draw = ImageDraw.Draw(board)
        draw.text((8, 7), "SOURCE", fill="black")
        draw.text((half[0] + 8, 7), "PREVIEW", fill="black")
        board.save(ROOT / "comparison-final.png", optimize=True)

        print(f"source={source.size[0]}x{source.size[1]}")
        print(f"preview={preview.size[0]}x{preview.size[1]}")
        for label, image in (("source", source), ("preview", preview)):
            logo = image.crop((0, 0, 220, 62))
            mask = Image.new("1", logo.size)
            mask.putdata([
                1 if (g > r * 1.20 and g > b * 1.12 and g < 170) else 0
                for r, g, b in logo.getdata()
            ])
            print(f"{label}_logo_bbox={mask.getbbox()}")
        for label, top, bottom in SECTIONS:
            a = source.crop((0, top, source.width, bottom))
            b = preview.crop((0, top, preview.width, bottom))
            diff = ImageChops.difference(a, b)
            stat = ImageStat.Stat(diff)
            mae = sum(stat.mean) / 3
            print(f"{label:6s} y={top:4d}-{bottom-1:4d} h={bottom-top:3d} mae={mae:6.2f}")


if __name__ == "__main__":
    main()
