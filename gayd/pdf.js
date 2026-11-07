const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+process.argv[2],{waitUntil:'load'});
await p.pdf({path:process.argv[3],format:'A4',printBackground:true});
await p.setViewportSize({width:794,height:1123});await p.screenshot({path:process.argv[4],fullPage:true});
await b.close();})();
