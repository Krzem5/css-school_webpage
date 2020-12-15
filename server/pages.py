import server
import storage
import auth
import api
import analytics
import utils
import json
import re



global PAGE_LIST,USER_PAGE_MAP,USER_CACHE
PAGE_LIST={}
USER_PAGE_MAP={}
USER_CACHE={}
with open("web/page_template.html","rb") as f:
	PAGE_TEMPLATE=f.read().split(b"$$$__DATA__$$$")
with open("web/user_template.html","rb") as f:
	USER_TEMPLATE=f.read().split(b"$$$__DATA__$$$")
with open("web/current_user_template.html","rb") as f:
	CURRENT_USER_TEMPLATE=f.read().split(b"$$$__DATA__$$$")



for k in storage.listdir("pages")[0]:
	dt=json.loads(storage.read(k+"/index.json"))
	id_=re.sub(r"[^a-zA-Z0-9-]","",k[7:].lower())
	PAGE_LIST[id_]={"nm":dt["title"],"author":dt["author"],"dt":dt,"cache":None}
	if (dt["author"] not in USER_PAGE_MAP):
		USER_PAGE_MAP[dt["author"]]=[]
	USER_PAGE_MAP[dt["author"]]+=[id_]



def _render_page(pg):
	o=PAGE_TEMPLATE[0]+bytes(pg["dt"]["title"],"utf-8")+PAGE_TEMPLATE[1]+bytes(f"<div class=\"title\">{pg['dt']['title']}</div><div class=\"desc\">{pg['dt']['desc']}</div>","utf-8")
	for k in pg["dt"]["data"]:
		k=re.sub(r"&lt;(br|span)&gt;",r"<\1>",k.replace("<","&lt;").replace(">","&gt;"))
		i=0
		while (i<len(k)):
			if (k[i:i+3]=="```"):
				si=i+0
				i+=3
				while (k[i:i+3]!="```"):
					i+=1
				k=k[:si]+f"<code class=\"c\">{k[si+3:i]}</code>"+k[i+3:]
				i+=9
			elif (k[i]=="*" and k[i+1]=="*"):
				b=0
				si=i+0
				i+=2
				while ((b%2)!=0 or k[i]!="*" or k[i+1]!="*"):
					if (k[i]=="*"):
						b+=1
					i+=1
				k=k[:si]+f"<span class=\"b\">{k[si+2:i]}</span>"+k[i+2:]
				i=si+15
			elif (k[i]=="*"):
				si=i+0
				i+=1
				while (k[i]!="*"):
					i+=1
				k=k[:si]+f"<span class=\"i\">{k[si+1:i]}</span>"+k[i+1:]
				i=si+15
			i+=1
		o+=bytes(f"<p class=\"p\">{k}</p>","utf-8")
	return o+PAGE_TEMPLATE[2]



def _render_user(dt):
	o=USER_TEMPLATE[0]+bytes(f"{dt['username']}\",img:\"{dt['img_url']}","utf-8")+USER_TEMPLATE[1]
	if (dt["username"] in USER_PAGE_MAP and len(USER_PAGE_MAP[dt["username"]])>0):
		for k in USER_PAGE_MAP[dt["username"]]:
			o+=bytes(f"<div class=\"e\"><div class=\"e-wr\"><div class=\"t\" onclick=\"window.location.href='/page/{k}'\">{PAGE_LIST[k]['nm']}</div><div class=\"a\" onclick=\"window.location.href='/user/{dt['username']}'\">By <span>@{dt['username']}</span></div></div></div>","utf-8")
	else:
		o+=b"<div class=\"err\">No Articles to Show</div>"
	return o+USER_TEMPLATE[2]



def _render_c_user(dt):
	o=CURRENT_USER_TEMPLATE[0]+bytes(f"{dt['username']}\",img:\"{dt['img_url']}","utf-8")+CURRENT_USER_TEMPLATE[1]
	if (dt["username"] in USER_PAGE_MAP and len(USER_PAGE_MAP[dt["username"]])>0):
		for k in USER_PAGE_MAP[dt["username"]]:
			o+=bytes(f"<div class=\"e\"><div class=\"e-wr\"><div class=\"t\" onclick=\"window.location.href='/page/{k}'\">{PAGE_LIST[k]['nm']}</div><div class=\"a\" onclick=\"window.location.href='/user/{dt['username']}'\">By <span>@{dt['username']}</span></div></div></div>","utf-8")
	else:
		o+=b"<div class=\"err\">No Articles to Show</div>"
	return o+CURRENT_USER_TEMPLATE[2]



@server.route("GET",r"/")
def index(url):
	server.set_code(200)
	server.set_header("Content-Type","text/html")
	return utils.cache("web/index.html")



@server.route("GET",r"/login")
def login(url):
	server.set_code(200)
	server.set_header("Content-Type","text/html")
	return utils.cache("web/login.html")



@server.route("GET",r"/signup")
def signup(url):
	server.set_code(200)
	server.set_header("Content-Type","text/html")
	return utils.cache("web/signup.html")



@server.route("GET",r"/admin")
def admin(url):
	tk,ok=api.read_token()
	if (ok==False or auth.is_admin(tk)[1]==False):
		server.set_code(307)
		server.set_header("Location","https://krzem.herokuapp.com/")
		return b""
	server.set_code(200)
	server.set_header("Content-Type","text/html")
	return utils.cache("web/admin.html")



@server.route("GET",r"/new")
def admin(url):
	tk,ok=api.read_token()
	if (ok==False):
		server.set_code(307)
		server.set_header("Location","https://krzem.herokuapp.com/")
		return b""
	server.set_code(200)
	server.set_header("Content-Type","text/html")
	return utils.cache("web/new.html")



@server.route("GET",r"/page/[a-z0-9-]+(?:\.html)?")
def page(url):
	url=url[6:].lower()
	if (url.endswith(".html")):
		url=url[:-5]
	server.set_code(200)
	server.set_header("Content-Type","text/html")
	if (url in PAGE_LIST):
		pg=PAGE_LIST[url]
		tk,ok=api.read_token()
		analytics.view_page(url,u_id=(auth.get_id(tk) if ok else None))
		if (pg["cache"]==None):
			pg["cache"]=_render_page(pg)
		return pg["cache"]
	else:
		server.set_code(404)
		return utils.cache("web/not-found.html")



@server.route("GET",r"/user/[a-zA-Z0-9\-_]+(?:\.html)?")
def user(url):
	global USER_CACHE
	url=url[6:].lower()
	if (url.endswith(".html")):
		url=url[:-5]
	server.set_code(200)
	server.set_header("Content-Type","text/html")
	dt=auth.get_user(url)
	if (dt!=None):
		tk,ok=api.read_token()
		id_=(auth.get_id(tk) if ok else None)
		analytics.view_user(url,u_id=id_)
		print(auth.get_id_from_username(url),id_)
		return (_render_c_user if id_!=None and auth.get_id_from_username(url)==id_ else _render_user)(dt)
	else:
		server.set_code(404)
		return utils.cache("web/not-found.html")



@server.route("GET",r"/js/[^/]*\.js")
def js_file(url):
	server.set_code(200)
	server.set_header("Content-Type","text/javascript")
	return utils.cache(f"web/{url}")



@server.route("GET",r"/css/[^/]*\.css")
def css_file(url):
	server.set_code(200)
	server.set_header("Content-Type","text/css")
	return utils.cache(f"web/{url}")



@server.route("GET",None)
def not_found(url):
	server.set_code(404)
	server.set_header("Content-Type","text/html")
	return utils.cache("web/not-found.html")
