import requests
import time
import sys
import json
import threading
import chardet
import base64



global _bc,_fs,_fs_u
REPO_NAME="_app_data"
with open("server/token.dt","r") as f:
	GITHUB_TOKEN=f.read().strip()
GITHUB_HEADERS="application/vnd.github.v3+json,application/vnd.github.mercy-preview+json"
_bc=None
_fs={}
_fs_u=[]



def _as_path(fp):
	return ("/" if fp[0] not in "\\/" else "")+fp.replace("\\","/")



def _request(m="get",**kw):
	kw["headers"]={**kw.get("headers",{}),"Authorization":f"token {GITHUB_TOKEN}","Accept":GITHUB_HEADERS,"User-Agent":"FileSystem API"}
	r=getattr(requests,("get" if m=="raw" else m))(**kw)
	if ("X-RateLimit-Remaining" in r.headers.keys() and r.headers["X-RateLimit-Remaining"]=="0"):
		print(r.headers)
		sys.exit(1)
	time.sleep(0.72)
	if (m=="raw"):
		return r
	if (type(r.json())==dict and "message" in r.json().keys() and r.json()["message"]=="Server Error"):
		print(r.json())
		return None
	return r.json()



def _read_fs(bc,fp=""):
	global _fs
	t=_request("get",url=f"https://api.github.com/repos/Krzem5/{REPO_NAME}/git/trees/{bc['commit']['tree']['sha']}")
	if ("message" in t and t["message"]=="Not Found"):
		return []
	for k in t["tree"]:
		print(k)
		if (k["type"]=="blob"):
			_fs[fp+"/"+k["path"]]=[k["url"],None]
		else:
			raise RuntimeError(f"Unknown File Type '{k['type']}'")



def _is_b(dt):
	if (len(dt)==0):
		return False
	dt=dt[:4096]
	r1=len(dt.translate(None,b"\t\r\n\f\b"+bytes(range(32,127))))/len(dt)
	r2=len(dt.translate(None,bytes(range(127,256))))/len(dt)
	if (r1>0.90 and r2>0.9):
		return True
	enc=chardet.detect(dt)
	enc_u=False
	if (enc["confidence"]>0.9 and enc["encoding"]!="ascii"):
		try:
			dt.decode(encoding=enc["encoding"])
			enc_u=True
		except:
			pass
	if ((r1>0.3 and r2<0.05) or (r1>0.8 and r2>0.8)):
		return (False if enc_u==True else True)
	else:
		return (True if enc_u==False and (b"\x00" in dt or b"\xff" in dt) else False)



def _write_loop():
	global _fs_u
	while (True):
		l,_fs_u=_fs_u[:],[]
		print(f"Saving FileSystem Files: {l}")
		if (len(l)>0):
			bl=[]
			for k in l:
				print(k)
				dt=f"File too Large (size = {len(_fs[k][1])} b)"
				b_sha=False
				if (len(_fs[k][1])<=50*1024*1024):
					b64=True
					if (_is_b(_fs[k][1])==False):
						try:
							dt=str(_fs[k][1],"utf-8").replace("\r\n","\n")
							b64=False
						except:
							pass
					if (b64==True):
						b_sha=True
						dt=str(base64.b64encode(_fs[k][1]),"utf-8")
						if (len(dt)>50*1024*1024):
							b_sha=False
							dt=f"File too Large (size = {len(dt)} b)"
						else:
							b=_request("post",url=f"https://api.github.com/repos/Krzem5/{REPO_NAME}/git/blobs",data=json.dumps({"content":dt,"encoding":"base64"}))
							if (b==None):
								b_sha=False
								dt="Github Server Error"
								raise RuntimeError(f"Error While creating Blob for File '{k}'")
							else:
								dt=b["sha"]
				bl+=[({"path":k[1:],"mode":"100644","type":"blob","content":dt} if b_sha==False else {"path":k[1:],"mode":"100644","type":"blob","sha":dt})]
			_request("patch",url=f"https://api.github.com/repos/Krzem5/{REPO_NAME}/git/refs/heads/main",data=json.dumps({"sha":_request("post",url=f"https://api.github.com/repos/Krzem5/{REPO_NAME}/git/commits",data=json.dumps({"message":f"Commit {time.time()}","tree":_request("post",url=f"https://api.github.com/repos/Krzem5/{REPO_NAME}/git/trees",data=json.dumps({"base_tree":_bc["sha"],"tree":bl}))["sha"],"parents":[_bc["sha"]]}))["sha"],"force":True}))
		time.sleep(60*5)



def exists(fp):
	return (True if _as_path(fp) in _fs else False)



def read(fp):
	fp=_as_path(fp)
	if (fp not in _fs):
		raise RuntimeError(f"File '{fp}' not Found")
	if (_fs[fp][1]==None):
		_fs[fp][1]=base64.b64decode(_request("get",url=_fs[fp][0])["content"])
	return _fs[fp][1]



def write(fp,dt):
	global _fs,_fs_u
	if (type(dt)!=bytes):
		raise TypeError(f"Expected 'bytes' type, found '{type(dt).__name__}' type")
	if (_is_b(dt)==True):
		dt=dt.replace(b"\r\n",b"\n")
	fp=_as_path(fp)
	if (fp not in _fs or _fs[fp][1]!=dt and fp not in _fs_u):
		_fs_u+=[fp]
	_fs[fp][1]=dt



_bc=_request("get",url=f"https://api.github.com/repos/Krzem5/{REPO_NAME}/branches/main")["commit"]
_read_fs(_bc)
threading.Thread(target=_write_loop).start()
