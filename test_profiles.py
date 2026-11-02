import unittest,time
from profiles import profile
from live import Monitor
class Tests(unittest.TestCase):
 def test_known_models_and_aliases(self):
  for label in ('OM-3501A','om3501a',' OM 3501A '):self.assertEqual((profile(label)['full_scale_w'],profile(label)['controls_verified'],profile(label)['known']),(3500,True,True))
  for label in ('OM-4001A','OM4001A'):self.assertEqual((profile(label)['full_scale_w'],profile(label)['controls_verified'],profile(label)['known']),(5000,False,True));self.assertEqual((profile(label)['reflected_max_w'],profile(label)['input_max_w'],profile(label)['screen_ma_range']),(250,100,[-80,80]))
 def test_unknown_models_are_monitoring_only_on_default_scale(self):
  for label in ('OM-4001C','OM-2000A+','',None):self.assertEqual((profile(label)['full_scale_w'],profile(label)['controls_verified'],profile(label)['known']),(3500,False,False))
 def test_profile_is_a_copy(self):
  profile('OM-3501A')['full_scale_w']=1;self.assertEqual(profile('OM-3501A')['full_scale_w'],3500)
  profile('OM-4001A')['screen_ma_range'][0]=0;self.assertEqual(profile('OM-4001A')['screen_ma_range'],[-80,80])
  profile('zzz')['screen_ma_range'][0]=0;self.assertEqual(profile('zzz')['screen_ma_range'],[-60,60])
  profile('zzz')['full_scale_w']=1;self.assertEqual(profile('zzz')['full_scale_w'],3500)
 def test_4001a_vendor_style_marks_and_tube_labels(self):
  p=profile('OM-4001A');self.assertEqual(p['forward_ticks_w'][-1],4800);self.assertEqual(len(p['forward_ticks_w']),13);self.assertEqual(p['reflected_ticks_w'],[0,50,100,150,200,250]);self.assertEqual(p['input_ticks_w'][-1],90)
  self.assertEqual((p['tube_labels'],p['grid_separate'],p['screen_ma_tick_step']),(['f','b'],True,20))
  d=profile('OM-3501A');self.assertEqual((d['tube_labels'],d['grid_separate']),(['A','B'],False));self.assertNotIn('forward_ticks_w',d)
 def monitor(self,model):
  m=Monitor(simulate=True);m.settings['model']=model;now=time.monotonic()
  m.state={'connection':'Connected','_received':now,'status':'Standby','transmitting':False,'_field_times':{}};return m
 def test_4001a_controls_blocked_and_snapshot_carries_profile(self):
  m=self.monitor('OM-4001A')
  with self.assertRaisesRegex(ValueError,'Monitoring only'):m.command('toggle','request-4001a',expected_mode='Standby')
  p=m.snapshot()['model_profile'];self.assertEqual((p['full_scale_w'],p['controls_verified']),(5000,False))
 def test_3501a_controls_still_accepted(self):
  m=self.monitor('OM-3501A');m.command('toggle','request-3501a',expected_mode='Standby');self.assertTrue(m.controls.pending)
class GridSignTests(unittest.TestCase):
 def snapshot(self,model,**fields):
  m=Monitor(simulate=True);m.settings['model']=model;now=time.monotonic()
  m.state={'connection':'Connected','_received':now,'_field_times':{k:now for k in fields},**fields};return m.snapshot()
 def test_4001a_grid_b_is_shown_with_the_vendor_sign(self):
  s=self.snapshot('OM-4001A',grid_a_v=141.0,grid_b_v=141.0);self.assertEqual((s['grid_a_v'],s['grid_b_v']),(141.0,-141.0))
  self.assertEqual(self.snapshot('OM-4001A',grid_a_v=141.0,grid_b_v=-3.0)['grid_b_v'],3.0)
 def test_missing_or_other_models_are_not_flipped(self):
  self.assertIsNone(self.snapshot('OM-4001A',grid_a_v=141.0).get('grid_b_v'))
  s=self.snapshot('OM-3501A',grid_a_v=75.0,grid_b_v=150.0);self.assertEqual((s['grid_b_v'],s['grid_v']),(150.0,-75.0))
class HoldTests(unittest.TestCase):
 OLD=-20.0
 def snapshot(self,model,connection='Connected',**fields):
  m=Monitor(simulate=True);m.settings['model']=model;now=time.monotonic()
  m.state={'connection':connection,'_received':now if connection=='Connected' else now-10,'_field_times':{k:self.OLD for k in fields},**fields};return m.snapshot()
 def test_4001a_holds_old_slow_readings_while_connected_or_delayed(self):
  for connection in ('Connected','Stale'):
   s=self.snapshot('OM-4001A',connection,plate_v=3250.0,screen_v=19.0,heater_a_v=9.0,mains_v=242.0,temperature_c=31.0,frequency_khz=14078,grid_a_v=141.0)
   self.assertEqual((s['plate_v'],s['screen_v'],s['heater_a_v'],s['mains_v'],s['temperature_c'],s['frequency_khz'],s['grid_a_v']),(3250.0,19.0,9.0,242.0,31.0,14078,141.0),connection)
 def test_4001a_does_not_hold_rf_derived_values_or_after_disconnect(self):
  self.assertIsNone(self.snapshot('OM-4001A',screen_ma=12.0,plate_v=3250.0)['screen_ma'])
  s=self.snapshot('OM-4001A','Disconnected',plate_v=3250.0,frequency_khz=14078);self.assertIsNone(s['plate_v']);self.assertIsNone(s['frequency_khz'])
 def test_3501a_and_unknown_models_still_blank_old_readings(self):
  for model in ('OM-3501A','OM-9999'):
   s=self.snapshot(model,plate_v=3250.0,frequency_khz=14078);self.assertIsNone(s['plate_v']);self.assertIsNone(s['frequency_khz'])
 def test_fresh_readings_are_unchanged(self):
  m=Monitor(simulate=True);m.settings['model']='OM-3501A';now=time.monotonic()
  m.state={'connection':'Connected','_received':now,'_field_times':{'plate_v':now},'plate_v':3250.0};self.assertEqual(m.snapshot()['plate_v'],3250.0)
if __name__=='__main__':unittest.main()
