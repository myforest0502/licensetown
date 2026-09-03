from pathlib import Path


def main():
    path = Path("tests/test_quiz_answer_numbering.py")
    text = path.read_text(encoding="utf-8")

    replacements = [
        (
            '        "parse_dashboard_recommendation_command",\n',
            '        "parse_dashboard_recommendation_command",\n        "parse_category_route_command",\n',
        ),
        (
            '        function_globals["reply_quiz_category_group_choice"] = (\n            lambda token: group_replies.append(token)\n        )\n',
            '        function_globals["reply_quiz_category_group_choice"] = (\n            lambda token, mode="study": group_replies.append((token, mode))\n        )\n',
        ),
        (
            '        function_globals["reply_quiz_category_choice"] = (\n            lambda token, group_name: category_replies.append((token, group_name))\n        )\n',
            '        function_globals["reply_quiz_category_choice"] = (\n            lambda token, group_name, mode="study": category_replies.append((token, group_name, mode))\n        )\n',
        ),
        (
            '        self.assertEqual(2, len(group_replies))\n        self.assertEqual(["基礎", "専門基礎"], [group for _, group in category_replies])\n        self.assertEqual(2, len(started))\n',
            '        self.assertEqual(["study", "nekketsu"], [mode for _, mode in group_replies])\n        self.assertEqual(["基礎", "専門基礎"], [group for _, group, _ in category_replies])\n        self.assertEqual(["study", "nekketsu"], [mode for _, _, mode in category_replies])\n        self.assertEqual(2, len(started))\n',
        ),
    ]

    for old, new in replacements:
        if old not in text:
            raise RuntimeError(f"expected test block not found: {old[:100]!r}")
        text = text.replace(old, new, 1)

    path.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
