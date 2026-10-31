const { chromium } = require('playwright');
const BASE='http://127.0.0.1:8931/letters/index.html';
const num=p=>p.evaluate(()=>document.querySelector('#ctlNum').textContent);
(async()=>{
  const b=await chromium.launch(); const R={};
  let c=await b.newContext({viewport:{width:1280,height:900}}); let p=await c.newPage();
  const errs=[]; p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>m.type()==='error'&&errs.push(m.text()));
  await p.goto(BASE,{waitUntil:'networkidle'});
  await p.click('#boxHit'); await p.waitForTimeout(3600); R.boxOpensAdvances=await num(p);
  const box=await p.locator('#souls').boundingBox();
  await p.mouse.move(box.x+box.width*0.6,box.y+box.height*0.5); await p.mouse.down();
  for(let k=1;k<=8;k++) await p.mouse.move(box.x+box.width*0.6-k*30,box.y+box.height*0.5,{steps:2});
  await p.mouse.up(); await p.waitForTimeout(900); R.dragAdvance=await num(p);
  const b2=await p.locator('#connection').boundingBox();
  await p.mouse.move(b2.x+200,b2.y+300); await p.mouse.down(); await p.mouse.move(b2.x+175,b2.y+300,{steps:10}); await p.waitForTimeout(200); await p.mouse.up(); await p.waitForTimeout(900);
  R.smallDragStays=await num(p);
  await p.keyboard.press('ArrowRight'); await p.waitForTimeout(800); await p.keyboard.press('ArrowRight'); await p.waitForTimeout(800);
  R.atInvite=await num(p);
  await p.keyboard.press('ArrowRight'); await p.waitForTimeout(2800);
  R.arrowOpensEnvelope=[await num(p), await p.evaluate(()=>document.querySelector('#invitation').classList.contains('open'))];
  await p.keyboard.press('ArrowRight'); await p.waitForTimeout(800); R.afterInvite=await num(p);
  await p.click('#menuBtn'); R.menuOpen=await p.evaluate(()=>!document.querySelector('#menu').hidden);
  await p.keyboard.press('Escape'); R.escFocus=await p.evaluate(()=>document.activeElement.id);
  R.gcal=(await p.getAttribute('#gcal','href')).includes('dates=20261121T143000Z%2F20261121T173000Z&ctz=Asia%2FKolkata');
  const dl=p.waitForEvent('download',{timeout:3000}).catch(()=>null); await p.click('#icsBtn'); const d=await dl;
  if(d){R.ics=require('fs').readFileSync(await d.path(),'utf8').split('\r\n').filter(l=>/DTSTART|DTEND|SUMMARY/.test(l));}
  await c.grantPermissions(['clipboard-read','clipboard-write']);
  await p.evaluate(()=>{delete navigator.share}); await p.click('.encl-actions .share-btn'); await p.waitForTimeout(300); R.share=await p.textContent('#shareStatus1');
  await p.keyboard.press('ArrowRight'); await p.waitForTimeout(800);
  await p.click('#againBtn'); await p.waitForTimeout(1300);
  R.again=[await num(p), await p.evaluate(()=>document.querySelector('#kbox').classList.contains('opened'))];
  R.errs=errs; await c.close();
  c=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true}); p=await c.newPage();
  await p.goto(BASE,{waitUntil:'networkidle'}); await p.click('#skip'); await p.waitForTimeout(3400);
  R.skip=[await num(p), await p.evaluate(()=>document.querySelector('#invitation').classList.contains('open')), await p.evaluate(()=>document.activeElement.className)];
  await p.goto(BASE+'#details',{waitUntil:'networkidle'}); R.deep=await num(p);
  const cdp=await c.newCDPSession(p); await p.goto(BASE+'#souls',{waitUntil:'networkidle'}); await p.waitForTimeout(300);
  const bb=await p.locator('#souls .sheet').boundingBox(); const y=bb.y+bb.height/2;
  await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:300,y}]});
  for(let k=1;k<=6;k++){await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:300-k*35,y}]});await p.waitForTimeout(16);}
  await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]}); await p.waitForTimeout(900);
  R.touchSwipe=await num(p); await c.close();
  c=await b.newContext({viewport:{width:390,height:844},reducedMotion:'reduce'}); p=await c.newPage();
  await p.goto(BASE,{waitUntil:'networkidle'}); await p.click('#openBtn'); await p.waitForTimeout(400); R.reduced=await num(p);
  await p.screenshot({path:'/home/claude/qa5/letters/w-reduced.png'}); await c.close();
  c=await b.newContext({viewport:{width:390,height:844},javaScriptEnabled:false}); p=await c.newPage();
  await p.goto(BASE,{waitUntil:'networkidle'}); const t=await p.evaluate(()=>document.body.innerText);
  R.noJsFacts=['Akshay','Priya','Saturday','21 November 2026','8:00 PM IST','9:55 PM IST','Priyanka Convention','Nallajerla','Andhra Pradesh'].every(s=>t.includes(s));
  R.noJsOverflow=await p.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
  R.forbidden=(t.match(/pellikoduku|lunch|morning|reception|haldi|sangeet|mehendi/i)||[null])[0];
  await p.screenshot({path:'/home/claude/qa5/letters/w-nojs.png',fullPage:true}); await c.close();
  for (const [w,h] of [[320,568],[360,640],[412,915],[820,1180]]){c=await b.newContext({viewport:{width:w,height:h}});p=await c.newPage();await p.goto(BASE,{waitUntil:'networkidle'});
    const res=[];for(const ch of ['arrival','souls','connection','moment','invitation','details','blessing']){await p.evaluate(x=>atlasGo(x),ch);await p.waitForTimeout(150);
      res.push(await p.evaluate(()=>{const a=document.querySelector('.card.is-active');const el=a.querySelector('.sheet-in,.inv-in');const ov=el?el.scrollHeight-el.clientHeight:0;return ov>4?a.id+':'+ov:null}))}
    R['innerOverflow'+w]=res.filter(Boolean); R['pageOverflow'+w]=await p.evaluate(()=>document.documentElement.scrollWidth-innerWidth); await c.close();}
  await b.close(); console.log(JSON.stringify(R,null,1));
})();
