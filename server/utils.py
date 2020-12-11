import threading
import builtins
import inspect
import datetime
import time



global _pq
_c={}
_pq=None



def _print_q():
	global _pq
	lt=time.time()
	fs=__import__("storage")
	fs.set_silent("log.log")
	dt=fs.read("log.log")
	while (True):
		if (len(_pq)>0):
			a,sf,_pq=" ".join([str(e) for e in _pq[0][0]]),_pq[0][1],_pq[1:]
			s=datetime.datetime.now().strftime(f"[{sf.filename[:-3]}{('.'+sf.function if sf.function!='<module>' else '')}, %H:%M:%S] {a}")
			builtins.print(s)
			dt+=bytes(s,"utf-8")+b"\n"
		if (time.time()>lt):
			lt=time.time()+30
			fs.write("log.log",dt)



def cache(fp):
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
		_pq+=[(a,inspect.getouterframes(inspect.currentframe(),2)[1])]
