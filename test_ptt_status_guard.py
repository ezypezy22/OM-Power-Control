import unittest,time
from decoder import Decoder
from controls import Controls

class StatusPTTGuardTests(unittest.TestCase):
 def state(self,d):
  return {**d.state,'connection':'Connected','_received':time.monotonic(),'controls_verified':True}
 def test_ptt_status_blocks_new_command_after_prior_idle(self):
  for antenna in ('0','1','2','A','F'):
   d=Decoder();d.feed(('PTTOFF;ST'+antenna+'111- ANT;').encode())
   self.assertTrue(d.state['transmitting']);self.assertFalse(d.state['rf_idle_confirmed'])
   with self.assertRaises(ValueError):Controls().request('toggle','status-ptt-'+antenna,self.state(d),expected_mode='Operate')
 def test_ptt_status_cancels_queued_command(self):
  d=Decoder();d.feed(b'PTTOFF;ST1110- YAGI;');c=Controls()
  c.request('toggle','queued-status-ptt',self.state(d),expected_mode='Operate')
  d.feed(b'ST1111- YAGI;');self.assertIsNone(c.take(self.state(d)));self.assertIsNone(c.pending)
 def test_idle_status_does_not_clear_ptt_latch(self):
  d=Decoder();d.feed(b'ST1111- YAGI;ST1110- YAGI;')
  self.assertTrue(d.state['transmitting']);self.assertFalse(d.state['rf_idle_confirmed'])
  d.feed(b'PTTOFF;');self.assertFalse(d.state['transmitting']);self.assertTrue(d.state['rf_idle_confirmed'])
