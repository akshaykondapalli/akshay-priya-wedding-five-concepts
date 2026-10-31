const { chromium } = require('playwright');
const fs=require('fs');
const base='http://127.0.0.1:8931/stars/index.html';
const out='/home/claude/qa5/stars/';
(async()=>{
  const b=await chromium.launch();
  const errs=[];
  const ctx=await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:true,hasTouch:true});
  const p=await ctx.newPage();
  p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
  p.on('pageerror',e=>errs.push('pageerror '+e.message));
  p.on('requestfailed',r=>errs.push('failed '+r.url()));
  p.on('response',r=>{if(r.status()>=400)errs.push(r.status()+' '+r.url())});
  await p.goto(base,{waitUntil:'networkidle'});await p.waitForTimeout(1200);
  await p.screenshot({path:out+'m-arrival.png'});
  const shots=process.argv.slice(2).length?process.argv.slice(2):['story:0.35','hour:0','hour:0.5','hour:1','invitation:0','details:0','details:1','blessing:0','blessing:1'];
  for(const s of shots){
    const [id,f]=s.split(':');
    await p.evaluate(([id,f])=>{const el=document.getElementById(id);const top=el.offsetTop;const span=Math.max(0,el.offsetHeight-innerHeight);window.scrollTo(0,top+span*parseFloat(f)+(id!=='hour'?parseFloat(f)*0:0));},[id,f]);
    await p.waitForTimeout(700);
    await p.screenshot({path:out+`m-${id}-${f}.png`});
  }
  const ov=await p.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
  console.log('overflow390',ov,'errors',JSON.stringify(errs));
  await b.close();
})();
