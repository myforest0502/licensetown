from pathlib import Path
import struct

from scripts.setup_rich_menu import (
    AREA_SPECS,
    IMAGE_HEIGHT,
    IMAGE_PATH,
    IMAGE_WIDTH,
    MAX_IMAGE_BYTES,
    TOP_HEIGHT,
    build_rich_menu,
    dry_run_payload,
    validate_image,
)


def jpeg_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as file:
        assert file.read(2) == b"\xff\xd8"
        while True:
            marker_start = file.read(1)
            if not marker_start:
                raise AssertionError("JPEG size marker not found")
            if marker_start != b"\xff":
                continue
            marker = file.read(1)
            while marker == b"\xff":
                marker = file.read(1)
            if marker in {bytes([value]) for value in range(0xC0, 0xC4)}:
                length = struct.unpack(">H", file.read(2))[0]
                data = file.read(length - 2)
                return struct.unpack(">HH", data[1:5])[::-1]
            if marker in {b"\xd8", b"\xd9"}:
                continue
            length = struct.unpack(">H", file.read(2))[0]
            file.seek(length - 2, 1)


def test_rich_menu_image_meets_line_requirements():
    validate_image()
    assert jpeg_size(IMAGE_PATH) == (IMAGE_WIDTH, IMAGE_HEIGHT)
    assert IMAGE_PATH.stat().st_size <= MAX_IMAGE_BYTES


def test_rich_menu_areas_are_four_equal_top_items_without_gaps():
    top = AREA_SPECS[:4]
    assert sum(spec[4] for spec in top) == IMAGE_WIDTH
    assert [spec[2] for spec in top] == [0, 625, 1250, 1875]
    assert all(spec[3] == 0 and spec[4] == 625 and spec[5] == TOP_HEIGHT for spec in top)
    assert AREA_SPECS[4][2:] == (0, TOP_HEIGHT, IMAGE_WIDTH, IMAGE_HEIGHT - TOP_HEIGHT)


def test_rich_menu_actions_exclude_consultation_and_complete_reset():
    expected = ["合格への道", "勉強する", "熱血モード", "教えて源さん", "ホームへ戻る"]
    assert [spec[1] for spec in AREA_SPECS] == expected
    assert all("相談する" not in value for spec in AREA_SPECS for value in spec[:2])
    assert all("ふりだしにもどる" not in value for spec in AREA_SPECS for value in spec[:2])
    menu = build_rich_menu()
    assert [area.action.text for area in menu.areas] == expected
    assert dry_run_payload()["size"] == [2500, 843]


def test_rich_menu_setup_does_not_embed_secrets():
    source = Path(__import__("scripts.setup_rich_menu", fromlist=["x"]).__file__).read_text(encoding="utf-8")
    assert "os.getenv(\"CHANNEL_ACCESS_TOKEN\")" in source
    assert "CHANNEL_SECRET=" not in source
