const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:900}});
await p.goto('http://127.0.0.1:8931/stars/index.html',{waitUntil:'networkidle'});await p.waitForTimeout(800);
for (const mode of ['both','noglow','nosil','none']){
 await p.evaluate(m=>{document.querySelector('.glow').style.display=(m==='noglow'||m==='none')?'none':'';document.querySelector('.sil').style.display=(m==='nosil'||m==='none')?'none':'';},mode);
 await p.waitForTimeout(300);
 const buf=await p.screenshot({clip:{x:100,y:470,width:4,height:30}});
 require('fs').writeFileSync('/tmp/claude-0/-home-claude/2cf5e8b2-6ab2-523a-8d34-c01756c66623/scratchpad/probe-'+mode+'.png',buf);
}
await b.close();})();
