import server
import storage
import auth
import api
import analytics
import utils
import requests
import json
import re
import time
import hashlib
import threading



global PAGE_LIST,USER_PAGE_MAP,USER_CACHE,IMG_CACHE
PAGE_LIST={}
USER_PAGE_MAP={}
USER_CACHE={}
IMG_CACHE={}
with open("web/page_template.html","rb") as f:
	PAGE_TEMPLATE=f.read().split(b"$$$__DATA__$$$")
with open("web/user_template.html","rb") as f:
	USER_TEMPLATE=f.read().split(b"$$$__DATA__$$$")
with open("web/current_user_template.html","rb") as f:
	CURRENT_USER_TEMPLATE=f.read().split(b"$$$__DATA__$$$")
_tl=threading.Lock()



_tl.acquire()
for k in storage.listdir("pages")[0]:
	vl=json.loads(storage.read(k+"/index.json"))
	id_=re.sub(r"[^a-zA-Z0-9\-]","",k[7:].lower())
	dt=json.loads(storage.read(f"{k}/{vl['current'][0]}.json"))
	PAGE_LIST[id_]={"vl":vl,"nm":dt["title"],"author":dt["author"],"dt":dt,"cache":None}
	if (dt["author"] not in USER_PAGE_MAP):
		USER_PAGE_MAP[dt["author"]]=[]
	USER_PAGE_MAP[dt["author"]]+=[id_]
_tl.release()



def _render_page(pg):
	return PAGE_TEMPLATE[0]+bytes(pg["dt"]["title"],"utf-8")+PAGE_TEMPLATE[1]+bytes(f"<div class=\"title\">{pg['dt']['title']}</div><div class=\"desc\">{pg['dt']['desc']}</div>"+pg["dt"]["data"],"utf-8")+PAGE_TEMPLATE[2]



def _render_user(dt):
	o=USER_TEMPLATE[0]+bytes(f"{dt['username']}\",verified:{('true' if dt['email_verified'] else 'false')},img:\"{dt['img_url']}","utf-8")+USER_TEMPLATE[1]
	if (dt["id"] in USER_PAGE_MAP and len(USER_PAGE_MAP[dt["id"]])>0):
		for k in USER_PAGE_MAP[dt["id"]]:
			o+=bytes(f"<div class=\"e\"><div class=\"e-wr\"><div class=\"t\" onclick=\"window.location.href='/page/{k}'\">{PAGE_LIST[k]['nm']}</div><div class=\"a\" onclick=\"window.location.href='/user/{dt['username']}'\">By <span>@{dt['username']}</span></div></div></div>","utf-8")
	else:
		o+=b"<div class=\"err\">No Articles to Show</div>"
	return o+USER_TEMPLATE[2]



def _render_c_user(dt):
	o=CURRENT_USER_TEMPLATE[0]+bytes(f"{dt['username']}\",verified:{('true' if dt['email_verified'] else 'false')},img:\"{dt['img_url']}","utf-8")+CURRENT_USER_TEMPLATE[1]
	if (dt["id"] in USER_PAGE_MAP and len(USER_PAGE_MAP[dt["id"]])>0):
		for k in USER_PAGE_MAP[dt["id"]]:
			o+=bytes(f"<div class=\"e\"><div class=\"e-wr\"><div class=\"t\" onclick=\"window.location.href='/page/{k}'\">{PAGE_LIST[k]['nm']}</div><div class=\"a\" onclick=\"window.location.href='/user/{dt['username']}'\">By <span>@{dt['username']}</span></div></div></div>","utf-8")
	else:
		o+=b"<div class=\"err\">No Articles to Show</div>"
	return o+CURRENT_USER_TEMPLATE[2]



def add_page(id_,dt):
	global PAGE_LIST,USER_PAGE_MAP
	_tl.acquire()
	vl=(PAGE_LIST[id_]["vl"] if id_ in PAGE_LIST else {"all":{}})
	dt_id=hashlib.md5(bytes(dt["title"]+"\x00"+dt["desc"]+"\x00"+dt["data"],"utf-8")).hexdigest()
	vl["current"]=(dt_id,int(time.time()))
	vl["all"][dt_id]=vl["current"][1]
	PAGE_LIST[id_]={"vl":vl,"nm":dt["title"],"author":dt["author"],"dt":dt,"cache":None}
	if (dt["author"] not in USER_PAGE_MAP):
		USER_PAGE_MAP[dt["author"]]=[]
	if (id_ not in USER_PAGE_MAP[dt["author"]]):
		USER_PAGE_MAP[dt["author"]]+=[id_]
	_tl.release()
	storage.write(f"pages/{id_}/index.json",bytes(json.dumps(vl),"utf-8"))
	storage.write(f"pages/{id_}/{dt_id}.json",bytes(json.dumps({"title":dt["title"],"desc":dt["desc"],"author":dt["author"],"data":dt["data"]}),"utf-8"))



def render(l):
	global IMG_CACHE
	o=""
	for j,k in enumerate(l):
		k=k.replace("<","&lt;").replace(">","&gt;")
		i=0
		ln=1
		while (i<len(k)):
			if (k[i]=="\n"):
				ln+=1
			elif (k[i:i+2]=="!["):
				si=i
				i+=2;
				while (k[i]!="]"):
					if (i>=len(k)):
						return (f"Unterminated Square Brackets in Paragraph {j}, Line {ln}",False)
					i+=1
				i+=1
				if (k[i]!="{"):
					i=si+1
					continue
				i+=1
				si2=i
				while (k[i]!="}"):
					if (i>=len(k)):
						return (f"Unterminated Curly Brackets in Paragraph {j}, Line {ln}",False)
					i+=1;
				u=k[si2:i]
				if (u not in IMG_CACHE):
					r=requests.get(u,headers={"Accept":"image/*","Accept-Encoding":"gzip,deflate,br"})
					r.headers={ek.lower():ev for ek,ev in r.headers.items()}
					print(r.content)
					if (r.status_code!=200 or "content-type" not in r.headers or r.headers["content-type"][:6]!="image/"):
						IMG_CACHE[u]=False
					else:
						IMG_CACHE[u]=True
				if (IMG_CACHE[u]==False):
					return (f"Unable to Load Image '{u}'",False)
				k=k[:si]+f"<img src=\"{u}\" alt=\"{k[si+2:si2-2]}\">"+k[i+1:]
				i+=24
			elif (k[i:i+3]=="```"):
				si=i+0
				i+=3
				while (k[i:i+3]!="```"):
					if (i>=len(k)):
						return (f"Unterminated Triple Quotes in Paragraph {j}, Line {ln}",False)
					i+=1
				k=k[:si]+f"<code class=\"c\">{k[si+3:i]}</code>"+k[i+3:]
				i+=19
			elif (k[i]=="*" and k[i+1]=="*"):
				b=0
				si=i+0
				i+=2
				while ((b%2)!=0 or k[i]!="*" or k[i+1]!="*"):
					if (i>=len(k)):
						return (f"Unterminated Double Quotes in Paragraph {j}, Line {ln}",False)
					if (k[i]=="*"):
						b+=1
					i+=1
				k=k[:si]+f"<span class=\"b\">{k[si+2:i]}</span>"+k[i+2:]
				i=si+15
			elif (k[i]=="*"):
				si=i+0
				i+=1
				while (k[i]!="*"):
					if (i>=len(k)):
						return (f"Unterminated Single Quotes in Paragraph {j}, Line {ln}",False)
					i+=1
				k=k[:si]+f"<span class=\"i\">{k[si+1:i]}</span>"+k[i+1:]
				i=si+15
			i+=1
		o+=f"<p class=\"p\">{k.replace(chr(10),'<br>')}</p>"
	return (o,True)



@server.route("GET",r"/")
def index(url):
	server.set_code(200)
	server.set_header("Content-Type","text/html")
	server.set_header("Cache-Control","public,max-age=31536000,immutable")
	return utils.cache("web/index.html")



@server.route("GET",r"/login")
def login(url):
	server.set_code(200)
	server.set_header("Content-Type","text/html")
	server.set_header("Cache-Control","public,max-age=31536000,immutable")
	return utils.cache("web/login.html")



@server.route("GET",r"/signup")
def signup(url):
	server.set_code(200)
	server.set_header("Content-Type","text/html")
	server.set_header("Cache-Control","public,max-age=31536000,immutable")
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
	server.set_header("Cache-Control","public,max-age=31536000,immutable")
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
	server.set_header("Cache-Control","public,max-age=31536000,immutable")
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
		return utils.cache("web/not_found.html")



@server.route("GET",r"/user/[a-zA-Z0-9\-_]+(?:\.html)?")
def user(url):
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
		return (_render_c_user if id_!=None and auth.get_id_from_username(url)==id_ else _render_user)(dt)
	else:
		server.set_code(404)
		return utils.cache("web/not_found.html")



@server.route("GET",None)
def not_found(url):
	server.set_code(404)
	server.set_header("Content-Type","text/html")
	return utils.cache("web/not_found.html")
