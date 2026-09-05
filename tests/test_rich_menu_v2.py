import io

from PIL import Image

from scripts.setup_rich_menu import (
    AREA_SPECS,
    IMAGE_HEIGHT,
    IMAGE_WIDTH,
    MAX_IMAGE_BYTES,
    build_menu_image_bytes,
)


def test_rich_menu_has_four_primary_actions_without_consultation():
    labels = [item[0] for item in AREA_SPECS]
    assert labels == ["合格への道", "勉強する", "熱血モード", "教えて源さん", "ホームへ戻る"]
    assert "相談する" not in labels


def test_generated_rich_menu_image_is_line_compatible():
    data = build_menu_image_bytes()
    assert len(data) <= MAX_IMAGE_BYTES
    image = Image.open(io.BytesIO(data))
    assert image.size == (IMAGE_WIDTH, IMAGE_HEIGHT)
    assert image.format == "JPEG"
