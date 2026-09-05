from __future__ import annotations

from flask import request


_STYLE = """<style id="marketing-viewport-fix-v09">
/* All modal-like dialogs in the public HP use the browser top layer and open from the viewport bottom. */
dialog.marketing-modal-overlay{width:100vw!important;height:100dvh!important;max-width:none!important;max-height:none!important;margin:0!important;border:0!important}
dialog.marketing-modal-overlay::backdrop{background:transparent!important}
.marketing-modal-overlay.is-open{display:flex!important;align-items:flex-end!important;justify-content:center!important;overflow-y:auto!important;overscroll-behavior:contain!important}
.marketing-modal-overlay.is-open>.marketing-modal-card{margin:0 auto 16px!important;max-height:calc(100dvh - 32px)!important;scroll-margin-bottom:0!important}
/* Hash fallback is also bottom-aligned. */
.marketing-modal-overlay:target{display:flex!important;align-items:flex-end!important;justify-content:center!important;overflow-y:auto!important;overscroll-behavior:contain!important}
.marketing-modal-overlay:target>.marketing-modal-card{margin:0 auto 16px!important;max-height:calc(100dvh - 32px)!important;scroll-margin-bottom:0!important}
/* The left bottom card headline must stay complete at PC widths. */
.brand-panel h2{font-size:15px!important;line-height:1.35!important;letter-spacing:-.035em!important;white-space:nowrap!important;overflow:visible!important}
@media(max-width:760px){
  .marketing-modal-overlay.is-open>.marketing-modal-card,.marketing-modal-overlay:target>.marketing-modal-card{margin-bottom:8px!important;max-height:calc(100dvh - 16px)!important}
}
</style>
<script id="marketing-viewport-fix-script-v09">
(function(){
  var savedScrollX=0;
  var savedScrollY=0;

  function resetPanel(panel){
    if(!panel) return;
    panel.scrollTop=0;
    var card=panel.querySelector('.marketing-modal-card');
    if(card) card.scrollTop=0;
  }

  function openPanel(panel){
    if(!panel) return;
    savedScrollX=window.scrollX;
    savedScrollY=window.scrollY;
    if(panel.parentElement!==document.body) document.body.appendChild(panel);
    if(typeof panel.showModal==='function' && !panel.open) panel.showModal();
    panel.classList.add('is-open');
    document.documentElement.classList.add('marketing-modal-open');
    document.body.style.overflow='hidden';
    requestAnimationFrame(function(){ resetPanel(panel); });
  }

  function closePanels(){
    document.querySelectorAll('.marketing-modal-overlay.is-open').forEach(function(panel){
      panel.classList.remove('is-open');
      if(typeof panel.close==='function' && panel.open) panel.close();
    });
    document.documentElement.classList.remove('marketing-modal-open');
    document.body.style.overflow='';
    window.scrollTo(savedScrollX,savedScrollY);
  }

  function panelFromLink(link){
    if(!link || !link.getAttribute) return null;
    var rawHref=link.getAttribute('href') || '';
    if(rawHref.indexOf('#')===-1) return null;
    var hash=rawHref.slice(rawHref.indexOf('#'));
    if(!hash || hash==='#') return null;
    var panel=document.querySelector(hash);
    if(!panel || !panel.matches('dialog.marketing-modal-overlay')) return null;
    return panel;
  }

  function bind(){
    document.addEventListener('click',function(event){
      var link=event.target.closest && event.target.closest('a[href*="#"]');
      var panel=panelFromLink(link);
      if(panel){
        event.preventDefault();
        openPanel(panel);
      }
    });

    document.querySelectorAll('.marketing-modal-close').forEach(function(link){
      link.addEventListener('click',function(event){
        event.preventDefault();
        event.stopPropagation();
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
    if(!location.hash) return;
    var panel=document.querySelector(location.hash);
    if(panel && panel.matches('dialog.marketing-modal-overlay')){
      requestAnimationFrame(function(){ resetPanel(panel); });
    }
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
        if 'id="marketing-viewport-fix-v09"' not in html:
            html = html.replace("</head>", _STYLE + "</head>", 1)
            response.set_data(html)
            response.headers["Content-Length"] = str(len(response.get_data()))
        return response
