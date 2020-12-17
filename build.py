import sys
import os
import json
import shutil
import re
import time
import hashlib
import subprocess



with open("./secret.dt","r") as f:
	APP_NAME,EMAIL,USER_NAME=f.read().replace("\r","").split("\n")[:3]
JS_OPERATORS=["()=>","_=>","=>","...",">>>=",">>=","<<=","|=","^=","&=","+=","-=","*=","/=","%=",";",",","?",":","||","&&","|","^","&","===","==","=","!==","!=","<<","<=","<",">>>",">>",">=",">","++","--","+","-","*","/","%","!","~",".","[","]","{","}","(",")"]
JS_KEYWORDS=["break","case","catch","const","const","continue","debugger","default","delete","do","else","enum","false","finally","for","function","if","in","instanceof","let","new","null","of","return","switch","this","throw","true","try","typeof","var","var","void","while","with"]
JS_RESERVED_IDENTIFIERS=JS_KEYWORDS+["AggregateError","alert","arguments","Array","ArrayBuffer","AsyncFunction","AsyncGenerator","AsyncGeneratorFunction","atob","Atomics","BigInt","BigInt64Array","BigUint64Array","blur","Boolean","btoa","caches","cancelAnimationFrame","cancelIdleCallback","captureEvents","chrome","clearInterval","clearTimeout","clientInformation","close","closed","confirm","console","cookieStore","createImageBitmap","crossOriginIsolated","crypto","customElements","DataView","Date","decodeURI","decodeURIComponent","defaultStatus","defaultstatus","devicePixelRatio","document","encodeURI","encodeURIComponent","Error","escape","eval","EvalError","external","fetch","find","Float32Array","Float64Array","focus","frameElement","frames","Function","Generator","GeneratorFunction","getComputedStyle","getSelection","globalThis","history","Image","indexedDB","Infinity","innerHeight","innerWidth","Int16Array","Int32Array","Int8Array","InternalError","Intl","isFinite","isNaN","isSecureContext","JSON","length","localStorage","location","locationbar","Map","matchMedia","Math","menubar","moveBy","moveTo","NaN","navigator","Number","Object","open","openDatabase","opener","origin","originIsolated","outerHeight","outerWidth","pageXOffset","pageYOffset","parent","parseFloat","parseInt","performance","personalbar","postMessage","print","Promise","prompt","Proxy","queueMicrotask","RangeError","ReferenceError","Reflect","RegExp","releaseEvents","requestAnimationFrame","requestIdleCallback","resizeBy","resizeTo","screen","screenLeft","screenTop","screenX","screenY","scroll","scrollbars","scrollBy","scrollTo","scrollX","scrollY","self","sessionStorage","Set","setInterval","setTimeout","SharedArrayBuffer","showDirectoryPicker","showOpenFilePicker","showSaveFilePicker","speechSynthesis","status","statusbar","stop","String","styleMedia","Symbol","SyntaxError","toolbar","top","trustedTypes","TypeError","Uint16Array","Uint32Array","Uint8Array","Uint8ClampedArray","undefined","unescape","uneval","URIError","visualViewport","WeakMap","WeakSet","WebAssembly","webkitCancelAnimationFrame","webkitRequestAnimationFrame","webkitRequestFileSystem","webkitResolveLocalFileSystemURL","WebSocket","window"]
JS_VAR_LETTERS="abcdefghijklmnopqrstuvwxyz"
JS_CONST_LETTERS="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
JS_REGEX_LIST={"dict":br"""{\s*(?:[$a-zA-Z0-9_]+|'(?:[^'\\]|\\.)*'|^"(?:[^"\\]|\\.)*"|^`(?:[^`\\]|\\.)*`)\s*:\s*""","dict_elem":br""",\s*(?:[$a-zA-Z0-9_]+|'(?:[^'\\]|\\.)*'|^"(?:[^"\\]|\\.)*"|^`(?:[^`\\]|\\.)*`)\s*:\s*""","float":br"\d+\.\d*(?:[eE][-+]?\d+)?|^\d+(?:\.\d*)?[eE][-+]?\d+|^\.\d+(?:[eE][-+]?\d+)?","int":br"0[xX][\da-fA-F]+|^0[0-7]*|^\d+","identifier":br"\.?[$_a-zA-Z0-9_]+(?:\.[$_a-zA-Z0-9_]+)*","string":br"""'(?:[^'\\]|\\.)*'|^"(?:[^"\\]|\\.)*"|^`(?:[^`\\]|\\.)*`""","regex":br"\/(?:\\.|\[(?:\\.|[^\]])*\]|[^\/])+\/[gimy]*","line_break":br"[\n\r]+|/\*(?:.|[\r\n])*?\*/","whitespace":br"[\ \t]+|//.*?(?:[\r\n]|$)","operator":bytes("|".join([re.sub(r"([\?\|\^\&\(\)\{\}\[\]\+\-\*\/\.])",r"\\\1",e) for e in JS_OPERATORS]),"utf-8")}



def _minify_html(html,fp):
	def _r(m):
		if (len(m[2])==0):
			return b"<"+m.group(1)+m.group(3)+b">"
		o=b"<"+m.group(1)
		for k in re.findall(br'''([a-z0-9\-_]+)\s*=\s*"((?:[^\"\\]|\\.)*)"''',m.group(2)):
			if (o[-1:]!=b"\""):
				o+=b" "
			q=(b"\"" if re.fullmatch(br"[a-z0-9\-_]+",k[1])==None else b"")
			o+=k[0]+b"="+q+k[1]+q
		return o+b">"
	o=re.sub(br"<(/?[a-z0-9\-_]+)\s*(.*?)\s*(/?)>",_r,re.sub(br"(?=(?P<tmp>[^\S ]\s*|\s{2,}))(?P=tmp)(?=(?P<txt>(?=(?P<tmp3>(?:(?=(?P<tmp2>[^<]+))(?P=tmp2)|<(?!\/?(?:textarea|pre)\b))*))(?P=tmp3))(?:<(?=(?P<tmp4>textarea|pre))(?P=tmp4)\b|$))",br"",html,re.I|re.M|re.X),re.I|re.M|re.X)
	print(f"Minified HTML File '{fp}': {len(html)} -> {len(o)} (-{round(10000-10000*len(o)/len(html))/100}%)")
	return o
def _minify_css(css,fp):
	sl=len(css)
	css=re.sub(br":\s*0(\.\d+(?:[cm]m|e[mx]|in|p[ctx]))\s*;",br":\1;",re.sub(br"#([0-9a-f])\1([0-9a-f])\2([0-9a-f])\3(\s|;)",br"#\1\2\3\4",re.sub(br"""url\(([\"'])([^)]*)\1\)""",br"url(\2)",re.sub(br"/\*[\s\S]*?\*/",b"",css))))
	i=0
	o=b""
	while (i<len(css)):
		m=re.match(br"\s*([^{]+?)\s*{",css[i:])
		if (m!=None):
			i+=m.end(0)+1
			b=1
			si=i-1
			while (b!=0):
				i+=1
				if (css[i:i+1]==b"{"):
					b+=1
				if (css[i:i+1]==b"}"):
					b-=1
			s=b",".join([re.sub(br"(?<=[\[\(>+=])\s+|\s+(?=[=~^$|>+\]\)])",b"",e.strip()) for e in m.group(1).split(b",")])
			if (re.split(br"\s",s)[0]==b"@keyframes"):
				v=[]
				l=[]
				t=[]
				for k in re.findall(br"\s*([^{]+?)\s*{\s*([^}]*?)\s*}",css[si:i]):
					v+=[{}]
					l+=[[]]
					t+=[k[0]]
					for e in re.findall(br"\s*(.*?)\s*:\s*(.*?)\s*(?:;|$)",k[1]):
						if (e[0].lower() not in l[-1]):
							l[-1]+=[e[0].lower()]
						v[-1][e[0].lower()]=e[1]
					if (len(l)==0):
						v=v[:-1]
						l=l[:-1]
						t=t[:-1]
				if (len(t)>0):
					o+=s+b"{"+b"".join([k+b"{"+b";".join([e+b":"+re.sub(br",\s+",b",",v[i][e]) for e in l[i]])+b";}" for i,k in enumerate(t)])+b"}"
			else:
				v={}
				l=[]
				for k in re.findall(br"\s*(.*?)\s*:\s*(.*?)\s*(?:;|$)",css[si:i].strip()):
					if (k[0].lower() not in l):
						l+=[k[0].lower()]
					v[k[0].lower()]=k[1]
				if (len(l)>0):
					o+=s+b"{"+b";".join([e+b":"+re.sub(br",\s+",b",",v[e]) for e in l])+b";}"
		i+=1
	print(f"Minified CSS File '{fp}': {sl} -> {len(o)} (-{round(10000-10000*len(o)/sl)/100}%)")
	return o
def _minify_js(js,fp):
	def _gen_i(il,b=JS_VAR_LETTERS):
		def _gen_next(v,b):
			n=1
			m=len(b)
			while (v>m):
				v-=m
				m*=len(b)
				n+=1
			v-=1
			o=""
			if (v==0):
				o=b[0]*n
			else:
				while (v):
					o=b[v%len(b)]+o
					v=v//len(b)
				o=b[0]*(n-len(o))+o
			return bytes(o,"utf-8")
		r=JS_RESERVED_IDENTIFIERS[:]
		for k in il:
			r+=k.values()
		i=1
		o=b""
		while (True):
			o=_gen_next(i,b)
			if (o not in r):
				break
			i+=1
		return o
	def _map_value(v,vml):
		for i in range(len(vml)-1,-1,-1):
			if (v in vml[i]):
				return vml[i][v]
		return None
	def _args(al):
		o=[]
		for k in al:
			if (len(o)>0):
				o+=[("operator",b",")]
			if (k[1]==True):
				o+=[("operator",b"...")]
			o+=[("identifier",k[0])]
		return o
	def _tokenize(s):
		i=0
		o=[]
		b=0
		while (i<len(s)):
			e=False
			for k,v in JS_REGEX_LIST.items():
				m=re.match(v,s[i:])
				if (m!=None):
					m=m.group(0)
					if (k=="line_break"):
						o+=[("operator",b";")]
					elif (k=="string" and m[:1]==b"`"):
						j=0
						ts=b""
						f=False
						while (j<len(m)):
							if (m[j:j+2]==b"${"):
								l,tj=_tokenize(m[j+2:])
								j+=tj+2
								o+=[("string"+("M" if f==True else "S"),ts)]+l
								ts=b""
								f=True
							else:
								ts+=m[j:j+1]
							j+=1
						o+=[("string"+("" if f==False else "E"),ts)]
					elif (k!="whitespace"):
						if (k=="identifier" and str(m,"utf-8") in JS_KEYWORDS):
							k="keyword"
						if (k in ["operator","dict"]):
							if (m[:1]==b"{"):
								b+=1
							elif (m==b"}"):
								b-=1
								if (b==-1):
									return (o,i)
						o+=[(k,m)]
					i+=len(m)
					e=True
					break
			if (e==True):
				continue
			raise RuntimeError(f"ERROR: {s[i:]}")
		return (o,i)
	def _write(tl,cvm,cvma,sl=0):
		o=b""
		i=0
		while (i<len(tl)):
			if (i>=sl and tl[i][0]=="identifier"):
				idl=tl[i][1].split(b".")
				if (idl[0] in cvm):
					idl[0]=cvm[idl[0]]
				for j,e in enumerate(idl[1:]):
					if (e in cvma):
						idl[j+1]=b"["+cvma[e]+b"]"
					else:
						idl[j+1]=b"."+e
				o+=b"".join(idl)
			elif (tl[i][0]=="keyword" and tl[i][1] in [b"false",b"true"]):
				o+={b"false":b"!1",b"true":b"!0"}[tl[i][1]]
			elif (tl[i][0]=="stringS"):
				o+=tl[i][1]+b"${"
				to,ti=_write(tl[i+1:],cvm,cvma)
				o+=to
				i+=ti+1
			elif (tl[i][0]=="stringM"):
				o+=b"}"+tl[i][1]+b"${"
			elif (tl[i][0]=="stringE"):
				o+=b"}"+tl[i][1]
				break
			else:
				if (tl[i][0]=="keyword" and tl[i][1] in [b"of",b"in"]):
					o+=b" "
				o+=tl[i][1]
				if (tl[i][0]=="keyword" and (tl[i][1] in [b"let",b"const",b"var",b"return",b"throw",b"new",b"of",b"in"] or (i+1<len(tl) and tl[i][1]==b"else" and tl[i+1][0]=="keyword" and tl[i+1][1]==b"if"))):
					o+=b" "
			i+=1
		return (o,i)
	ofl=len(js)
	tl,_=_tokenize(js)
	i=0
	vm=[{}]
	ef=[]
	dl=[]
	efbl={}
	ee={}
	bl=0
	vfm={}
	vfma={}
	v_nm=False
	while (i<len(tl)):
		if (tl[i][0]=="identifier"):
			idl=tl[i][1].split(b".")
			if (len(idl[0])>0):
				if (str(idl[0],"utf-8") in JS_RESERVED_IDENTIFIERS):
					if (idl[0] not in vfm):
						vfm[idl[0]]=1
					else:
						vfm[idl[0]]+=1
				else:
					if (i>0 and tl[i-1][0]=="keyword" and tl[i-1][1] in [b"let",b"const",b"var"]):
						vm[-1][idl[0]]=_gen_i(vm)
						idl[0]=vm[-1][idl[0]]
					elif (str(idl[0],"utf-8") not in JS_RESERVED_IDENTIFIERS and (i==0 or (tl[i-1][0]!="operator" or tl[i-1][1]!=b"."))):
						mv=_map_value(idl[0],vm)
						if (mv==None):
							print(f"Variable '{str(idl[0],'utf-8')}' is not mapped!")
							v_nm=True
						else:
							idl[0]=mv
			for k in idl[1:]:
				if (k not in vfma):
					vfma[k]=1
				else:
					vfma[k]+=1
			tl[i]=("identifier",b".".join(idl))
		elif (tl[i][0]=="dict"):
			dl+=[True]
		elif (tl[i][0]=="keyword"):
			if (tl[i][1]==b"function"):
				si=i
				assert(i+5<len(tl))
				assert(tl[i+1][0]=="identifier")
				assert(str(tl[i+1][1],"utf-8") not in JS_RESERVED_IDENTIFIERS)
				nm=vm[-1][tl[i+1][1]]=_gen_i(vm)
				vm+=[{}]
				assert(tl[i+2][0]=="operator")
				assert(tl[i+2][1]==b"(")
				i+=3
				al=[]
				while (True):
					if (len(al)>0 and tl[i][0]=="operator" and tl[i][1]==b","):
						i+=1
					if (tl[i][0]=="operator" and tl[i][1]==b")"):
						i+=1
						break
					va=False
					if (tl[i][0]=="operator" and tl[i][1]==b"..."):
						va=True
						i+=1
					assert(tl[i][0]=="identifier")
					vm[-1][tl[i][1]]=_gen_i(vm)
					al+=[(vm[-1][tl[i][1]],va)]
					i+=1
				assert(tl[i][0]=="operator")
				assert(tl[i][1]==b"{")
				dl+=[False]
				ef+=[(bl,bl,si,i-si,nm,al)]
				if (bl not in efbl):
					efbl[bl]=[]
				efbl[bl]+=[len(ef)-1]
		elif (tl[i][0]=="operator"):
			s_ee=True
			ot=tl[i][1]
			if (tl[i][1]==b"{"):
				vm+=[{}]
				dl+=[False]
				ef+=[None]
				bl+=1
			elif (tl[i][1]==b"}"):
				if (dl[-1]==False):
					if (ef[-1]!=None):
						cbl,ocbl,si,fl,nm,al=ef[-1]
						efbl[ocbl].remove(len(ef)-1)
						j=1
						if (tl[si+fl+1][0]=="keyword" and tl[si+fl+1][1]==b"return"):
							j+=1
							cbl=ocbl
						ftl=([("keyword",b"let"),("identifier",nm),("operator",b"=")] if nm!=None else [])+([("operator",b"_=>")] if len(al)==0 else ([("identifier",al[0][0]),("operator",b"=>")] if len(al)==1 and al[0][1]==False else [("operator",b"(")]+_args(al)+[("operator",b")"),("operator",b"=>")]))
						tl=tl[:si]+ftl+([("operator",b"{")] if cbl==None else [])+tl[si+fl+j:i]+([("operator",b"}")] if cbl==None else [])+[("operator",b";")]+tl[i+1:]
						i+=-fl+len(ftl)-2+(2 if cbl==None else 0)-j+1
					vm=vm[:-1]
					ef=ef[:-1]
					bl-=1
				dl=dl[:-1]
				s_ee=False
			elif (tl[i][1]==b")"):
				bl-=1
				s_ee=False
			elif (tl[i][1]==b";"):
				if ((i>0 and tl[i-1][0]=="operator" and tl[i-1][1]==b"{") or (i+1<len(tl) and ((tl[i+1][0]=="operator" and tl[i+1][1] in [b";",b"}",b")"]) or (tl[i+1][0]=="keyword" and tl[i+1][1]==b"else"))) or i==len(tl)-1):
					tl=tl[:i]+tl[i+1:]
					i-=1
				else:
					s_ee=False
			elif (tl[i][1]==b"()=>"):
				tl[i]=("operator",b"_=>")
			elif (tl[i][1]==b"("):
				af=False
				if (i==0 or tl[i-1][0]!="identifier"):
					si=i+0
					al=[]
					i+=1
					vm+=[{}]
					while (True):
						if (len(al)>0 and tl[i][0]=="operator" and tl[i][1]==b","):
							i+=1
						if (tl[i][0]=="operator" and tl[i][1]==b")"):
							i+=1
							break
						va=False
						if (tl[i][0]=="operator" and tl[i][1]==b"..."):
							va=True
							i+=1
						if (tl[i][0]!="identifier"):
							al=None
							break
						vm[-1][tl[i][1]]=_gen_i(vm)
						al+=[(vm[-1][tl[i][1]],va)]
						i+=1
					if (al==None or tl[i][0]!="operator" or tl[i][1]!=b"=>"):
						i=si
						vm=vm[:-1]
					else:
						i+=1
						af=True
						if (tl[i][0]=="operator" and tl[i][1]==b"{"):
							ef+=[(bl,bl,si,i-si,None,al)]
							if (bl not in efbl):
								efbl[bl]=[]
							efbl[bl]+=[len(ef)-1]
							dl+=[False]
						else:
							i-=1
							if (bl not in ee):
								ee[bl]=[]
							ee[bl]+=[(si,i-si,al)]
				if (af==False):
					bl+=1
					s_ee=False
			if (bl in efbl):
				for j in efbl[bl]:
					if (ef[j][0]==-1):
						ef[j]=(None,*ef[j][1:])
			if (s_ee==False):
				if (bl in ee):
					for k in ee[bl]:
						si,fl,al=k
						ftl=([("operator",b"_=>")] if len(al)==0 else ([("identifier",al[0][0]),("operator",b"=>")] if len(al)==1 and al[0][1]==False else [("operator",b"(")]+_args(al)+[("operator",b")"),("operator",b"=>")]))
						tl=tl[:si]+ftl+tl[si+fl+1:]
						i+=-fl+len(ftl)-1
						vm=vm[:-1]
					del ee[bl]
				if (bl in efbl):
					for j in efbl[bl]:
						if (ef[j][0]==bl):
							ef[j]=(-1,*ef[j][1:])
		i+=1
	if (v_nm):
		quit()
	cvml=[]
	for k,v in vfm.items():
		if (v>1):
			cvml+=[(len(k)*v,k,v,False)]
	for k,v in vfma.items():
		if (v>1):
			cvml+=[(len(k)*v,k,v,True)]
	cvml=sorted(cvml,key=lambda e:-e[0])
	cvm={}
	cvma={}
	sl=[]
	for k in cvml:
		if (k[3]==False):
			mv=_gen_i([cvm,cvma],b=JS_CONST_LETTERS)
			if (len(mv)*(k[2]+1)+len(k[1])+2<=len(k[1])*k[2]):
				cvm[k[1]]=mv
				if (len(sl)==0):
					sl=[("keyword",b"let")]
				else:
					sl+=[("operator",b",")]
				sl+=[("identifier",mv),("operator",b"="),("identifier",k[1])]
		else:
			mv=_gen_i([cvm,cvma],b=JS_CONST_LETTERS)
			if (len(mv)+len(k[1])+(len(mv)+1)*k[2]+4<=(len(k[1])+1)*k[2]):
				cvma[k[1]]=mv
				if (len(sl)==0):
					sl=[("keyword",b"let")]
				else:
					sl+=[("operator",b",")]
				sl+=[("identifier",mv),("operator",b"="),("string",b"\""+k[1]+b"\"")]
	if (len(sl)>0):
		tl=sl+[("operator",b";")]+tl
	o,_=_write(tl,cvm,cvma,sl=len(sl))
	print(f"Minified JS File '{fp}': {ofl} -> {len(o)} (-{round(10000-10000*len(o)/ofl)/100}%)")
	return o



def _copy(fp,f=lambda e,fp:e):
	with open(fp,"rb") as rf,open(f"build\\{fp}","wb") as wf:
		wf.write(f(rf.read(),fp))



if (os.path.exists("build")==False):
	os.mkdir("build")
	cwd=os.getcwd()
	os.chdir("build")
	if (subprocess.run(["git","init"]).returncode!=0):
		os.chdir(cwd)
		quit()
	if (subprocess.run(["git","config","--global","user.email",f"\"{EMAIL}\""]).returncode!=0):
		os.chdir(cwd)
		quit()
	if (subprocess.run(["git","config","--global","user.name",f"\"{USER_NAME}\""]).returncode!=0):
		os.chdir(cwd)
		quit()
	if (subprocess.run(["heroku","git:remote","-a",APP_NAME]).returncode!=0):
		os.chdir(cwd)
		quit()
	os.chdir(cwd)
for k in os.listdir("build"):
	if (k==".git"):
		continue
	if (os.path.isdir(f"build\\{k}")==True):
		shutil.rmtree(f"build\\{k}")
	else:
		os.remove(f"build\\{k}")
os.mkdir(f"build\\web")
os.mkdir(f"build\\web/js")
os.mkdir(f"build\\web/css")
os.mkdir(f"build\\server")
for fn in os.listdir("web"):
	if (fn[-5:]==".html"):
		_copy(f"web\\{fn}",f=_minify_html)
for fn in os.listdir("web\\css"):
	_copy(f"web\\css\\{fn}",f=_minify_css)
for fn in os.listdir("web\\js"):
	_copy(f"web\\js\\{fn}",f=_minify_js)
for fn in os.listdir("server"):
	if (os.path.isfile(f"server\\{fn}")==True):
		_copy(f"server\\{fn}")
with open(f"build\\runtime.txt","w") as f:
	f.write("python-3.9.1")
with open(f"build\\requirements.txt","w") as f:
	f.write("requests==2.22.0\nchardet==3.0.4\n")
with open(f"build\\Procfile","w") as f:
	f.write("web: python server/main.py\n")
cwd=os.getcwd()
os.chdir("build")
if (subprocess.run(["git","add","."]).returncode!=0):
	os.chdir(cwd)
	quit()
if (subprocess.run(["git","commit","-am",f"\"Push {time.time()}\""]).returncode!=0):
	os.chdir(cwd)
	quit()
if (subprocess.run(["git","push","-f","heroku","master"]).returncode!=0):
	os.chdir(cwd)
	quit()
os.chdir(cwd)
