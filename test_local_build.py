import isolated_settings
import time,unittest
from unittest.mock import patch
import admin_password
from live import Monitor
class LocalBuildTests(unittest.TestCase):
 def monitor(self):
  m=Monitor(simulate=True);m.settings['model']='OM-4001A';m.state={'connection':'Connected','status':'Operate','transmitting':False,'_received':time.monotonic(),'info':{'model':'OM4001A','firmware':'03.42'}};return m
 def test_only_accepted_password_replaces_existing(self):
  m=self.monitor()
  with patch.object(admin_password,'save') as save:
   m.command('autotune','remember-test',password='newpass',remember=True);save.assert_not_called()
   self.assertEqual(m.controls.take(m.control_state()),b'P');m.observe_controls(['ACK']);self.assertEqual(m.controls.take(m.control_state()),b'newpass;');save.assert_not_called()
   m.observe_controls(['POK']);save.assert_called_once_with('newpass');self.assertNotIn('newpass',str(m.snapshot()))
 def test_wrong_typed_remember_never_saves_or_deletes_existing(self):
  m=self.monitor()
  with patch.object(admin_password,'save') as save,patch.object(admin_password,'forget') as forget:
   m.command('autotune','bad-remember',password='wrong',remember=True);m.controls.take(m.control_state());m.observe_controls(['ACK']);m.controls.take(m.control_state());m.observe_controls(['PSWFAIL'])
   save.assert_not_called();forget.assert_not_called();self.assertFalse(m.controls.rejected_stored);self.assertIsNone(m.controls.pending)
 def test_model_change_rechecks_password_requirement_before_wire_send(self):
  m=self.monitor();m.settings['model']='OM-3501A';m.state.pop('info');m.command('autotune','changed-model')
  m.state['info']={'model':'OM4001A','firmware':'03.42'};self.assertIsNone(m.controls.take(m.control_state()));self.assertIn('admin password',m.controls.message)
