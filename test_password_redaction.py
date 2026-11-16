import json,tempfile,unittest
from pathlib import Path
from wire_trace import WireTrace,TracedSocket
class Wire:
 def __init__(self):self.sent=[]
 def sendall(self,data):self.sent.append(data)
class Tests(unittest.TestCase):
 def test_the_password_never_reaches_the_trace_file(self):
  path=Path(tempfile.mkdtemp())/'t.jsonl';trace=WireTrace(path);wire=Wire();sock=TracedSocket(wire,trace)
  sock.sendall(b'P');trace.redact_next=True;sock.sendall(b'hunter2;');sock.sendall(b'L');trace.close()
  text=path.read_text();self.assertNotIn(b'hunter2;'.hex(),text);self.assertNotIn('hunter2',text)
  rows=[json.loads(l) for l in text.splitlines()];self.assertEqual([r['hex'] for r in rows],[b'P'.hex(),'redacted',b'L'.hex()])
  self.assertEqual(wire.sent,[b'P',b'hunter2;',b'L'])   # the amplifier still receives it
if __name__=='__main__':unittest.main()
