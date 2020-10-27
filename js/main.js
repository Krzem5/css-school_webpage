const SIDEBAR_DATA=[
	{
		"nm": "Main Page",
		"url": null
	},
	{
		"nm": "Test Page",
		"url": "test.html"
	},
	{
		"nm": "How to Code, Part I",
		"url": "how-to-code.html"
	},
	{
		"nm": "How to Code, Part II",
		"url": "how-to-code-2.html"
	}
];



document.addEventListener("DOMContentLoaded",()=>{
	if (!/^https?:\/\/[a-zA-Z0-9]+\.github\.io\//.test(window.location.href)){
		// window.location.href="https://krzem5.github.io/Css-School_Webpage/";
	}
	document.querySelectorAll(".bg-r .bg .wr .top .icon")[0].onclick=()=>{
		window.location.href="/Css-School_Webpage";
	};
	let te=document.querySelectorAll(".bg-r .bg .wr .top .title")[0];
	te.innerHTML=te.innerText.split("").map((e)=>{
		return `<span class="c">${e}</span>`;
	}).join("");
	let se=document.querySelectorAll(".bg-r .bg .wr .side")[0];
	for (let k of SIDEBAR_DATA){
		se.innerHTML+=`<div class="elem" onclick="window._load('${k.url}')">${k.nm}</div>`;
	}
	window._load=(url)=>{
		if (url=="null"){
			window.location.href="/Css-School_Webpage/";
			return;
		}
		fetch(`/Css-School_Webpage${(!/^[\\\/]/.test(url[0])?"/":"")+url}`).catch((e)=>{
			return null;
		}).then((e)=>{
			if (e==null||e.ok==false){
				window.location.href="/Css-School_Webpage/not-found.html";
				console.log(e);
				return null;
			}
			else{
				window.location.href=e.url;
			}
		});
	}
	window._el=false;
	setTimeout(()=>{
		window._li=setInterval(()=>{
			if (window._el===true){
				document.querySelectorAll(".bg-r .bg")[0].style.height=`${Number.parseInt(r.getBoundingClientRect().height)+170}px`;
				document.querySelectorAll(".bg-r .bg .wr")[0].style.height=`${Number.parseInt(r.getBoundingClientRect().height)+120}px`;
				document.querySelectorAll(".bg-r .bg .wr")[0].classList.add("l");
				setTimeout(()=>{
					document.querySelectorAll(".bg-r .bg .wr .loading")[0].style.display="none";
				},1000);
				clearInterval(window._li);
			}
		},10);
	},750);
	let r=document.querySelectorAll(".bg-r .bg .wr .main")[0];
	dt=JSON.parse(r.innerHTML);
	r.innerHTML=`<div class="title">${dt.title}</div><div class="desc">${dt.desc}</div>`;
	for (let k of dt.data){
		if (typeof k==="string"){
			k.replace(/</gm,"&lt;").replace(/>/gm,"&gt;").replace(/&lt;(br|span)&gt;/gm,"<$1>");
			for (let i=0;i<k.length;i++){
				if (k.substring(i,i+3)=="```"){
					si=i;
					i+=3;
					while (k.substring(i,i+3)!="```"){
						i++;
					}
					k=`${k.substring(0,si)}<code class="c">${k.substring(si+3,i)}</code>${k.substring(i+3)}`;
					i+=9;
				}
				else if (k[i]=="*"&&k[i+1]=="*"){
					b=0;
					si=i;
					i+=2;
					while ((b%2)!=0||k[i]!="*"||k[i+1]!="*"){
						if (k[i]=="*"){
							b++;
						}
						i++;
					}
					k=`${k.substring(0,si)}<span class="b">${k.substring(si+2,i)}</span>${k.substring(i+2)}`;
					i=si+15;
				}
				else if (k[i]=="*"){
					si=i;
					i++;
					while (k[i]!="*"){
						i++;
					}
					k=`${k.substring(0,si)}<span class="i">${k.substring(si+1,i)}</span>${k.substring(i+1)}`;
					i=si+15;
				}
			}
			r.innerHTML+=`<p class="p">${k}</p>`
		}
	}
	window._el=true;
},false);
