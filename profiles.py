"""Per-model display and control profiles. The model name selects limits; it never selects a protocol."""
import re

# controls_verified: Operate/Standby, power and auto-tune were validated on hardware for this model.
PROFILES={
 'OM3501A':{'name':'OM-3501A','full_scale_w':3500,'reflected_max_w':500,'input_max_w':100,'screen_ma_range':[-60,60],'controls_verified':True},
 # Protocol per the manufacturer's rev.4 document (OM4001A matches OM3501A apart from two-tube values).
 # Meter ranges match the vendor's own client; controls stay locked until validated on hardware.
 'OM4001A':{'name':'OM-4001A','full_scale_w':5000,'reflected_max_w':250,'input_max_w':100,'screen_ma_range':[-80,80],'controls_verified':False},
}
DEFAULT={'name':None,'full_scale_w':3500,'reflected_max_w':500,'input_max_w':100,'screen_ma_range':[-60,60],'controls_verified':False,'known':False}

def profile(model):
 """Profile for a model label; unknown models get the 3500 W scale and monitoring only."""
 p=PROFILES.get(re.sub(r'[^A-Z0-9]','',str(model or '').upper()))
 return {**p,'screen_ma_range':list(p['screen_ma_range']),'known':True} if p else {**DEFAULT,'screen_ma_range':list(DEFAULT['screen_ma_range'])}
