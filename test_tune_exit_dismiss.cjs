const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const root=__dirname+'/';
const html=fs.readFileSync(root+'live.html','utf8'),script=html.split('<script>')[1].split('</script>')[0].replace('__PRESENTATION__',fs.readFileSync(root+'presentation.js','utf8'));
const nodes={},node=id=>nodes[id]??={options:[{value:'OM-3501A'}],textContent:'',value:'',checked:false,disabled:false,hidden:false,dataset:{},style:{},classList:{toggle(){},remove(){}},setAttribute(){},removeAttribute(){},showModal(){this.open=true},close(){this.open=false}};
let beeps=0,intervals=0,clears=0;class AudioContext{constructor(){this.state='running';this.currentTime=0}createOscillator(){return {frequency:{},connect(){},start(){beeps++},stop(){}}}createGain(){return {gain:{},connect(){}}}}
let state={connection:'Connected',status:'Operate',age_seconds:0,transmitting:false,autotune_phase:'idle',control:{},settings:{model:'OM-3501A',host:'simulation',port:10001},model_profile:{name:'OM-3501A',controls_verified:true}};
const ctx=vm.createContext({document:{getElementById:node,body:{classList:{toggle(){}}}},window:{AudioContext},localStorage:{getItem(){return null},setItem(){}},crypto:{randomUUID(){return 'alarm-check'}},setTimeout(){},setInterval(){intervals++;return intervals},clearInterval(){clears++},confirm(){return false},fetch:async()=>({ok:true,json:async()=>state})});
vm.runInContext(script,ctx);
(async()=>{
 const refresh=async change=>{state={...state,...change};await vm.runInContext('refresh()',ctx)};
 await new Promise(r=>setImmediate(r));
 await refresh({autotune_phase:'waiting',transmitting:false});assert.equal(node('autotuneBanner').hidden,false);
 await node('atExit').onclick();assert.equal(node('autotuneBanner').hidden,false,'waiting message remains until exit confirmation');
 await refresh({autotune_phase:'cancelled',control:{pending:true}});assert.equal(node('autotuneBanner').hidden,false,'pending exit is not treated as confirmed');
 await refresh({control:{pending:false}});assert.equal(node('autotuneBanner').hidden,true,'confirmed exit clears banner');assert.equal(node('autotuneDialog').open,false,'confirmed exit closes window');
 await refresh({transmitting:true});assert.equal(node('autotuneBanner').hidden,true);assert.equal(beeps,0,'later normal RF stays silent');
 await refresh({autotune_phase:'entered',transmitting:false});await refresh({autotune_phase:'waiting'});assert.equal(node('autotuneBanner').hidden,false,'a new tuning session restores its message');
 await node('atExit').onclick();await refresh({control:{uncertain:true}});assert.equal(node('autotuneBanner').hidden,false,'unconfirmed exit keeps warning visible');
 await refresh({autotune_phase:'cancelled',control:{uncertain:false}});assert.equal(node('autotuneBanner').hidden,false,'later status cannot silently clear an uncertain exit');
 console.log('Explicit Auto-tune Exit: waiting retained until confirmed; fresh idle confirmation closes banner/window; new tune restores; uncertain exit remains visible; later normal RF silent.');
})().catch(e=>{console.error(e);process.exitCode=1});
