import server
import storage
import auth
import utils
import json
import re



global PAGE_LIST,USER_CACHE
PAGE_LIST={}
USER_CACHE={}
with open("web/page_template.html","rb") as f:
	PAGE_TEMPLATE=f.read().split(b"$$$__DATA__$$$")
with open("web/user_template.html","rb") as f:
	USER_TEMPLATE=f.read().split(b"$$$__DATA__$$$")



for k in storage.listdir("pages")[0]:
	dt=json.loads(storage.read(k+"/index.json"))
	PAGE_LIST[re.sub(r"[^a-zA-Z0-9-]","",k[7:].lower())]={"nm":dt["title"],"views":0,"author":dt["author"],"dt":dt,"cache":None}



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
	return USER_TEMPLATE[0]+bytes(f"{dt['username']}\",img:\"{dt['img_url']}","utf-8")+USER_TEMPLATE[1]



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
	server.set_code(200)
	server.set_header("Content-Type","text/html")
	return utils.cache("web/admin.html")



@server.route("GET",r"/page/[a-zA-Z0-9-]+(?:\.html)?")
def page(url):
	global PAGE_LIST
	url=url[6:].lower()
	if (url.endswith(".html")):
		url=url[:-5]
	server.set_code(200)
	server.set_header("Content-Type","text/html")
	if (url in PAGE_LIST):
		pg=PAGE_LIST[url]
		pg["views"]+=1
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
		if (url not in USER_CACHE):
			USER_CACHE[url]=_render_user(dt)
		return USER_CACHE[url]
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
