"""LicenseTownクローズドβ用Rich Menuを作成し、既定メニューへ設定する。"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from linebot import LineBotApi
from linebot.models import MessageAction, RichMenu, RichMenuArea, RichMenuBounds, RichMenuSize


IMAGE_PATH = Path(__file__).resolve().parents[1] / "static" / "rich_menu" / "rich_menu_beta.jpg"
IMAGE_WIDTH = 2500
IMAGE_HEIGHT = 843
MAX_IMAGE_BYTES = 1_000_000
TOP_HEIGHT = 588

# 相談モードは主導線から廃止。上段は4機能を画像の並びと同じ等幅で配置する。
AREA_SPECS = (
    ("合格への道", "合格への道", 0, 0, 625, TOP_HEIGHT),
    ("勉強する", "勉強する", 625, 0, 625, TOP_HEIGHT),
    ("教えて源さん", "教えて源さん", 1250, 0, 625, TOP_HEIGHT),
    ("熱血モード", "熱血モード", 1875, 0, 625, TOP_HEIGHT),
    ("ホームへ戻る", "ホームへ戻る", 0, TOP_HEIGHT, IMAGE_WIDTH, IMAGE_HEIGHT - TOP_HEIGHT),
)


def build_rich_menu() -> RichMenu:
    return RichMenu(
        size=RichMenuSize(width=IMAGE_WIDTH, height=IMAGE_HEIGHT),
        selected=True,
        name="LicenseTown Closed Beta",
        chat_bar_text="メニュー",
        areas=[
            RichMenuArea(
                bounds=RichMenuBounds(x=x, y=y, width=width, height=height),
                action=MessageAction(label=label, text=text),
            )
            for label, text, x, y, width, height in AREA_SPECS
        ],
    )


def validate_image() -> None:
    if not IMAGE_PATH.is_file():
        raise FileNotFoundError(f"Rich Menu画像がありません: {IMAGE_PATH}")
    if IMAGE_PATH.stat().st_size > MAX_IMAGE_BYTES:
        raise ValueError("Rich Menu画像がLINEの1MB上限を超えています。")


def dry_run_payload() -> dict:
    return {
        "image": str(IMAGE_PATH),
        "size": [IMAGE_WIDTH, IMAGE_HEIGHT],
        "areas": [
            {"label": label, "text": text, "x": x, "y": y, "width": width, "height": height}
            for label, text, x, y, width, height in AREA_SPECS
        ],
    }


def create_and_set_default(set_default: bool = True) -> str:
    validate_image()
    channel_access_token = os.getenv("CHANNEL_ACCESS_TOKEN")
    if not channel_access_token:
        raise RuntimeError("CHANNEL_ACCESS_TOKENを環境変数へ設定してください。")

    api = LineBotApi(channel_access_token)
    rich_menu_id = api.create_rich_menu(rich_menu=build_rich_menu())
    try:
        with IMAGE_PATH.open("rb") as image_file:
            api.set_rich_menu_image(rich_menu_id, "image/jpeg", image_file)
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
    validate_image()
    if args.dry_run:
        print(json.dumps(dry_run_payload(), ensure_ascii=False, indent=2))
        return
    rich_menu_id = create_and_set_default(set_default=not args.no_default)
    print(f"Rich Menuを作成しました: {rich_menu_id}")


if __name__ == "__main__":
    main()
