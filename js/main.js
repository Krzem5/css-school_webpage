const SIDEBAR_DATA=[
	{
		"nm": "How to Code, Part I",
		"url": "/how-to-code.html"
	},
	{
		"nm": "How to Code, Part II",
		"url": "/how-to-code-2.html"
	}
];



document.addEventListener("DOMContentLoaded",()=>{
	if (!/^https?:\/\/[a-zA-Z0-9]+\.github\.io\//.test(window.location.href)){
		console.log(window.location.href);
		// window.location.href="https://krzem5.github.io/Css-School_Webpage/";
	}
	document.querySelectorAll(".bg .wr .top .icon")[0].onclick=()=>{
		window.location.href="/";
	};
	let se=document.querySelectorAll(".bg .wr .side")[0];
	for (let k of SIDEBAR_DATA){
		se.innerHTML+=`<div class="elem" onclick="document.location.href='${k.url}'">${k.nm}</div>`;
	}
},false);
