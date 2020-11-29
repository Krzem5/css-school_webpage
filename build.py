import sys
import os
import json
import shutil
import re



PROD=(True if "--prod" in sys.argv else False)
with open("web/_template.html","r") as f:
	TEMPLATE=f.read().split("$$$__DATA__$$$")[:2]



if (os.path.exists("build")):
	shutil.rmtree("build",ignore_errors=True)
os.mkdir("build")
for fn in os.listdir("sites"):
	with open(f"sites/{fn}","r") as f:
		dt=json.loads(f.read())
	with open(f"build/{fn[:-4]}html","w") as f:
		f.write(TEMPLATE[0])
		f.write(f"<div class=\"title\">{dt['title']}</div><div class=\"desc\">{dt['desc']}</div>")
		for k in dt["data"]:
			k=re.sub(r"&lt;(br|span)&gt;",r"<\1>",k.replace("<","&lt;").replace(">","&gt;"))
			for i in range(0,len(k)):
				if (k[i:i+3]=="```"):
					si=i
					i+=3
					while (k[i:i+3]!="```"):
						i+=1
					k=k[:si]+f"<code class=\"c\">{k[si+3:i]}</code>"+k[i+3:]
					i+=9
				elif (k[i:i+2]=="**"):
					b=0
					si=i
					i+=2
					while ((b%2)!=0 or k[i]!="*" or k[i+1]!="*"):
						if (k[i]=="*"):
							b+=1
						i+=1
					k=k[:si]+f"<span class=\"b\">{k[si+2:i]}</span>"+k[i+2:]
					i=si+15
				elif (k[i]=="*"):
					si=i
					i+=1
					while (k[i]!="*"):
						i+=1
					k=k[:si]+f"<span class=\"i\">{k[si+1:i]}</span>"+k[i+1:]
					i=si+15
			f.write(f"<p class=\"p\">{k}</p>")
		f.write(TEMPLATE[1])
os.mkdir("build/js")
for fn in os.listdir("web/js"):
	with open(f"web/js/{fn}","r") as f:
		dt=f.read()
	with open(f"build/js/{fn}","w") as f:
		f.write(dt)
os.mkdir("build/css")
for fn in os.listdir("web/css"):
	with open(f"web/css/{fn}","r") as f:
		dt=f.read()
	with open(f"build/css/{fn}","w") as f:
		f.write(dt)
