import isolated_settings
import time,unittest
from unittest.mock import patch
from decoder import Decoder
from live import Monitor
from controls import Controls
from test_info import Amplifier,INFO_3501

class SafetyReviewTests(unittest.TestCase):
 def monitor(self,data=b'ST1100- ANT;PTTOFF;',age=0):
  d=Decoder();d.feed(data);now=time.monotonic();m=Monitor(simulate=True);m.settings['model']='OM-3501A'
  m.state={**d.state,'connection':'Connected','_received':now,'_field_times':{k:now-age for k in d.field_revisions}}
  return m
 def test_unsupported_reported_models_block_standalone_and_shared_controls(self):
  for model in ('OM4001C','OM2501A','OM2000A+'):
   for source in ('standalone','DXC'):
    for action,mode in (('toggle','Standby'),('on','Off'),('off','Standby')):
     m=self.monitor();m.state.update(status=mode,info={'model':model,'firmware':'03.42'})
     with self.assertRaisesRegex(ValueError,'Monitoring only'):m.command(action,'unknown-model-'+action,source=source)
     self.assertIsNone(m.controls.pending)
 def test_unsupported_model_arrival_cancels_already_queued_commands(self):
  for action,mode in (('toggle','Standby'),('on','Off'),('off','Standby')):
   m=self.monitor();m.state['status']=mode;m.command(action,'queued-model-'+action)
   m.state['info']={'model':'OM4001C','firmware':'03.42'}
   self.assertIsNone(m.controls.take(m.control_state()));self.assertIsNone(m.controls.pending)
 def test_hard_fault_stays_latched_with_fresh_unrelated_data(self):
  for source in ('standalone','DXC'):
   m=self.monitor(b'ST1100- ANT;PTTOFF;HF;WG11;',age=3600)
   self.assertTrue(m.control_state()['fault_active']);self.assertEqual(m.snapshot()['fault']['kind'],'hard_fault')
   with self.assertRaisesRegex(ValueError,'fault'):m.command('toggle','aged-fault-'+source,source=source)
 def test_aged_fault_cancels_queued_command(self):
  m=self.monitor();m.command('toggle','queued-fault')
  m.state['faults']={'hard_fault':{'kind':'hard_fault','text':'fault'}};m.state['_field_times']['fault:hard_fault']=time.monotonic()-3600
  self.assertIsNone(m.controls.take(m.control_state()));self.assertIsNone(m.controls.pending)
 def test_stop_remains_available_during_latched_fault(self):
  m=self.monitor(b'ST1110- ANT;PTTON;AUTO;AUTO:AUTOTUNE IN PROGRESS;HF;',age=3600)
  m.command('autotune-stop','stop-latched-fault');self.assertEqual(m.controls.take(m.control_state()),b'8')
 def test_all_valid_ptt_statuses_revoke_idle_even_when_fragmented(self):
  for antenna in '0123456789AF':
   for tuning in ('-','0','1'):
    wire=('ST'+antenna+'111'+tuning+' ANT;').encode()
    for cut in range(len(wire)+1):
     d=Decoder();d.feed(b'PTTOFF;');d.feed(wire[:cut]);d.feed(wire[cut:])
     self.assertTrue(d.state['transmitting']);self.assertFalse(d.state['rf_idle_confirmed'])
 def test_worker_cancels_queued_command_when_status_reports_ptt(self):
  def queue_then_ptt():
   m.command('toggle','worker-ptt-status',expected_mode='Standby');return b'ST1111- ANT;'
  m=Monitor(allow_hardware=True);m.settings.update(host='192.0.2.1',model='OM-3501A')
  amp=Amplifier(m,[b'ST1100- ANT;PTTOFF;',INFO_3501,queue_then_ptt,b'TE63;'])
  with patch('live.socket.create_connection',return_value=amp):m.run()
  self.assertNotIn(b'O',amp.sent);self.assertIsNone(m.controls.pending)
 def test_worker_cancels_queued_command_when_unknown_model_arrives(self):
  def queue_then_info():
   m.command('toggle','worker-unsupported',expected_mode='Standby');return b'INFO:1,2,0,03.42,1,OM4001C;'
  m=Monitor(allow_hardware=True);m.settings.update(host='192.0.2.1',model='OM-3501A')
  amp=Amplifier(m,[b'ST1100- ANT;PTTOFF;',queue_then_info,b'TE63;'])
  with patch('live.socket.create_connection',return_value=amp),patch('live.IDENTIFY_SECONDS',0):m.run()
  self.assertNotIn(b'O',amp.sent);self.assertIsNone(m.controls.pending)
if __name__=='__main__':unittest.main()
