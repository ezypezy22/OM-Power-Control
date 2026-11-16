import unittest,time
from unittest.mock import patch
from controls import Controls
class Tests(unittest.TestCase):
 def state(self,**kw):return {'connection':'Connected','_received':time.monotonic(),'status':'Standby','transmitting':False,**kw}
 def test_toggle_once_and_confirm(self):
  c=Controls();s=self.state();c.request('toggle','request-123',s);self.assertEqual(c.take(s),b'O');self.assertIsNone(c.take(s));c.observe(['TE63']);self.assertIsNotNone(c.pending);c.observe(['OPERATE']);self.assertIsNone(c.pending);c.request('toggle','request-123',s);self.assertIsNone(c.take(s))
 def test_no_retry_after_timeout(self):
  c=Controls();s=self.state();c.request('off','request-123',s);self.assertEqual(c.take(s),b'Z');c.pending['sent']-=6;c.tick();self.assertTrue(c.uncertain);self.assertIsNone(c.take(s))
  with self.assertRaises(ValueError):c.request('off','request-456',s)
 def test_power_confirmations(self):
  for action,token,wire,status in [('on','WA180',b'Y','Off'),('off','COON',b'Z','Standby')]:
   c=Controls();s=self.state(status=status);c.request(action,'request-123',s);self.assertEqual(c.take(s),wire);c.observe([token]);self.assertIsNone(c.pending);self.assertFalse(c.uncertain)
 def test_guards(self):
  for change in [{'transmitting':True},{'status':'Warming up'},{'status':'Cooling down'},{'connection':'Disconnected'},{'_received':time.monotonic()-5}]:
   c=Controls()
   with self.assertRaises(ValueError):c.request('toggle','request-123',self.state(**change))
 def test_power_off_is_allowed_while_warming_up_but_nothing_else(self):
  # The vendor client can cancel a warm-up with Power off; every other command stays blocked during the countdown.
  s=self.state(status='Warming up')
  for action in ('toggle','on'):
   with self.assertRaises(ValueError):Controls().request(action,'request-123',s)
  c=Controls();c.request('off','request-123',s);self.assertEqual(c.take(s),b'Z');c.observe(['COON']);self.assertIsNone(c.pending);self.assertFalse(c.uncertain)
  for action in ('toggle','on','off'):
   with self.assertRaises(ValueError):Controls().request(action,'request-123',self.state(status='Cooling down'))
  c=Controls();c.request('off','request-123',s);self.assertIsNone(c.take(self.state(status='Cooling down')));self.assertIsNone(c.pending)
 def test_transmit_after_queue(self):
  c=Controls();c.request('toggle','request-123',self.state());self.assertIsNone(c.take(self.state(transmitting=True)));self.assertIsNone(c.pending)
 def test_loss_never_requeues(self):
  c=Controls();s=self.state();c.request('toggle','request-123',s);c.take(s);c.lost();self.assertTrue(c.uncertain);self.assertIsNone(c.take(s))
 def test_expected_mode_request_and_dispatch(self):
  c=Controls()
  with self.assertRaises(ValueError):c.request('toggle','request-123',self.state(status='Operate'),'Standby')
  c.request('toggle','request-456',self.state(status='Standby'),'Standby')
  self.assertIsNone(c.take(self.state(status='Operate')));self.assertIsNone(c.pending)
 def test_expected_confirmation_and_mismatch(self):
  for start,reply,uncertain in [('Standby','OPERATE',False),('Operate','STBY',False),('Standby','STBY',True)]:
   c=Controls();s=self.state(status=start);c.request('toggle','request-123',s,start);self.assertEqual(c.take(s),b'O');c.observe([reply]);self.assertEqual(c.uncertain,uncertain);self.assertIsNone(c.pending)
 def test_stale_or_countdown_before_dispatch(self):
  for state in [self.state(_received=time.monotonic()-4),self.state(status='Cooling down')]:
   c=Controls();c.request('off','request-123',self.state());self.assertIsNone(c.take(state));self.assertIsNone(c.pending)
 def test_power_state_change_before_dispatch(self):
  for action,start,end in [('on','Off','Standby'),('off','Standby','Off'),('toggle','Standby','Off')]:
   c=Controls();c.request(action,'request-123',self.state(status=start));self.assertIsNone(c.take(self.state(status=end)));self.assertIsNone(c.pending)
 def test_redundant_power_actions(self):
  for action,status in [('on','Operate'),('on','Standby'),('on','On'),('off','Off')]:
   with self.assertRaises(ValueError):Controls().request(action,'request-123',self.state(status=status))
if __name__=='__main__':unittest.main()

class FanTests(unittest.TestCase):
 def state(self,**kw):return {'connection':'Connected','_received':time.monotonic(),'status':'Standby','transmitting':False,**kw}
 def test_fan_commands_send_the_documented_bytes_and_confirm_on_the_reply(self):
  for action,wire,token in [('fan-temp',b'3','BLOWER:TEMP'),('fan-ptt',b'4','BLOWER:PTT'),('fan-always',b'5','BLOWER:ALWAYS')]:
   c=Controls();s=self.state();c.request(action,'request-123',s);self.assertEqual(c.take(s),wire)
   c.observe(['BLOWER:'+('TEMP' if token!='BLOWER:TEMP' else 'PTT')]);self.assertIsNotNone(c.pending)   # a different mode is not a confirmation
   c.observe([token]);self.assertIsNone(c.pending);self.assertFalse(c.uncertain)
 def test_fan_is_blocked_while_transmitting_or_counting_down_and_never_with_an_expected_mode(self):
  for change in ({'transmitting':True},{'status':'Cooling down'},{'status':'Warming up'}):
   with self.assertRaises(ValueError):Controls().request('fan-ptt','request-123',self.state(**change))
  with self.assertRaises(ValueError):Controls().request('fan-ptt','request-123',self.state(),'Standby')
 def test_fan_follows_the_basic_controls_gate(self):
  with self.assertRaises(ValueError):Controls().request('fan-ptt','request-123',self.state(controls_verified=False))
  Controls().request('fan-ptt','request-123',self.state(controls_verified=False,basic_controls=True))

class RefusalTests(unittest.TestCase):
 def test_a_password_refusal_is_reported_not_left_uncertain(self):
  s={'connection':'Connected','_received':time.monotonic(),'status':'Operate','transmitting':False}
  c=Controls();c.request('autotune','request-123',s);self.assertEqual(c.take(s),b'L')
  c.observe(['TE60','BADPSW']);self.assertIsNone(c.pending);self.assertFalse(c.uncertain);self.assertIn('refused',c.message)

class UnlockTests(unittest.TestCase):
 def state(self):return {'connection':'Connected','_received':time.monotonic(),'status':'Operate','transmitting':False}
 def test_unlock_then_tune_sends_p_password_then_l_once_each(self):
  s=self.state();c=Controls();c.request('autotune','request-123',s,password='secret')
  self.assertEqual(c.take(s),b'P');self.assertFalse(c.last_secret);self.assertIsNone(c.take(s))
  c.observe(['ACK']);self.assertEqual(c.take(s),b'secret;');self.assertTrue(c.last_secret);self.assertIsNone(c.pending['password'])
  c.observe(['POK']);self.assertEqual(c.take(s),b'L');self.assertFalse(c.last_secret)
  c.observe(['AUTO']);s['autotune_phase']='entered';self.assertEqual(c.take(s),b'&')
 def test_rejected_or_unready_unlock_stops_without_retry_or_uncertainty(self):
  for first,second,text in (('NAK',None,'not ready'),('ACK','PSWFAIL','rejected')):
   s=self.state();c=Controls();c.request('autotune','request-123',s,password='bad');c.take(s);c.observe([first])
   if second:c.take(s);c.observe([second])
   self.assertIsNone(c.pending);self.assertFalse(c.uncertain);self.assertIn(text,c.message);self.assertIsNone(c.take(s))
 def test_password_is_validated_and_only_for_autotune(self):
  for bad in ('','x'*11,'a;b','sp ace','é'):
   with self.assertRaises(ValueError):Controls().request('autotune','request-123',self.state(),password=bad)
  with self.assertRaises(ValueError):Controls().request('toggle','request-123',self.state(),password='abc')

class RejectionCountTests(unittest.TestCase):
 def test_a_rejected_password_is_counted_for_the_page(self):
  s={'connection':'Connected','_received':time.monotonic(),'status':'Operate','transmitting':False}
  c=Controls();self.assertEqual(c.view()['password_rejections'],0)
  c.request('autotune','request-123',s,password='bad');c.take(s);c.observe(['ACK']);c.take(s);c.observe(['PSWFAIL'])
  self.assertEqual(c.view()['password_rejections'],1)
