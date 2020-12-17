import storage
import auth
import utils
import time
import struct
import threading



global _pg_v,_u_v,_u
_pg_v={}
_u_v={}
_u=True



def _write_a_db():
	global _u
	while (True):
		utils.print(f"Saving Analytics Database... (save={_u})")
		if (_u):
			_u=False
			o=b""
			for k,v in list(_pg_v.items()):
				o+=struct.pack(f"<{len(bytes(k,'utf-8'))}sBI",bytes(k,"utf-8"),0,v[0])
				for e,ev in list(v[2].items()):
					e=int(e,16)
					o+=struct.pack(f"<2QI",e>>64,e&0xffffffffffffffff,ev)
				o+=struct.pack(f"<2QI",0,0,v[1])
			o+=struct.pack(f"<B",0)
			for k,v in list(_u_v.items()):
				k=int(k,16)
				o+=struct.pack(f"<2QI",k>>64,k&0xffffffffffffffff,v[0])
				for e,ev in list(v[2].items()):
					e=int(e,16)
					o+=struct.pack(f"<2QI",e>>64,e&0xffffffffffffffff,ev)
				o+=struct.pack(f"<2QI",0,0,v[1])
			o+=struct.pack(f"<2Q",0,0)
			storage.write("analytics.db",o)
		time.sleep(150)



def view_page(id_,u_id=None):
	global _pg_v,_u
	if (id_ not in _pg_v):
		_pg_v[id_]=[1,0,{}]
	else:
		_pg_v[id_][0]+=1
	if (u_id==None):
		_pg_v[id_][1]+=1
	else:
		if (u_id not in _pg_v[id_][2]):
			_pg_v[id_][2][u_id]=1
		else:
			_pg_v[id_][2][u_id]+=1
	_u=True



def view_user(id_,u_id=None):
	global _u_v,_u
	id_=auth.get_id_from_username(id_)
	if (id_ not in _u_v):
		_u_v[id_]=[1,0,{}]
	else:
		_u_v[id_][0]+=1
	if (u_id==None):
		_u_v[id_][1]+=1
	else:
		if (u_id not in _u_v[id_][2]):
			_u_v[id_][2][u_id]=1
		else:
			_u_v[id_][2][u_id]+=1
	_u=True



def page_views(id_):
	if (id_ in _pg_v):
		return _pg_v[id_][0]
	return 0



if (storage.exists("analytics.db")):
	o=storage.read("analytics.db")
	i=0
	while (True):
		l=0
		while (o[i+l]!=0):
			l+=1
		if (l==0):
			i+=1
			break
		id_=str(o[i:i+l],"utf-8")
		um={}
		v=struct.unpack("<I",o[i+l+1:i+l+5])[0]
		i+=l+5
		while (True):
			e=struct.unpack("<2QI",o[i:i+20])
			u_id=(e[0]<<64)|e[1]
			i+=20
			if (u_id==0):
				_pg_v[id_]=[v,e[2],um]
				break
			um[hex(u_id)[2:]]=e[2]
	while (True):
		e=struct.unpack("<2Q",o[i:i+16])
		id_=(e[0]<<64)|e[1]
		if (id_==0):
			break
		id_=hex(id_)[2:]
		um={}
		i+=16
		v=struct.unpack("<I",o[i:i+4])[0]
		i+=4
		while (True):
			e=struct.unpack("<2QI",o[i:i+20])
			u_id=(e[0]<<64)|e[1]
			i+=20
			if (u_id==0):
				_u_v[id_]=[v,e[2],um]
				break
			um[hex(u_id)[2:]]=e[2]
threading.Thread(target=_write_a_db).start()
