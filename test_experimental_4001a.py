"""Portable protocol/model tests; no amplifier or RF is accessed."""
import isolated_settings
import time,unittest
from live import Monitor
from decoder import Decoder
from unittest.mock import patch
ACK='I accept unverified OM4001A controls and Auto Tune'
class Experimental4001ATests(unittest.TestCase):
 def monitor(self,**changes):
  m=Monitor(simulate=True);m.settings['model']='OM-4001A';d=Decoder();d.feed(b'ST1110- ANT;PTTOFF;')
  now=time.monotonic();m.state={**d.state,'connection':'Connected','_received':now,'_field_times':{k:now for k in d.field_revisions},'info':{'model':'OM4001A','firmware':'03.42'},**changes};return m
 def enable(self,m):m.configure_experimental({'enabled':True,'acknowledgement':ACK})
 def test_default_off_then_explicit_session_opt_in(self):
  m=self.monitor()
  for action in ('toggle','autotune'):
   with self.assertRaisesRegex(ValueError,'Monitoring only'):m.command(action,'default-'+action)
  self.enable(m);s=m.snapshot();self.assertTrue(s['experimental_4001a']);self.assertFalse(s['model_profile']['controls_verified']);self.assertTrue(s['model_profile']['experimental_tuning']);self.assertNotIn('experimental_4001a',m.settings)
  m.command('autotune','experiment-tune');self.assertEqual(m.controls.take(m.control_state()),b'L')
  m.controls.observe(['AUTO']);m.state['autotune_phase']='entered';self.assertEqual(m.controls.take(m.control_state()),b'&')
  m.controls.observe(['AUTO:WAITING FOR INPUT POWER']);self.assertIsNone(m.controls.pending)
 def test_explicit_ack_and_actual_model_firmware_required(self):
  for info in (None,{'model':'OM3501A','firmware':'03.42'},{'model':'OM4001C','firmware':'03.42'},{'model':'OM4001A','firmware':'03.15'},{'model':'OM4001A','firmware':'unknown'}):
   with self.subTest(info=info),self.assertRaises(ValueError):self.enable(self.monitor(info=info))
  with self.assertRaises(ValueError):self.monitor().configure_experimental({'enabled':True,'acknowledgement':'yes'})
 def test_enable_requires_fresh_idle_fault_free_state(self):
  for change in ({'transmitting':True},{'rf_idle_confirmed':False},{'_received':time.monotonic()-5},{'connection':'Disconnected'},{'faults':{'hard_fault':{'kind':'hard_fault','text':'HF'}}}):
   with self.subTest(change=change),self.assertRaises(ValueError):self.enable(self.monitor(**change))
 def test_restricted_modes_cannot_opt_in(self):
  for mode in ('read_only','mode_test','power_test','readiness_test','tune_test'):
   m=self.monitor();setattr(m,mode,True)
   with self.assertRaises(ValueError):self.enable(m)
 def test_queue_rechecks_rf_fault_freshness_model_and_permission(self):
  for change in ({'transmitting':True},{'_received':time.monotonic()-5},{'info':{'model':'OM4001C','firmware':'03.42'}},{'info':{'model':'OM4001A','firmware':'03.15'}},{'faults':{'hard_fault':{'kind':'hard_fault','text':'HF'}}}):
   m=self.monitor();self.enable(m);m.command('autotune','queued-tuning');m.state.update(change);self.assertIsNone(m.controls.take(m.control_state()))
 def test_guards_countdown_shared_controls_and_stop_preserved(self):
  m=self.monitor();self.enable(m)
  with self.assertRaises(ValueError):m.command('off','shared-experiment',source='DXC')
  for status in ('Warming up','Cooling down'):
   m.state['status']=status
   with self.assertRaises(ValueError):m.command('off','countdown-'+status)
  m.state.update(status='Operate',autotune_phase='tuning',transmitting=True,faults={'hard_fault':{'kind':'hard_fault','text':'HF'}})
  m.command('autotune-stop','experimental-stop');self.assertEqual(m.controls.take(m.control_state()),b'8')
 def test_cannot_revoke_permission_during_tuning_and_resets_on_disconnect(self):
  m=self.monitor();self.enable(m);m.state['autotune_phase']='waiting'
  with self.assertRaises(ValueError):m.configure_experimental({'enabled':False,'acknowledgement':''})
  m.disconnect();self.assertFalse(m.experimental_4001a);self.assertFalse(self.monitor().experimental_4001a)
 def test_reconnect_resets_and_changed_model_cancels(self):
  m=self.monitor();self.enable(m)
  with patch('live.threading.Thread') as thread:
   m.connect();self.assertFalse(m.experimental_4001a);thread.return_value.start.assert_called_once()
 def test_unknown_reply_never_succeeds_and_failure_never_retries(self):
  m=self.monitor();self.enable(m);m.command('autotune','unknown-tune');self.assertEqual(m.controls.take(m.control_state()),b'L');m.controls.observe(['BADPSW']);self.assertIsNone(m.controls.take(m.control_state()))
  d=Decoder();d.feed(b'AUTO;AUTO:UNRECOGNIZED;SAVE USER;');self.assertNotEqual(d.state['autotune_phase'],'succeeded');self.assertFalse(d.state['autotune_saved'])
