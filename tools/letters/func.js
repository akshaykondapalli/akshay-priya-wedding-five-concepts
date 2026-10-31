const { chromium } = require('playwright');
const BASE='http://127.0.0.1:8931/letters/index.html';
(async()=>{
  const b=await chromium.launch(); const R={};
  // drag with mouse on desktop
  let c=await b.newContext({viewport:{width:1280,height:860}}); let p=await c.newPage();
  const errs=[]; p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>m.type()==='error'&&errs.push(m.text()));
  await p.goto(BASE,{waitUntil:'networkidle'});
  await p.click('#seal'); await p.waitForTimeout(2300);
  R.afterSeal=await p.evaluate(()=>document.querySelector('#ctlNum').textContent);
  const box=await p.locator('#souls').boundingBox();
  await p.mouse.move(box.x+box.width*0.6,box.y+box.height*0.5); await p.mouse.down();
  for(let k=1;k<=8;k++){await p.mouse.move(box.x+box.width*0.6-k*30,box.y+box.height*0.5,{steps:2});}
  await p.mouse.up(); await p.waitForTimeout(900);
  R.afterDragLeft=await p.evaluate(()=>document.querySelector('#ctlNum').textContent);
  // small drag springs back
  const b2=await p.locator('#connection').boundingBox();
  await p.mouse.move(b2.x+200,b2.y+300); await p.mouse.down(); await p.mouse.move(b2.x+170,b2.y+300,{steps:10}); await p.waitForTimeout(200); await p.mouse.up(); await p.waitForTimeout(900);
  R.afterSmallDrag=await p.evaluate(()=>document.querySelector('#ctlNum').textContent);
  await p.keyboard.press('ArrowRight'); await p.waitForTimeout(700);
  R.afterArrow=await p.evaluate(()=>document.querySelector('#ctlNum').textContent);
  await p.keyboard.press('ArrowLeft'); await p.waitForTimeout(700);
  R.afterArrowLeft=await p.evaluate(()=>document.querySelector('#ctlNum').textContent);
  await p.click('#menuBtn'); R.menuOpen=await p.evaluate(()=>!document.querySelector('#menu').hidden);
  await p.keyboard.press('Escape'); R.menuClosedEsc=await p.evaluate(()=>document.querySelector('#menu').hidden && document.activeElement.id);
  await p.click('#menuBtn'); await p.click('text=The itinerary'); await p.waitForTimeout(800);
  R.menuNav=await p.evaluate(()=>[document.querySelector('#ctlNum').textContent,location.hash]);
  R.gcal=await p.getAttribute('#gcal','href');
  const dl=p.waitForEvent('download',{timeout:3000}).catch(()=>null); await p.click('#icsBtn'); const d=await dl;
  if(d){const fs=require('fs');const path=await d.path();R.ics=fs.readFileSync(path,'utf8').split('\r\n').filter(l=>/DTSTART|DTEND|SUMMARY|LOCATION/.test(l));}
  R.mapsHref=await p.getAttribute('.itin-actions a.btn-ink','href');
  await c.grantPermissions(['clipboard-read','clipboard-write']);
  await p.evaluate(()=>window.atlasGo('blessing')); await p.waitForTimeout(500);
  await p.evaluate(()=>{delete navigator.share}); await p.click('#shareBtn'); await p.waitForTimeout(300);
  R.share=await p.textContent('#shareStatus');
  R.inertOthers=await p.evaluate(()=>[...document.querySelectorAll('.card')].filter(c=>c.inert).length);
  R.errs=errs; await c.close();
  // skip link from arrival
  c=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true}); p=await c.newPage();
  await p.goto(BASE,{waitUntil:'networkidle'}); await p.click('#skip'); await p.waitForTimeout(900);
  R.skip=await p.evaluate(()=>[document.querySelector('#ctlNum').textContent,document.activeElement.className]);
  // deep link
  await p.goto(BASE+'#details',{waitUntil:'networkidle'}); R.deep=await p.evaluate(()=>document.querySelector('#ctlNum').textContent);
  await c.close();
  // touch swipe via synthetic pointer events
  c=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true}); p=await c.newPage();
  await p.goto(BASE+'#souls',{waitUntil:'networkidle'});
  const cdp=await c.newCDPSession(p);
  const bb=await p.locator('#souls').boundingBox(); const y=bb.y+bb.height/2;
  await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:300,y}]});
  for(let k=1;k<=6;k++){await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:300-k*35,y}]});await p.waitForTimeout(16);}
  await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]}); await p.waitForTimeout(900);
  R.touchSwipe=await p.evaluate(()=>document.querySelector('#ctlNum').textContent);
  await c.close();
  // reduced motion
  c=await b.newContext({viewport:{width:390,height:844},reducedMotion:'reduce'}); p=await c.newPage();
  await p.goto(BASE,{waitUntil:'networkidle'}); await p.click('#openBtn'); await p.waitForTimeout(300);
  R.reducedOpen=await p.evaluate(()=>document.querySelector('#ctlNum').textContent);
  await p.screenshot({path:'/home/claude/qa5/letters/reduced-motion.png'}); await c.close();
  // no JS
  c=await b.newContext({viewport:{width:390,height:844},javaScriptEnabled:false}); p=await c.newPage();
  await p.goto(BASE,{waitUntil:'networkidle'});
  const t=await p.evaluate(()=>document.body.innerText);
  R.noJs=['Akshay','Priya','21 November 2026','8:00 PM IST','9:55 PM IST','Priyanka Convention','Nallajerla'].every(s=>t.includes(s));
  R.noJsOverflow=await p.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
  await p.screenshot({path:'/home/claude/qa5/letters/nojs.png',fullPage:false});
  R.forbidden=(t.match(/pellikoduku|lunch|morning|reception|haldi|sangeet|mehendi/i)||[null])[0];
  await c.close(); await b.close(); console.log(JSON.stringify(R,null,1));
})();
