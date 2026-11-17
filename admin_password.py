"""The amplifier's admin password, remembered on this computer so tuning does not ask every time.

It is a file in the app's data folder that only the current user account can read (mode 0600 on macOS). It is not
encrypted: file permissions are the only protection, the same trade-off as the manufacturer's own client. The
engine reads it itself; no endpoint ever returns it to the page, and it never goes into settings.json or a trace."""
import os
from pathlib import Path
import settings

def valid(password):
 return isinstance(password,str) and 1<=len(password)<=10 and all(33<=ord(c)<=126 and c!=';' for c in password)

def path():return settings.location().with_name('admin-password')

def exists():return path().is_file()

def read():
 try:text=path().read_text(encoding='ascii').strip()
 except (OSError,UnicodeError):return None
 return text if valid(text) else None

def save(password):
 if not valid(password):raise ValueError('The admin password is 1 to 10 characters, without semicolons')
 p=path();p.parent.mkdir(parents=True,exist_ok=True)
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
 try:os.write(fd,password.encode('ascii'))
 finally:os.close(fd)
 try:os.chmod(p,0o600)
 except OSError:pass

def forget():
 try:path().unlink()
 except FileNotFoundError:pass
