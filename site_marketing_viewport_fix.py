from __future__ import annotations

from flask import request


_STYLE = """<style id="marketing-viewport-fix-v06">
/* Real-browser fixes: open overlays independently of the page scroll position. */
.marketing-modal-overlay.is-open{display:flex!important;align-items:flex-start!important;justify-content:center!important;overflow-y:auto!important;overscroll-behavior:contain!important}
.marketing-modal-overlay.is-open>.marketing-modal-card{margin:0 auto!important;max-height:calc(100dvh - 32px)!important;scroll-margin-top:0!important}
/* Keep hash-based :target as a no-JS fallback. */
.marketing-modal-overlay:target{align-items:flex-start!important;justify-content:center!important;overflow-y:auto!important;overscroll-behavior:contain!important}
.marketing-modal-overlay:target>.marketing-modal-card{margin:0 auto!important;max-height:calc(100dvh - 32px)!important;scroll-margin-top:0!important}
/* The left bottom card headline must stay complete at PC widths. */
.brand-panel h2{font-size:15px!important;line-height:1.35!important;letter-spacing:-.035em!important;white-space:nowrap!important;overflow:visible!important}
@media(max-width:760px){
  .marketing-modal-overlay.is-open>.marketing-modal-card,.marketing-modal-overlay:target>.marketing-modal-card{max-height:calc(100dvh - 16px)!important}
}
</style>
<script id="marketing-viewport-fix-script-v06">
(function(){
  function resetPanel(panel){
    if(!panel) return;
    panel.scrollTop=0;
    var card=panel.querySelector('.marketing-modal-card');
    if(card) card.scrollTop=0;
  }
  function openPanel(panel){
    if(!panel) return;
    panel.classList.add('is-open');
    document.documentElement.classList.add('marketing-modal-open');
    document.body.style.overflow='hidden';
    requestAnimationFrame(function(){ resetPanel(panel); });
  }
  function closePanels(){
    document.querySelectorAll('.marketing-modal-overlay.is-open').forEach(function(panel){
      panel.classList.remove('is-open');
    });
    document.documentElement.classList.remove('marketing-modal-open');
    document.body.style.overflow='';
  }
  function bind(){
    var faqLink=document.querySelector('.marketing-contact-link');
    var lineLink=document.querySelector('.marketing-line-button');
    var faqPanel=document.getElementById('faq-all-panel');
    var linePanel=document.getElementById('line-start-panel');
    if(faqLink && faqPanel){
      faqLink.addEventListener('click',function(event){
        event.preventDefault();
        openPanel(faqPanel);
      });
    }
    if(lineLink && linePanel){
      lineLink.addEventListener('click',function(event){
        event.preventDefault();
        openPanel(linePanel);
      });
    }
    document.querySelectorAll('.marketing-modal-close').forEach(function(link){
      link.addEventListener('click',function(event){
        event.preventDefault();
        closePanels();
      });
    });
    document.querySelectorAll('.marketing-modal-overlay').forEach(function(panel){
      panel.addEventListener('click',function(event){
        if(event.target===panel) closePanels();
      });
    });
    document.addEventListener('keydown',function(event){
      if(event.key==='Escape') closePanels();
    });
  }
  function resetHashFallback(){
    if(location.hash!=="#faq-all-panel" && location.hash!=="#line-start-panel") return;
    requestAnimationFrame(function(){ resetPanel(document.querySelector(location.hash)); });
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',bind); else bind();
  window.addEventListener('hashchange', resetHashFallback);
  window.addEventListener('load', resetHashFallback);
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
        if 'id="marketing-viewport-fix-v06"' not in html:
            html = html.replace("</head>", _STYLE + "</head>", 1)
            response.set_data(html)
            response.headers["Content-Length"] = str(len(response.get_data()))
        return response
