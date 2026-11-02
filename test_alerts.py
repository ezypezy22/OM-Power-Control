import unittest,time
from decoder import Decoder,ALERT_NAMES
from controls import Controls
from live import Monitor,alert_age
class Tests(unittest.TestCase):
 def test_warning_and_second_limit_with_fragmentation(self):
  for token,kind,code in [(b'WG11;','warning',11),(b'FA4;','limit',4),(b'WG15;','warning',15)]:
   for cut in range(len(token)+1):
    d=Decoder();d.feed(token[:cut]);d.feed(token[cut:]);a=d.state['alert']
    self.assertEqual((a['kind'],a['code']),(kind,code));self.assertIn(ALERT_NAMES[code],a['text']);self.assertEqual(d.field_revisions['alert'],1)
 def test_unknown_alert_number_is_still_reported(self):
  d=Decoder();d.feed(b'WG99;');self.assertEqual(d.state['alert']['code'],99);self.assertIn('99',d.state['alert']['text'])
 def test_fault_tokens(self):
  for token,kind in [(b'HF;','hard_fault'),(b'HVF;','hv_fault'),(b'FERROR;','soft_start')]:
   d=Decoder();d.feed(token);self.assertEqual(d.state['alert']['kind'],kind)
  d=Decoder();d.feed(b'HF;HF;');self.assertEqual(d.field_revisions['alert'],2)
 def test_alert_does_not_change_operating_state_or_rf(self):
  d=Decoder();d.feed(b'ST1110- HEXBEAM;WG2;');self.assertEqual(d.state['status'],'Operate');self.assertFalse(d.state['transmitting'])
 def test_cooling_temperature_and_countdown(self):
  d=Decoder();d.feed(b'COON;CT52;');self.assertEqual((d.state['status'],d.state['cooling_temp_c']),('Cooling down',52))
  d.feed(b'CT47;');self.assertEqual(d.state['cooling_temp_c'],47)
  d.feed(b'CO30;');self.assertNotIn('cooling_temp_c',d.state);self.assertEqual(d.state['countdown'],30)
  d.feed(b'CT44;');self.assertNotIn('countdown',d.state)
  d.feed(b'PAOFF;');self.assertEqual(d.state['status'],'Off');self.assertNotIn('cooling_temp_c',d.state)
 def test_alert_expiry(self):
  base={'alert':{'kind':'warning','code':1,'text':'x'},'_field_times':{'alert':100.0}}
  self.assertIsNotNone(alert_age(base,110)[0]);self.assertIsNone(alert_age(base,131)[0])
  hf={'alert':{'kind':'hard_fault'},'_field_times':{'alert':100.0}};self.assertIsNotNone(alert_age(hf,104)[0]);self.assertIsNone(alert_age(hf,106)[0])
  hv={'alert':{'kind':'hv_fault'},'_field_times':{'alert':100.0}};self.assertIsNotNone(alert_age(hv,100000)[0])
  self.assertEqual(alert_age({},5),(None,None))
 def test_hard_fault_blocks_commands_but_not_tune_stop(self):
  now=time.monotonic();s={'connection':'Connected','_received':now,'status':'Operate','transmitting':False,'fault_active':True}
  for action in ('toggle','off','autotune'):
   with self.assertRaises(ValueError):Controls().request(action,'request-123',s)
  c=Controls();c.request('toggle','request-124',{**s,'fault_active':False});self.assertIsNone(c.take(s));self.assertIsNone(c.pending)
  t={**s,'transmitting':True,'autotune_phase':'tuning'};c=Controls();c.request('autotune-stop','request-125',t);self.assertEqual(c.take(t),b'8')
 def test_monitor_snapshot_and_control_state(self):
  m=Monitor(simulate=True);now=time.monotonic()
  m.state={'connection':'Connected','_received':now,'alert':{'kind':'hard_fault','code':None,'text':'t'},'_field_times':{'alert':now}}
  self.assertTrue(m.control_state()['fault_active']);self.assertEqual(m.snapshot()['alert']['kind'],'hard_fault')
  m.state['_field_times']['alert']=now-10;self.assertFalse(m.control_state()['fault_active']);self.assertIsNone(m.snapshot()['alert'])
class PositionTests(unittest.TestCase):
 def test_load_and_tune_percent(self):
  msg=b'LO1890;TU2550;'
  for cut in range(len(msg)+1):
   d=Decoder();d.feed(msg[:cut]);d.feed(msg[cut:]);self.assertAlmostEqual(d.state['load_pct'],63.0);self.assertAlmostEqual(d.state['tune_pct'],85.0);self.assertEqual(d.state['autotune_load_raw'],1890)
 def test_new_tune_clears_previous_positions(self):
  d=Decoder();d.feed(b'LO1890;TU2550;');d.feed(b'AUTO;');self.assertNotIn('load_pct',d.state);self.assertNotIn('tune_pct',d.state)
  d.feed(b'LO0;');self.assertEqual(d.state['load_pct'],0)
class PlacementTests(unittest.TestCase):
 def test_alert_banner_sits_directly_under_the_operating_state(self):
  from pathlib import Path
  html=Path(__file__).with_name('live.html').read_text(encoding='utf-8')
  state=html.index('id="operatingState"');banner=html.index('id="alertBanner"');power=html.index('FORWARD POWER')
  self.assertTrue(state<banner<power);self.assertEqual(html.count('id="alertBanner"'),1)
if __name__=='__main__':unittest.main()
