_c={}



def cache(fp):
	if (fp in _c):
		return _c[fp]
	with open(fp,"rb") as f:
		_c[fp]=f.read()
	return _c[fp]
