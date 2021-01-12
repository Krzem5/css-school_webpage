from functools import cmp_to_key
import analytics
import auth
import json
import pages
import re
import server
import traceback
import utils
import ws



JSON_TYPE_MAP={list:"array",str:"string",int:"int",float:"float",bool:"boolean"}



def _pg_cmp(a,b):
	if (a[1]!=b[1]):
		return b[1]-a[1]
	return (1 if a[2]>b[2] else -1)



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
		elif (v["p"]=="query"):
			if (k not in q and "d" not in v):
				server.set_code(400)
				server.set_header("Content-Type","application/json")
				return ({"error":{"code":f"E_{eb.upper()}_FIELD","message":f"Required Field '{k}' is Missing from Request Query","link":f"{d_url}#usage"}},False)
			o[k]=(q[k] if k in q else v["d"])
			try:
				o[k]=v["t"](o[k])
			except:
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



def read_token():
	h=server.headers()
	tk=None
	if ("cookie" in h):
		for k in h["cookie"].split(b";"):
			k=k.split(b"=")
			if (k[0]==b"__ctoken"):
				return (str(k[1],"utf-8"),True)
	if ("authorization" in h):
		tk=h["authorization"]
	else:
		server.set_code(401)
		return ({"error":{"code":"E_UNAUTHORIZED","message":"This Request Requires Authorization","link":"/docs/api/request-authorization"}},False)
	tk=tk.split(b" ")
	if (len(tk)!=2 or tk[0].lower()!=b"bearer"):
		server.set_code(401)
		return ({"error":{"code":"E_UNAUTHORIZED","message":"This Request Requires Authorization","link":"/docs/api/request-authorization"}},False)
	return (str(tk[1],"utf-8"),True)



@server.route("GET",r"/api/v1/popular")
def popular(url):
	dt,ok=_validate("popular","/docs/api/popular",{"count":{"t":int,"p":"query","d":10,"range":[1,100]}})
	if (ok==False):
		return dt
	server.set_code(200)
	server.set_header("Content-Type","application/json")
	return [{"name":e[2],"url":f"/page/{e[0]}","author":auth.get_username_from_id(pages.PAGE_LIST[e[0]]["author"])} for e in sorted([(e,analytics.page_views(e),pages.PAGE_LIST[e]["nm"]) for e in pages.PAGE_LIST.keys()],key=cmp_to_key(_pg_cmp))[:dt["count"]]]



@server.route("GET",r"/api/v1/user_data")
def user_data(url):
	tk,ok=read_token()
	if (ok==False):
		return tk
	server.set_code(200)
	server.set_header("Content-Type","application/json")
	return auth.user_data(tk,server.address())



@server.route("PUT",r"/api/v1/save")
def save(url):
	dt,ok=_validate("save","/docs/api/save",{"id":{"t":str,"p":"body"},"title":{"t":str,"p":"body"},"desc":{"t":str,"p":"body"},"p":{"t":list,"p":"body"}},body=True)
	if (ok==False):
		return dt
	tk,ok=read_token()
	if (ok==False):
		return tk
	dt["id"]=re.sub(r"[^a-z0-9\-]","",dt["id"])[:32]
	dt["title"]=re.sub(r"[^a-zA-Z0-9_\- ]","",dt["title"])[:64]
	dt["desc"]=re.sub(r"[^a-zA-Z0-9_\-\.\!\(\)\?\% ]","",dt["desc"])[:256]
	server.set_code(200)
	server.set_header("Content-Type","application/json")
	id_=auth.get_id(tk)
	if (id_==None):
		return {"status":auth.RETURN_CODE["invalid_token"]}
	for k,v in pages.PAGE_LIST.items():
		if (k==dt["id"] and v["author"]!=id_):
			return {"status":auth.RETURN_CODE["id_already_used"]}
		elif (k!=dt["id"] and v["nm"]==dt["title"]):
			return {"status":auth.RETURN_CODE["title_already_used"]}
	pg,ok=pages.render(dt["p"])
	if (ok==False):
		return {"status":auth.RETURN_CODE["malformated_input"],"reason":pg}
	pages.add_page(dt["id"],{"title":dt["title"],"desc":dt["desc"],"author":id_,"data":dt["p"]},pg)
	return {"status":auth.RETURN_CODE["ok"]}



@server.route("GET",r"/api/v1/admin")
def admin(url):
	tk,ok=read_token()
	if (ok==False):
		return tk
	server.set_code(200)
	server.set_header("Content-Type","application/json")
	return auth.admin(tk,server.address())



@server.route("POST",r"/api/v1/admin/users")
def get_users(url):
	dt,ok=_validate("admin_users","/docs/api",{"query":{"t":str,"p":"body"}},body=True)
	if (ok==False):
		return dt
	tk,ok=read_token()
	if (ok==False):
		return tk
	server.set_code(200)
	server.set_header("Content-Type","application/json")
	return auth.get_users(tk,dt["query"],server.address())



@server.route("PUT",r"/api/v1/admin/set_name")
def admin_set_name(url):
	dt,ok=_validate("admin_set_name","/docs/api",{"name":{"t":str,"p":"body"},"id":{"t":str,"p":"body"}},body=True)
	if (ok==False):
		return dt
	tk,ok=read_token()
	if (ok==False):
		return tk
	server.set_code(200)
	server.set_header("Content-Type","application/json")
	return auth.admin_set_name(tk,dt["id"],dt["name"],server.address())



@server.route("PUT",r"/api/v1/admin/flip_tag")
def admin_flip_tag(url):
	dt,ok=_validate("admin_flip_tag","/docs/api",{"tag":{"t":int,"p":"body","range":[0,3]},"id":{"t":str,"p":"body"}},body=True)
	if (ok==False):
		return dt
	tk,ok=read_token()
	if (ok==False):
		return tk
	server.set_code(200)
	server.set_header("Content-Type","application/json")
	return auth.admin_flip_tag(tk,dt["id"],dt["tag"],server.address())



@server.route("POST",r"/api/v1/admin/pages")
def get_pages(url):
	dt,ok=_validate("admin_users","/docs/api",{"query":{"t":str,"p":"body"}},body=True)
	if (ok==False):
		return dt
	tk,ok=read_token()
	if (ok==False):
		return tk
	server.set_code(200)
	server.set_header("Content-Type","application/json")
	return auth.get_pages(tk,dt["query"],server.address())



@server.route("GET",r"/api/v1/admin/logs")
def create_ws_url(url):
	tk,ok=read_token()
	if (ok==False):
		return tk
	server.set_code(200)
	server.set_header("Content-Type","application/json")
	return auth.create_ws_url(tk,server.address())



@server.route("GET",r"/api/v1/admin/logs/[a-zA-Z0-9]{32}")
def create_log_ws(url):
	r,ok=auth.remove_ws_url(url[19:],server.address())
	if (ok==False):
		server.set_code(404)
		return r
	server.set_code(-1)
	ws.handle(server.client_socket(),cf=utils.ws_logs_start,df=utils.ws_logs_end,h_dt=server.raw_request())



@server.route("POST",r"/api/v1/auth/check_user")
def check_user(url):
	dt,ok=_validate("usercheck","/docs/api/check-username",{"username":{"t":str,"p":"body"}},body=True)
	if (ok==False):
		return dt
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
	tk,ok=read_token()
	if (ok==False):
		return tk
	server.set_code(200)
	server.set_header("Content-Type","application/json")
	return auth.check_token(tk,server.address())



@server.route("POST",r"/api/v1/auth/refresh_token")
def refresh_token(url):
	tk,ok=read_token()
	if (ok==False):
		return tk
	server.set_code(200)
	server.set_header("Content-Type","application/json")
	return auth.refresh_token(tk,server.address())



@server.route("PUT",r"/api/v1/auth/logout")
def logout(url):
	tk,ok=read_token()
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
# @server.route("POST","/api/v1/auth/delete")
