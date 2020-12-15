import utils
import os
import json
import socket
import threading
import re
import traceback



CHUNK_SIZE=1024
HTTP_CODES=(100,101,102,103,200,201,202,203,204,205,206,207,208,226,300,301,302,303,304,305,307,308,400,401,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,421,422,423,424,425,426,428,429,431,451,500,501,502,503,504,505,506,507,508,510,511)
HTTP_CODE_MAP={100:"Continue",101:"Switching Protocols",102:"Processing",103:"Early Hints",200:"Ok",201:"Created",202:"Accepted",203:"Non Authoritative Information",204:"No Content",205:"Reset Content",206:"Partial Content",207:"Multi Status",208:"Already Reported",226:"Im Used",300:"Multiple Choices",301:"Moved Permanently",302:"Found",303:"See Other",304:"Not Modified",305:"Use Proxy",307:"Temporary Redirect",308:"Permanent Redirect",400:"Bad Request",401:"Unauthorized",402:"Payment Required",403:"Forbidden",404:"Not Found",405:"Method Not Allowed",406:"Not Acceptable",407:"Proxy Authentication Required",408:"Request Timeout",409:"Conflict",410:"Gone",411:"Length Required",412:"Precondition Failed",413:"Request Entity Too Large",414:"Request Uri Too Long",415:"Unsupported Media Type",416:"Requested Range Not Satisfiable",417:"Expectation Failed",418:"Im A Teapot",421:"Misdirected Request",422:"Unprocessable Entity",423:"Locked",424:"Failed Dependency",425:"Too Early",426:"Upgrade Required",428:"Precondition Required",429:"Too Many Requests",431:"Request Header Fields Too Large",451:"Unavailable For Legal Reasons",500:"Internal Server Error",501:"Not Implemented",502:"Bad Gateway",503:"Service Unavailable",504:"Gateway Timeout",505:"Http Version Not Supported",506:"Variant Also Negotiates",507:"Insufficient Storage",508:"Loop Detected",510:"Not Extended",511:"Network Authentication Required"}
global _epl
_epl={}



def _handle(cs,a):
	threading.current_thread()._cs=cs
	_dt=b""
	while (True):
		try:
			dtc=cs.recv(CHUNK_SIZE)
			if (not dtc):
				break
			_dt+=dtc
		except socket.timeout:
			break
		except ConnectionResetError:
			return
	if (len(_dt)==0):
		return
	threading.current_thread()._r_dt=_dt
	(t,url,threading.current_thread()._rv),threading.current_thread()._rh,threading.current_thread()._rdt=str(_dt.split(b"\r\n")[0],"utf-8").split(" "),{str(e.split(b":")[0],"utf-8").lower():e[len(e.split(b":")[0])+2:] for e in _dt.split(b"\r\n\r\n")[0].split(b"\r\n")[1:] if len(e)!=0},_dt[len(_dt.split(b"\r\n\r\n")[0])+4:]
	url=re.sub(r"/\.+/","/./",re.sub(r"\\\.+\\",r"\\.\\",url))
	url,q=url.split("?")[0],url[len(url.split("?")[0])+1:]
	threading.current_thread()._a=a
	threading.current_thread()._q={e.split("=")[0]:e[len(e.split("=")[0])+1:] for e in q.split("&")}
	threading.current_thread()._h={"Content-Type":"text/plain","Content-Length":None}
	threading.current_thread()._rc=200
	c=None
	try:
		e=True
		if (t in _epl):
			for k in _epl[t]["l"]:
				if (re.fullmatch(k[0],url)!=None):
					e=False
					utils.print(f"Method={t}, URL='{url}', Handler='{k[1].__code__.co_filename.replace('.py','')}.{k[1].__code__.co_name}'")
					c=k[1](url)
					if (type(c)==list or type(c)==dict):
						c=json.dumps(c)
					if (type(c)!=bytes):
						c=bytes(str(c),"utf-8")
					break
		if ("*" in _epl and e==True):
			for k in _epl["*"]["l"]:
				if (re.fullmatch(k[0],url)!=None):
					e=False
					utils.print(f"Method={t}, URL='{url}', Handler='{k[1].__code__.co_filename.replace('.py','')}.{k[1].__code__.co_name}'")
					c=k[1](url)
					if (type(c)==list or type(c)==dict):
						c=json.dumps(c)
					if (type(c)!=bytes):
						c=bytes(str(c),"utf-8")
					break
		if (t in _epl and e==True and _epl[t]["f"]!=None):
			e=False
			utils.print(f"Method={t}, URL='{url}', Handler='{_epl[t]['f'].__code__.co_filename.replace('.py','')}.{_epl[t]['f'].__code__.co_name}'")
			c=_epl[t]["f"](url)
			if (type(c)==list or type(c)==dict):
				c=json.dumps(c)
			if (type(c)!=bytes):
				c=bytes(str(c),"utf-8")
		if (e==True):
			c=bytes(f"Unimplemented Method '{t}' for URL '{url}'","utf-8")
			threading.current_thread()._rc=501
	except Exception as e:
		traceback.print_exception(None,e,e.__traceback__)
		c=bytes("Internal Server Error","utf-8")
		threading.current_thread()._rc=500
	if (threading.current_thread()._rc!=-1):
		if (threading.current_thread()._h["Content-Length"]==None):
			threading.current_thread()._h["Content-Length"]=len(c)
		cs.sendall(bytes(f"HTTP/1.1 {threading.current_thread()._rc} {HTTP_CODE_MAP[threading.current_thread()._rc]}"+"".join([f"\r\n{k}: {v}" for k,v in threading.current_thread()._h.items()])+"\r\n\r\n","utf-8")+c)



def route(m,url):
	def _wr(f):
		global _epl
		if (f.__code__.co_argcount!=1):
			raise RuntimeError("Route Funcions Must Have Exactly 1 Argument: URL")
		if (m not in list(_epl.keys())):
			_epl[m]={"l":[],"f":None}
		if (url!=None):
			_epl[m]["l"]+=[(url,f)]
		else:
			if (_epl[m]["f"]!=None):
				utils.print(f"Override Fallback for Method '{m}'!")
			_epl[m]["f"]=f
		return f
	return _wr



def client_socket():
	return threading.current_thread()._cs



def address():
	return threading.current_thread()._a



def raw_request():
	return threading.current_thread()._r_dt



def queries():
	return {**threading.current_thread()._q}



def query(k):
	return threading.current_thread()._q[k]



def headers():
	return {**threading.current_thread()._rh}



def header(k):
	return threading.current_thread()._rh[k]



def body():
	return threading.current_thread()._rdt



def set_code(c):
	if (c==-1):
		threading.current_thread()._rc=-1
		return
	if (c not in HTTP_CODES):
		raise RuntimeError(f"Unknown HTTP Code '{c}'!")
	if (threading.current_thread()._rc==-1):
		raise RuntimeError(f"Overriding Non-Returning Socket Handler!")
	threading.current_thread()._rc=c



def set_header(k,v):
	threading.current_thread()._h[k]=v



def set_headers(d):
	threading.current_thread()._h.update(d)



def run(p):
	ss=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	ss.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
	ss.bind(("0.0.0.0",p))
	ss.listen(5)
	utils.print(f"Server started on port {p}...")
	while (True):
		cs,a=ss.accept()
		cs.settimeout(0.1)
		threading.Thread(target=_handle,args=(cs,a),kwargs={}).start()
