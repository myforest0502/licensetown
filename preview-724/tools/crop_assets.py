from pathlib import Path

from PIL import Image


SOURCE = Path(r"C:\Users\M'sPC\OneDrive\Desktop2\HP作成用\元画像S.png")
OUT = Path(__file__).resolve().parents[1] / "assets"

# Only source-specific visual material is rasterized. Text, cards, layout, and UI
# are rebuilt in HTML/CSS.
CROPS = {
    "hero-phone.png": (437, 62, 724, 458),
    "hero-landscape.png": (62, 360, 282, 434),
    "problem-1.png": (87, 565, 163, 645),
    "problem-2.png": (243, 568, 322, 645),
    "problem-3.png": (400, 569, 468, 645),
    "problem-4.png": (547, 567, 652, 645),
    "feature-1.png": (101, 728, 151, 775),
    "feature-2.png": (260, 728, 308, 776),
    "feature-3.png": (413, 730, 467, 777),
    "feature-4.png": (566, 723, 623, 778),
    "step-1.png": (118, 1233, 169, 1285),
    "step-2.png": (274, 1233, 325, 1285),
    "step-3.png": (430, 1233, 482, 1285),
    "step-4.png": (586, 1233, 638, 1285),
    "terakoya.png": (351, 1353, 689, 1551),
    "portrait.png": (273, 1928, 369, 2041),
    "cta-phone.png": (510, 2041, 640, 2141),
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with Image.open(SOURCE) as image:
        for name, box in CROPS.items():
            image.crop(box).save(OUT / name, optimize=True)


if __name__ == "__main__":
    main()
