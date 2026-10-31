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
 def monitor(self,model):
  m=Monitor(simulate=True);m.settings['model']=model;now=time.monotonic()
  m.state={'connection':'Connected','_received':now,'status':'Standby','transmitting':False,'_field_times':{}};return m
 def test_4001a_controls_blocked_and_snapshot_carries_profile(self):
  m=self.monitor('OM-4001A')
  with self.assertRaisesRegex(ValueError,'Monitoring only'):m.command('toggle','request-4001a',expected_mode='Standby')
  p=m.snapshot()['model_profile'];self.assertEqual((p['full_scale_w'],p['controls_verified']),(5000,False))
 def test_3501a_controls_still_accepted(self):
  m=self.monitor('OM-3501A');m.command('toggle','request-3501a',expected_mode='Standby');self.assertTrue(m.controls.pending)
if __name__=='__main__':unittest.main()
