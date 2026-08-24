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

const initializeFrame=frame=>{
  const syncFrame=()=>{
    fitFrame(frame);
    const doc=frame.contentDocument;
    if(!doc||doc.documentElement.dataset.siteFrameWired==='true')return;
    doc.documentElement.dataset.siteFrameWired='true';
    wireFrameLinks(frame);
    wireFrameScroll(frame);
    frame.contentWindow.addEventListener('resize',()=>fitFrame(frame));
  };
  frame.addEventListener('load',syncFrame);
  if(frame.contentDocument?.readyState==='complete'&&frame.contentDocument.location.href!=='about:blank')syncFrame();
};

frames.forEach(initializeFrame);
window.addEventListener('resize',()=>frames.forEach(fitFrame));
