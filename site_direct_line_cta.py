from __future__ import annotations

import re
from html import escape

from flask import request

from site_marketing_refresh import _onboarding_url


DIRECT_CTA_STYLE = """<style id="site-direct-line-cta-v01">
.marketing-line-button{box-shadow:0 5px 14px rgba(7,131,41,.18)!important}
@media(max-width:760px){
  .marketing-mobile-free .marketing-line-start{display:flex!important;flex-direction:column!important;gap:8px!important}
  .marketing-mobile-free .marketing-line-start>div{order:1!important;width:100%!important}
  .marketing-mobile-free .marketing-line-qr{order:2!important;margin-top:7px!important}
  .marketing-mobile-free .marketing-line-button{display:block!important;width:min(360px,100%)!important;margin:0 auto!important;padding:14px 18px!important;font-size:16px!important}
  .marketing-mobile-free .marketing-qr-help{display:block!important;margin:7px 0 0!important;font-size:9px!important}
  .marketing-mobile-free .marketing-qr-help:before{content:'スマホで見ている方は、上のボタンからそのままLINEを開けます。';display:block;margin-bottom:5px;color:#087d2d;font-weight:700}
  .marketing-mobile-free .marketing-line-qr{width:104px!important;height:104px!important;opacity:.92}
}
</style>"""


def _apply_direct_line_cta(html: str, page_path: str) -> str:
    target = _onboarding_url()
    if not target:
        return html

    escaped_target = escape(target, quote=True)
    modal_href = re.escape(f'{page_path}#line-start-panel')
    html = re.sub(
        rf'<a class="marketing-line-button" href="{modal_href}">LINEで無料ではじめる　›</a>',
        f'<a class="marketing-line-button" href="{escaped_target}" target="_blank" rel="noopener noreferrer">LINEで無料ではじめる　›</a>',
        html,
        count=1,
    )
    html = re.sub(r'<style id="site-direct-line-cta-v01">.*?</style>', '', html, flags=re.DOTALL)
    return html.replace('</head>', DIRECT_CTA_STYLE + '</head>', 1)


def install_site_direct_line_cta(app) -> None:
    @app.after_request
    def apply_site_direct_line_cta(response):
        if response.status_code != 200 or response.mimetype != 'text/html' or response.direct_passthrough:
            return response
        if request.path not in {'/site/view/pc', '/site/view/mobile'}:
            return response
        html = response.get_data(as_text=True)
        response.set_data(_apply_direct_line_cta(html, request.path))
        response.headers['Content-Length'] = str(len(response.get_data()))
        return response
