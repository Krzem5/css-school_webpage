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
	document.querySelectorAll(".bg-r .bg .wr .top .icon")[0].onclick=()=>{
		window.location.href="/";
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
},false);
