"""Single outstanding, non-retrying commands owned by the socket worker."""
import re,time
COMMANDS={'toggle':(b'O',{'OPERATE','STBY'}),'on':(b'Y',{'PAON','WA'}),'off':(b'Z',{'PAOFF','COON','CO'}),'autotune':(b'L',{'AUTO'}),'autotune-exit':(b'*',{'AUTOESC','SAVE DEFAULT'}),'autotune-stop':(b'8',{'STOP','AUTO:AUTOTUNE ABORTED'}),'fan-temp':(b'3',{'BLOWER:TEMP'}),'fan-ptt':(b'4',{'BLOWER:PTT'}),'fan-always':(b'5',{'BLOWER:ALWAYS'})}
FAN_ACTIONS=('fan-temp','fan-ptt','fan-always')   # auxiliary fan mode (OM-2501A/3501A/4001A; the OM-4001C has no such command)
# Seconds to wait for confirmation. Stop and Exit move the tuning capacitors before the amplifier answers, so they get longer.
TIMEOUTS={'autotune-stop':15,'autotune-exit':15}
# A Stop or Exit confirmation that arrives after its window still settles the result, within this many seconds.
LATE_SECONDS=30
BASIC_ACTIONS=('toggle','on','off',*FAN_ACTIONS)
ACTIVE_TUNE={'entered','waiting','tuning','unknown','aborted'}
def tune_guard(action,state,stage=0):
 phase=state.get('autotune_phase')
 if action=='autotune':
  if state.get('status')!='Operate':return 'Select Operate before starting automatic tuning'
  if (stage==0 and phase in ACTIVE_TUNE) or (stage==1 and phase not in ('entered','waiting')):return 'Automatic tuning state changed; review the amplifier'
 elif action=='autotune-stop':
  if (stage==0 and phase!='tuning') or (stage==1 and phase not in ('aborted','tuning')):return 'Stop is verified only during active automatic tuning'
 elif action=='autotune-exit':
  if phase!='waiting' and not (phase=='aborted' and state.get('autotune_abort_origin') in ('rf_lost','stop')):return 'Exit is verified while waiting or after an RF-interrupted tune; check amplifier after Stop'
 elif phase in ACTIVE_TUNE:return 'Automatic tuning is active or unrecognized; exit the waiting state before other controls'
 return None

def countdown_blocks(status,action):
 """A warm-up or cool-down countdown blocks commands, except Power off while warming up (it cancels the warm-up,
 as the vendor client allows)."""
 return status=='Cooling down' or (status=='Warming up' and action!='off')

def blocked(state,action):
 """True when the model in force may not take this command: unverified models are monitoring only, except that
 a profile with basic_controls still allows Operate/Standby, power on/off and the auxiliary fan mode (never tuning)."""
 return state.get('controls_verified') is False and not (state.get('basic_controls') is True and action in BASIC_ACTIONS)

class Controls:
 def __init__(self):self.pending=None;self.message='';self.uncertain=False;self.seen=set();self.last_sent=float('-inf');self.last_secret=False;self.rejections=0;self.rejected_stored=False;self.late=None
 def request(self,action,key,state,expected_mode=None,password=None,stored=False):
  now=time.monotonic()
  if action not in COMMANDS:raise ValueError('Unknown control')
  if not isinstance(key,str) or not 8<=len(key)<=100:raise ValueError('Invalid request identifier')
  if password is not None and (action!='autotune' or not isinstance(password,str) or not 1<=len(password)<=10 or not all(33<=ord(c)<=126 and c!=';' for c in password)):raise ValueError('The admin password is 1 to 10 characters, without semicolons')
  if key in self.seen:return
  if self.pending or self.uncertain:raise ValueError('Wait for confirmation; reconnect after an unconfirmed result')
  if state.get('connection')!='Connected' or now-state.get('_received',0)>3:raise ValueError('Fresh amplifier communication is required')
  if blocked(state,action):raise ValueError('Monitoring only: controls are unverified for this model' if action in BASIC_ACTIONS else 'Monitoring only: tuning is not verified for this model')
  if state.get('model_pending'):raise ValueError('Waiting for the amplifier to report its model; try again in a moment')
  if state.get('fault_active') and action!='autotune-stop':raise ValueError('Amplifier fault active; commands are blocked until it clears')
  if state.get('transmitting') and action!='autotune-stop':raise ValueError('Stop transmission before changing amplifier state')
  reason=tune_guard(action,state)
  if reason:raise ValueError(reason)
  status=state.get('status','Unknown')
  if expected_mode is not None and (action!='toggle' or expected_mode not in ('Operate','Standby') or status!=expected_mode):raise ValueError('Amplifier mode changed; review the updated button before trying again')
  if countdown_blocks(status,action):raise ValueError('Wait for the amplifier countdown to finish')
  if action=='toggle' and status=='Off':raise ValueError('Turn the amplifier on first')
  if action=='on' and status in ('On','Operate','Standby'):raise ValueError('Amplifier is already on')
  if action=='off' and status=='Off':raise ValueError('Amplifier is already off')
  if action!='autotune-stop' and now-self.last_sent<2:raise ValueError('Please wait before sending another command')
  self.seen.add(key)
  if len(self.seen)>1000:raise ValueError('Reconnect before sending additional commands')
  self.pending={'id':key,'action':action,'password':password,'stored':bool(stored and password is not None),'unlock':0 if password is not None else None,'sent':None,'expected_mode':expected_mode,'exit_after_stop':action=='autotune-stop' and state.get('stop_exits_tuning') is True,'exit_after_rf_abort':action=='autotune-exit' and state.get('autotune_phase')=='aborted','exit_abort_origin':state.get('autotune_abort_origin') if action=='autotune-exit' and state.get('autotune_phase')=='aborted' else None};self.message='Command queued'
 def take(self,state):
  if not self.pending or self.pending['sent'] is not None:return None
  reason=None
  # Recheck the model in force right before sending: an INFO reply that arrived after the command
  # was queued may have selected a monitoring-only profile.
  if blocked(state,self.pending['action']):reason='the amplifier reported a model whose controls are unverified (monitoring only)'
  elif state.get('model_pending'):reason='the amplifier has not reported its model yet'
  elif state.get('fault_active') and self.pending['action']!='autotune-stop':reason='amplifier fault is active'
  elif state.get('transmitting') and self.pending['action']!='autotune-stop':reason='amplifier is transmitting'
  elif state.get('connection')!='Connected' or time.monotonic()-state.get('_received',0)>3:reason='fresh amplifier data is unavailable'
  elif countdown_blocks(state.get('status'),self.pending['action']):reason='amplifier countdown is active'
  elif self.pending['action']=='on' and state.get('status') in ('On','Operate','Standby'):reason='amplifier is already on'
  elif self.pending['action']=='off' and state.get('status')=='Off':reason='amplifier is already off'
  elif self.pending['action']=='toggle' and state.get('status')=='Off':reason='amplifier is off'
  elif self.pending.get('expected_mode') and state.get('status')!=self.pending['expected_mode']:reason='amplifier mode changed'
  if not reason and self.pending['action']=='autotune-exit' and self.pending.get('exit_abort_origin') and state.get('autotune_abort_origin')!=self.pending['exit_abort_origin']:reason='tuning abort state changed'
  if not reason:reason=tune_guard(self.pending['action'],state,self.pending.get('stage',0))
  if reason:
   self.pending=None;self.message='Command cancelled: '+reason;return None
  self.pending['ever_sent']=True;self.pending['sent']=time.monotonic();self.last_sent=self.pending['sent'];self.message='Sent once; waiting for amplifier confirmation'
  self.last_secret=False
  if self.pending['action']=='autotune' and self.pending.get('unlock') in (0,1):
   # Admin unlock before tuning (vendor protocol): P, wait for 06H, then the password ending with ';', wait for POK;.
   if self.pending['unlock']==0:self.message='Unlocking tuning: waiting for the amplifier to accept the password step';return b'P'
   secret=self.pending['password'];self.pending['password']=None;self.last_secret=True;self.message='Password sent once; waiting for the amplifier'
   return secret.encode('ascii')+b';'
  if self.pending['action']=='autotune-stop' and self.pending.get('stage')==1:return b'*'   # leave tuning mode after the stop
  return b'&' if self.pending['action']=='autotune' and self.pending.get('stage')==1 else COMMANDS[self.pending['action']][0]
 NOT_TUNING=re.compile(r'ST[0-9AF]\d{3}-.*')
 @classmethod
 def _confirms(cls,p,tokens):
  """A reply that settles Stop or Exit. Leaving tuning mode, shown by a status whose tuning flag is '-', also counts:
  the OM-4001A answers Exit with PTTOFF only (2026-11-16 trace), never AUTOESC or SAVE."""
  leaving=p['action']=='autotune-exit' or (p['action']=='autotune-stop' and p.get('stage')==1)
  if leaving and any(cls.NOT_TUNING.fullmatch(t) for t in tokens):return True
  return any(t in cls._wanted(p) for t in tokens)
 def wants_status(self):
  """True while an exit from tuning mode awaits confirmation: the engine then asks for status ('?', allowed at any time)."""
  now=time.monotonic();p=self.pending
  if p and p['sent'] is not None and now-p['sent']>=1 and (p['action']=='autotune-exit' or (p['action']=='autotune-stop' and p.get('stage')==1)):return True
  return bool(self.uncertain and self.late and now<self.late['until'] and (self.late['pending']['action']=='autotune-exit' or self.late['pending'].get('stage')==1))
 @staticmethod
 def _wanted(p):
  if p['action']=='autotune-stop' and p.get('stage')==1:return {'AUTOESC','SAVE USER','SAVE DEFAULT'}
  if p['action']=='autotune-exit':return {'SAVE USER','SAVE DEFAULT'} if p.get('exit_abort_origin')=='stop' else {'SAVE DEFAULT'} if p.get('exit_after_rf_abort') else {'AUTOESC'}
  return COMMANDS[p['action']][1]
 def observe(self,tokens):
  if not self.pending and self.uncertain and self.late and time.monotonic()<self.late['until'] and self._confirms(self.late['pending'],tokens):
   # The amplifier did confirm, only late (it was still moving the capacitors): the result is known after all.
   action=self.late['pending']['action'];self.late=None;self.uncertain=False
   self.message={'autotune-stop':'Auto-tune stop confirmed by amplifier (late); stop RF manually','autotune-exit':'Automatic tuning exit confirmed by amplifier (late)'}[action];return
  if not self.pending or self.pending['sent'] is None:return
  action=self.pending['action']
  if action=='autotune' and self.pending.get('unlock') in (0,1):
   if self.pending['unlock']==0:
    if 'NAK' in tokens:self.pending=None;self.message='Amplifier is not ready for the admin password. No retry was sent.'
    elif 'ACK' in tokens:self.pending.update(unlock=1,sent=None);self.message='Amplifier ready for the admin password'
   elif 'PSWFAIL' in tokens:self.rejected_stored=bool(self.pending.get('stored'));self.pending=None;self.rejections+=1;self.message='Amplifier rejected the admin password. No retry was sent.'+(' The saved password was removed; enter it again.' if self.rejected_stored else '')
   elif 'POK' in tokens:self.pending.update(unlock=2,sent=None);self.message='Admin mode unlocked; entering automatic tuning'
   return
  if action in ('autotune','autotune-exit','autotune-stop') and 'BADPSW' in tokens:
   # The amplifier refused the command: the outcome is known, nothing took effect, so this is not an uncertain result.
   self.pending=None;self.message='Amplifier refused the command (admin password required before tuning). No retry was sent.';return
  if action=='autotune':
   if self.pending.get('stage',0)==0 and 'AUTO' in tokens:
    self.pending.update(stage=1,sent=None);self.message='Automatic mode acknowledged; preparing tuning';return
   if self.pending.get('stage')==1 and ('AUTO:WAITING FOR INPUT POWER' in tokens or any(t.startswith('AUTO:INCREASE INPUT POWER ABOVE') for t in tokens)):
    self.pending=None;self.message='Automatic tuning ready; operator supplies tuning RF';return
   if any(t.startswith('AUTO') for t in tokens):
    self.pending=None;self.uncertain=True;self.message='Unexpected automatic-tuning response. Check amplifier; no retry was sent.'
   return
  if action=='autotune-stop':
   if self.pending.get('stage',0)==0 and any(t in COMMANDS['autotune-stop'][1] for t in tokens) and self.pending.get('exit_after_stop'):
    self.pending.update(stage=1,sent=None);self.message='Auto-tune stopped by amplifier; leaving tuning mode';return
   if self.pending.get('stage')==1:
    if self._confirms(self.pending,tokens):self.pending=None;self.message='Auto-tune stopped and tuning mode exited; stop RF manually'
    return
  wanted=self._wanted(self.pending)
  if (action=='autotune-exit' and self._confirms(self.pending,tokens)) or any(t in wanted or (t.startswith('WA') and 'WA' in wanted and t[2:].isdigit()) or (t.startswith('CO') and 'CO' in wanted and t[2:].isdigit()) for t in tokens):
   action=self.pending['action']
   expected=self.pending.get('expected_mode')
   if action=='toggle' and expected:
    target='STBY' if expected=='Operate' else 'OPERATE'
    mode_tokens=[t for t in tokens if t in ('STBY','OPERATE')]
    if not mode_tokens or mode_tokens[-1]!=target:
     self.pending=None;self.uncertain=True;self.message='Amplifier reported a different mode than requested. No retry was sent.';return
   defaults=action=='autotune-exit' and self.pending.get('exit_after_rf_abort')
   stopped_saved=defaults and self.pending.get('exit_abort_origin')=='stop' and 'SAVE USER' in tokens
   self.pending=None;self.message={'toggle':'Operating mode confirmed by amplifier','on':'Power-on accepted by amplifier','off':'Shutdown accepted by amplifier','autotune-exit':'Automatic tuning exit confirmed','autotune-stop':'Auto-tune stopped by amplifier; stop RF manually','fan-temp':'Auxiliary fan set to temperature control','fan-ptt':'Auxiliary fan set to PTT control','fan-always':'Auxiliary fan set to always on'}[action]
   if defaults:self.message='Stopped tune exited; amplifier reported user settings saved, not successful tuning' if stopped_saved else 'Auto-tune exited; amplifier reported default settings saved'
 def tick(self):
  if self.pending and self.pending['sent'] is not None and time.monotonic()-self.pending['sent']>TIMEOUTS.get(self.pending['action'],5):
   if self.pending['action'] in TIMEOUTS:self.late={'pending':self.pending,'until':time.monotonic()+LATE_SECONDS}
   self.pending=None;self.uncertain=True;self.message='No command confirmation. It may have taken effect; no retry was sent. Reconnect to reassess.'
 def lost(self):
  if self.pending:
   sent=self.pending.get('ever_sent',self.pending['sent'] is not None);self.pending=None;self.uncertain=sent;self.message='Connection lost; command result unknown. No retry was sent.' if sent else 'Unsent command cancelled'
 def view(self):return {'pending':self.pending is not None,'pending_action':self.pending['action'] if self.pending else None,'cooldown_remaining':max(0,round(2-(time.monotonic()-self.last_sent),2)),'uncertain':self.uncertain,'password_rejections':self.rejections,'message':self.message}
