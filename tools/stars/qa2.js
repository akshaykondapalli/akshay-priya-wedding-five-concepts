const { chromium } = require('playwright');
const base='http://127.0.0.1:8931/stars/index.html';
const out='/home/claude/qa5/stars/';
(async()=>{
  const b=await chromium.launch(); const res={};
  for (const [name,vp,m] of [['android-412',{width:412,height:915},true],['tablet-820',{width:820,height:1180},true],['desktop-1440',{width:1440,height:900},false]]){
    const c=await b.newContext({viewport:vp,deviceScaleFactor:m?2:1,isMobile:m,hasTouch:m}); const p=await c.newPage(); const errs=[];
    p.on('console',x=>{if(x.type()==='error')errs.push(x.text())}); p.on('pageerror',e=>errs.push(e.message));
    await p.goto(base,{waitUntil:'networkidle'}); await p.waitForTimeout(1200);
    await p.screenshot({path:out+name+'-first.png'});
    await p.evaluate(()=>{const h=document.getElementById('hour');scrollTo(0,h.offsetTop+h.offsetHeight-innerHeight)}); await p.waitForTimeout(800);
    await p.screenshot({path:out+name+'-hour.png'});
    res[name]={errs,overflow:await p.evaluate(()=>document.documentElement.scrollWidth-innerWidth)}; await c.close();
  }
  // 360 overflow + reduced motion + menu + share/calendar/maps links
  const c=await b.newContext({viewport:{width:360,height:740},reducedMotion:'reduce',isMobile:true,hasTouch:true,deviceScaleFactor:2}); const p=await c.newPage(); const errs=[];
  p.on('console',x=>{if(x.type()==='error')errs.push(x.text())}); p.on('pageerror',e=>errs.push(e.message));
  await p.goto(base,{waitUntil:'networkidle'}); await p.waitForTimeout(600);
  res.rm={overflow360:await p.evaluate(()=>document.documentElement.scrollWidth-innerWidth)};
  await p.evaluate(()=>{const h=document.getElementById('hour');scrollTo(0,h.offsetTop)}); await p.waitForTimeout(400);
  res.rm.dialAtHour=await p.evaluate(()=>document.getElementById('dialTime').textContent);
  await p.screenshot({path:out+'rm-360-hour.png'});
  await p.click('#menuBtn'); await p.waitForTimeout(300); res.rm.menuOpen=await p.evaluate(()=>document.getElementById('menu').open);
  await p.screenshot({path:out+'rm-360-menu.png'});
  await p.keyboard.press('Escape'); res.rm.menuClosedByEsc=!(await p.evaluate(()=>document.getElementById('menu').open));
  await p.click('#menuBtn'); await p.click('#menu a[href="#details"]'); await p.waitForTimeout(400);
  res.rm.menuNavDetails=await p.evaluate(()=>Math.abs(document.getElementById('details').getBoundingClientRect().top)<5);
  const [dl]=await Promise.all([p.waitForEvent('download',{timeout:3000}).catch(()=>null),p.click('#ics')]);
  res.rm.icsDownload=dl?dl.suggestedFilename():null;
  if(dl){const fs=require('fs');const pth=await dl.path();res.rm.icsBody=fs.readFileSync(pth,'utf8').split('\r\n').filter(l=>/DTSTART|DTEND|SUMMARY|LOCATION/.test(l));}
  await c.grantPermissions?.(['clipboard-read','clipboard-write']).catch(()=>{});
  await p.click('#share'); await p.waitForTimeout(300); res.rm.shareMsg=await p.evaluate(()=>document.getElementById('shareMsg').textContent);
  res.rm.links=await p.evaluate(()=>({maps:document.querySelector('a[href*="google.com/maps"]').href,gcal:document.getElementById('gcal').href,back:document.querySelector('.back').getAttribute('href')}));
  // music toggle
  await p.click('#music'); await p.waitForTimeout(500); res.rm.musicPressed=await p.evaluate(()=>document.getElementById('music').getAttribute('aria-pressed')+' / '+document.querySelector('#music .lbl').textContent);
  await p.click('#music'); res.rm.musicOff=await p.evaluate(()=>document.getElementById('music').getAttribute('aria-pressed'));
  res.rm.errs=errs;
  // no-JS
  const c3=await b.newContext({viewport:{width:390,height:844},javaScriptEnabled:false}); const p3=await c3.newPage();
  await p3.goto(base,{waitUntil:'networkidle'}); res.nojs={text:(await p3.evaluate(()=>document.body.innerText)).includes('9:55 PM IST')};
  await p3.evaluate(()=>scrollTo(0,document.getElementById('invitation').offsetTop)); await p3.screenshot({path:out+'nojs-invitation.png'});
  console.log(JSON.stringify(res,null,1)); await b.close();
})();
