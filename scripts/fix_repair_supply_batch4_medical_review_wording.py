from pathlib import Path

replacements = {
    Path('data/question_bank/questions.json'): {
        '針筋電図によるマッピング中、1個のα運動ニューロンの軸索が損傷していることが分かった。この損傷によって神経入力を直接失う筋線維はどれか。': '1個のα運動ニューロンの軸索だけが選択的に損傷したと仮定する。この損傷によって神経入力を直接失う筋線維はどれか。',
    },
    Path('docs/repair-supply-phase2-batch4-item-design-v02.md'): {
        "During needle EMG mapping, loss of one alpha motor neuron's axon is known to have occurred. Which muscle fibers would directly lose neural input from that lesion?": "Assume that only the axon of one alpha motor neuron is selectively injured. Which muscle fibers would directly lose neural input from that lesion?",
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
