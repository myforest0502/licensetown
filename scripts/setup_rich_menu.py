"""LicenseTownクローズドβ用Rich Menuを作成し、既定メニューへ設定する。"""

from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path

from PIL import Image
from linebot import LineBotApi
from linebot.models import MessageAction, RichMenu, RichMenuArea, RichMenuBounds, RichMenuSize


SOURCE_IMAGE_PATH = Path(__file__).resolve().parents[1] / "static" / "rich_menu" / "rich_menu_beta.jpg"
IMAGE_WIDTH = 2500
IMAGE_HEIGHT = 843
MAX_IMAGE_BYTES = 1_000_000
TOP_HEIGHT = 588
TOP_ITEM_WIDTH = 625

# Existing source image layout: 合格への道 / 勉強する / 相談する / 熱血 / 教えて源さん
# We remove the consultation tile and redistribute the remaining four tiles equally.
_SOURCE_TOP_AREAS = (
    (0, 0, 562, TOP_HEIGHT),
    (562, 0, 471, TOP_HEIGHT),
    (1495, 0, 474, TOP_HEIGHT),
    (1969, 0, 531, TOP_HEIGHT),
)

AREA_SPECS = (
    ("合格への道", "合格への道", 0, 0, TOP_ITEM_WIDTH, TOP_HEIGHT),
    ("勉強する", "勉強する", TOP_ITEM_WIDTH, 0, TOP_ITEM_WIDTH, TOP_HEIGHT),
    ("熱血モード", "熱血モード", TOP_ITEM_WIDTH * 2, 0, TOP_ITEM_WIDTH, TOP_HEIGHT),
    ("教えて源さん", "教えて源さん", TOP_ITEM_WIDTH * 3, 0, TOP_ITEM_WIDTH, TOP_HEIGHT),
    ("ホームへ戻る", "ホームへ戻る", 0, TOP_HEIGHT, IMAGE_WIDTH, IMAGE_HEIGHT - TOP_HEIGHT),
)


def build_rich_menu() -> RichMenu:
    return RichMenu(
        size=RichMenuSize(width=IMAGE_WIDTH, height=IMAGE_HEIGHT),
        selected=True,
        name="LicenseTown Closed Beta v2",
        chat_bar_text="メニュー",
        areas=[
            RichMenuArea(
                bounds=RichMenuBounds(x=x, y=y, width=width, height=height),
                action=MessageAction(label=label, text=text),
            )
            for label, text, x, y, width, height in AREA_SPECS
        ],
    )


def validate_source_image() -> None:
    if not SOURCE_IMAGE_PATH.is_file():
        raise FileNotFoundError(f"Rich Menu元画像がありません: {SOURCE_IMAGE_PATH}")


def build_menu_image_bytes() -> bytes:
    """Create the 4-column rich-menu JPEG from the existing 5-column source image."""
    validate_source_image()
    source = Image.open(SOURCE_IMAGE_PATH).convert("RGB")
    if source.size != (IMAGE_WIDTH, IMAGE_HEIGHT):
        raise ValueError(
            f"Rich Menu元画像サイズが想定外です: {source.size} / expected {(IMAGE_WIDTH, IMAGE_HEIGHT)}"
        )

    canvas = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), "white")
    for index, (x, y, width, height) in enumerate(_SOURCE_TOP_AREAS):
        tile = source.crop((x, y, x + width, y + height))
        tile = tile.resize((TOP_ITEM_WIDTH, TOP_HEIGHT), Image.Resampling.LANCZOS)
        canvas.paste(tile, (TOP_ITEM_WIDTH * index, 0))

    bottom = source.crop((0, TOP_HEIGHT, IMAGE_WIDTH, IMAGE_HEIGHT))
    canvas.paste(bottom, (0, TOP_HEIGHT))

    buffer = io.BytesIO()
    canvas.save(buffer, format="JPEG", quality=94, optimize=True)
    image_bytes = buffer.getvalue()
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise ValueError("生成したRich Menu画像がLINEの1MB上限を超えています。")
    return image_bytes


def dry_run_payload() -> dict:
    image_bytes = build_menu_image_bytes()
    return {
        "source_image": str(SOURCE_IMAGE_PATH),
        "generated_image_bytes": len(image_bytes),
        "size": [IMAGE_WIDTH, IMAGE_HEIGHT],
        "areas": [
            {"label": label, "text": text, "x": x, "y": y, "width": width, "height": height}
            for label, text, x, y, width, height in AREA_SPECS
        ],
    }


def create_and_set_default(set_default: bool = True) -> str:
    image_bytes = build_menu_image_bytes()
    channel_access_token = os.getenv("CHANNEL_ACCESS_TOKEN")
    if not channel_access_token:
        raise RuntimeError("CHANNEL_ACCESS_TOKENを環境変数へ設定してください。")

    api = LineBotApi(channel_access_token)
    rich_menu_id = api.create_rich_menu(rich_menu=build_rich_menu())
    try:
        api.set_rich_menu_image(rich_menu_id, "image/jpeg", io.BytesIO(image_bytes))
        if set_default:
            api.set_default_rich_menu(rich_menu_id)
    except Exception:
        api.delete_rich_menu(rich_menu_id)
        raise
    return rich_menu_id


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="APIを呼ばず設定内容だけ表示します。")
    parser.add_argument("--no-default", action="store_true", help="作成後に既定メニューへ設定しません。")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps(dry_run_payload(), ensure_ascii=False, indent=2))
        return
    rich_menu_id = create_and_set_default(set_default=not args.no_default)
    print(f"Rich Menuを作成しました: {rich_menu_id}")


if __name__ == "__main__":
    main()
