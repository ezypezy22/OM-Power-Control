"""Per-model display and control profiles. The model name selects limits; it never selects a protocol."""
import copy,re

# controls_verified: Operate/Standby, power and auto-tune were validated on hardware for this model.
PROFILES={
 'OM3501A':{'tube_labels':['A','B'],'grid_separate':False,'grid_b_sign':1,'hold_slow_readings':False,'screen_v_zero_while_warming':False,'fresh_seconds':3,'grid_zero_when_off':False,'name':'OM-3501A','full_scale_w':3500,'reflected_max_w':500,'input_max_w':100,'screen_ma_range':[-60,60],'controls_verified':True},
 # Protocol per the manufacturer's rev.4 document (OM4001A matches OM3501A apart from two-tube values).
 # Meter ranges match the vendor's own client; controls stay locked until validated on hardware.
 'OM4001A':{'name':'OM-4001A','full_scale_w':5000,'reflected_max_w':250,'input_max_w':100,'screen_ma_range':[-80,80],'controls_verified':False,
  # Tick labels and tube naming follow the vendor client (Ugrid f / Ugrid b, Uheat f / Uheat b).
  'forward_ticks_w':list(range(0,5000,400)),'reflected_ticks_w':list(range(0,251,50)),'input_ticks_w':list(range(0,91,10)),
  'screen_ma_tick_step':20,'tube_labels':['f','b'],'grid_separate':True,
  # The vendor client shows grid b with the opposite sign to the received UGB value (+141 received, -141 shown).
  'grid_b_sign':-1,
  # Keep the last slow reading on screen until the next one arrives (the vendor client does not blank it).
  'hold_slow_readings':True,
  # The amp reports a constant US19 through warm-up (and in Standby); the vendor client shows 0 V while warming.
  'screen_v_zero_while_warming':True,
  # The amp answers the once-a-second # poll only every ~3.2 s (up to ~4.4 s); with the PA off nothing else is sent,
  # so the 3 s default marked the link stale every few seconds. Wait longer before calling the link delayed.
  'fresh_seconds':8,
  # The grid bias supply reads ~140 V with the PA off (raw UGA/UGB); the vendor client shows grid voltages as 0 then.
  'grid_zero_when_off':True},
}
DEFAULT={'tube_labels':['A','B'],'grid_separate':False,'grid_b_sign':1,'hold_slow_readings':False,'screen_v_zero_while_warming':False,'fresh_seconds':3,'grid_zero_when_off':False,'name':None,'full_scale_w':3500,'reflected_max_w':500,'input_max_w':100,'screen_ma_range':[-60,60],'controls_verified':False,'known':False}

def profile(model):
 """Profile for a model label; unknown models get the 3500 W scale and monitoring only."""
 p=PROFILES.get(re.sub(r'[^A-Z0-9]','',str(model or '').upper()))
 return {**copy.deepcopy(p),'known':True} if p else copy.deepcopy(DEFAULT)
