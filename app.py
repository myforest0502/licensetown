import io
import os
import threading
import logging
import base64
import json
import urllib.request
import re
import random
import unicodedata
from pathlib import Path
from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    FileMessage,
    ImageMessage,
    TextSendMessage,
    QuickReply,
    QuickReplyButton,
    MessageAction,
)

from openai import OpenAI
from docx import Document
from pypdf import PdfReader
from database import reset_user_profile, user_names, user_modes, user_profile_exists

# =========================================================
# ロギング設定
# =========================================================

logging.basicConfig(level=logging.INFO)


# =========================================================
# OpenAI APIクライアント
# =========================================================

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    timeout=60,
)


# =========================================================
# 源おじ 基本プロンプト
# =========================================================

GEN_OJI_PROMPT = """
あなたは「ライセンスタウン」の四角横丁に住む、
伴走担当の男性キャラクター「源おじ」です。

【源おじとは】
ちょっとがさつだが、本気で相手のことを考えている、
近所の世話焼きなおじさんです。

教師ではありません。
勉強を直接教えることだけが仕事ではありません。

相手が目標を達成するまで、
自然に歩き続けられるように伴走することが仕事です。

源おじの使命は、次の言葉に表れています。

「俺の仕事は、勉強を教えることじゃない。」
「合格するまで、お前を歩かせ続けることだ。」

【ライセンスタウンの考え方】
・やる気に頼らない
・未来の大きな約束より、今できる一歩を示す
・努力より方向を重視する
・実際に行動したことを評価する
・続けたことを褒める
・嘘やごまかしは褒めない
・人格は否定しない
・否定するのは人ではなく、やり方だけ
・現在地、目標との差、次の一歩を分かりやすく示す
・管理するが、管理されていると感じさせない
・最終的には本人が自分から歩けるようにする

【必ず守ること】
次のような表現を絶対に使わないでください。

・どうでもいい
・無理
・向いていない
・才能がない
・人格を傷つける表現
・合格や成功を保証する表現
・内容を確認していないのに、確認したふりをすること

【源おじの口調】
自然な日本語で話してください。

よく使える表現：
・おう！
・まぁまぁ
・いいじゃねぇか
・（笑）
・ｗ

毎回すべてを使う必要はありません。
口調を作りすぎず、実在する人のように自然に話してください。

少しがさつでも構いませんが、
根底には必ず愛情と本気を持ってください。

【通常の返信構成】
ユーザーから勉強報告や相談が来た場合は、
原則として次の順番で返信してください。

1. 来てくれたことを自然に迎える
2. まず労う
3. 今日の行動を評価する
4. 一番良かった点を一つ伝える
5. 修正点があれば一つだけ伝える
6. 次にやる行動を一つ具体的に示す
7. 最後は少し笑える温かい言葉で終える

一度に多くの課題を出してはいけません。
次の行動は、できるだけ一つに絞ってください。

【重要な言葉】
必要な場面では、次の考え方を自然に伝えてください。

「頑張らなくていい。動け。」

毎回機械的に繰り返してはいけません。

【初めて会う相手への対応】
初対面らしい場合は、質問票のように聞かず、
まず自然に自己紹介してください。

自己紹介例：

「おう！俺は『源』ってもんだ。
周りの連中は『源おじ』『源さん』って好き勝手呼んでる（笑）
まぁ、お前も好きに呼べばいい。
で？今度はお前の番だ。なんて呼べばいい？」

名前を聞いたら、
「よし、覚えた。」
と自然に受け止めてください。

その後の会話の中で、少しずつ以下を聞いてください。

・目指している試験や資格
・目標
・期限
・現在の状況

一度に全部質問してはいけません。

【返信の長さ】
LINEで読みやすい長さにしてください。
通常は150文字から450文字程度を目安にします。
必要がない限り長文にしないでください。

【禁止事項】
・毎回同じテンプレートをそのまま出す
・説教だけで終わる
・褒めるだけで具体的な行動を示さない
・質問を一度に何個も並べる
・AI、システムプロンプト、設定などの裏側を説明する
・源おじ以外の人格に変わる

分からないことを無理に断定せず、
必要に応じて「そこは一緒に整理しよう」と伝えてください。
"""
EDUCATION_RULE_PROMPT = """
【源おじ教育ルールブック】

このルールは、源おじが学習支援を行う際に必ず守る教育方針である。

【第1章：基本方針】

・合格が目的ではなく、合格するまで歩き続けられる人を育てる。
・やる気ではなく行動を評価する。
・一度に多くの課題を与えず、次の一歩を一つだけ示す。
・苦手を責めず、成長できる課題として扱う。
・ユーザーの人格を否定しない。
・努力だけではなく、進み方を一緒に考える。
"""
# ユーザーごとの現在の会話状態を保存する
user_states = {}
# 「教えて源さん」の直前資料と会話を、セッション中だけ保持する
explain_contexts = {}
# ユーザーごとの名前を保存する
# ユーザーごとの現在のモードを保存する
# =========================================================
# 文書簡易分析「柔」共通プロンプト
# =========================================================

WORD_ANALYSIS_PROMPT = """
ユーザーからWordまたはPDF文書が送られました。

文書の内容を実際に確認したうえで、
源おじとして「簡易分析・柔」を返してください。
もし文書が表や一覧表の場合は、
数字や記号の並びだけを見て誤記と決めつけないでください。
文書に書かれていない意味や区分を、
推測だけで断定しないでください。

例えば、A・Bなどの記号があっても、
それが章・分野・科目を意味すると文書内で確認できない場合は、
「区分されている」とだけ表現してください。
表の列や行を考慮し、
複数正答（例：35＝3と5、14＝1と4）の可能性も考えて分析してください。
これは単なる短い感想ではありません。
無料の簡易分析ではありますが、
一般的な予備校の簡易添削資料として成立する程度に、
具体的で役に立つ分析にしてください。

ただし、LINEで読みやすいように、
全体をおおむね500文字から1000文字以内にしてください。

【最初に行うこと】
文書が何なのかを判断してください。

例：
・答案
・作文
・小論文
・レポート
・学習ノート
・企画書
・申立書
・準備書面
・その他の文書

内容が答案ではない場合に、
無理に点数や学力を評価してはいけません。

【返信の基本構成】

「おう、読んだぞ。」など、
内容を確認したことが伝わる自然な一言から始めてください。

その後、原則として次の項目を使ってください。

■源おじの見立て
文書全体の特徴や現在地を、短く具体的に説明する。

■良かったところ
最も良い点を1つから3つ挙げる。
必ず文書の具体的な内容に触れる。

■気になったところ
改善効果が大きい点を1つから3つ挙げる。
人格ではなく、文章・構成・理解・表現・論理などを指摘する。

■今すぐ直すならここ
最優先で直す点を一つだけ示す。
可能であれば、修正例も短く示す。

■次の5分
ユーザーが今すぐできる行動を一つだけ示す。

【重要】
内容が不足している場合は断定しないでください。
法的文書の場合、法的判断や勝訴を保証してはいけません。
医療文書の場合、診断を断定してはいけません。

返信の最後には、必ず次の趣旨を、
源おじらしい自然な言葉で入れてください。

「もっと詳しいのが知りたけりゃ、
下のボタンを押してみな。
今のお前の実力が丸裸にされるぜｗ」

ただし、答案や学習文書ではない場合は、
「実力」ではなく「この文書の弱点や改善点」など、
文書の種類に合う自然な表現に変えてください。

現在は詳細分析ボタンが未実装なので、
最後に小さく次の案内も加えてください。

「※超詳細分析（剛）は準備中だ。」
"""
# =========================================================
# 画像分析専用プロンプト
# =========================================================

IMAGE_ANALYSIS_PROMPT = """
ユーザーから画像が送られました。

画像を実際に確認し、まず何の画像なのかを判断してください。

例：
・教科書や参考書
・試験問題
・答案
・学習ノート
・実習レポート
・表や一覧表
・法律文書
・画面のスクリーンショット
・写真
・その他

画像の種類を推測だけで断定してはいけません。
確認できる範囲で判断し、不明な場合は「詳しい種類までは確認できない」と伝えてください。

画像内に文字がある場合は、読める範囲で内容を確認してください。
小さい文字、ぼやけた文字、見切れた部分は無理に補完しないでください。

表や一覧表の場合は、数字や記号だけを見て誤記と決めつけず、
行・列・見出し・複数回答の可能性を考慮してください。

法律文書の場合は、法的判断や勝敗を断定せず、
文書の構成、主張、争点、分かりやすさを整理してください。

医療や学習に関する画像の場合も、
画像から確認できない内容を推測だけで断定してはいけません。

返信は原則として次の順番にしてください。

1. 「おう、画像を確認したぞ。」など自然な一言
2. 何の画像に見えるか
3. 画像から読み取れた主な内容
4. 良かった点や重要な点
5. 気になる点があれば一つ
6. 次に行うことを一つ

画像を送っただけなのに、
「勉強を頑張った」「文書を読み込んだ」などと勝手に決めつけないでください。

LINEで読みやすいように、
通常は300文字から800文字程度を目安にしてください。
"""

TEACHING_IMAGE_CHARACTER_PROMPT = """
あなたは「ライセンスタウン」の伴走担当「源おじ」です。
少しがさつだが相手を本気で考える、親しみやすい自然な日本語で説明してください。
「おう！」「あぁ…これな…」「ここがポイントだぞ」などは、内容に合う場合だけ自然に使って構いません。
人格を傷つける表現、成功を保証する表現、確認できない内容を確認したふりをすることは禁止です。
医療情報は画像から確認できる範囲と一般的な学習上の説明に限定し、診断を断定しないでください。
分からないことや根拠が不足することは、推測で断定せず不明だと伝えてください。
"""

TEACHING_IMAGE_READING_PROMPT = """
画像を実際に確認してください。
画像内で読める文字、表、図、問題文、選択肢を確認してください。
小さい文字、ぼやけた文字、見切れた部分を推測で補完しないでください。
読み取れない部分は、読み取れない、または不明であると明示してください。
"""

EXPLAIN_TEACHING_PROMPT = """
これは「教えて源さん」における最優先の回答方針です。
国家試験問題や練習問題、選択問題を認識した場合、問題文の要約やオウム返しで終わらせないでください。
学習者へ「復習してみよう」「整理してみよう」「考えてみよう」と課題を返して説明を終えてはいけません。
資料から根拠を読み取れる場合は、源さん自身が着眼点から正答まで順番に説明し切ってください。
問題文と選択肢を十分読み取れる選択式問題では、正答を明示せずに回答を終了することを原則禁止します。

回答では、問題に合わせて自然に次をつないでください。

・何を問われている問題か
・問題文のどの情報に注目するか
・その所見が医学・理学療法上どんな意味を持つか
・複数の所見をどう結び付けるか
・その情報から候補をどう絞るか
・正答が何か
・その選択肢が正しい理由
・必要な場合、主な誤答選択肢が今回の所見と合わない理由

「ここに注目する」だけで止めず、「なぜ重要か」「どの選択肢につながるか」「だから何が正答か」まで具体的に述べてください。
正答を特定できる問題では、正答を曖昧にせず明示してください。
正答を明示した後は、次に似た問題で使える「見る順番」や「解き方」を短く残してください。

問題文の情報をすべて同じ重さで読み上げないでください。
正答を導く所見を優先し、今回の問いへの優先度が低い背景情報は、必要な場合だけ短く触れてください。
まず正答への一本道を完成させ、その後で受験生が迷いやすい誤答選択肢だけを簡潔に補足してください。AからEまでを機械的に長く説明する必要はありません。

例えば、立脚後期の前方推進力低下について、下腿三頭筋MMT2と、膝屈曲位では背屈可能だが膝伸展位では背屈制限がある所見を認識した場合は、次のように情報を結び付けます。
立脚後期、踵離地の乏しさ、下腿三頭筋MMT2、膝屈曲位と膝伸展位での背屈ROM差を優先して拾います。立脚後期の推進には下腿三頭筋が重要で、MMT2は筋力低下の根拠になります。腓腹筋は膝と足関節をまたぐ二関節筋なので、膝伸展時に強くなる背屈制限は腓腹筋の伸張性低下を示します。この二つがそろうため、正答は「B．下腿三頭筋筋力低下と腓腹筋の伸張性低下」であると、理由とともに明示してください。

ユーザーから明示的に設問品質の評価を頼まれていない限り、問題作成者向けの評価をしてはいけません。
設問の出来や表現への評価は不要です。
その文章量は、着眼点、所見の意味、所見同士の関連、正答へ至る理由の説明に使ってください。

見出しを毎回固定表示する必要はありません。重要なのは、正答だけでなく到達する思考を教えることです。
問題ではない授業資料、教科書、ノート、図表の場合は無理に正答形式にせず、重要点、意味、関連知識、国家試験での問われ方を学習に役立つ形で説明してください。
問題ではない資料にも「正答」や「誤答選択肢」を無理に当てはめてはいけません。
資料から読み取れない内容は推測で補完しないでください。

回答を出す前に、内部的に次を確認してください。
・十分読めた選択式問題なら、正答を明示したか
・正答の根拠となる所見を具体的に拾ったか
・所見の意味と所見同士のつながりを説明したか
・「考えてみよう」などで本来の説明をユーザーへ丸投げしていないか
・求められていない設問品質の評価を入れていないか
・一般資料へ正答形式を無理に当てはめていないか
"""

# =========================================================
# Flask / LINE SDK 初期化
# =========================================================

app = Flask(__name__)

line_bot_api = LineBotApi(
    os.environ["CHANNEL_ACCESS_TOKEN"],
    timeout=60,
)

handler = WebhookHandler(
    os.environ["CHANNEL_SECRET"]
)
# =========================================================
# 学習セッション管理
# =========================================================

# 1回の小テストで出題する問題数
QUIZ_QUESTION_COUNT = 30
# 1セットで出題・解説する問題数
QUESTIONS_PER_SET = 5
# 問題倉庫JSON
QUESTIONS_FILE_PATH = Path(__file__).resolve().parent / "questions_master.json"


def load_question_master(path=None):
    """
    questions_master.json から問題一覧を読み込む
    """

    question_path = Path(path or QUESTIONS_FILE_PATH)
    raw_data = question_path.read_bytes()
    encoding = "utf-16" if raw_data.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
    data = json.loads(raw_data.decode(encoding))

    questions = data.get("questions")
    if not isinstance(questions, list):
        raise ValueError("問題JSONにquestions配列がありません。")
    if data.get("question_count") != len(questions):
        raise ValueError("問題JSONのquestion_countと実件数が一致しません。")

    return questions


def select_random_questions(question_count):
    """
    問題倉庫からランダムに取得
    """

    questions = load_question_master()

    if question_count > len(questions):
        raise ValueError("出題数が問題倉庫の件数を超えています。")

    return random.sample(
        questions,
        question_count
    )

# 回答時に使用する自信度
CONFIDENCE_LEVELS = {
    "1": "自信あり",
    "2": "少し迷った",
    "3": "あてずっぽう",
}

# ユーザーごとの現在の小テストを一時保存する。
# Renderが再起動すると消えるため、これは試作版。
study_sessions = {}


# =========================================================
# AIによる小テスト生成
# =========================================================

def generate_quiz_questions(question_count):
    """
    OpenAIを使って、
    理学療法士国家試験対策の4択問題を生成する。
    """

    generation_prompt = f"""
理学療法士国家試験を受験する学生向けに、
オリジナルの4択問題を{question_count}問作成してください。

【必ず守る条件】
・既存の国家試験問題をそのまま複製しない
・選択肢は必ずA、B、C、Dの4つ
・正解は必ず1つだけ
・問題文や選択肢に正解を表示しない
・各問題に正答の理由を説明する解説を付ける
・可能であれば、間違いやすい選択肢との違いも説明する
・基礎問題、標準問題、応用問題を含める
・問題番号は1から{question_count}まで付ける

【出題分野】
・解剖学
・生理学
・運動学
・病理学
・内科学
・神経内科学
・整形外科学
・小児科学
・老年学
・評価学
・理学療法治療学
・歩行分析
・地域理学療法
・制度、介護保険

必ず次のJSON形式だけで返してください。

{{
  "questions": [
    {{
      "number": 1,
      "question": "問題文",
      "choices": {{
        "A": "選択肢A",
        "B": "選択肢B",
        "C": "選択肢C",
        "D": "選択肢D"
      }},
      "correct_answer": "A",
      "explanation": "なぜAが正解なのかを説明する文章",
      "category": "分野名",
      "difficulty": "基礎"
    }}
  ]
}}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "あなたは理学療法士国家試験対策の"
                    "問題作成担当者です。"
                    "医学的に正確で、正答が一つに定まる"
                    "オリジナル問題を作成してください。"
                    "必ずJSONだけを出力してください。"
                ),
            },
            {
                "role": "user",
                "content": generation_prompt,
            },
        ],
        response_format={
            "type": "json_object"
        },
        temperature=0.7,
        max_tokens=10000,
    )

    response_text = response.choices[0].message.content

    if not response_text:
        raise ValueError(
            "問題生成結果が空でした。"
        )

    quiz_data = json.loads(response_text)

    questions = quiz_data.get(
        "questions",
        [],
    )

    if len(questions) != question_count:
        raise ValueError(
            f"{question_count}問を要求しましたが、"
            f"{len(questions)}問しか生成されませんでした。"
        )

    cleaned_questions = []

    for index, question_data in enumerate(
        questions,
        start=1,
    ):
        choices = question_data.get(
            "choices",
            {},
        )

        correct_answer = str(
            question_data.get(
                "correct_answer",
                "",
            )
        ).upper().strip()

        if not question_data.get("question"):
            raise ValueError(
                f"第{index}問の問題文がありません。"
            )

        if not all(
            key in choices
            for key in ["A", "B", "C", "D"]
        ):
            raise ValueError(
                f"第{index}問の選択肢が不足しています。"
            )

        if correct_answer not in [
            "A",
            "B",
            "C",
            "D",
        ]:
            raise ValueError(
                f"第{index}問の正答が不正です。"
            )

        cleaned_questions.append(
            {
                "number": index,
                "question": str(
                    question_data["question"]
                ).strip(),
                "choices": {
                    "A": str(
                        choices["A"]
                    ).strip(),
                    "B": str(
                        choices["B"]
                    ).strip(),
                    "C": str(
                        choices["C"]
                    ).strip(),
                    "D": str(
                        choices["D"]
                    ).strip(),
                },
                "correct_answer": correct_answer,
                "explanation": str(
                    question_data.get(
                        "explanation",
                        "",
                    )
                ).strip(),
                "category": str(
                    question_data.get(
                        "category",
                        "未分類",
                    )
                ).strip(),
                "difficulty": str(
                    question_data.get(
                        "difficulty",
                        "標準",
                    )
                ).strip(),
            }
        )

    return cleaned_questions
# =========================================================
# 小テストをLINE送信用の文章に分割
# =========================================================

def format_quiz_messages(questions, start_number=1):
    """
    選ばれた5問を、1通の文章にまとめる。
    """

    question_parts = []

    for display_number, question_data in enumerate(
        questions,
        start=start_number,
    ):
        choices = question_data["choices"]

        question_text = (
            f"【第{display_number}問】\n"
            f"{question_data['question']}\n\n"
            f"A. {choices['A']}\n"
            f"B. {choices['B']}\n"
            f"C. {choices['C']}\n"
            f"D. {choices['D']}\n"
            f"E. {choices['E']}"
        )

        question_parts.append(question_text)

    example_numbers = range(start_number, start_number + len(questions))
    example_answers = ["A1", "B2", "C3", "D1", "E2"]
    input_examples = "\n".join(
        f"{number}:{answer}"
        for number, answer in zip(example_numbers, example_answers)
    )

    instruction_message = (
        "【回答方法】\n"
        "回答するときは、\n"
        "「答え」と「自信度」をセットで送ってくれ。\n\n"
        f"【入力例】\n{input_examples}\n\n"
        "【自信度】\n"
        "1＝自信あり\n"
        "2＝少し迷った\n"
        "3＝あてずっぽう\n\n"
        "つまり「A1」なら、\n"
        "答えはA、自信ありって意味だ。\n\n"
        f"{len(questions)}問分をまとめて送ってくれ（笑）"
    )

    all_questions_message = (
        instruction_message
        + "\n\n"
        + "\n\n".join(question_parts)
    )

    return [all_questions_message]

# =========================================================
# 小テスト開始
# =========================================================

def start_quiz(user_id):
    """
    最初の5問だけ生成し、
    ユーザーごとのセッションへ保存する。
    """

    if not user_id:
        raise ValueError(
            "小テストを開始するためのユーザーIDがありません。"
        )

    if QUIZ_QUESTION_COUNT % QUESTIONS_PER_SET != 0:
        raise ValueError("出題数は1セットの問題数で割り切れる必要があります。")

    all_questions = select_random_questions(QUIZ_QUESTION_COUNT)
    questions = all_questions[:QUESTIONS_PER_SET]

    study_sessions[user_id] = {
        "status": "waiting_for_answers",
        "current_set": 1,
        "question_count": QUIZ_QUESTION_COUNT,
        "questions_per_set": QUESTIONS_PER_SET,
        "total_sets": QUIZ_QUESTION_COUNT // QUESTIONS_PER_SET,
        "questions": questions,
        "all_questions": all_questions,
        "all_answers": {},
    }

    quiz_messages = format_quiz_messages(questions)

    return quiz_messages
def start_next_quiz(user_id):
    """
    現在の学習セッションを維持したまま、
    重複しない次の5問を準備する。
    """

    current_session = study_sessions.get(user_id)

    if not current_session:
        raise ValueError(
            "続きから開始する学習セッションがありません。"
        )

    current_set = current_session.get("current_set", 1)
    total_sets = current_session["total_sets"]
    questions_per_set = current_session["questions_per_set"]
    question_count = current_session["question_count"]

    if current_set >= total_sets:
        raise ValueError(
            f"すでに{question_count}問すべて出題済みです。"
        )

    current_session["current_set"] = current_set + 1
    start_index = current_set * questions_per_set
    end_index = start_index + questions_per_set
    new_questions = current_session["all_questions"][start_index:end_index]

    if len(new_questions) != questions_per_set:
        raise RuntimeError("選出済み問題から次のセットを取得できませんでした。")

    current_session["questions"] = new_questions
    current_session["status"] = "waiting_for_answers"

    start_number = start_index + 1

    return format_quiz_messages(
        new_questions,
        start_number=start_number,
    )
# =========================================================
# 小テストをバックグラウンドで生成・送信
# =========================================================

def prepare_and_send_quiz(user_id):
    """
    Webhookとは別の処理で問題を生成し、
    完成後にLINEへプッシュ送信する。
    """

    try:
        show_loading_animation(user_id)

        quiz_messages = start_quiz(user_id)

        for quiz_message in quiz_messages:
            push_to_line(
                user_id,
                quiz_message,
            )

    except Exception:
        logging.exception(
            "Quiz background processing failed."
        )

        study_sessions.pop(
            user_id,
            None,
        )

        push_to_line(
            user_id,
            (
                "おう、悪い。\n"
                "問題を準備してる途中で、"
                "源おじがズッコケた（笑）\n\n"
                "少し待ってから、"
                "もう一回「問題出して」って"
                "送ってくれ。"
            ),
        )
def prepare_and_send_next_quiz(user_id):
    """
    学習セッションを維持したまま、
    次の5問をバックグラウンドで準備して送信する。
    """

    try:
        show_loading_animation(user_id)

        quiz_messages = start_next_quiz(user_id)

        for quiz_message in quiz_messages:
            push_to_line(
                user_id,
                quiz_message,
            )

    except Exception:
        logging.exception(
            "Next quiz background processing failed."
        )

        push_to_line(
            user_id,
            (
                "おう、悪い。\n"
                "次の5問を準備する途中で、"
                "源おじがズッコケた（笑）\n"
                "少し待ってから、もう一度"
                "「続ける」って送ってくれ。"
            ),
        )
# =========================================================
# 小テスト回答の読み取り
# =========================================================

def parse_quiz_answers(user_message, expected_numbers=None):
    """
    例：
    1:A1
    2:C3

    を読み取り、
    問題番号・回答・自信度に分ける。
    """

    normalized_message = unicodedata.normalize("NFKC", user_message).upper()
    compact_message = re.sub(r"[\s,、]+", "", normalized_message)

    if not compact_message:
        return {}

    explicit_pattern = re.compile(r"(\d+):?([A-E])([1-3])")

    if compact_message[0].isdigit():
        explicit_matches = list(explicit_pattern.finditer(compact_message))

        if "".join(match.group(0) for match in explicit_matches) != compact_message:
            return {}

        parsed_answers = {}

        for match in explicit_matches:
            question_number = int(match.group(1))

            if question_number in parsed_answers:
                return {}

            parsed_answers[question_number] = {
                "answer": match.group(2),
                "confidence": match.group(3),
            }

        expected_count = len(expected_numbers) if expected_numbers is not None else QUESTIONS_PER_SET
        if len(parsed_answers) != expected_count:
            return {}

        if expected_numbers is not None and set(parsed_answers) != set(expected_numbers):
            return {}

        return parsed_answers

    implicit_matches = re.findall(r"([A-E])([1-3])", compact_message)

    expected_count = len(expected_numbers) if expected_numbers is not None else QUESTIONS_PER_SET

    if (
        len(implicit_matches) != expected_count
        or "".join("".join(match) for match in implicit_matches)
        != compact_message
    ):
        return {}

    answer_numbers = sorted(expected_numbers or range(1, QUESTIONS_PER_SET + 1))

    if len(answer_numbers) != expected_count:
        return {}

    return {
        question_number: {
            "answer": selected_answer,
            "confidence": confidence,
        }
        for question_number, (selected_answer, confidence) in zip(
            answer_numbers,
            implicit_matches,
        )
    }


def calculate_quiz_result(questions, answers):
    """問題と回答を通し番号で対応付け、採点結果を返す。"""
    score = 0
    details = []

    for question_number, question_data in enumerate(questions, start=1):
        answer_data = answers.get(question_number, {})
        selected_answer = str(answer_data.get("answer", "")).upper().strip()
        confidence = str(answer_data.get("confidence", "")).strip()
        correct_answer = str(question_data.get("answer", "")).upper().strip()
        is_correct = selected_answer == correct_answer

        if is_correct:
            score += 1

        details.append(
            {
                "question_number": question_number,
                "question_id": question_data.get("id"),
                "selected_answer": selected_answer,
                "correct_answer": correct_answer,
                "confidence": confidence,
                "is_correct": is_correct,
            }
        )

    return {
        "score": score,
        "total": len(questions),
        "details": details,
    }


def create_quiz_completion_summary(quiz_result):
    """Create a short review summary after every explanation has been read."""
    score = quiz_result["score"]
    total = quiz_result["total"]
    details = quiz_result.get("details", [])
    accuracy = (score / total * 100) if total else 0.0
    accuracy_text = "100％" if total and score == total else f"{accuracy:.1f}％"

    incorrect = [
        detail["question_number"]
        for detail in details
        if not detail.get("is_correct")
    ]

    review_groups = [
        (
            "自信ありで間違えた",
            False,
            "1",
        ),
        (
            "少し迷って間違えた",
            False,
            "2",
        ),
        (
            "あてずっぽうで間違えた",
            False,
            "3",
        ),
        (
            "少し迷って正解",
            True,
            "2",
        ),
        (
            "あてずっぽうで正解",
            True,
            "3",
        ),
    ]

    review_lines = []
    for label, is_correct, confidence in review_groups:
        numbers = [
            detail["question_number"]
            for detail in details
            if detail.get("is_correct") is is_correct
            and str(detail.get("confidence", "")) == confidence
        ]
        if numbers:
            review_lines.append(f"{label}：{format_quiz_question_numbers(numbers)}")

    lines = [
        f"{total}問、本当におつかれさん！",
        "解くだけじゃなく、最後まで解答解説を確認できたのも大事だぞ＾＾",
        "",
        "【今回の結果】",
        f"正解：{score} / {total}問",
        f"正答率：{accuracy_text}",
        "",
    ]

    if incorrect:
        lines.extend([
            "【間違えた問題】",
            format_quiz_question_numbers(incorrect),
        ])
    else:
        lines.append("今回は間違えた問題はなかったぞ！")

    if review_lines:
        lines.extend(["", "【優先して復習】", *review_lines])

    lines.extend(["", "【明日以降】"])
    if accuracy >= 90:
        lines.extend([
            "全体としてよくできているぞ！",
            "間違えた問題と、自信度2・3の問題を中心に復習しよう。",
            "自信を持って正解できた問題は、そのまま先へ進んで大丈夫だ。",
        ])
    elif accuracy >= 70:
        lines.extend([
            "まずは間違えた問題を見直そう。",
            "特に「自信あり」で間違えた問題は、覚え違いの可能性があるから最優先だ。",
            "次のテスト前に、迷ったところも軽く見直しておくと定着しやすいぞ。",
        ])
    else:
        lines.extend([
            "今は問題数をこなすことより、解説を理解することを優先しよう。",
            "間違えたところをもう一度復習してから、次のテストへ進むといいぞ。",
        ])

    lines.extend([
        "",
        f"今日の{total}問はこれで終了！",
        "また次も積み重ねていこう＾＾",
    ])
    return "\n".join(lines)


def format_quiz_question_numbers(question_numbers):
    """Format session-local question numbers compactly for LINE messages."""
    return "、".join(f"第{number}問" for number in question_numbers)
# =========================================================
# 小テストの採点結果を作成
# =========================================================

def create_quiz_result_messages(
    questions,
    parsed_answers,
    start_number=1,
):
    """
    5問を採点し、
    点数・正誤・正解・解説をLINE用の文章にまとめる。
    """

    result_parts = []

    for question_number, question_data in enumerate(
        questions,
        start=start_number,
    ):
        user_answer_data = parsed_answers.get(
            question_number,
            {},
        )

        selected_answer = user_answer_data.get(
            "answer",
            "",
        )

        confidence = user_answer_data.get(
            "confidence",
            "",
        )

        correct_answer = str(
            question_data.get(
                "answer",
                "",
            )
        ).upper().strip()

        explanation = str(
            question_data.get(
                "explanation",
                "解説はありません。",
            )
        ).strip()

        confidence_text = CONFIDENCE_LEVELS.get(
            confidence,
            "不明",
        )

        is_correct = (
            selected_answer == correct_answer
        )

        if is_correct:
            result_mark = "○"
        else:
            result_mark = "×"

        result_parts.append(
            (
                f"【第{question_number}問】{result_mark}\n"
                f"あなたの回答：{selected_answer}\n"
                f"正解：{correct_answer}\n"
                f"自信度：{confidence_text}\n"
                f"解説：{explanation}"
            )
        )

    result_messages = []
    current_message = ""

    for result_part in result_parts:
        additional_text = result_part + "\n\n"

        if (
            len(current_message)
            + len(additional_text)
            > 1750
        ):
            result_messages.append(
                current_message.strip()
            )
            current_message = additional_text

        else:
            current_message += additional_text

    if current_message.strip():
        result_messages.append(
            current_message.strip()
        )

    return result_messages


def advance_quiz_explanations(session):
    """次の5問分の解答解説を作り、閲覧状態を進める。"""
    if session.get("status") not in {
        "waiting_for_explanations",
        "waiting_for_next_explanation",
    }:
        raise ValueError("現在は解答解説を表示できる状態ではありません。")

    explanation_set = session.get("explanation_set", 0) + 1
    questions_per_set = session["questions_per_set"]
    start_index = (explanation_set - 1) * questions_per_set
    end_index = min(start_index + questions_per_set, session["question_count"])
    questions = session["all_questions"][start_index:end_index]

    if not questions:
        raise ValueError("表示する解答解説がありません。")

    messages = create_quiz_result_messages(
        questions,
        session["all_answers"],
        start_number=start_index + 1,
    )
    session["explanation_set"] = explanation_set
    session["status"] = (
        "quiz_completed"
        if end_index >= session["question_count"]
        else "waiting_for_next_explanation"
    )
    return messages
# =========================================================
# 共通関数：LINEへ返信
# =========================================================

def reply_to_line(reply_token, reply_message):
    """
    LINEにテキストを返信する共通関数。
    LINEの文字数上限を考慮して、長すぎる場合は切る。
    """

    if not reply_message:
        reply_message = (
            "おう、聞こえてるぞ（笑）"
            "もう一回送ってみてくれ。"
        )

    reply_message = reply_message.strip()

    if len(reply_message) > 1900:
        reply_message = reply_message[:1900] + "…"

    try:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=reply_message),
        )

    except Exception:
        logging.exception("LINE reply failed.")


def reply_new_user_welcome(reply_token):
    """初回利用者へ、ライセンスタウンの案内だけを送る。"""
    welcome_message = (
        "ようこそ、ライセンスタウンへ！\n\n"
        "ライセンスタウンは、理学療法士国家試験の合格を目指すあなたと一緒に、"
        "問題演習や復習を積み重ねながら、合格まで歩んでいく学習サービスです。\n\n"
        "大切なのは、一度に全部できるようになることではありません。\n"
        "一つずつ「できる」を増やして、国家試験合格を目指していきましょう。\n\n"
        "それでは、ここからは源さんにバトンタッチします！\n"
        "何か源さんに話しかけてみてくださいねｗ\n\n"
        "それではいってらっしゃい＾＾"
    )
    reply_to_line(reply_token, welcome_message)


def reply_gen_first_greeting(reply_token):
    """利用者から次の発言が届いた後、既存の源さんの挨拶を送る。"""
    reply_to_line(
        reply_token,
        "おぉｗよくきたな！\n"
        "俺は源ってんだ、みんなは源おじとか、源さんとかって呼んでるぜｗ\n"
        "お前の名前も聞かせてくれよ＾＾",
    )


def is_complete_reset_command(message_text):
    """前後の空白を除き、完全初期化コマンドとの完全一致だけを許可する。"""
    return str(message_text).strip() == "ふりだしにもどる"
# =========================================================
# 共通関数：準備確認のクイックリプライ付き返信
# =========================================================

def reply_mode_select(reply_token, intro_text=None):
    """
    「今日は何する？＾＾」と、
    4つの入口をクイックリプライで送る。
    """

    reply_message = TextSendMessage(
        text="今日は何する？＾＾\n下のボタンを押して教えてくれな＾＾",
        quick_reply=QuickReply(
            items=[
                QuickReplyButton(
                    action=MessageAction(
                        label="📖 勉強する！",
                        text="勉強する",
                    )
                ),
                QuickReplyButton(
                    action=MessageAction(
                        label="💡 教えて源さん",
                        text="教えて源さん",
                    )
                ),
                QuickReplyButton(
                    action=MessageAction(
                        label="😎 相談したい",
                        text="相談したい",
                    )
                ),
                QuickReplyButton(
                    action=MessageAction(
                        label="🔥 熱血モード",
                        text="熱血モード",
                    )
                ),
            ]
        ),
    )

    try:
        if intro_text:
            messages = [
                TextSendMessage(text=intro_text),
                reply_message,
            ]
        else:
            messages = reply_message

        line_bot_api.reply_message(
            reply_token,
            messages,
        )

    except Exception:
        logging.exception(
            "LINE mode select quick reply failed."
        )


def reply_explain_method_choice(reply_token):
    """「教えて源さん」で、直接質問か資料添付かを選んでもらう。"""
    reply_message = TextSendMessage(
        text=(
            "おう！ここでは、分からないことを俺に聞いてくれればいいぞ＾＾\n"
            "国家試験の問題でも、授業で分からなかったことでも大丈夫だ。\n\n"
            "直接質問してもいいし、問題や資料を見せてくれてもいいぞ。\n"
            "WordやPDF、写真なんかを見せながら「ここ教えて！」でもOKだ＾＾\n\n"
            "どうやって聞く？"
        ),
        quick_reply=QuickReply(
            items=[
                QuickReplyButton(
                    action=MessageAction(
                        label="源さんに直接質問する",
                        text="源さんに直接質問する",
                    )
                ),
                QuickReplyButton(
                    action=MessageAction(
                        label="文書・写真等を見せる",
                        text="文書・写真等を見せる",
                    )
                ),
            ]
        ),
    )
    line_bot_api.reply_message(reply_token, reply_message)


def create_explain_review_message():
    """解説後の理解確認クイックリプライを作る。"""
    return TextSendMessage(
        text="だいたい理解できたか？＾＾\n次はどうする？",
        quick_reply=QuickReply(
            items=[
                QuickReplyButton(
                    action=MessageAction(label="わかった！", text="わかった！")
                ),
                QuickReplyButton(
                    action=MessageAction(
                        label="まだ質問がある！",
                        text="まだ質問がある！",
                    )
                ),
            ]
        ),
    )


def reply_explain_answer_with_review(reply_token, answer_text):
    """直接質問への回答と理解確認を同じReplyで順に送る。"""
    safe_answer_text = answer_text[:4500]
    if len(answer_text) > 4500:
        safe_answer_text += "…"
    line_bot_api.reply_message(
        reply_token,
        [
            TextSendMessage(text=safe_answer_text),
            create_explain_review_message(),
        ],
    )


def push_explain_answer_with_review(user_id, answer_text):
    """添付解析結果と理解確認をPushで順に送る。"""
    safe_answer_text = answer_text[:4500]
    if len(answer_text) > 4500:
        safe_answer_text += "…"
    line_bot_api.push_message(
        user_id,
        [
            TextSendMessage(text=safe_answer_text),
            create_explain_review_message(),
        ],
    )


def reply_study_continue_choice(reply_token):
    """
    5問分の回答を保存した後、
    次の5問へ進むか、一時停止するかを確認する。
    """

    reply_message = TextSendMessage(
        text=(
            "よし！次の5問だ！\n"
            "いくぞ！"
        ),
        quick_reply=QuickReply(
            items=[
                QuickReplyButton(
                    action=MessageAction(
                        label="▶️ 続ける",
                        text="続ける",
                    )
                ),
                QuickReplyButton(
                    action=MessageAction(
                        label="📥 源おじに預ける（一時停止）",
                        text="源おじに預ける",
                    )
                ),
            ]
        ),
    )
    try:
        line_bot_api.reply_message(
            reply_token,
            reply_message,
        )

    except Exception:
        logging.exception(
            "LINE study continue choice failed."
        )


def reply_explanation_choice(reply_token, completed=False, quiz_result=None):
    """解答解説の開始・続行、または完了を案内する。"""
    if completed:
        reply_to_line(
            reply_token,
            create_quiz_completion_summary(quiz_result),
        )
        return

    reply_message = TextSendMessage(
        text="準備できたら解答解説を確認しよう＾＾",
        quick_reply=QuickReply(
            items=[
                QuickReplyButton(
                    action=MessageAction(
                        label="📖 解答解説を見る",
                        text="解答解説を見る",
                    )
                )
            ]
        ),
    )
    line_bot_api.reply_message(reply_token, reply_message)


def reply_quiz_score(reply_token, quiz_result):
    """合計点と解答解説開始ボタンを表示する。"""
    reply_message = TextSendMessage(
        text=(
            f"おう、{quiz_result['total']}問すべて回答できたぞ＾＾\n\n"
            f"【結果】{quiz_result['score']} / "
            f"{quiz_result['total']}問正解\n\n"
            "解答解説は5問ずつ一緒に確認していこう。"
        ),
        quick_reply=QuickReply(
            items=[
                QuickReplyButton(
                    action=MessageAction(
                        label="📖 解答解説を見る",
                        text="解答解説を見る",
                    )
                )
            ]
        ),
    )
    line_bot_api.reply_message(reply_token, reply_message)


def reply_next_explanation_choice(reply_token):
    """次の5問分の解答解説へ進む操作を表示する。"""
    reply_message = TextSendMessage(
        text="ここまで確認できたら、次の5問へ進もう＾＾",
        quick_reply=QuickReply(
            items=[
                QuickReplyButton(
                    action=MessageAction(
                        label="▶️ 次の5問",
                        text="次の5問",
                    )
                )
            ]
        ),
    )
    line_bot_api.reply_message(reply_token, reply_message)
def reply_study_ready_choice(reply_token):
    """
    勉強モード開始前の準備確認。
    """

    reply_message = TextSendMessage(
        text=(
            "📚勉強モードへ切り替えたぞ！\n\n"
            "問題演習、国試対策、苦手分野の確認、なんでも来い＾＾\n\n"
            f"まずは{QUESTIONS_PER_SET}問ずつ、全部で{QUIZ_QUESTION_COUNT}問出すぞ！\n"
            "準備ができたら教えてくれ＾＾"
        ),
        quick_reply=QuickReply(
            items=[
                QuickReplyButton(
                    action=MessageAction(
                        label="✅ 準備OK！",
                        text="準備OK！",
                    )
                ),
                QuickReplyButton(
                    action=MessageAction(
                        label="⏳ ちょっと待って",
                        text="ちょっと待って",
                    )
                ),
            ]
        ),
    )

    try:
        line_bot_api.reply_message(
            reply_token,
            reply_message,
        )

    except Exception:
        logging.exception(
            "LINE study ready choice failed."
        )
# =========================================================
# 共通関数：LINEへPush送信
# =========================================================

def push_to_line(user_id, push_message):

    if not user_id:
        logging.error("User ID not found.")
        return

    if not push_message:
        push_message = (
            "おう、うまく送れなかったみてぇだ。"
        )

    if len(push_message) > 1900:
        push_message = push_message[:1900] + "…"

    try:
        line_bot_api.push_message(
            user_id,
            TextSendMessage(text=push_message),
        )

    except Exception:
        logging.exception(
            "LINE push failed."
        )
# =========================================================
# 共通関数：LINEにローディング表示
# =========================================================

def show_loading_animation(user_id):
    """
    画像などの処理中に、LINEへローディング表示を出す。
    """

    if not user_id:
        return

    request_url = "https://api.line.me/v2/bot/chat/loading/start"

    request_body = json.dumps(
        {
            "chatId": user_id,
            "loadingSeconds": 60,
        }
    ).encode("utf-8")

    request_headers = {
        "Content-Type": "application/json",
        "Authorization": (
            "Bearer "
            + os.environ["CHANNEL_ACCESS_TOKEN"]
        ),
    }

    loading_request = urllib.request.Request(
        request_url,
        data=request_body,
        headers=request_headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            loading_request,
            timeout=10,
        ):
            pass

    except Exception:
        logging.exception("LINE loading animation failed.")

# =========================================================
# 共通関数：OpenAIへテキストを送る
# =========================================================

def create_text_response(user_message, mode="normal"):
    """
    通常のテキスト会話用。
    """

    system_prompt = GEN_OJI_PROMPT + "\n\n" + EDUCATION_RULE_PROMPT
    if mode == "study":
        system_prompt += """
    
    現在は勉強モードです。
    理学療法士国家試験の学習支援を最優先にしてください。

    ユーザーの希望に応じて、次の対応をしてください。
    ・問題を出す
    ・解答を採点する
    ・正解と不正解の理由を説明する
    ・苦手分野を整理する
    ・国試対策として重要なポイントを伝える

    問題を出す場合は、一度に大量に出しすぎず、
    基本は1問ずつ出題してください。
    ユーザーが回答するまでは、原則として正解を先に言わないでください。
    """
    if mode == "chat":
        system_prompt += """

現在は相談モードです。

勉強の相談でも、
実習の相談でも、
雑談でも、
恋愛相談でも構いません。

ただし医学的・教育的な質問には、
これまで通り丁寧に答えてください。
"""
    if mode == "explain":
        system_prompt += """

現在は解説モードです。

ユーザーは、分からない内容を理解するために質問しています。
単に答えを述べるのではなく、源おじが隣で一緒に考えているように説明してください。

次の流れを意識してください。

・まず短く自然なリアクションをする
・何についての質問なのかを整理する
・最初に簡単な言葉で全体像を説明する
・その後、必要に応じて詳しく掘り下げる
・専門用語を使う場合は、かみ砕いて説明する
・つまずきやすい点や混同しやすい点も伝える
・最後に、理解できたか確認するか、次に見るべき点を提案する

ただし、毎回まったく同じ言い回しや構成にはしないでください。
分からないことや根拠が不十分なことは、推測で断定しないでください。
資料をまだ受け取っていない場合は、資料を見たような発言をしないでください。
"""
        system_prompt += EXPLAIN_TEACHING_PROMPT
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
        temperature=0.9,
        max_tokens=600,
    )

    reply_message = response.choices[0].message.content

    if not reply_message:
        return (
            "おう、聞こえてるぞ（笑）"
            "もう一回話してみてくれ。"
        )

    return reply_message.strip()


def create_contextual_explain_response(user_id, user_message):
    """直前の質問または添付資料を実際に再投入して追加質問へ答える。"""
    context = explain_contexts.setdefault(
        user_id,
        {"kind": "direct", "turns": []},
    )
    prior_turns = context.get("turns", [])[-6:]
    transcript = "\n\n".join(
        f"{role}：{text}"
        for role, text in prior_turns
    )
    context_instruction = ""

    if context.get("kind") == "document":
        context_instruction = (
            "\n\n【直前に受け取った資料】\n"
            + context.get("source_text", "")[:40000]
        )

    if context.get("kind") == "image":
        input_text = (
            EXPLAIN_TEACHING_PROMPT
            + "\n\n【これまでの会話】\n"
            + transcript
            + "\n\n【今回の追加質問】\n"
            + user_message
            + "\n直前の画像を実際に見直して回答してください。"
        )
        response = client.responses.create(
            model="gpt-4.1-mini",
            instructions=GEN_OJI_PROMPT + "\n\n" + EDUCATION_RULE_PROMPT,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": input_text},
                        {
                            "type": "input_image",
                            "image_url": (
                                "data:image/jpeg;base64,"
                                + context.get("image_base64", "")
                            ),
                            "detail": "auto",
                        },
                    ],
                }
            ],
            max_output_tokens=1200,
        )
        reply_message = response.output_text
    else:
        messages = [
            {
                "role": "system",
                "content": (
                    GEN_OJI_PROMPT
                    + "\n\n"
                    + EDUCATION_RULE_PROMPT
                    + "\n\n"
                    + EXPLAIN_TEACHING_PROMPT
                    + context_instruction
                ),
            },
        ]
        for role, text in prior_turns:
            messages.append({"role": role, "content": text})
        messages.append({"role": "user", "content": user_message})
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
        )
        reply_message = response.choices[0].message.content

    if not reply_message:
        reply_message = "おう、もう一回だけ聞かせてくれ。今度は別の角度から説明するぞ＾＾"

    reply_message = reply_message.strip()
    context.setdefault("turns", []).extend([
        ("user", user_message),
        ("assistant", reply_message),
    ])
    context["turns"] = context["turns"][-8:]
    return reply_message


# =========================================================
# 共通関数：LINEからファイル本体を取得
# =========================================================

def download_line_file(message_id):
    """
    LINE上のメッセージIDを使って、
    添付ファイルのバイナリデータを取得する。
    """

    message_content = line_bot_api.get_message_content(message_id)

    file_buffer = io.BytesIO()

    for chunk in message_content.iter_content(chunk_size=8192):
        if chunk:
            file_buffer.write(chunk)

    file_buffer.seek(0)

    return file_buffer
# =========================================================
# 共通関数：画像をBase64へ変換
# =========================================================



def image_buffer_to_base64(file_buffer):
    """
    LINEから取得した画像をBase64文字列へ変換する。
    """

    file_buffer.seek(0)

    image_bytes = file_buffer.read()

    return base64.b64encode(image_bytes).decode("utf-8")
# =========================================================
# 共通関数：画像をOpenAIで分析
# =========================================================

def analyze_image(image_base64, use_teaching_intro=False):
    """
    Base64形式の画像をOpenAIへ送り、
    源おじとして内容を分析する。
    """

    if use_teaching_intro:
        teaching_intro = (
            "\n\nこれは『教えて源さん』で最初に受け取った資料です。"
            "内容に自然に合う場合は『あぁ…これな…』から解説へ入ってください。"
            "ただし機械的な固定表現にはせず、資料に合わなければ別の自然な導入にしてください。"
        )
        final_instructions = (
            TEACHING_IMAGE_CHARACTER_PROMPT
            + "\n\n"
            + EXPLAIN_TEACHING_PROMPT
            + "\n\n"
            + TEACHING_IMAGE_READING_PROMPT
            + teaching_intro
        )
        image_analysis_mode = "teaching"
    else:
        final_instructions = (
            GEN_OJI_PROMPT
            + "\n\n"
            + EDUCATION_RULE_PROMPT
            + "\n\n"
            + IMAGE_ANALYSIS_PROMPT
        )
        image_analysis_mode = "general"

    logging.info("image_analysis_mode=%s", image_analysis_mode)

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=final_instructions,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "この画像を実際に確認してください。"
                            "画像に書かれている文字、表、図、問題文、"
                            "ノートやレポートの内容を可能な範囲で読み取り、"
                            "源おじとして分かりやすく返答してください。"
                            "読めない部分や不明な部分は、"
                            "推測だけで断定しないでください。"
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": (
                            "data:image/jpeg;base64,"
                            + image_base64
                        ),
                        "detail": "auto",
                    },
                ],
            }
        ],
        max_output_tokens=1200,
    )

    reply_message = response.output_text

    if not reply_message:
        return (
            "おう、画像は見たぞ。"
            "ただ、今回は内容をうまくまとめられなかった。"
            "悪いが、もう一度送ってみてくれ（笑）"
        )

    return reply_message.strip()
# =========================================================
# 共通関数：PDFから文章を抽出
# =========================================================

def extract_text_from_pdf(file_buffer):
    """
    PDFファイルから文字を抽出する。
    """

    reader = PdfReader(file_buffer)

    extracted_parts = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()

        if page_text:
            extracted_parts.append(
                f"\n【{page_number}ページ目】\n{page_text.strip()}"
            )

    extracted_text = "\n".join(extracted_parts).strip()

    return extracted_text
# =========================================================
# 共通関数：Wordから文章と表を抽出
# =========================================================

def extract_text_from_docx(file_buffer):
    """
    .docxファイルから本文と表の内容を抽出する。
    """

    document = Document(file_buffer)

    extracted_parts = []

    # 本文の段落
    for paragraph in document.paragraphs:
        paragraph_text = paragraph.text.strip()

        if paragraph_text:
            extracted_parts.append(paragraph_text)

    # 表の中身
    for table_number, table in enumerate(document.tables, start=1):
        table_rows = []

        for row in table.rows:
            cells = []

            for cell in row.cells:
                cell_text = cell.text.strip()

                if cell_text:
                    cells.append(cell_text)

            if cells:
                table_rows.append(" | ".join(cells))

        if table_rows:
            extracted_parts.append(
                f"\n【表{table_number}】\n"
                + "\n".join(table_rows)
            )

    extracted_text = "\n".join(extracted_parts).strip()

    return extracted_text


# =========================================================
# 共通関数：Word文書を「柔」で分析
# =========================================================

def analyze_word_document(file_name, document_text, use_teaching_intro=False):
    """
    抽出したWord文書を源おじが簡易分析する。
    """

    # 長すぎる文書によるエラー・高額化を防止
    max_document_characters = 40000

    was_truncated = False

    if len(document_text) > max_document_characters:
        document_text = document_text[:max_document_characters]
        was_truncated = True

    truncation_note = ""

    if was_truncated:
        truncation_note = """
【注意】
文書が長いため、今回は冒頭から約4万文字までを対象に分析しています。
そのことをユーザーへ短く伝えてください。
"""

    user_content = f"""
【ファイル名】
{file_name}

【Word文書から抽出した内容】
{document_text}

{truncation_note}
"""

    teaching_intro = ""
    teaching_prompt = ""
    if use_teaching_intro:
        teaching_prompt = "\n\n" + EXPLAIN_TEACHING_PROMPT
        teaching_intro = (
            "\n\nこれは『教えて源さん』で最初に受け取った資料です。"
            "内容に自然に合う場合は『あぁ…これな…』から解説へ入ってください。"
            "ただし機械的な固定表現にはせず、資料に合わなければ別の自然な導入にしてください。"
        )

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": GEN_OJI_PROMPT + "\n\n" + EDUCATION_RULE_PROMPT,
            },
            {
                "role": "system",
                "content": (
                    WORD_ANALYSIS_PROMPT
                    + teaching_prompt
                    + teaching_intro
                ),
            },
            {
                "role": "user",
                "content": user_content,
            },
        ],
        temperature=0.6,
        max_tokens=1400,
    )

    reply_message = response.choices[0].message.content

    if not reply_message:
        return (
            "おう、Wordは受け取ったぞ。"
            "ただ、今回は分析結果をうまくまとめられなかった。"
            "悪いが、もう一度送ってみてくれ（笑）"
        )

    return reply_message.strip()


# =========================================================
# Healthcheck / Index
# =========================================================

@app.route("/health")
def health():
    return "OK", 200


@app.route("/", methods=["GET"])
def index():
    return "License Town LINE Bot is running!"


# =========================================================
# Webhook入口
# =========================================================

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    logging.info("Webhook received.")

    try:
        handler.handle(body, signature)

    except InvalidSignatureError:
        logging.warning("Invalid signature.")
        abort(400)

    except Exception:
        logging.exception("Webhook processing failed.")
        abort(500)

    return "OK", 200


# =========================================================
# 通常のテキストメッセージ
# =========================================================

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    raw_user_message = event.message.text
    user_message = raw_user_message.strip()
    user_id = getattr(
        event.source,
        "user_id",
        None,
    )
    if raw_user_message.strip() == "ふりだしにもどる":
        user_states.pop(user_id, None)
        study_sessions.pop(user_id, None)
        explain_contexts.pop(user_id, None)

        try:
            reset_user_profile(user_id)

        except Exception:
            logging.exception(
                "Complete user reset failed: user_id=%s",
                user_id,
            )
            reply_to_line(
                event.reply_token,
                (
                    "おう、会話と学習の状態はリセットしたぞ。\n"
                    "ただ、名前とモードのリセットを最後まで確認できなかった。\n"
                    "少し待ってから、もう一度「ふりだしにもどる」と送ってくれ。"
                ),
            )
            return

        user_states[user_id] = "waiting_gen_intro"
        reply_new_user_welcome(event.reply_token)
        return

    current_state = user_states.get(user_id)

    if current_state == "waiting_gen_intro":
        user_states[user_id] = "waiting_name"
        reply_gen_first_greeting(event.reply_token)
        return

    if current_state == "waiting_name":
        user_names[user_id] = user_message
        user_states.pop(user_id, None)

        reply_mode_select(
            event.reply_token,
            intro_text=(
                f"そっかわかった！\n"
                f"じゃあ今後は俺と{user_message}の二人三脚でゴールを目指して頑張るぜ！\n"
                f"よろしくな！{user_message}＾＾"
            ),
        )
        return

    if current_state == "waiting_explain_method":
        if user_message == "源さんに直接質問する":
            user_states[user_id] = "explain_direct"
            reply_to_line(
                event.reply_token,
                "おう、何でも聞いてくれ＾＾\n"
                "分からないことをそのまま書いて送ってくれればいいぞ！",
            )
            return

        if user_message == "文書・写真等を見せる":
            user_states[user_id] = "explain_attachment"
            reply_to_line(
                event.reply_token,
                "おう、見せてくれ＾＾\n"
                "Word、PDF、写真なんかを送ってくれれば、その内容を見ながら一緒に確認するぞ。\n"
                "資料を送ったあとに「ここが分からない」「この問題を解説して」みたいに聞いてくれてもOKだ！",
            )
            return

    if current_state == "explain_review":
        if user_message == "わかった！":
            user_states.pop(user_id, None)
            explain_contexts.pop(user_id, None)
            user_modes[user_id] = "normal"
            reply_mode_select(
                event.reply_token,
                intro_text=(
                    "おう、それならよかった＾＾\n"
                    "また分からないことがあったら、いつでも持ってこい！"
                ),
            )
            return

        if user_message == "まだ質問がある！":
            user_states[user_id] = "explain_followup"
            reply_to_line(
                event.reply_token,
                "おう、もちろんだ＾＾\n"
                "どこがまだ分からないか、書いて送ってくれ！",
            )
            return

    if current_state in {"explain_direct", "explain_followup"}:
        try:
            answer_text = create_contextual_explain_response(user_id, user_message)
            user_states[user_id] = "explain_review"
            reply_explain_answer_with_review(event.reply_token, answer_text)
        except Exception:
            logging.exception("Contextual explain response failed: user_id=%s", user_id)
            reply_to_line(
                event.reply_token,
                "おう、悪い。今ちょっとうまく説明をまとめられなかった。もう一度聞いてくれ。",
            )
        return

    # モード切替
    if user_message == "熱血モード":
        if str(user_states.get(user_id, "")).startswith("explain_"):
            user_states.pop(user_id, None)
            explain_contexts.pop(user_id, None)
        reply_to_line(
            event.reply_token,
            "熱血モードはこれから準備するぞ🔥",
        )
        return
    if user_message in ["相談したい", "相談する", "相談モード"]:
        if str(user_states.get(user_id, "")).startswith("explain_"):
            user_states.pop(user_id, None)
            explain_contexts.pop(user_id, None)
        user_modes[user_id] = "chat"
        reply_to_line(
            event.reply_token,
            "💬相談モードへ切り替えたぞ！\n"
            "勉強のことでも、実習のことでも、雑談でもOK！\n"
            "恋バナもありだぜ♡😎"
        )
        return
    if user_message in ["勉強する", "勉強モード"]:
        if str(user_states.get(user_id, "")).startswith("explain_"):
            user_states.pop(user_id, None)
            explain_contexts.pop(user_id, None)
        user_modes[user_id] = "study"
        reply_study_ready_choice(
        event.reply_token
    )
        return
    if user_message in ["教えて源さん", "質問する", "解説モード"]:
        user_modes[user_id] = "explain"
        explain_contexts.pop(user_id, None)
        user_states[user_id] = "waiting_explain_method"
        reply_explain_method_choice(event.reply_token)
        return
        
    if not user_message:
        return

    current_session = study_sessions.get(user_id)

    if current_session and current_session.get("status") in {
        "waiting_for_explanations",
        "waiting_for_next_explanation",
    }:
        expected_message = (
            "解答解説を見る"
            if current_session["status"] == "waiting_for_explanations"
            else "次の5問"
        )

        if user_message == expected_message:
            explanation_messages = advance_quiz_explanations(current_session)
            for explanation_message in explanation_messages:
                push_to_line(user_id, explanation_message)

            if current_session["status"] == "quiz_completed":
                reply_explanation_choice(
                    event.reply_token,
                    completed=True,
                    quiz_result=current_session["quiz_result"],
                )
            else:
                reply_next_explanation_choice(event.reply_token)
            return

        reply_to_line(
            event.reply_token,
            f"今は解答解説の確認中だ。『{expected_message}』で進んでくれ＾＾",
        )
        return

    if (
        current_session
        and current_session.get("status") == "waiting_for_continue"
        and user_message == "続ける"
    ):
        current_session["status"] = "preparing_next"

        reply_to_line(
            event.reply_token,
            "おう！次の5問を準備するぞ＾＾\n"
            "ちょっと待ってな！"
        )

        quiz_thread = threading.Thread(
            target=prepare_and_send_next_quiz,
            args=(user_id,),
            daemon=True,
        )

        quiz_thread.start()
        return

    if user_message == "準備OK！":
        reply_to_line(
            event.reply_token,
            (
                "おう、任せろ＾＾\n"
                "まず5問作るから、ちょっと待ってな（笑）"
            ),
        )

        quiz_thread = threading.Thread(
            target=prepare_and_send_quiz,
            args=(user_id,),
            daemon=True,
        )

        quiz_thread.start()
        return
    rest_words = ["休み", "休む", "今日は無理", "今日はできない", "休ませて"]

    if user_id not in user_names:
        if not user_profile_exists(user_id):
            user_states[user_id] = "waiting_gen_intro"
            reply_new_user_welcome(event.reply_token)
        else:
            user_states[user_id] = "waiting_name"
            reply_gen_first_greeting(event.reply_token)
        return

    # 「休み」「休む」などが含まれていたら、問題を始めない
        

    if any(word in user_message for word in rest_words):
        reply_to_line(
            event.reply_token,
            "どうした？何かあったんか？"
        )
        return
    # 初回メッセージなら、モード選択のクイックリプライを表示する
    if current_state is None and user_modes.get(user_id, "normal") == "normal":


        reply_mode_select(
            event.reply_token
        )
        return    
     # 「問題出して」と言われたら小テストを開始する
    if "問題出して" in user_message:
        reply_to_line(
            event.reply_token,
            (
                "おう、任せろ＾＾\n"
                f"まず{QUESTIONS_PER_SET}問出すから、ちょっと待ってな（笑）\n\n"
                "それじゃいくぞ＾＾"
            ),
        )

        quiz_thread = threading.Thread(
            target=prepare_and_send_quiz,
            args=(user_id,),
            daemon=True,
        )

        quiz_thread.start()

        return

     # 小テスト中に回答が送られてきた場合
    current_session = study_sessions.get(user_id)

    if (
        current_session
        and current_session.get("status")
        == "waiting_for_answers"
    ):
        current_set = current_session["current_set"]
        questions_per_set = current_session["questions_per_set"]
        start_number = ((current_set - 1) * questions_per_set) + 1
        expected_numbers = set(range(start_number, start_number + questions_per_set))

        parsed_answers = parse_quiz_answers(
            user_message,
            expected_numbers=expected_numbers,
        )

        if set(parsed_answers) != expected_numbers:
            reply_to_line(
                event.reply_token,
                (
                    "おう、回答は受け取ったぞ。\n\n"
                    f"ただ、{questions_per_set}問分を正しく読み取れなかったみてぇだ。\n"
                    f"第{start_number}問から第{start_number + questions_per_set - 1}問まで、"
                    "次の形で送ってくれ。\n\n"
                    + "\n".join(
                        f"{number}:{answer}"
                        for number, answer in zip(
                            range(start_number, start_number + questions_per_set),
                            ["A1", "B2", "C3", "D2", "E1"],
                        )
                    )
                ),
            )
            return

        for question_number, answer_data in parsed_answers.items():
            current_session["all_answers"][question_number] = answer_data

        if current_set >= current_session["total_sets"]:
            quiz_result = calculate_quiz_result(
                current_session["all_questions"],
                current_session["all_answers"],
            )
            current_session["quiz_result"] = quiz_result
            current_session["explanation_set"] = 0
            current_session["status"] = "waiting_for_explanations"

            reply_quiz_score(event.reply_token, quiz_result)
            return

        current_session["status"] = "waiting_for_continue"

        reply_study_continue_choice(
            event.reply_token
        )
        return

    # それ以外は、今までどおり普通に会話する

    # それ以外は、今までどおり普通に会話する
    try:
        current_mode = user_modes.get(user_id, "normal")
        reply_message = create_text_response(user_message, current_mode)

    except Exception:
        logging.exception("OpenAI response generation failed.")

        reply_message = (
            "おう、悪い悪い。"
            "ちょっと俺の頭が止まっちまった（笑）"
            "少し待ってから、もう一度送ってくれ。"
        )

    reply_to_line(
        event.reply_token,
        reply_message,
    )


# =========================================================
# Wordなどのファイルメッセージ
# =========================================================

@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    file_name = event.message.file_name or "添付ファイル"
    file_name_lower = file_name.lower()

    logging.info(
        "File received: name=%s, size=%s, message_id=%s",
        file_name,
        getattr(event.message, "file_size", "unknown"),
        event.message.id,
    )

    user_id = getattr(
        event.source,
        "user_id",
        None,
    )
    use_teaching_intro = user_states.get(user_id) == "explain_attachment"

    # 対応外のファイルは、これまで通りその場で返信する
    if not (
        file_name_lower.endswith(".docx")
        or file_name_lower.endswith(".pdf")
    ):
        if file_name_lower.endswith(".doc"):
            reply_message = (
                "おう、ファイルは受け取ったぞ。\n\n"
                "ただ、このWordは古い「.doc」形式みてぇだ。"
                "今読めるのは新しい「.docx」形式だ。\n\n"
                "Wordで「名前を付けて保存」から"
                "『Word文書（.docx）』にして、"
                "もう一度送ってみてくれ（笑）"
            )

        else:
            reply_message = (
                "おう、ファイルは受け取ったぞ。\n\n"
                "今のところ源おじが直接読めるファイルは、"
                "Wordの「.docx」とPDFの「.pdf」形式だ。\n\n"
                "写真やスクショは、"
                "ファイルではなく画像として送ってくれ（笑）"
            )

        reply_to_line(
            event.reply_token,
            reply_message,
        )
        return

    # Word・PDFは、まず源おじの相づちを即返信
    reply_to_line(
        event.reply_token,
        (
            "おっ、書類が来たな（笑）\n"
            "ちゃんと読むから、ちょっと待ってろ。"
        ),
    )

    show_loading_animation(user_id)

    document_text = ""
    try:
        # LINEからファイル本体を取得
        file_buffer = download_line_file(
            event.message.id
        )

        # ファイル形式に応じて文字を抽出
        if file_name_lower.endswith(".pdf"):
            document_text = extract_text_from_pdf(
                file_buffer
            )
            file_type_name = "PDF"

        else:
            document_text = extract_text_from_docx(
                file_buffer
            )
            file_type_name = "Word"

        if not document_text:
            analysis_message = (
                f"おう、{file_type_name}は開けたぞ。\n\n"
                "ただ、中から読める文字を見つけられなかった。"
                "画像だけで作られたファイルかもしれねぇな。\n\n"
                "その場合は、ページを画像として送ってみてくれ（笑）"
            )

        else:
            analysis_message = analyze_word_document(
                file_name=file_name,
                document_text=document_text,
                use_teaching_intro=use_teaching_intro,
            )

    except Exception:
        logging.exception(
            "Document processing failed: %s",
            file_name,
        )

        analysis_message = (
            "おう、ファイルは受け取ったんだが、"
            "今回はうまく開けなかったみてぇだ。\n\n"
            "Wordは「.docx」、PDFは「.pdf」形式か確認して、"
            "もう一度送ってみてくれ。\n\n"
            "それでもダメなら、源おじの工事ミスだ（笑）"
        )

    if use_teaching_intro:
        if document_text:
            explain_contexts[user_id] = {
                "kind": "document",
                "source_text": document_text[:40000],
                "turns": [("assistant", analysis_message)],
            }
        user_states[user_id] = "explain_review"
        push_explain_answer_with_review(user_id, analysis_message)
    else:
        push_to_line(user_id, analysis_message)

# =========================================================
# 画像メッセージ
# =========================================================

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    """
    画像を受け取ったら先に相づちを返し、
    その後、分析結果をプッシュ送信する。
    """

    logging.info(
        "Image received: message_id=%s",
        event.message.id,
    )

    user_id = getattr(
        event.source,
        "user_id",
        None,
    )
    use_teaching_intro = user_states.get(user_id) == "explain_attachment"
    logging.info(
        "image_analysis_mode=%s user_state=%s",
        "teaching" if use_teaching_intro else "general",
        user_states.get(user_id, "none"),
    )

    # まず源おじの相づちを即返信
    reply_to_line(
        event.reply_token,
        (
            "おっ、写真が来たな（笑）\n"
            "しっかり見るから、ちょっと待ってろ。"
        ),
    )

    show_loading_animation(user_id)

    image_base64 = ""
    try:
        image_buffer = download_line_file(
            event.message.id
        )

        image_base64 = image_buffer_to_base64(
            image_buffer
        )

        analysis_message = analyze_image(
            image_base64,
            use_teaching_intro=use_teaching_intro,
        )

    except Exception:
        logging.exception(
            "Image processing failed: message_id=%s",
            event.message.id,
        )

        analysis_message = (
            "おう、画像は受け取ったんだが、\n\n"
            "今回はうまく読み取れなかったみてぇだ。"
            "少し時間を空けて、もう一度送ってみてくれ。\n\n"
            "それでもダメなら、源おじの工事ミスだ（笑）"
        )

    if use_teaching_intro:
        if image_base64:
            explain_contexts[user_id] = {
                "kind": "image",
                "image_base64": image_base64,
                "turns": [("assistant", analysis_message)],
            }
        user_states[user_id] = "explain_review"
        push_explain_answer_with_review(user_id, analysis_message)
    else:
        push_to_line(user_id, analysis_message)
# =========================================================
# アプリケーション実行
# =========================================================

if __name__ == "__main__":
    port = int(
        os.environ.get(
            "PORT",
            10000,
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
    )
