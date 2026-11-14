const assert=require('node:assert/strict'),{autotunePresentation}=require('./presentation.js');
const base={connection:'Connected',age_seconds:0,status:'Operate',settings:{model:'OM-3501A'},transmitting:false,autotune_phase:'idle'};
for(const guard of [{fault:{kind:'hard_fault',text:'Hard fault'}},{fault:{kind:'hv_fault',text:'Residual voltage'}},{model_pending:true}]){
 let p=autotunePresentation({...base,...guard});assert.equal(p.startDisabled,true);assert.ok(p.reason);
 p=autotunePresentation({...base,...guard,autotune_phase:'waiting'});assert.equal(p.exitDisabled,true);
 p=autotunePresentation({...base,...guard,autotune_phase:'tuning',transmitting:true});assert.equal(p.stopDisabled,!!guard.model_pending);
}
assert.equal(autotunePresentation(base).startDisabled,false);
assert.equal(autotunePresentation({...base,autotune_phase:'waiting'}).exitDisabled,false);
console.log('Fault/model wait inhibit Start and Exit; independently permitted Stop and healthy controls preserved.');
