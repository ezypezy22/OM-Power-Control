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
 const ready='Automatic tuning ready; operator supplies tuning RF';
 await refresh({autotune_phase:'waiting',control:{message:ready}});assert.equal(vm.runInContext('controlFeedback(lastState)',ctx),ready);
 await refresh({autotune_phase:'tuning',transmitting:true});assert.equal(node('commandMessage').textContent.includes(ready),false,'readiness ends when tuning starts');
 await refresh({autotune_phase:'succeeded',autotune_saved:true});assert.equal(node('atResultTitle').textContent,'SUCCESSFUL AUTOTUNE');assert.equal(node('commandMessage').textContent.includes(ready),false,'success popup does not leave readiness below it');
 await refresh({transmitting:false,rf_idle_confirmed:true});await node('autotuneDismiss').onclick();await refresh({});assert.equal(node('commandMessage').textContent.includes(ready),false,'dismissing success never restores stale readiness');
 await refresh({autotune_phase:'waiting',control:{message:ready}});assert.equal(vm.runInContext('controlFeedback(lastState)',ctx),ready,'next tune can show readiness');
 const warning='No command confirmation. It may have taken effect; no retry was sent. Reconnect to reassess.';
 await refresh({autotune_phase:'succeeded',control:{message:warning,uncertain:true}});assert.match(node('commandMessage').textContent,/uncertain/i,'uncertain warning preserved');assert.equal(vm.runInContext('controlFeedback(lastState)',ctx),warning);
 console.log('OM3501A readiness clears at tuning/success and stays cleared after dismissal; next tune and uncertainty preserved.');
})().catch(e=>{console.error(e);process.exitCode=1});
