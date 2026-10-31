"""Per-model display and control profiles. The model name selects limits; it never selects a protocol."""
import re

# controls_verified: Operate/Standby, power and auto-tune were validated on hardware for this model.
PROFILES={
 'OM3501A':{'name':'OM-3501A','full_scale_w':3500,'controls_verified':True},
 # Protocol per the manufacturer's rev.4 document (OM4001A matches OM3501A apart from two-tube values).
 # Display scale is a placeholder until checked against hardware; controls stay locked.
 'OM4001A':{'name':'OM-4001A','full_scale_w':4000,'controls_verified':False},
}
DEFAULT={'name':None,'full_scale_w':3500,'controls_verified':False,'known':False}

def profile(model):
 """Profile for a model label; unknown models get the 3500 W scale and monitoring only."""
 p=PROFILES.get(re.sub(r'[^A-Z0-9]','',str(model or '').upper()))
 return {**p,'known':True} if p else dict(DEFAULT)
