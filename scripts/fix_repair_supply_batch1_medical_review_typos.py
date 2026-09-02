from pathlib import Path

replacements = {
    Path('data/question_bank/questions.json'): {
        '前頸部瘻痕による屈曲拘縮': '前頸部瘢痕による屈曲拘縮',
        '前頸部瘻痕の短縮・伸張性の変化': '前頸部瘢痕の短縮・伸張性の変化',
        '腋窩部瘻痕の伸張性': '腋窩部瘢痕の伸張性',
    },
    Path('data/question_bank/explanations.json'): {
        '錥体路徴候': '錐体路徴候',
        '前頸部熱傷では瘻痕短縮': '前頸部熱傷では瘢痕短縮',
        '前頸部瘻痕の短縮・伸張性': '前頸部瘢痕の短縮・伸張性',
        '前頸部瘻痕短縮': '前頸部瘢痕短縮',
    },
    Path('data/question_bank/question_tags.json'): {
        '錥体路徴候': '錐体路徴候',
        '前頸部熱傷瘻痕拘縮を予防する頸部伸展位': '前頸部熱傷瘢痕拘縮を予防する頸部伸展位',
        '前頸部瘻痕': '前頸部瘢痕',
    },
}

for path, mapping in replacements.items():
    text = path.read_text(encoding='utf-8')
    for old, new in mapping.items():
        count = text.count(old)
        if count != 1:
            raise SystemExit(f'{path}: expected exactly one {old!r}, got {count}')
        text = text.replace(old, new)
    path.write_text(text, encoding='utf-8')
