import server
import pages
import auth
import json
import traceback
from functools import cmp_to_key



JSON_TYPE_MAP={list:"array",str:"string",int:"int",float:"float",bool:"boolean"}



def _pg_cmp(a,b):
	if (a[1]["views"]!=b[1]["views"]):
		return b[1]["views"]-a[1]["views"]
	return (1 if a[1]["nm"]>b[1]["nm"] else -1)



def _read_token():
	h=server.headers()
	tk=None
	print(h)
	if ("Authorization" in h):
		tk=h["Authorization"]
	elif ("authorization" in h):
		tk=h["authorization"]
	else:
		server.set_code(401)
		return ({"error":{"code":"E_UNAUTHORIZED","message":"This Request Requires Authorization","link":"/docs/api/request-authorization"}},False)
	tk=tk.split(" ")
	if (len(tk)!=2 or tk[0].lower()!="bearer"):
		server.set_code(401)
		return ({"error":{"code":"E_UNAUTHORIZED","message":"This Request Requires Authorization","link":"/docs/api/request-authorization"}},False)
	return (tk[1],True)





def _validate(eb,d_url,t,body=False):
	b_dt=None
	if (body==True):
		try:
			b_dt=json.loads(server.body())
		except json.JSONDecodeError as e:
			traceback.print_exception(None,e,e.__traceback__)
			server.set_code(400)
			server.set_header("Content-Type","application/json")
			return ({"error":{"code":"E_JSON","message":"Unable to Deserialize JSON","link":"/docs/api/request-format"}},False)
	q=server.queries()
	o={}
	for k,v in t.items():
		if (v["p"]=="body"):
			if (k not in b_dt and "d" not in v):
				server.set_code(400)
				server.set_header("Content-Type","application/json")
				return ({"error":{"code":f"E_{eb.upper()}_FIELD","message":f"Required Field '{k}' is Missing from Request Body","link":f"{d_url}#usage"}},False)
			o[k]=(b_dt[k] if k in b_dt else v["d"])
			if (type(o[k])!=v["t"]):
				server.set_code(400)
				server.set_header("Content-Type","application/json")
				return ({"error":{"code":f"E_{eb.upper()}_FIELD_TYPE","message":f"Field '{k}' should have '{JSON_TYPE_MAP.get(v['t'],'object')}' type, but has '{JSON_TYPE_MAP.get(type(o[k]),'object')}' type","link":f"{d_url}#usage"}},False)
			if ("range" in v):
				if (o[k]<v["range"][0] or o[k]>v["range"][1]):
					server.set_code(400)
					server.set_header("Content-Type","application/json")
					return ({"error":{"code":f"E_{eb.upper()}_FIELD_RANGE","message":f"Field '{k}' should be between '{v['range'][0]}' and '{v['range'][1]}', but has a value of '{o[k]}'","link":f"{d_url}#usage"}},False)
		else:
			raise RuntimeError(v["p"])
	return (o,True)



@server.route("GET",r"/api/v1/popular")
def popular(url):
	server.set_code(200)
	server.set_header("Content-Type","application/json")
	print({k:{**v,"cache":None,"dt":None} for k,v in pages.PAGE_LIST.items()})
	return [{"name":e[1]["nm"],"url":f"/page/{e[0]}"} for e in sorted(pages.PAGE_LIST.items(),key=cmp_to_key(_pg_cmp))[:10]]



@server.route("GET",r"/api/v1/user_data")
def user_data(url):
	tk,ok=_read_token()
	if (ok==False):
		return tk
	server.set_code(200)
	server.set_header("Content-Type","application/json")
	return auth.user_data(tk,server.address())



@server.route("POST",r"/api/v1/auth/check_user")
def check_user(url):
	dt,ok=_validate("usercheck","/docs/api/check-username",{"username":{"t":str,"p":"body"},"similar":{"t":int,"p":"body","d":0,"range":[0,10]}},body=True)
	if (ok==False):
		return dt
	print(dt)
	server.set_code(200)
	server.set_header("Content-Type","application/json")
	return {"status":auth.check_username(dt["username"])}



@server.route("POST",r"/api/v1/auth/check_email")
def check_email(url):
	dt,ok=_validate("emailcheck","/docs/api/check-email",{"email":{"t":str,"p":"body"}},body=True)
	if (ok==False):
		return dt
	server.set_code(200)
	server.set_header("Content-Type","application/json")
	return {"status":auth.check_email(dt["email"])}



@server.route("POST",r"/api/v1/auth/signup")
def signup(url):
	dt,ok=_validate("signup","/docs/api/signup",{"username":{"t":str,"p":"body"},"email":{"t":str,"p":"body"},"password":{"t":str,"p":"body"}},body=True)
	if (ok==False):
		return dt
	server.set_code(200)
	server.set_header("Content-Type","application/json")
	return auth.signup(dt["username"],dt["email"],dt["password"],server.address())



@server.route("POST",r"/api/v1/auth/login")
def login(url):
	dt,ok=_validate("login","/docs/api/login",{"email":{"t":str,"p":"body"},"password":{"t":str,"p":"body"}},body=True)
	if (ok==False):
		return dt
	server.set_code(200)
	server.set_header("Content-Type","application/json")
	return auth.login(dt["email"],dt["password"],server.address())



@server.route("PUT",r"/api/v1/auth/check_token")
def check_token(url):
	tk,ok=_read_token()
	if (ok==False):
		return tk
	server.set_code(200)
	server.set_header("Content-Type","application/json")
	return auth.check_token(tk,server.address())



@server.route("POST",r"/api/v1/auth/refresh_token")
def refresh_token(url):
	tk,ok=_read_token()
	if (ok==False):
		return tk
	server.set_code(200)
	server.set_header("Content-Type","application/json")
	return auth.refresh_token(tk,server.address())



@server.route("PUT",r"/api/v1/auth/logout")
def logout(url):
	tk,ok=_read_token()
	if (ok==False):
		return tk
	server.set_code(200)
	server.set_header("Content-Type","application/json")
	return auth.logout(tk,server.address())



@server.route("*",r"/api/v1(?:/.*)?")
def route_error(url):
	server.set_code(400)
	server.set_header("Content-Type","application/json")
	return {"error":{"code":"E_APIUSAGE","message":"Unable to Process Request","link":"/docs/api/where-to-start"}}



@server.route("*",r"/api/.*")
def version_error(url):
	server.set_code(400)
	server.set_header("Content-Type","application/json")
	return {"error":{"code":"E_NOAPIVERSION","message":"Please Specify an Api Version to Use","link":"/docs/api/versions"}}



# @server.route("PUT","/api/v1/auth/profile_image")
# @server.route("PUT","/api/v1/auth/password")
# @server.route("PUT","/api/v1/auth/name")
# @server.route("GET","/api/v1/auth/user_data")
# @server.route("PUT","/api/v1/auth/logout")
# @server.route("POST","/api/v1/auth/delete")
