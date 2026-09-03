from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"expected source block not found in {path}")
    file_path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    replace_once(
        "question_bank.py",
        '''QUESTION_BANK_DIR = Path(__file__).resolve().parent / "data" / "question_bank"\nEXPECTED_QUESTION_COUNT = 1737\nEXPECTED_QUESTION_IDS = {\n    f"Q{number}" for number in range(1, EXPECTED_QUESTION_COUNT + 1)\n}\n''',
        '''QUESTION_BANK_DIR = Path(__file__).resolve().parent / "data" / "question_bank"\nBANK_MANIFEST_PATH = QUESTION_BANK_DIR / "bank_manifest.json"\n\n\ndef _load_bank_manifest() -> dict:\n    data = json.loads(BANK_MANIFEST_PATH.read_text(encoding="utf-8-sig"))\n    if not isinstance(data, dict):\n        raise ValueError("bank_manifest.json must contain a JSON object")\n    required = {\n        "bank_version", "first_question_number", "last_question_number", "question_count"\n    }\n    missing = required - set(data)\n    if missing:\n        raise ValueError(f"bank_manifest.json missing: {sorted(missing)}")\n    first = data["first_question_number"]\n    last = data["last_question_number"]\n    count = data["question_count"]\n    if not isinstance(data["bank_version"], str) or not data["bank_version"].strip():\n        raise ValueError("bank_manifest.json bank_version must be a non-empty string")\n    if not all(type(value) is int for value in (first, last, count)):\n        raise ValueError("bank_manifest.json range/count values must be integers")\n    if first < 1 or last < first or count != last - first + 1:\n        raise ValueError("bank_manifest.json range/count contract is inconsistent")\n    return data\n\n\n_BANK_MANIFEST = _load_bank_manifest()\nQUESTION_BANK_VERSION = _BANK_MANIFEST["bank_version"]\nFIRST_QUESTION_NUMBER = _BANK_MANIFEST["first_question_number"]\nLAST_QUESTION_NUMBER = _BANK_MANIFEST["last_question_number"]\nEXPECTED_QUESTION_COUNT = _BANK_MANIFEST["question_count"]\nEXPECTED_QUESTION_IDS = {\n    f"Q{number}" for number in range(FIRST_QUESTION_NUMBER, LAST_QUESTION_NUMBER + 1)\n}\n''',
    )

    replace_once(
        "scripts/validate_question_bank.py",
        '''DEFAULT_BANK_DIR = REPOSITORY_ROOT / "data" / "question_bank"\nDEFAULT_SCHEMA_PATH = DEFAULT_BANK_DIR / "schema" / "question_bank_schema_v1.json"\nDEFAULT_REGISTRY_PATH = DEFAULT_BANK_DIR / "knowledge_nodes.json"\nQUESTION_BANK_FILES = {\n''',
        '''DEFAULT_BANK_DIR = REPOSITORY_ROOT / "data" / "question_bank"\nDEFAULT_SCHEMA_PATH = DEFAULT_BANK_DIR / "schema" / "question_bank_schema_v1.json"\nDEFAULT_REGISTRY_PATH = DEFAULT_BANK_DIR / "knowledge_nodes.json"\nDEFAULT_MANIFEST_PATH = DEFAULT_BANK_DIR / "bank_manifest.json"\nQUESTION_BANK_FILES = {\n''',
    )

    replace_once(
        "scripts/validate_question_bank.py",
        '''EXPECTED_QUESTION_COUNT = 1737\nEXPECTED_IDS = {f"Q{number}" for number in range(1, EXPECTED_QUESTION_COUNT + 1)}\n''',
        '''\ndef _load_declared_manifest(path: Path = DEFAULT_MANIFEST_PATH) -> dict[str, Any]:\n    data = json.loads(path.read_text(encoding="utf-8-sig"))\n    if not isinstance(data, dict):\n        raise ValueError("bank_manifest.json must contain a JSON object")\n    required = {\n        "bank_version", "first_question_number", "last_question_number", "question_count"\n    }\n    missing = required - set(data)\n    if missing:\n        raise ValueError(f"bank_manifest.json missing: {sorted(missing)}")\n    first = data["first_question_number"]\n    last = data["last_question_number"]\n    count = data["question_count"]\n    if not isinstance(data["bank_version"], str) or not data["bank_version"].strip():\n        raise ValueError("bank_manifest.json bank_version must be a non-empty string")\n    if not all(type(value) is int for value in (first, last, count)):\n        raise ValueError("bank_manifest.json range/count values must be integers")\n    if first < 1 or last < first or count != last - first + 1:\n        raise ValueError("bank_manifest.json range/count contract is inconsistent")\n    return data\n\n\n_DECLARED_MANIFEST = _load_declared_manifest()\nFIRST_QUESTION_NUMBER = _DECLARED_MANIFEST["first_question_number"]\nLAST_QUESTION_NUMBER = _DECLARED_MANIFEST["last_question_number"]\nEXPECTED_QUESTION_COUNT = _DECLARED_MANIFEST["question_count"]\nEXPECTED_IDS = {\n    f"Q{number}" for number in range(FIRST_QUESTION_NUMBER, LAST_QUESTION_NUMBER + 1)\n}\n''',
    )

    replace_once(
        "scripts/backfill_node_learning_history.py",
        "from question_bank import get_question_tag\n",
        "from question_bank import get_question_tag, question_ids\n\n\nFORMAL_QUESTION_IDS = frozenset(question_ids())\n",
    )
    replace_once(
        "scripts/backfill_node_learning_history.py",
        "    return number if 1 <= number <= 1737 else None\n",
        "    return number if f\"Q{number}\" in FORMAL_QUESTION_IDS else None\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
