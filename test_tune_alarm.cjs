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
 await node('autotuneStart').onclick();await refresh({transmitting:true});assert.equal(beeps,0,'canceling initial confirmation stays silent');
 await refresh({autotune_phase:'waiting',transmitting:false});await refresh({autotune_phase:'cancelled'});await refresh({transmitting:true});assert.equal(beeps,0,'unused canceled tune cannot sound during later normal RF');
 await refresh({autotune_phase:'idle',transmitting:false});await refresh({autotune_phase:'waiting'});await refresh({autotune_phase:'tuning',transmitting:true});await refresh({autotune_phase:'succeeded'});assert.equal(beeps,1,'current completed tune with RF still on must alarm');
 await refresh({transmitting:null,rf_state_unknown:true});assert.equal(clears,0,'uncertain RF must not silence a current alarm');
 await refresh({connection:'Stale',transmitting:false,rf_state_unknown:false});await refresh({connection:'Connected',transmitting:true});assert.equal(clears,0,'stale idle data must not settle current tune');
 await refresh({transmitting:false});assert.equal(clears,1,'fresh RF off ends the alert');await refresh({transmitting:true});assert.equal(beeps,1,'old success cannot restart sound on later RF');assert.equal(node('atResult').dataset.stop,'false');
 await refresh({autotune_phase:'idle',transmitting:false});await refresh({autotune_phase:'waiting'});await refresh({autotune_phase:'tuning',transmitting:true});await refresh({autotune_phase:'aborted'});assert.equal(beeps,2,'new aborted tune with RF on must still alarm');
 await refresh({transmitting:false});await refresh({autotune_phase:'unknown',transmitting:true});assert.equal(beeps,2,'later terminal status changes must not rearm settled session');
 await refresh({autotune_phase:'idle',transmitting:false});await refresh({autotune_phase:'unknown',transmitting:true});assert.equal(beeps,2,'loading an old unknown result cannot arm audio');
 console.log('Auto-tune audio: canceled/old results stay silent on normal RF; current result alarms, unknown/stale RF holds, fresh RF-off settles, new tunes rearm.');
})().catch(e=>{console.error(e);process.exitCode=1});
