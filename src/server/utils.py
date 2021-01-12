import builtins
import datetime
import inspect
import threading
import time
import ws



global _c,_pq,_l_ws,_sc
_c={}
_pq=None
_l_ws={}
_sc=None
_tl=threading.Lock()



def _print_q():
	global _pq,_l_ws
	lt=time.time()
	fs=__import__("storage")
	fs.set_silent("log.log")
	dt=fs.read("log.log")
	lc=dt.count(b"\n")
	while (True):
		if (len(_pq)>0):
			_tl.acquire()
			a,sf,_pq=" ".join([str(e) for e in _pq[0][0]]),_pq[0][1],_pq[1:]
			_tl.release()
			s=datetime.datetime.now().strftime(f"[{sf.filename[:-3]}{('.'+sf.function if sf.function!='<module>' else '')}, %H:%M:%S] {a}")
			builtins.print(s)
			s=bytes(s,"utf-8")
			for k,v in list(_l_ws.items()):
				if (v[1]==False):
					_l_ws[k]=(v[0],True)
					ws.send(b"1"+dt[:-1],thr=v[0])
				ws.send(b"0"+s,thr=v[0])
			dt+=s+b"\n"
			lc+=1
			if (lc>1024):
				dt=dt[dt.index(b"\n")+1:]
		if (time.time()>lt):
			lt=time.time()+30
			fs.write("log.log",dt)



def cache(fp):
	global _c
	if (fp in _c):
		return _c[fp]
	with open(fp,"rb") as f:
		_c[fp]=f.read()
	return _c[fp]



def print(*a):
	global _pq
	if (_pq==None):
		_pq=[(a,inspect.getouterframes(inspect.currentframe(),2)[1])]
		threading.Thread(target=_print_q).start()
	else:
		_tl.acquire()
		_pq+=[(a,inspect.getouterframes(inspect.currentframe(),2)[1])]
		_tl.release()



def ws_logs_start():
	global _sc,_l_ws
	def _ws_keep_alive(a,t):
		while (a in _l_ws):
			ws.send(b"null",thr=t)
			time.sleep(20)
	if (_sc==None):
		_sc=__import__("server")
	a=_sc.address()
	_l_ws[a]=(threading.current_thread(),False)
	thr=threading.Thread(target=_ws_keep_alive,args=(a,_l_ws[a][0]))
	thr.daemon=True
	thr.start()



def ws_logs_end():
	global _l_ws
	del _l_ws[_sc.address()]
