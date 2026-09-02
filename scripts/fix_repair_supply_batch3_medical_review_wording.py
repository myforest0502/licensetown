from pathlib import Path

replacements = {
    Path('data/question_bank/explanations.json'): {
        '手の外来筋は筋腹・起始が前腕側にあり、腱が手へ入って手指に作用する筋群である。': '手の外来筋は筋腹が前腕側にあり、腱が手へ入って手指に作用する筋群である。',
    },
    Path('docs/repair-supply-phase2-batch3-item-design-v02.md'): {
        '手の外来筋は筋腹・起始が前腕側にあり、腱が手へ入って手指に作用する筋群である。': '手の外来筋は筋腹が前腕側にあり、腱が手へ入って手指に作用する筋群である。',
    },
}

for path, mapping in replacements.items():
    text = path.read_text(encoding='utf-8')
    for old, new in mapping.items():
        count = text.count(old)
        if count != 1:
            raise SystemExit(f'{path}: expected exactly one occurrence of {old!r}, got {count}')
        text = text.replace(old, new)
    path.write_text(text, encoding='utf-8')
