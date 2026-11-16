import isolated_settings  # noqa: F401
import os,stat,time,unittest
from unittest.mock import patch
import admin_password,profiles,simulator
from live import Monitor

class StoreTests(unittest.TestCase):
 def setUp(self):admin_password.forget()
 tearDown=setUp
 def test_round_trip_is_private_and_validated(self):
  self.assertFalse(admin_password.exists());self.assertIsNone(admin_password.read())
  admin_password.save('hunter2');self.assertEqual(admin_password.read(),'hunter2');self.assertTrue(admin_password.exists())
  self.assertEqual(stat.S_IMODE(os.stat(admin_password.path()).st_mode),0o600)
  for bad in ('','x'*11,'a;b','sp ace','é'):
   with self.assertRaises(ValueError):admin_password.save(bad)
  self.assertEqual(admin_password.read(),'hunter2')
  admin_password.forget();admin_password.forget();self.assertIsNone(admin_password.read())
 def test_a_tampered_file_is_ignored(self):
  admin_password.path().write_text('has space;');self.assertIsNone(admin_password.read())
 def test_it_is_kept_beside_the_settings_not_inside_them(self):
  import settings
  self.assertEqual(admin_password.path().parent,settings.location().parent);self.assertNotEqual(admin_password.path(),settings.location())

class EngineTests(unittest.TestCase):
 def setUp(self):
  admin_password.forget()
  self.patches=[patch.dict(profiles.PROFILES['OM4001A'],{'controls_verified':True}),patch.object(simulator,'simulator_for',lambda m:simulator.Simulated4001A(start='Operate'))]
  for p in self.patches:p.start()
  self.m=Monitor(simulate=True);self.m.settings['model']='OM-4001A';self.m.settings['host']='simulation';self.m.connect()
  for _ in range(100):
   s=self.m.snapshot()
   if s.get('connection')=='Connected' and s.get('info') and s.get('status')=='Operate':break
   time.sleep(.1)
 def tearDown(self):
  self.m.disconnect();self.m.thread and self.m.thread.join(3);admin_password.forget()
  for p in self.patches:p.stop()
 def tune(self,**kw):
  self.m.command('autotune','request-%f'%time.time(),**kw)
  for _ in range(80):
   s=self.m.snapshot()
   if not s['control']['pending'] and s['control']['message']!='Command queued':break
   time.sleep(.1)
  return s
 def test_remember_then_use_saved_without_typing(self):
  s=self.tune(password='0000000000',remember=True)
  self.assertEqual(s['autotune_phase'],'waiting');self.assertTrue(s['admin_password_saved']);self.assertEqual(admin_password.read(),'0000000000')
  self.assertNotIn('0000000000',str(s))   # the snapshot only says whether one is saved
 def test_a_saved_password_unlocks_without_the_page_sending_it(self):
  admin_password.save('0000000000');s=self.tune(use_saved=True)
  self.assertEqual(s['autotune_phase'],'waiting');self.assertTrue(admin_password.exists())
 def test_use_saved_when_nothing_is_saved_asks_for_it(self):
  with self.assertRaises(ValueError):self.m.command('autotune','request-%f'%time.time(),use_saved=True)
 def test_a_wrong_remembered_password_is_forgotten_after_one_attempt(self):
  s=self.tune(password='wrong',remember=True)
  for _ in range(30):
   if not admin_password.exists():break
   time.sleep(.1)
  self.assertFalse(admin_password.exists());self.assertIn('rejected',self.m.snapshot()['control']['message'])
 def test_a_wrong_typed_password_leaves_a_good_saved_one_alone(self):
  admin_password.save('0000000000');self.tune(password='wrong');time.sleep(.3)
  self.assertEqual(admin_password.read(),'0000000000')
if __name__=='__main__':unittest.main()
