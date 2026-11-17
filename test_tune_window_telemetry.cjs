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
 await refresh({autotune_phase:'waiting',frequency_khz:3573,screen_ma:12,transmitting:true,forward:100,reflected:4,swr:1.1});
 assert.equal(node('atFrequency').textContent,'3.573 MHz');assert.equal(node('atScreenGauge').hidden,false);assert.equal(node('atScreenValue').textContent,'12 mA');assert.equal(node('atScreenNeedle').hidden,false);assert.equal(node('atScreenNeedle').style.left,'60%');
 for(const swr of [1,1.5,2,3]){await refresh({swr});assert.equal(node('atSWR').textContent,swr.toFixed(1)+':1');assert.equal(node('atSWR').style.color,vm.runInContext('swrReadout(lastState).color',ctx))}
 assert.equal(node('atInput').textContent.includes('Band '),false);
 for(const model of ['OM4001A','OM2501A','UNKNOWN']){await refresh({info:{model}});assert.equal(node('atScreenGauge').hidden,true,model+' must omit Iscreen')}
 await refresh({info:{model:'OM3501A'},screen_ma:-30});assert.equal(node('atScreenGauge').hidden,false);assert.equal(node('atScreenNeedle').style.left,'25%');
 await refresh({age_seconds:20});assert.equal(node('atFrequency').textContent,'— MHz');assert.equal(node('atSWR').textContent,'—');assert.equal(node('atScreenValue').textContent,'— mA');assert.equal(node('atScreenNeedle').hidden,true);
 await refresh({age_seconds:0,transmitting:false});assert.equal(node('atSWR').textContent,'—');
 assert(html.indexOf('id="atScreenGauge"')>html.indexOf('id="atLoadVal"'));assert(html.indexOf('id="atScreenGauge"')<html.indexOf('id="atOutVal"'));
 console.log('Tuning window frequency/SWR, OM3501A-only Iscreen, model precedence, stale values and meter placement pass.');
})().catch(e=>{console.error(e);process.exitCode=1});
