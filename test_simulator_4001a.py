import isolated_settings  # noqa: F401  (keep tests off the real settings file)
import re,time,unittest
from unittest.mock import patch
from decoder import Decoder
from simulator import Simulated4001A,SimulatedAmplifier,simulator_for
from live import Monitor

class Clock:
 def __init__(self):self.now=1000.0
 def __call__(self):return self.now

def drain(sim):
 with sim.lock:data=bytes(sim.queue);sim.queue.clear()
 return data
def tokens(data):return [t for t in data.decode('ascii').split(';') if t]
def batch(data):return dict(re.findall(r'(IP|UP|UGA|UGB|US|UHA|UHB|UM|TE)(-?[\d.]+)',data.decode('ascii')))

class WireTests(unittest.TestCase):
 def setUp(self):self.clock=Clock();self.sim=Simulated4001A(warmup_seconds=20,cooldown_seconds=30,clock=self.clock)
 def ask(self,data):self.sim.sendall(data);return drain(self.sim)
 def test_session_status_and_frequency(self):
  self.assertEqual(self.ask(b'C'),b'CON;');self.assertEqual(self.ask(b'?'),b'ST0000- NO ANTENNA SWITCH;');self.assertEqual(self.ask(b'F'),b'FR18100;')
 def test_off_telemetry_matches_the_capture(self):
  self.assertEqual(batch(self.ask(b'#')),{'IP':'0','UP':'0','UGA':'139','UGB':'139','US':'0','UHA':'0.0','UHB':'0.0','UM':'244','TE':'68'})
  self.assertEqual(self.ask(b'#')[:0],b'')
 def test_poll_replies_are_throttled_to_about_every_3_2_seconds(self):
  self.assertIn(b'TE68',self.ask(b'#'))
  for _ in range(3):
   self.clock.now+=1.0
   if _<2:self.assertEqual(self.ask(b'#'),b'',_)
  self.clock.now+=0.3;self.assertIn(b'TE68',self.ask(b'#'))
 def test_no_ptt_noise_on_polls(self):
  self.assertNotIn(b'PTTOFF',self.ask(b'#')+self.ask(b'?'))
 def test_warm_up_sequence_and_values(self):
  self.assertEqual(self.ask(b'Y'),b'WA20;');seen=[]
  for _ in range(20):
   self.clock.now+=1.0;self.sim.sendall(b'?');seen+=tokens(drain(self.sim))
  waits=[int(t[2:]) for t in seen if re.fullmatch(r'WA\d+',t)]
  self.assertEqual(waits,list(range(19,0,-1)));i=seen.index('PTTOFF');self.assertEqual(seen[i:i+3],['PTTOFF','PAON','STBY'])
  self.assertEqual(tokens(self.ask(b'?'))[-1],'ST0100- NO ANTENNA SWITCH')
 def test_batch_values_through_warm_up_and_standby(self):
  self.ask(b'Y');self.clock.now+=10.0;mid=batch(self.ask(b'#'))
  self.assertEqual((mid['US'],mid['UGA'],mid['UGB']),('19','128','128'));self.assertTrue(1500<int(mid['UP'])<1700);self.assertTrue(8.0<=float(mid['UHA'])<=8.9)
  self.clock.now+=11.0;done=batch(self.ask(b'#'))
  self.assertEqual((done['US'],done['UGA'],done['UGB'],done['UHA']),('19','140','141','9.0'));self.assertTrue(3200<int(done['UP'])<3300)
 def test_operate_toggle_only_when_fully_on(self):
  self.assertEqual(self.ask(b'O'),b'');self.ask(b'Y');self.clock.now+=5;reply=self.ask(b'O');self.assertNotIn(b'OPERATE',reply);self.assertNotIn(b'STBY',reply)
  self.clock.now+=20;self.ask(b'?');self.assertEqual(self.ask(b'O'),b'OPERATE;');self.assertEqual(self.ask(b'?'),b'ST0110- NO ANTENNA SWITCH;');self.assertEqual(self.ask(b'O'),b'STBY;')
 def test_cooling_reports_temperature_then_off(self):
  self.sim.set_power(True);self.clock.now+=25;self.ask(b'?');self.assertEqual(self.sim.mode,'Standby')
  self.assertEqual(self.ask(b'Z'),b'COON;');temps=[]
  for _ in range(30):
   self.clock.now+=1.0;self.sim.sendall(b'?');temps+=[int(t[2:]) for t in tokens(drain(self.sim)) if re.fullmatch(r'CT\d+',t)]
  self.assertEqual(self.sim.mode,'Off');self.assertTrue(temps and all(t>40 for t in temps) and temps==sorted(temps,reverse=True))
 def test_off_commands_are_ignored_when_already_in_that_state(self):
  self.sim.set_power(False);self.assertEqual(self.sim.mode,'Off');self.ask(b'Z');self.assertEqual(self.sim.mode,'Off')
  self.sim.set_power(True);self.sim.set_power(True);self.assertEqual(self.sim.mode,'Warming up')
 def test_injected_alerts(self):
  for token in ('WG11','FA4','HF','HVF','FERROR','WG15'):self.sim.inject(token);self.assertEqual(drain(self.sim),token.encode()+b';')
  self.sim.inject('CLEAR');self.assertEqual(drain(self.sim),b'')
  for token in ('WG0','WG16','XX','HF;ST0000',None,11):
   with self.assertRaises(ValueError):self.sim.inject(token)
 def test_hard_fault_repeats_every_second_until_cleared(self):
  self.sim.inject('HF');self.assertEqual(drain(self.sim),b'HF;')
  for _ in range(3):
   self.clock.now+=1.0;self.sim.sendall(b'?');self.assertIn(b'HF;',drain(self.sim))
  self.clock.now+=0.4;self.sim.sendall(b'?');self.assertNotIn(b'HF;',drain(self.sim))
  self.sim.inject('CLEAR');self.assertEqual(drain(self.sim),b'')
  self.clock.now+=5.0;self.sim.sendall(b'?');self.assertNotIn(b'HF;',drain(self.sim))
  self.sim.inject('HVF');self.clock.now+=5.0;self.sim.sendall(b'?');self.assertEqual(drain(self.sim).count(b'HVF'),1)
 def test_decoder_follows_the_whole_session(self):
  d=Decoder();status=[]
  for command,advance in ((b'C',0),(b'?',0),(b'Y',0)):self.sim.sendall(command);d.feed(drain(self.sim));status.append(d.state.get('status'))
  for _ in range(21):
   self.clock.now+=1.0;self.sim.sendall(b'#');self.sim.sendall(b'?');d.feed(drain(self.sim));status.append(d.state['status'])
  self.assertEqual((status[1],status[2],status[-1]),('Off','Warming up','Standby'));self.assertIn('Warming up',status)
  self.assertEqual((d.state['grid_a_v'],d.state['grid_b_v'],d.state['screen_v']),(140.0,141.0,19.0))

class SelectionTests(unittest.TestCase):
 def test_simulator_for_model(self):
  for model in ('OM-4001A','om4001a'):self.assertIsInstance(simulator_for(model),Simulated4001A)
  for model in ('OM-3501A','OM-9999','',None):self.assertIs(type(simulator_for(model)),SimulatedAmplifier)
 def test_3501a_simulator_has_no_extra_controls(self):
  sim=SimulatedAmplifier();self.assertEqual(sim.FEATURES,())
  with self.assertRaises(ValueError):sim.set_power(True)
  with self.assertRaises(ValueError):sim.inject('HF')

class MonitorTests(unittest.TestCase):
 def wait(self,monitor,test,seconds=12):
  end=time.monotonic()+seconds
  while time.monotonic()<end:
   snap=monitor.snapshot()
   if test(snap):return snap
   time.sleep(.1)
  self.fail('condition not reached; last state: '+str({k:snap.get(k) for k in ('connection','status','screen_v','grid_a_v','error')}))
 def test_monitor_shows_off_warm_up_and_standby_with_the_vendor_display_rules(self):
  with patch('simulator.simulator_for',return_value=Simulated4001A(warmup_seconds=5)):
   monitor=Monitor(simulate=True);monitor.settings['model']='OM-4001A';monitor.connect()
   try:
    off=self.wait(monitor,lambda s:s['connection']=='Connected' and s.get('status')=='Off' and s.get('grid_a_v') is not None)
    self.assertEqual((off['grid_a_v'],off['grid_b_v']),(0.0,0.0));self.assertEqual(off['sim_features'],['power','alert']);self.assertEqual(off['model_profile']['name'],'OM-4001A')
    monitor.simulator.set_power(True)
    warm=self.wait(monitor,lambda s:s.get('status')=='Warming up' and s.get('screen_v') is not None);self.assertEqual(warm['screen_v'],0.0)
    ready=self.wait(monitor,lambda s:s.get('status')=='Standby' and s.get('screen_v')==19.0 and s.get('grid_b_v')==-141.0)
    self.assertEqual(ready['connection'],'Connected');self.assertEqual(ready['grid_b_v'],-141.0)
    monitor.simulator.inject('WG11');alert=self.wait(monitor,lambda s:s.get('alert'));self.assertEqual(alert['alert']['kind'],'warning')
   finally:monitor.disconnect();monitor.thread.join(4)
 def test_3501a_monitor_reports_no_simulator_extras(self):
  monitor=Monitor(simulate=True);monitor.settings['model']='OM-3501A';monitor.simulator=simulator_for('OM-3501A');self.assertEqual(monitor.snapshot()['sim_features'],[])
class ModelOptionTests(unittest.TestCase):
 def test_simulation_model_option(self):
  from live import simulation_model
  cur={'host':'simulation','port':10001,'model':'OM-3501A','callsign':'','auto_connect':False,'secondary_measurement':'reflected','share_dxc':False}
  self.assertEqual(simulation_model('om-4001a',False,cur),'OM-4001A');self.assertEqual(simulation_model('OM-3501A',False,cur),'OM-3501A')
  with self.assertRaises(ValueError):simulation_model('OM-4001A',True,cur)
  with self.assertRaises(ValueError):simulation_model('x'*41,False,cur)
  with self.assertRaises(ValueError):simulation_model('',False,cur)
 def test_extra_simulator_controls_stay_hidden_when_unsupported(self):
  from pathlib import Path
  html=Path(__file__).with_name('live.html').read_text(encoding='utf-8')
  # connectRow sets display:flex, which would override the hidden attribute without this rule.
  self.assertLess(html.index('.connectRow[hidden]{display:none}'),html.index('.connectRow{display:flex'))
  self.assertIn('id="simExtras" hidden',html)
if __name__=='__main__':unittest.main()

class FanTests(unittest.TestCase):
 def test_decoder_reads_the_fan_mode(self):
  d=Decoder();d.feed(b'BLOWER:PTT;');self.assertEqual(d.state['fan_mode'],'ptt')
  d.feed(b'BLOWER:ALWAYS;');self.assertEqual(d.state['fan_mode'],'always')
 def test_simulators_report_and_change_the_fan_mode(self):
  for sim in (Simulated4001A(),SimulatedAmplifier()):
   sim.sendall(b'2');self.assertEqual(drain(sim),b'BLOWER:TEMP;')
   sim.sendall(b'5');self.assertEqual(drain(sim),b'BLOWER:ALWAYS;')

class UnlockSimTests(unittest.TestCase):
 def test_tuning_needs_the_admin_password_on_the_4001a(self):
  sim=Simulated4001A(start='Operate');sim.sendall(b'L');self.assertEqual(drain(sim),b'BADPSW;')
  sim.sendall(b'P');self.assertEqual(drain(sim),b'\x06');sim.sendall(b'wrong;');self.assertEqual(drain(sim),b'PSWFAIL;')
  sim.sendall(b'P');drain(sim);sim.sendall(b'0000000000;');self.assertEqual(drain(sim),b'POK;')
  sim.sendall(b'L');self.assertEqual(drain(sim),b'AUTO;')
 def test_decoder_keeps_ack_bytes_apart_from_the_next_reply(self):
  d=Decoder();d.feed(b'\x06POK;');self.assertEqual(d.tokens,['ACK','POK'])

class TunePositionTests(unittest.TestCase):
 def test_positions_are_reported_while_tuning_and_decode_to_percent(self):
  for sim in (SimulatedAmplifier(),Simulated4001A(start='Operate')):
   sim.phase='tuning';sim.rf=True;sim.started=time.monotonic()-3;sim.sendall(b'#');d=Decoder();d.feed(drain(sim))
   self.assertTrue(10<d.state['tune_pct']<=20.1,d.state);self.assertTrue(30<d.state['load_pct']<=62.5,d.state)

class OffsetTests(unittest.TestCase):
 def test_offset_value_follows_the_vendor_scale(self):
  d=Decoder();d.feed(b'OT10;OT100;');self.assertEqual(d.state['autotune_offset_raw'],100)
  sim=SimulatedAmplifier();sim.phase='tuning';sim.rf=True;sim.started=time.monotonic()-3;sim.sendall(b'#');d=Decoder();d.feed(drain(sim))
  self.assertTrue(40<=d.state['autotune_offset_raw']<=100)

class LowInputPromptTests(unittest.TestCase):
 def test_increase_input_prompt_keeps_the_tune_waiting_and_reports_the_minimum(self):
  d=Decoder();d.feed(b'AUTO;AUTO:WAITING FOR INPUT POWER;')
  d.feed(b'AUTO:INCREASE INPUT POWER ABOVE 8.0W!;')
  self.assertEqual(d.state['autotune_phase'],'waiting');self.assertTrue(d.state['autotune_low_input']);self.assertEqual(d.state['autotune_min_input_w'],8.0)
  d.feed(b'AUTO:AUTOTUNE IN PROGRESS;');self.assertEqual(d.state['autotune_phase'],'tuning');self.assertFalse(d.state['autotune_low_input'])
 def test_prompt_is_accepted_as_the_reply_to_preparing_the_tune(self):
  from controls import Controls
  s={'connection':'Connected','_received':time.monotonic(),'status':'Operate','transmitting':False}
  c=Controls();c.request('autotune','request-123',s);c.take(s);c.observe(['AUTO']);s['autotune_phase']='entered';self.assertEqual(c.take(s),b'&')
  c.observe(['AUTO:INCREASE INPUT POWER ABOVE 8.0W!']);self.assertIsNone(c.pending);self.assertFalse(c.uncertain)

class TuningFlagTests(unittest.TestCase):
 def test_leaving_tuning_mode_ends_the_tune_in_the_decoder(self):
  d=Decoder();d.feed(b'AUTO;AUTO:WAITING FOR INPUT POWER;AUTO:AUTOTUNE IN PROGRESS;STOP;AUTO:AUTOTUNE ABORTED;')
  d.feed(b'ST01100 NO ANTENNA SWITCH;');self.assertEqual(d.state['autotune_phase'],'aborted');self.assertEqual(d.state['tune_mode'],'auto')
  d.feed(b'ST0110- NO ANTENNA SWITCH;');self.assertEqual(d.state['autotune_phase'],'cancelled');self.assertIsNone(d.state['tune_mode']);self.assertEqual(d.state['status'],'Operate')
 def test_4001a_simulator_exits_silently_like_the_real_amplifier(self):
  sim=Simulated4001A(start='Operate');sim.phase='aborted';sim.sendall(b'?');self.assertTrue(drain(sim).startswith(b'ST01100'))
  sim.sendall(b'*');self.assertEqual(drain(sim),b'PTTOFF;');sim.sendall(b'?');self.assertTrue(drain(sim).startswith(b'ST0110-'))

class StopEndToEndTests(unittest.TestCase):
 def test_stop_during_a_tune_leaves_tuning_mode_without_locking_controls(self):
  import admin_password,profiles,simulator
  with patch.dict(profiles.PROFILES['OM4001A'],{'controls_verified':True,'stop_exits_tuning':True}),patch.object(simulator,'simulator_for',lambda m:Simulated4001A(start='Operate')):
   admin_password.forget();m=Monitor(simulate=True);m.settings['model']='OM-4001A';m.settings['host']='simulation';m.connect()
   try:
    def wait(cond,limit=8):
     end=time.monotonic()+limit
     while time.monotonic()<end:
      s=m.snapshot()
      if cond(s):return s
      time.sleep(.05)
     self.fail('timed out: '+str({k:s.get(k) for k in ('status','autotune_phase','control')}))
    wait(lambda s:s.get('connection')=='Connected' and s.get('info') and s.get('status')=='Operate')
    m.command('autotune','request-tune-1',password='0000000000');wait(lambda s:s.get('autotune_phase')=='waiting' and not s['control']['pending'])
    m.simulator.set_input(True);wait(lambda s:s.get('autotune_phase')=='tuning')
    m.command('autotune-stop','request-stop-1');wait(lambda s:s['control']['pending_action']=='autotune-stop' and m.simulator.phase is None)
    m.simulator.set_input(False)   # the operator releases RF; the engine then asks for status
    s=wait(lambda s:not s['control']['pending'])
    self.assertEqual(s.get('autotune_phase'),'cancelled');self.assertFalse(s['control']['uncertain'])
    after=m.simulator.sent[m.simulator.sent.index(b'8'):]
    self.assertEqual([x for x in after if x in (b'8',b'*')],[b'8',b'*']);self.assertIn(b'?',after)
   finally:m.disconnect();m.thread and m.thread.join(3)
