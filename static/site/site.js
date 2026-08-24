const frames=[document.getElementById('pc-view'),document.getElementById('mobile-view')];

const fitFrame=frame=>{
  const doc=frame.contentDocument;
  if(!doc)return;
  const contentHeight=doc.documentElement.scrollHeight;
  if(frame.id==='mobile-view'){
    const stage=document.getElementById('mobile-stage');
    const scale=Math.min(1,document.documentElement.clientWidth/724);
    frame.style.width='724px';
    frame.style.height=`${contentHeight}px`;
    frame.style.transform=`scale(${scale})`;
    stage.style.height=`${contentHeight*scale}px`;
  }else{
    frame.style.height=`${contentHeight}px`;
  }
};

const wireFrameLinks=frame=>{
  const doc=frame.contentDocument;
  if(!doc)return;
  doc.addEventListener('click',event=>{
    const anchor=event.target.closest('a[href^="#"]');
    if(!anchor)return;
    const target=doc.querySelector(anchor.getAttribute('href'));
    if(!target)return;
    event.preventDefault();
    const scale=frame.getBoundingClientRect().width/frame.offsetWidth;
    const top=window.scrollY+frame.getBoundingClientRect().top+target.getBoundingClientRect().top*scale;
    window.scrollTo({top,behavior:'smooth'});
  });
};

const wireFrameScroll=frame=>{
  const doc=frame.contentDocument;
  if(!doc)return;
  doc.addEventListener('wheel',event=>{
    event.preventDefault();
    window.scrollBy({top:event.deltaY,left:event.deltaX});
  },{passive:false});
  let previousTouchY=null;
  doc.addEventListener('touchstart',event=>{
    previousTouchY=event.touches[0]?.clientY??null;
  },{passive:true});
  doc.addEventListener('touchmove',event=>{
    const currentTouchY=event.touches[0]?.clientY;
    if(previousTouchY===null||currentTouchY===undefined)return;
    event.preventDefault();
    window.scrollBy({top:previousTouchY-currentTouchY});
    previousTouchY=currentTouchY;
  },{passive:false});
  doc.addEventListener('touchend',()=>{previousTouchY=null},{passive:true});
};

const prepareFrameHtml=(frame,html)=>{
  const sourceDoc=new DOMParser().parseFromString(html,'text/html');
  const baseUrl=new URL(frame.dataset.base,window.location.origin);
  sourceDoc.querySelectorAll('[src]').forEach(element=>{
    const value=element.getAttribute('src');
    if(!value||/^(?:[a-z]+:|\/|#)/i.test(value))return;
    const resolved=new URL(value,baseUrl);
    element.setAttribute('src',`${resolved.pathname}${resolved.search}${resolved.hash}`);
  });
  sourceDoc.querySelectorAll('link[href]').forEach(element=>{
    const value=element.getAttribute('href');
    if(!value||/^(?:[a-z]+:|\/|#)/i.test(value))return;
    const resolved=new URL(value,baseUrl);
    element.setAttribute('href',`${resolved.pathname}${resolved.search}${resolved.hash}`);
  });
  const base=sourceDoc.createElement('base');
  base.href=frame.dataset.base;
  sourceDoc.head.prepend(base);
  const extraStylesheet=sourceDoc.createElement('link');
  extraStylesheet.rel='stylesheet';
  extraStylesheet.href=frame.dataset.extra;
  sourceDoc.head.append(extraStylesheet);
  return `<!doctype html>${sourceDoc.documentElement.outerHTML}`;
};

const loadFrame=async frame=>{
  try{
    const response=await fetch(frame.dataset.source,{cache:'no-store'});
    if(!response.ok)throw new Error(`source ${response.status}`);
    const html=prepareFrameHtml(frame,await response.text());
    frame.srcdoc=html;
    frame.addEventListener('load',()=>{
      fitFrame(frame);
      wireFrameLinks(frame);
      wireFrameScroll(frame);
      frame.contentWindow.addEventListener('resize',()=>fitFrame(frame));
    },{once:true});
  }catch(error){
    console.error('LicenseTown page load failed',error);
  }
};

frames.forEach(loadFrame);
window.addEventListener('resize',()=>frames.forEach(fitFrame));
