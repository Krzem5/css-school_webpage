import re
import hashlib
import secrets
import time
import hmac
import base64



MIN_USERNAME_LEN=3
MAX_USERNAME_LEN=24
MIN_PASSWORD_LEN=6
MAX_PASSWORD_LEN=64
USERNAME_VALID_LETTERS="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
RETURN_CODE={"ok":0,"username_to_short":1,"username_to_long":2,"username_invalid":3,"username_used":4,"email_invalid":5,"email_used":6,"password_to_short":7,"password_to_long":8,"password_invalid":9,"login_fail":10,"invalid_token":11}
DB_ID_LEN=16
DB_KEY_USERNAME=0
DB_KEY_EMAIL=1
DB_KEY_PASSWORD=2
DB_KEY_TIME=3
DB_KEY_IP=4
DB_KEY_TOKEN=5
DB_KEY_TOKEN_END=6
DB_KEY_EMAIL_VERIFICATION=7
TOKEN_LEN=18
TOKEN_EXP_DATE=300000



_db={}
_db_em={}



def _check_token(tk):
	t=time.time()
	for k,v in _db.items():
		if (v[DB_KEY_TOKEN_END]>=t and v[DB_KEY_TOKEN]!=None):
			r=(0 if len(tk)==len(v[DB_KEY_TOKEN]) else 1)
			for i in range(0,min(len(tk),len(v[DB_KEY_TOKEN]))):
				if (tk[i]!=v[DB_KEY_TOKEN][i]):
					r|=1
			if (r==0):
				return k
	return None



def check_username(nm):
	if (len(nm)<MIN_USERNAME_LEN):
		return RETURN_CODE["username_to_short"]
	if (len(nm)>MAX_USERNAME_LEN):
		return RETURN_CODE["username_to_long"]
	for k in nm:
		if (k not in USERNAME_VALID_LETTERS):
			return RETURN_CODE["username_invalid"]
	for e in _db.values():
		if (e[DB_KEY_USERNAME]==nm):
			return RETURN_CODE["username_used"]
	return RETURN_CODE["ok"]



def check_email(em,db=True):
	if (re.fullmatch(r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",em)==None):
		return RETURN_CODE["email_invalid"]
	if (db==True):
		for e in _db.values():
			if (e[DB_KEY_EMAIL]==em):
				return RETURN_CODE["email_used"]
	return RETURN_CODE["ok"]



def signup(nm,em,pw,ip):
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
	_db[id_]=[nm,em,hashlib.sha256(bytes(id_,"utf-8")+b"\x00"+bytes(em,"utf-8")+b"\x00"+pw).hexdigest(),time.time(),f"{ip[0]}:{ip[1]}",None,0,False]
	_db_em[em]=id_
	print(_db,_db_em)
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
	_db[id_][DB_KEY_TOKEN_END]=time.time()+TOKEN_EXP_DATE
	return {"status":RETURN_CODE["ok"],"token":_db[id_][DB_KEY_TOKEN]}



def check_token(tk,ip):
	return {"status":RETURN_CODE[("invalid_token" if _check_token(tk)==None else "ok")]}



def refresh_token(tk,ip):
	id_=_check_token(tk)
	if (id_==None):
		return {"status":RETURN_CODE["invalid_token"]}
	_db[id_][DB_KEY_TOKEN]=str(base64.urlsafe_b64encode(secrets.token_bytes(TOKEN_LEN)),"utf-8")
	_db[id_][DB_KEY_TOKEN_END]=time.time()+TOKEN_EXP_DATE
	return {"status":RETURN_CODE["ok"],"token":_db[id_][DB_KEY_TOKEN]}


def user_data(tk,ip):
	id_=_check_token(tk)
	if (id_==None):
		return {"status":RETURN_CODE["invalid_token"]}
	return {"status":RETURN_CODE["ok"],"username":_db[id_][DB_KEY_USERNAME],"email":_db[id_][DB_KEY_EMAIL],"email_verified":_db[id_][DB_KEY_EMAIL_VERIFICATION]}



def logout(tk,ip):
	id_=_check_token(tk)
	if (id_==None):
		return {"status":RETURN_CODE["invalid_token"]}
	_db[id_][DB_KEY_TOKEN]=None
	_db[id_][DB_KEY_TOKEN_END]=0
	return {"status":RETURN_CODE["ok"]}
