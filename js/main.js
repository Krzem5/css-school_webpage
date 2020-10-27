const SIDEBAR_DATA=[
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
	document.querySelectorAll(".bg .wr .top .icon")[0].onclick=()=>{
		window.location.href="/Css-School_Webpage";
	};
	let te=document.querySelectorAll(".bg .wr .top .title")[0];
	te.innerHTML=te.innerText.split("").map((e)=>{
		return `<span class="c">${e}</span>`;
	}).join("");
	let se=document.querySelectorAll(".bg .wr .side")[0];
	for (let k of SIDEBAR_DATA){
		se.innerHTML+=`<div class="elem" onclick="window._load('${k.url}'">${k.nm}</div>`;
	}
	window._load=(u)=>{
		fetch(`/Css-School_Webpage${(!/^[\\\/]/.test(u[0])?"/":"")+u}`).then((e)=>{
			if (e.ok==false){
				console.log(e);
				return null;
			}
			return e.text();
		}).then((txt)=>{
			console.log(txt);
		});
	}
	window._load("main.html");
},false);
