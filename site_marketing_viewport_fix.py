from __future__ import annotations

from flask import request


_STYLE = """<style id="marketing-viewport-fix-v05">
/* Real-browser fixes: modal content must open from the top, never centered/cropped. */
.marketing-modal-overlay:target{align-items:flex-start!important;justify-content:center!important;overflow-y:auto!important;overscroll-behavior:contain!important}
.marketing-modal-overlay:target>.marketing-modal-card{margin:0 auto!important;max-height:calc(100dvh - 32px)!important;scroll-margin-top:0!important}
/* The left bottom card headline must stay complete at PC widths. */
.brand-panel h2{font-size:15px!important;line-height:1.35!important;letter-spacing:-.035em!important;white-space:nowrap!important;overflow:visible!important}
@media(max-width:760px){
  .marketing-modal-overlay:target>.marketing-modal-card{max-height:calc(100dvh - 16px)!important}
}
</style>
<script id="marketing-viewport-fix-script-v05">
(function(){
  function resetOpenPanel(){
    if(location.hash!=="#faq-all-panel" && location.hash!=="#line-start-panel") return;
    requestAnimationFrame(function(){
      var panel=document.querySelector(location.hash);
      if(!panel) return;
      panel.scrollTop=0;
      var card=panel.querySelector('.marketing-modal-card');
      if(card) card.scrollTop=0;
    });
  }
  window.addEventListener('hashchange', resetOpenPanel);
  window.addEventListener('load', resetOpenPanel);
})();
</script>"""


def install_site_marketing_viewport_fix(app) -> None:
    @app.after_request
    def apply_site_marketing_viewport_fix(response):
        if response.status_code != 200 or response.mimetype != "text/html" or response.direct_passthrough:
            return response
        if request.path not in {"/site/view/pc", "/site/view/mobile"}:
            return response
        html = response.get_data(as_text=True)
        if 'id="marketing-viewport-fix-v05"' not in html:
            html = html.replace("</head>", _STYLE + "</head>", 1)
            response.set_data(html)
            response.headers["Content-Length"] = str(len(response.get_data()))
        return response
