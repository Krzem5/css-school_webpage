import storage
import utils
import time
import struct
import threading



global _pg_v,_u
_pg_v={}
_u=True



def _write_a_db():
	global _u
	while (True):
		utils.print(f"Saving Analytics Database... (save={_u})")
		if (_u):
			_u=False
			o=b""
			for k,v in list(_pg_v.items()):
				o+=struct.pack(f"<{len(bytes(k,'utf-8'))}sBI",bytes(k,"utf-8"),0,v)
			storage.write("analytics.db",o)
		time.sleep(15)



def view_page(id_):
	global _pg_v,_u
	if (id_ not in _pg_v):
		_pg_v[id_]=1
	else:
		_pg_v[id_]+=1
	_u=True



def page_views(id_):
	if (id_ in _pg_v):
		return _pg_v[id_]
	return 0



if (storage.exists("analytics.db")):
	o=storage.read("analytics.db")
	i=0=
	while (i<len(o)):
		l=0
		while (o[i+l]!=0):
			l+=1
		_pg_v[str(o[i:i+l],"utf-8")]=struct.unpack("<I",o[i+l+1:i+l+5])[0]
		i+=l+5
threading.Thread(target=_write_a_db).start()
