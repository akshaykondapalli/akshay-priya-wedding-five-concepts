const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:900,height:260}});
await p.goto(process.argv[2]);await p.waitForTimeout(800);await p.screenshot({path:process.argv[3]});await b.close();})();
