import io
from pathlib import Path

from PIL import Image

from scripts.setup_rich_menu import (
    AREA_SPECS,
    IMAGE_HEIGHT,
    IMAGE_WIDTH,
    MAX_IMAGE_BYTES,
    SOURCE_IMAGE_PATH,
    TOP_HEIGHT,
    TOP_ITEM_WIDTH,
    build_menu_image_bytes,
    build_rich_menu,
    dry_run_payload,
    validate_source_image,
)


def test_rich_menu_source_and_generated_image_meet_line_requirements():
    validate_source_image()
    assert SOURCE_IMAGE_PATH.is_file()
    data = build_menu_image_bytes()
    assert len(data) <= MAX_IMAGE_BYTES
    image = Image.open(io.BytesIO(data))
    assert image.size == (IMAGE_WIDTH, IMAGE_HEIGHT)
    assert image.format == "JPEG"


def test_rich_menu_areas_match_four_column_visual_without_gaps():
    primary = AREA_SPECS[:4]
    assert sum(spec[4] for spec in primary) == IMAGE_WIDTH
    assert [spec[2] for spec in primary] == [0, TOP_ITEM_WIDTH, TOP_ITEM_WIDTH * 2, TOP_ITEM_WIDTH * 3]
    assert all(spec[3] == 0 and spec[4] == TOP_ITEM_WIDTH and spec[5] == TOP_HEIGHT for spec in primary)
    assert AREA_SPECS[4][2:] == (0, TOP_HEIGHT, IMAGE_WIDTH, IMAGE_HEIGHT - TOP_HEIGHT)


def test_rich_menu_actions_exclude_consultation_and_complete_reset():
    expected = ["合格への道", "勉強する", "熱血モード", "教えて源さん", "ホームへ戻る"]
    assert [spec[1] for spec in AREA_SPECS] == expected
    assert "相談する" not in expected
    assert all("ふりだしにもどる" not in value for spec in AREA_SPECS for value in spec[:2])
    menu = build_rich_menu()
    assert [area.action.text for area in menu.areas] == expected
    assert dry_run_payload()["size"] == [2500, 843]


def test_rich_menu_setup_does_not_embed_secrets():
    source = Path(__import__("scripts.setup_rich_menu", fromlist=["x"]).__file__).read_text(encoding="utf-8")
    assert "os.getenv(\"CHANNEL_ACCESS_TOKEN\")" in source
    assert "CHANNEL_SECRET=" not in source
