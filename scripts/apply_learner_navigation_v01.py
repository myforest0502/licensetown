from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"expected source block not found in {path}: {old[:140]!r}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


def append_once(path: str, marker: str, text_to_append: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if marker in text:
        return
    p.write_text(text.rstrip() + "\n\n" + text_to_append.strip() + "\n", encoding="utf-8")


def patch_goukaku_ui() -> None:
    path = "goukaku_ui.py"
    replace_once(
        path,
        "from dashboard_real_data_shadow import build_dashboard_real_data_shadow\n",
        "from dashboard_real_data_shadow import build_dashboard_real_data_shadow\nfrom pass_readiness import build_pass_readiness\nfrom learner_readiness_presentation import build_learner_readiness_presentation\n",
    )
    replace_once(path, "def build_dashboard(user_id=None):\n", "def build_dashboard(user_id=None, include_learner_navigation=False):\n")
    replace_once(
        path,
        '        "dashboard_real_data_shadow_enabled": False,\n        "dashboard_real_data_shadow": None,\n',
        '        "dashboard_real_data_shadow_enabled": False,\n        "dashboard_real_data_shadow": None,\n        "learner_navigation_enabled": False,\n        "learner_navigation": None,\n',
    )
    replace_once(
        path,
        "        if field_preview or overall_preview or shadow_preview or phase12_preview:\n            attempts = get_question_attempts(user_id)\n            evidence = build_field_evidence(attempts)\n        if field_preview or overall_preview or shadow_preview:\n            progress = build_field_progress(evidence)\n",
        "        if field_preview or overall_preview or shadow_preview or phase12_preview or include_learner_navigation:\n            attempts = get_question_attempts(user_id)\n            evidence = build_field_evidence(attempts)\n        if field_preview or overall_preview or shadow_preview or include_learner_navigation:\n            progress = build_field_progress(evidence)\n",
    )
    replace_once(
        path,
        '''        if shadow_preview:\n            legacy_recommended_field = (\n                dashboard["recommended_study"][0][0]\n                if dashboard["recommended_study"] else None\n            )\n            dashboard["dashboard_real_data_shadow_enabled"] = True\n            dashboard["dashboard_real_data_shadow"] = build_dashboard_real_data_shadow(\n                attempts,\n                evidence=evidence,\n                progress=progress,\n                legacy_overall_progress_percent=dashboard["overall_progress"],\n                legacy_weak_fields=dashboard["weak_fields"],\n                legacy_recommended_field=legacy_recommended_field,\n            )\n''',
        '''        shadow_result = None\n        if shadow_preview or include_learner_navigation:\n            legacy_recommended_field = (\n                dashboard["recommended_study"][0][0]\n                if dashboard["recommended_study"] else None\n            )\n            shadow_result = build_dashboard_real_data_shadow(\n                attempts,\n                evidence=evidence,\n                progress=progress,\n                legacy_overall_progress_percent=dashboard["overall_progress"],\n                legacy_weak_fields=dashboard["weak_fields"],\n                legacy_recommended_field=legacy_recommended_field,\n            )\n            if shadow_preview:\n                dashboard["dashboard_real_data_shadow_enabled"] = True\n                dashboard["dashboard_real_data_shadow"] = shadow_result\n        if include_learner_navigation:\n            readiness = build_pass_readiness(\n                attempts,\n                field_evidence=evidence,\n                progress=progress,\n            )\n            dashboard["learner_navigation_enabled"] = True\n            dashboard["learner_navigation"] = build_learner_readiness_presentation(\n                readiness, shadow_result\n            )\n''',
    )
    replace_once(
        path,
        '    dashboard = build_dashboard(user_id)\n    if user_id and dashboard["recommended_study"]:\n        recommended_name, recommended_count = dashboard["recommended_study"][0]\n        record_activity_event(\n            user_id,\n            "recommendation_plan",\n            {"field": recommended_name, "goal": recommended_count},\n        )\n',
        '''    dashboard = build_dashboard(user_id, include_learner_navigation=bool(user_id))\n    if user_id:\n        navigation = dashboard.get("learner_navigation") or {}\n        action = navigation.get("today_action") or {}\n        if action.get("field"):\n            record_activity_event(\n                user_id,\n                "recommendation_plan",\n                {\n                    "field": action["field"],\n                    "goal": action["count"],\n                    "learning_intent": action["learning_intent"],\n                    "reason_code": action["reason_code"],\n                    "source": "learner_navigation",\n                },\n            )\n        elif dashboard["recommended_study"]:\n            recommended_name, recommended_count = dashboard["recommended_study"][0]\n            record_activity_event(\n                user_id,\n                "recommendation_plan",\n                {"field": recommended_name, "goal": recommended_count},\n            )\n''',
    )


def patch_app() -> None:
    path = "app.py"
    replace_once(
        path,
        '''    current_recommendations = build_dashboard(user_id).get("recommended_study", [])\n    if (field_name, question_count) not in current_recommendations:\n        return {\n            "ok": False,\n            "message": "おすすめ内容が更新されました。画面を再読み込みしてください。",\n        }, 409\n\n    try:\n''',
        '''    source = str(payload.get("source", "")).strip()\n    if source == "learner_navigation":\n        dashboard = build_dashboard(user_id, include_learner_navigation=True)\n        action = ((dashboard.get("learner_navigation") or {}).get("today_action") or {})\n        expected = (\n            action.get("field"),\n            int(action.get("count") or 0),\n            action.get("learning_intent"),\n            action.get("reason_code"),\n        )\n        received = (\n            field_name,\n            question_count,\n            str(payload.get("intent", "")).strip(),\n            str(payload.get("reason", "")).strip(),\n        )\n        if received != expected:\n            return {\n                "ok": False,\n                "message": "おすすめ内容が更新されました。画面を再読み込みしてください。",\n            }, 409\n    else:\n        current_recommendations = build_dashboard(user_id).get("recommended_study", [])\n        if (field_name, question_count) not in current_recommendations:\n            return {\n                "ok": False,\n                "message": "おすすめ内容が更新されました。画面を再読み込みしてください。",\n            }, 409\n\n    try:\n''',
    )


def patch_template() -> None:
    path = "templates/goukaku/home.html"
    anchor = '  {% if read_only %}<div class="readonly-banner"><b>閲覧専用</b><span>保存済みの学習データを表示しています</span></div>{% endif %}\n'
    block = '''  {% if dashboard.learner_navigation_enabled and not read_only %}\n  {% set nav = dashboard.learner_navigation %}\n  <section class="learner-navigation" aria-label="今日の学習ナビ">\n    <article class="learner-current-card">\n      <span class="learner-nav-kicker">現在地</span>\n      <h2>{{ nav.headline }}</h2>\n      <p>{{ nav.summary }}</p>\n    </article>\n    <article class="learner-today-card">\n      <span class="learner-nav-kicker">今日やること</span>\n      {% if nav.today_action.field %}\n      <h2>{{ nav.today_action.field }}を{{ nav.today_action.count }}問</h2>\n      <p>{{ nav.today_action.reason }}</p>\n      {% if learner_preview %}\n      <button type="button" class="learner-nav-action learner-preview-inert" aria-disabled="true" tabindex="-1">{{ nav.today_action.button_label }}</button>\n      {% else %}\n      <button class="learner-nav-action recommend-challenge"\n        data-recommendation-start-url="{{ url_for('start_dashboard_recommendation') }}"\n        data-dashboard-token="{{ dashboard_token }}"\n        data-recommendation-field="{{ nav.today_action.field }}"\n        data-recommendation-count="{{ nav.today_action.count }}"\n        data-recommendation-source="learner_navigation"\n        data-recommendation-intent="{{ nav.today_action.learning_intent }}"\n        data-recommendation-reason="{{ nav.today_action.reason_code }}">{{ nav.today_action.button_label }}</button>\n      <p class="recommend-challenge-status" data-recommendation-status role="status" aria-live="polite"></p>\n      {% endif %}\n      {% else %}\n      <h2>まず5問から始めよう</h2><p>学習データが増えると、今日の優先分野が見えてきます。</p>\n      {% endif %}\n    </article>\n    {% if nav.attention_items %}\n    <article class="learner-attention-card">\n      <span class="learner-nav-kicker">注意が必要なところ</span>\n      <div class="learner-attention-list">{% for item in nav.attention_items %}<div><b>{{ item.field }}</b><span>{{ item.label }}</span><p>{{ item.message }}</p></div>{% endfor %}</div>\n    </article>\n    {% endif %}\n    <details class="learner-nav-details">\n      <summary>今の学習状況を詳しく見る</summary>\n      <div class="learner-nav-detail-grid">\n        <section><h3>できていること</h3>{% for item in nav.stable_areas %}<p><b>{{ item.field }}</b><br>{{ item.message }}</p>{% else %}<p>時間を空けても確認できた記録は、これから増えていきます。</p>{% endfor %}</section>\n        <section><h3>直していること</h3>{% for item in nav.repair_areas %}<p><b>{{ item.field }}</b><br>{{ item.message }}</p>{% else %}<p>今すぐ優先する修復項目は目立っていません。</p>{% endfor %}</section>\n        <section><h3>まだ確認できていないこと</h3>{% for item in nav.coverage_gaps %}<p><b>{{ item.field }}</b><br>{{ item.message }}</p>{% endfor %}</section>\n        <section><h3>次の確認</h3><p>{{ nav.retention_message }}</p><p>{{ nav.trial100_message }}</p></section>\n      </div>\n    </details>\n  </section>\n  {% endif %}\n'''
    replace_once(path, anchor, anchor + block)


def patch_js() -> None:
    path = "static/goukaku/goukaku.js"
    replace_once(
        path,
        '''    if (await liffReady) {\n      await window.liff.sendMessages([{\n        type: 'text',\n        text: button.dataset.recommendationLineCommand,\n      }]);\n      window.liff.closeWindow();\n      return;\n    }\n''',
        '''    const structuredNavigation = button.dataset.recommendationSource === 'learner_navigation';\n    if (!structuredNavigation && await liffReady) {\n      await window.liff.sendMessages([{\n        type: 'text',\n        text: button.dataset.recommendationLineCommand,\n      }]);\n      window.liff.closeWindow();\n      return;\n    }\n''',
    )
    replace_once(
        path,
        '''        field: button.dataset.recommendationField,\n        count: Number(button.dataset.recommendationCount),\n''',
        '''        field: button.dataset.recommendationField,\n        count: Number(button.dataset.recommendationCount),\n        source: button.dataset.recommendationSource || '',\n        intent: button.dataset.recommendationIntent || '',\n        reason: button.dataset.recommendationReason || '',\n''',
    )


def patch_css() -> None:
    append_once(
        "static/goukaku/goukaku.css",
        ".learner-navigation{",
        r'''
.learner-navigation{display:grid;gap:12px;margin:0 0 16px}.learner-navigation>article,.learner-nav-details{border-radius:18px;padding:16px;background:#fff;box-shadow:0 6px 20px rgba(27,66,48,.08);border:1px solid rgba(38,120,79,.12)}.learner-current-card{border-left:5px solid #32835b!important}.learner-nav-kicker{display:block;font-size:12px;font-weight:800;letter-spacing:.04em;color:#33765a;margin-bottom:5px}.learner-navigation h2{font-size:21px;line-height:1.35;margin:0 0 6px}.learner-navigation p{margin:0;line-height:1.55}.learner-today-card{background:linear-gradient(135deg,#f4fbf7,#fff)!important}.learner-nav-action{width:100%;margin-top:12px;padding:13px 16px;border:0;border-radius:999px;font-weight:800;font-size:16px;cursor:pointer}.learner-attention-list{display:grid;gap:9px}.learner-attention-list>div{padding:10px 0;border-top:1px solid rgba(0,0,0,.06)}.learner-attention-list>div:first-child{border-top:0}.learner-attention-list b{margin-right:8px}.learner-attention-list span{font-size:12px;font-weight:700}.learner-attention-list p{font-size:14px;margin-top:4px}.learner-nav-details summary{cursor:pointer;font-weight:800}.learner-nav-detail-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:14px}.learner-nav-detail-grid section{padding:12px;border-radius:12px;background:rgba(247,250,248,.9)}.learner-nav-detail-grid h3{font-size:15px;margin:0 0 8px}.learner-nav-detail-grid p{font-size:13px;margin:0 0 10px}.learner-nav-detail-grid p:last-child{margin-bottom:0}
@media(max-width:700px){.learner-navigation{gap:8px;margin-bottom:12px}.learner-navigation>article,.learner-nav-details{padding:13px;border-radius:15px}.learner-navigation h2{font-size:19px}.learner-navigation p{font-size:14px}.learner-nav-action{margin-top:9px;padding:12px}.learner-nav-detail-grid{grid-template-columns:1fr}.learner-attention-card{padding-top:11px!important;padding-bottom:11px!important}}
''',
    )


def main() -> int:
    patch_goukaku_ui()
    patch_app()
    patch_template()
    patch_js()
    patch_css()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
