#!/usr/bin/env python3
"""Wrap a built dashboard HTML in an AES-GCM encrypted lock-screen shell.
Usage: encrypt_page.py <in.html> <out.html> <password>"""
import sys, os, json, base64, secrets, hashlib
from datetime import date

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
except ImportError:
    os.system(f"{sys.executable} -m pip install -q cryptography --break-system-packages")
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes

src, dst, pw = sys.argv[1], sys.argv[2], sys.argv[3]
plain = open(src, "rb").read()
salt = secrets.token_bytes(16)
iv = secrets.token_bytes(12)
kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=200_000)
key = kdf.derive(pw.encode())
ct = AESGCM(key).encrypt(iv, plain, None)
b64 = lambda b: base64.b64encode(b).decode()

shell = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>TNG Leadership Command Center</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
body{{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
 background:#f7f7f4;font-family:'Inter',sans-serif;color:#1d2826}}
.box{{background:#fff;border:1px solid #e6e9e4;border-radius:18px;padding:48px 44px;max-width:380px;width:90%;
 box-shadow:0 1px 2px rgba(29,40,38,.05),0 18px 44px -18px rgba(29,40,38,.14);text-align:center}}
.box img{{height:52px;margin-bottom:18px}}
h1{{font-family:'Cormorant Garamond',serif;font-weight:600;font-size:26px;margin:0 0 6px}}
p{{color:#68776f;font-size:13px;margin:0 0 22px}}
input{{width:100%;box-sizing:border-box;padding:12px 14px;font:inherit;border:1px solid #e6e9e4;border-radius:10px;
 text-align:center;letter-spacing:.1em}}
input:focus{{outline:2px solid #07626133}}
button{{width:100%;margin-top:12px;padding:12px;font:inherit;font-weight:600;letter-spacing:.14em;font-size:11px;
 text-transform:uppercase;color:#fff;background:#076261;border:0;border-radius:10px;cursor:pointer}}
button:hover{{background:#0a7a79}}
.err{{color:#b3402f;font-size:12px;margin-top:10px;display:none}}
.foot{{margin-top:26px;font-size:10px;letter-spacing:.12em;color:#9aa6a0;text-transform:uppercase}}
</style></head><body>
<div class="box">
<img src="https://media-production.lp-cdn.com/cdn-cgi/image/format=auto,quality=85,fit=scale-down,width=400/https://media-production.lp-cdn.com/media/1abc07f7-edce-49cb-b4ce-ec2cd52a4508" alt="TNG">
<h1>Leadership Command Center</h1>
<p>Enter the team password to open today's dashboard.</p>
<form id="f"><input type="password" id="pw" placeholder="••••••••" autofocus>
<button type="submit">Unlock dashboard</button>
<div class="err" id="err">That's not it — try again.</div></form>
<div class="foot">© The Newcomer Group · Internal Tool<br>Build {date.today().isoformat()}</div>
</div>
<script>
const SALT="{b64(salt)}",IV="{b64(iv)}",CT="{b64(ct)}";
const ub=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
document.getElementById("f").addEventListener("submit",async e=>{{
 e.preventDefault();
 const pw=document.getElementById("pw").value;
 try{{
  const km=await crypto.subtle.importKey("raw",new TextEncoder().encode(pw),"PBKDF2",false,["deriveKey"]);
  const key=await crypto.subtle.deriveKey({{name:"PBKDF2",salt:ub(SALT),iterations:200000,hash:"SHA-256"}},km,
    {{name:"AES-GCM",length:256}},false,["decrypt"]);
  const pt=await crypto.subtle.decrypt({{name:"AES-GCM",iv:ub(IV)}},key,ub(CT));
  const html=new TextDecoder().decode(pt);
  sessionStorage.setItem("tngOk","1");
  document.open();document.write(html);document.close();
 }}catch(err){{document.getElementById("err").style.display="block";}}
}});
</script></body></html>"""
open(dst, "w").write(shell)
print(f"encrypted {src} -> {dst} ({os.path.getsize(dst)//1024} KB)")
