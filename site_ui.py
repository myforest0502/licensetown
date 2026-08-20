import os

from flask import Blueprint, render_template


site_ui = Blueprint("site_ui", __name__)

# Public copy is deliberately centralized so the published figure can be
# updated without editing the page layout.
QUESTION_COUNT_LABEL = os.getenv("SITE_QUESTION_COUNT_LABEL", "1,500問以上収録")


@site_ui.get("/site")
def home():
    return render_template(
        "site/home.html",
        question_count_label=QUESTION_COUNT_LABEL,
        line_url=os.getenv("LINE_ADD_FRIEND_URL", "").strip(),
    )
