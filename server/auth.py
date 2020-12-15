import server
import storage
import utils
import re
import hashlib
import secrets
import time
import base64
import threading
import struct



MIN_USERNAME_LEN=3
MAX_USERNAME_LEN=24
MIN_PASSWORD_LEN=6
MAX_PASSWORD_LEN=64
EMAIL_REGEX=re.compile(r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$")
USERNAME_VALID_LETTERS="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
RETURN_CODE={"ok":0,"username_to_short":1,"username_to_long":2,"username_invalid":3,"username_used":4,"email_invalid":5,"email_used":6,"password_to_short":7,"password_to_long":8,"password_invalid":9,"login_fail":10,"invalid_token":11,"not_admin":12,"regex_error":13,"invalid_url":14,"invalid_id":15,"invalid_tag":16}
DB_ID_LEN=16
DB_KEY_USERNAME=0
DB_KEY_EMAIL=1
DB_KEY_PASSWORD=2
DB_KEY_TIME=3
DB_KEY_IP=4
DB_KEY_TOKEN=5
DB_KEY_TOKEN_END=6
DB_KEY_EMAIL_VERIFIED=7
DB_KEY_IMAGE=8
DB_KEY_ADMIN=9
DB_KEY_DISABLED=10
TOKEN_LEN=18
TOKEN_EXP_DATE=1800
WS_URL_EXP_TIME=60



global _db,_db_em,_db_u_nm,_db_u,_ws_url
_db={}
_db_em={}
_db_u_nm={}
_db_u=True
_ws_url={}



def _write_db():
	global _db_u
	while (True):
		utils.print(f"Saving Auth Database... (save={_db_u})")
		if (_db_u):
			_db_u=False
			o=b""
			for k,v in list(_db.items()):
				k=int(k,16)
				p=int(v[DB_KEY_PASSWORD],16)
				v[DB_KEY_TIME]=int(v[DB_KEY_TIME])
				o+=struct.pack(f"<2QB{len(v[DB_KEY_USERNAME])}s{len(v[DB_KEY_EMAIL])}sB4QI4BH{len(v[DB_KEY_IMAGE])}sB",k>>64,k&0xffffffffffffffff,len(v[DB_KEY_USERNAME])|((1 if v[DB_KEY_EMAIL_VERIFIED] else 0)<<5)|((1 if v[DB_KEY_ADMIN] else 0)<<6)|((1 if v[DB_KEY_DISABLED] else 0)<<7),bytes(v[DB_KEY_USERNAME],"utf-8"),bytes(v[DB_KEY_EMAIL],"utf-8"),0,p>>192,(p>>128)&0xffffffffffffffff,(p>>64)&0xffffffffffffffff,p&0xffffffffffffffff,v[DB_KEY_TIME],int(v[DB_KEY_IP].split(".")[0]),int(v[DB_KEY_IP].split(".")[1]),int(v[DB_KEY_IP].split(".")[2]),int(v[DB_KEY_IP].split(".")[3].split(":")[0]),int(v[DB_KEY_IP].split(":")[1]),bytes(v[DB_KEY_IMAGE],"utf-8"),0)
			storage.write("database.db",o)
		time.sleep(300)



def _check_token(tk):
	t=int(time.time())
	for k,v in _db.items():
		if (v[DB_KEY_TOKEN_END]>=t and v[DB_KEY_TOKEN]!=None):
			r=(0 if len(tk)==len(v[DB_KEY_TOKEN]) else 1)
			for i in range(0,min(len(tk),len(v[DB_KEY_TOKEN]))):
				if (tk[i]!=v[DB_KEY_TOKEN][i]):
					r|=1
			if (r==0):
				return k
	return None



def get_id(tk):
	return _check_token(tk)



def get_id_from_username(nm):
	return _db_u_nm[nm]



def check_username(nm):
	if (len(nm)<MIN_USERNAME_LEN):
		return RETURN_CODE["username_to_short"]
	if (len(nm)>MAX_USERNAME_LEN):
		return RETURN_CODE["username_to_long"]
	for k in nm:
		if (k not in USERNAME_VALID_LETTERS):
			return RETURN_CODE["username_invalid"]
	for e in _db.values():
		if (e[DB_KEY_USERNAME].lower()==nm.lower()):
			return RETURN_CODE["username_used"]
	return RETURN_CODE["ok"]



def check_email(em,db=True):
	if (EMAIL_REGEX.fullmatch(em)==None):
		return RETURN_CODE["email_invalid"]
	if (db==True):
		for e in _db.values():
			if (e[DB_KEY_EMAIL].lower()==em.lower()):
				return RETURN_CODE["email_used"]
	return RETURN_CODE["ok"]



def signup(nm,em,pw,ip):
	global _db,_db_em,_db_u_nm,_db_u
	r=check_username(nm)
	if (r!=RETURN_CODE["ok"]):
		return {"status":r}
	r=check_email(em)
	if (r!=RETURN_CODE["ok"]):
		return {"status":r}
	pw=bytes(pw,"utf-8")
	if (len(pw)<MIN_PASSWORD_LEN):
		return {"status":RETURN_CODE["password_to_short"]}
	if (len(pw)>MAX_PASSWORD_LEN):
		return {"status":RETURN_CODE["password_to_long"]}
	r=0
	for k in pw:
		if (k<0x1f or k==0x7f):
			r|=1
	if (r!=0):
		return {"status":RETURN_CODE["password_invalid"]}
	id_=secrets.token_hex(DB_ID_LEN)
	while (id_=="0"*auth.DB_ID_LEN*2 or id_=="0"*(auth.DB_ID_LEN*2-1)+"1"):
		id_=secrets.token_hex(DB_ID_LEN)
	id_=hex(id_)[2:]
	_db[id_]=[nm,em,hashlib.sha256(bytes(id_,"utf-8")+b"\x00"+bytes(em,"utf-8")+b"\x00"+pw).hexdigest(),int(time.time()),f"{ip[0]}:{ip[1]}",None,0,False,"https://via.placeholder.com/128",False,False]
	_db_em[em]=id_
	_db_u_nm[nm.lower()]=id_
	_db_u=True
	return {"status":RETURN_CODE["ok"]}



def login(em,pw,ip):
	r=check_email(em,db=False)
	if (r!=RETURN_CODE["ok"]):
		return {"status":r}
	if (em not in _db_em):
		return {"status":RETURN_CODE["login_fail"]}
	pw=bytes(pw,"utf-8")
	if (len(pw)<MIN_PASSWORD_LEN):
		return {"status":RETURN_CODE["login_fail"]}
	if (len(pw)>MAX_PASSWORD_LEN):
		return {"status":RETURN_CODE["login_fail"]}
	id_=_db_em[em]
	pw_h=hashlib.sha256(bytes(id_,"utf-8")+b"\x00"+bytes(em,"utf-8")+b"\x00"+pw).hexdigest()
	r=0
	for i,k in enumerate(pw_h):
		if (k!=_db[id_][DB_KEY_PASSWORD][i]):
			r|=1
	if (r!=0):
		return {"status":RETURN_CODE["login_fail"]}
	_db[id_][DB_KEY_TOKEN]=str(base64.urlsafe_b64encode(secrets.token_bytes(TOKEN_LEN)),"utf-8")
	_db[id_][DB_KEY_TOKEN_END]=int(time.time())+TOKEN_EXP_DATE
	server.set_header("Set-cookie",f"__ctoken={_db[id_][DB_KEY_TOKEN]};Max-Age={TOKEN_EXP_DATE};SameSite=Secure;Secure;HttpOnly;Path=/")
	return {"status":RETURN_CODE["ok"]}



def check_token(tk,ip):
	return {"status":RETURN_CODE[("invalid_token" if _check_token(tk)==None else "ok")]}



def refresh_token(tk,ip):
	id_=_check_token(tk)
	if (id_==None):
		return {"status":RETURN_CODE["invalid_token"]}
	_db[id_][DB_KEY_TOKEN]=str(base64.urlsafe_b64encode(secrets.token_bytes(TOKEN_LEN)),"utf-8")
	_db[id_][DB_KEY_TOKEN_END]=int(time.time())+TOKEN_EXP_DATE
	return {"status":RETURN_CODE["ok"],"token":_db[id_][DB_KEY_TOKEN]}



def user_data(tk,ip):
	id_=_check_token(tk)
	if (id_==None):
		return {"status":RETURN_CODE["invalid_token"]}
	return {"status":RETURN_CODE["ok"],"username":_db[id_][DB_KEY_USERNAME],"email":_db[id_][DB_KEY_EMAIL],"email_verified":_db[id_][DB_KEY_EMAIL_VERIFIED],"image":_db[id_][DB_KEY_IMAGE]}



def logout(tk,ip):
	id_=_check_token(tk)
	if (id_==None):
		return {"status":RETURN_CODE["invalid_token"]}
	_db[id_][DB_KEY_TOKEN]=None
	_db[id_][DB_KEY_TOKEN_END]=0
	return {"status":RETURN_CODE["ok"]}



def get_user(u_nm):
	u_nm=u_nm.lower()
	if (u_nm not in _db_u_nm):
		return None
	id_=_db_u_nm[u_nm]
	if (_db[id_][DB_KEY_DISABLED]):
		return None
	return {"username":_db[id_][DB_KEY_USERNAME],"time":_db[id_][DB_KEY_TIME],"email_verified":_db[id_][DB_KEY_EMAIL_VERIFIED],"img_url":_db[id_][DB_KEY_IMAGE]}



def is_admin(tk):
	id_=_check_token(tk)
	if (id_==None):
		return ({"status":RETURN_CODE["invalid_token"]},False)
	elif (_db[id_][DB_KEY_ADMIN]!=True):
		return ({"status":RETURN_CODE["not_admin"]},False)
	return (None,True)



def admin(tk,ip):
	id_=_check_token(tk)
	if (id_==None):
		return {"status":RETURN_CODE["invalid_token"]}
	elif (_db[id_][DB_KEY_ADMIN]!=True):
		return {"status":RETURN_CODE["not_admin"]}
	return {"status":RETURN_CODE["ok"],"username":_db[id_][DB_KEY_USERNAME]}



def get_users(tk,q,ip):
	id_=_check_token(tk)
	if (id_==None):
		return {"status":RETURN_CODE["invalid_token"]}
	elif (_db[id_][DB_KEY_ADMIN]!=True):
		return {"status":RETURN_CODE["not_admin"]}
	u,e,t=True,True,True
	if (q.count(":")>0):
		s,q=q.split(":")[0],q[len(q.split(":")[0])+1:]
		u,e,t=False,False,False
		for k in s:
			if (k=="u"):
				u=True
			if (k=="e"):
				e=True
			if (k=="t"):
				t=True
		if (u==e and e==t and t==False):
			u,e,t=True,True,True
	try:
		q=re.compile(q,re.I)
	except re.error:
		return {"status":RETURN_CODE["regex_error"]}
	o=[]
	for k,v in list(_db.items()):
		ts=" ".join((["disabled"] if v[DB_KEY_DISABLED] else [])+(["logged-in"] if v[DB_KEY_TOKEN] else [])+(["verified-email"] if v[DB_KEY_EMAIL_VERIFIED] else [])+(["admin"] if v[DB_KEY_ADMIN] else []))
		if ((u and q.search(v[DB_KEY_USERNAME])!=None) or (e and q.search(v[DB_KEY_EMAIL])!=None) or (t and q.search(ts)!=None)):
			o+=[{"id":k,"username":v[DB_KEY_USERNAME],"email":v[DB_KEY_EMAIL],"password":v[DB_KEY_PASSWORD],"time":v[DB_KEY_TIME],"ip":v[DB_KEY_IP],"token":v[DB_KEY_TOKEN],"token_end":v[DB_KEY_TOKEN_END],"email_verified":v[DB_KEY_EMAIL_VERIFIED],"image":v[DB_KEY_IMAGE],"admin":v[DB_KEY_ADMIN],"disabled":v[DB_KEY_DISABLED]}]
	return {"status":RETURN_CODE["ok"],"users":o}



def admin_set_name(tk,t_id,nm,ip):
	global _db,_db_u_nm,_db_u
	id_=_check_token(tk)
	if (id_==None):
		return {"status":RETURN_CODE["invalid_token"]}
	if (_db[id_][DB_KEY_ADMIN]!=True):
		return {"status":RETURN_CODE["not_admin"]}
	if (t_id not in _db):
		return {"status":RETURN_CODE["invalid_id"]}
	r=check_username(nm)
	if (r!=RETURN_CODE["ok"]):
		return {"status":r}
	del _db_u_nm[_db[t_id][DB_KEY_USERNAME].lower()]
	_db_u_nm[nm.lower()]=t_id
	_db[t_id][DB_KEY_USERNAME]=nm
	_db_u=True
	return {"status":RETURN_CODE["ok"]}



def admin_flip_tag(tk,t_id,tag,ip):
	global _db,_db_u
	id_=_check_token(tk)
	if (id_==None):
		return {"status":RETURN_CODE["invalid_token"]}
	if (_db[id_][DB_KEY_ADMIN]!=True):
		return {"status":RETURN_CODE["not_admin"]}
	if (t_id not in _db):
		return {"status":RETURN_CODE["invalid_id"]}
	if (tag==0):
		_db[t_id][DB_KEY_DISABLED]=not _db[t_id][DB_KEY_DISABLED]
	elif (tag==1 and _db[t_id][DB_KEY_TOKEN]!=0):
		_db[t_id][DB_KEY_TOKEN]=None
		_db[t_id][DB_KEY_TOKEN_END]=0
	elif (tag==2):
		_db[t_id][DB_KEY_EMAIL_VERIFIED]=not _db[t_id][DB_KEY_EMAIL_VERIFIED]
	elif (tag==3):
		_db[t_id][DB_KEY_ADMIN]=not _db[t_id][DB_KEY_ADMIN]
	else:
		return {"status":RETURN_CODE["invalid_tag"]}
	_db_u=True
	return {"status":RETURN_CODE["ok"]}



def create_ws_url(tk,ip):
	global _ws_url
	id_=_check_token(tk)
	if (id_==None):
		return {"status":RETURN_CODE["invalid_token"]}
	if (_db[id_][DB_KEY_ADMIN]!=True):
		return {"status":RETURN_CODE["not_admin"]}
	url=secrets.token_hex(16)
	_ws_url[url]=time.time()+WS_URL_EXP_TIME
	return {"status":RETURN_CODE["ok"],"url":url}



def remove_ws_url(url,ip):
	global _ws_url
	if (url not in _ws_url):
		return ({"status":RETURN_CODE["invalid_url"]},False)
	t=_ws_url[url]
	del _ws_url[url]
	if (t<time.time()):
		return ({"status":RETURN_CODE["invalid_url"]},False)
	return (None,True)



if (storage.exists("database.db")):
	o=storage.read("database.db")
	i=0
	while (i<len(o)):
		k1,k2,f=struct.unpack("<2QB",o[i:i+17])
		k=hex(k1<<64|k2)[2:]
		d,a,ve,l=(f>>7)&1,(f>>6)&1,(f>>5)&1,f&0x1f
		i+=17
		el=0
		while (o[i+l+el]!=0):
			el+=1
		p1,p2,p3,p4=struct.unpack("<4Q",o[i+l+el+1:i+l+el+33])
		il=0
		while (o[i+l+el+il+43]!=0):
			il+=1
		_db[k]=[str(o[i:i+l],"utf-8"),str(o[i+l:i+l+el],"utf-8"),hex((p1<<192)|(p2<<128)|(p3<<64)|p4)[2:],struct.unpack("<I",o[i+l+el+33:i+l+el+37])[0],".".join([str(e) for e in struct.unpack("<4B",o[i+l+el+37:i+l+el+41])])+":"+str(struct.unpack("<H",o[i+l+el+41:i+l+el+43])[0]),None,0,(True if ve else False),str(o[i+l+el+43:i+l+el+il+43],"utf-8"),(True if a else False),(True if d else False)]
		_db_em[_db[k][DB_KEY_EMAIL]]=k
		_db_u_nm[_db[k][DB_KEY_USERNAME].lower()]=k
		i+=l+el+il+44
threading.Thread(target=_write_db).start()
