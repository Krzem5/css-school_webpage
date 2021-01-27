import base64
import datetime
import json
import requests
import sys
import threading
import time
import utils



global _bc,_fs,_fs_d,_fs_s,_fs_u
REPO_NAME="_app_data"
with open("server/token.dt","r") as f:
	GITHUB_TOKEN=f.read().strip()
GITHUB_HEADERS="application/vnd.github.v3+json,application/vnd.github.mercy-preview+json"
_bc=None
_fs={}
_fs_d={}
_fs_s=[]
_fs_u=[]
_tl=threading.Lock()



def _as_path(fp):
	return ("/" if len(fp)==0 or fp[0] not in "\\/" else "")+fp.lower().replace("\\","/")



def _add_dirs(fp):
	global _fs_d
	assert(fp[0]=="/")
	dl=fp.split("/")[1:-1]
	d="/"
	i=0
	while (True):
		if (i==len(dl)):
			if (d not in _fs_d):
				_fs_d[d]={"d":[],"f":[fp]}
			elif (fp not in _fs_d[d]["f"]):
				_fs_d[d]["f"]+=[fp]
			break
		nd=(d if i>0 else "")+"/"+dl[i]
		if (d not in _fs_d):
			_fs_d[d]={"d":[nd],"f":[]}
		elif (nd not in _fs_d[d]["d"]):
			_fs_d[d]["d"]+=[nd]
		d=nd
		i+=1



def _remove_dirs(fp):
	global _fs_d
	assert(fp[0]=="/")
	dl=fp.split("/")[:-1]
	d="/".join(dl)
	if (fp in _fs_d[d]["f"]):
		_fs_d[d]["f"].remove(fp)
	if (len(_fs_d[d]["d"])==0 and len(_fs_d[d]["f"])==0):
		for i in range(len(dl)-1,0,-1):
			nd=("/" if i==1 else "/".join(dl[:i]))
			del _fs_d[d]
			if (d in _fs_d[nd]["d"]):
				_fs_d[nd]["d"].remove(d)
			if (len(_fs_d[nd]["d"])>0 or len(_fs_d[nd]["f"])>0):
				break
			d=nd



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



def _read_fs(bt,fp="",_l=False):
	global _fs
	utils.print(f"Reading Directory '{_as_path(fp)}' (sha={bt})")
	t=_request("get",url=f"https://api.github.com/repos/Krzem5/{REPO_NAME}/git/trees/{bt}")
	if ("message" in t and t["message"]=="Not Found"):
		return []
	if (_l==False):
		_tl.acquire()
	for k in t["tree"]:
		if (k["type"]=="blob"):
			_fs[fp+"/"+k["path"].lower()]=[k["url"],None,True]
			_add_dirs(fp+"/"+k["path"].lower())
		elif (k["type"]=="tree"):
			_read_fs(k["sha"],fp=fp+"/"+k["path"].lower(),_l=True)
		else:
			raise RuntimeError(f"Unknown File Type '{k['type']}'")
	if (_l==False):
		_tl.release()



def _is_b(dt):
	if (len(dt)==0):
		return False
	dt=dt[:4096]
	r1=len(dt.translate(None,b"\t\r\n\f\b"+bytes(range(32,127))))/len(dt)
	r2=len(dt.translate(None,bytes(range(127,256))))/len(dt)
	if (r1>0.90 and r2>0.9):
		return True
	enc_u=False
	try:
		dt.decode(encoding="utf-8")
		enc_u=True
	except:
		pass
	if ((r1>0.3 and r2<0.05) or (r1>0.8 and r2>0.8)):
		return (False if enc_u==True else True)
	else:
		return (True if enc_u==False and (b"\x00" in dt or b"\xff" in dt) else False)



def _write_fs():
	global _bc,_fs_u
	while (True):
		if (len(_fs_u)>0):
			_tl.acquire()
			bl=[]
			for k in _fs_u:
				if (k in _fs):
					if (k not in _fs_s):
						utils.print(f"Saving FileSystem File: '{k}'")
					_fs[k][2]=True
					dt=f"File too Large (size = {len(_fs[k][1])} b)"
					b_sha=False
					if (len(_fs[k][1])<=50*1024*1024):
						b64=True
						if (_is_b(_fs[k][1])==False):
							try:
								dt=str(_fs[k][1],"cp1252").replace("\r\n","\n")
								b64=False
							except:
								pass
						if (b64==True):
							b_sha=True
							dt=str(base64.b64encode(_fs[k][1]),"cp1252")
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
				else:
					if (k not in _fs_s):
						utils.print(f"Deleting FileSystem File: '{k}'")
					bl+=[{"path":k[1:],"mode":"100644","type":"blob","sha":None}]
			_fs_u=[]
			_bc=_request("post",url=f"https://api.github.com/repos/Krzem5/{REPO_NAME}/git/commits",data=json.dumps({"message":datetime.datetime.now().strftime("Commit %m/%d/%Y, %H:%M:%S"),"tree":_request("post",url=f"https://api.github.com/repos/Krzem5/{REPO_NAME}/git/trees",data=json.dumps({"base_tree":_bc["sha"],"tree":bl}))["sha"],"parents":[_bc["sha"]]}))
			_request("patch",url=f"https://api.github.com/repos/Krzem5/{REPO_NAME}/git/refs/heads/main",data=json.dumps({"sha":_bc["sha"],"force":True}))
			_tl.release()
		time.sleep(150)



def listdir(fp):
	fp=_as_path(fp)
	if (fp not in _fs_d):
		return ([],[])
	return (_fs_d[fp]["d"][:],_fs_d[fp]["f"][:])



def exists(fp):
	return (True if _as_path(fp) in _fs else False)



def set_silent(fp):
	global _fs,_fs_s
	fp=_as_path(fp)
	_tl.acquire()
	if (fp not in _fs):
		_fs[fp]=[None,None,False]
	_fs_s+=[fp]
	_tl.release()



def read(fp):
	global _fs
	fp=_as_path(fp)
	if (fp not in _fs):
		raise RuntimeError(f"File '{fp}' not Found")
	if (_fs[fp][1]==None):
		_tl.acquire()
		if (_fs[fp][0]==None):
			_fs[fp][1]=b""
		else:
			_fs[fp][1]=base64.b64decode(_request("get",url=_fs[fp][0])["content"])
		_tl.release()
	return _fs[fp][1]



def write(fp,dt):
	global _fs,_fs_u
	if (type(dt)!=bytes):
		raise TypeError(f"Expected 'bytes', found '{type(dt).__name__}'")
	if (_is_b(dt)==True):
		dt=dt.replace(b"\r\n",b"\n")
	fp=_as_path(fp)
	_tl.acquire()
	_add_dirs(fp)
	if (fp not in _fs or _fs[fp][1]!=dt and fp not in _fs_u):
		_fs_u+=[fp]
	if (fp not in _fs):
		_fs[fp]=[None,dt,False]
	else:
		_fs[fp][1]=dt
	_tl.release()



def delete(fp):
	global _fs,_fs_u
	fp=_as_path(fp)
	_tl.acquire()
	if (fp in _fs):
		if (_fs[fp][2]==True):
			if (fp not in _fs_u):
				_fs_u+=[fp]
		del _fs[fp]
		_remove_dirs(fp)
	_tl.release()



_bc=_request("get",url=f"https://api.github.com/repos/Krzem5/{REPO_NAME}/branches/main")["commit"]
_read_fs(_bc["commit"]["tree"]["sha"])
threading.Thread(target=_write_fs).start()
