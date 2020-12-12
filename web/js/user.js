document.addEventListener("DOMContentLoaded",()=>{
	let be=document.querySelector(".bg");
	let wre=document.querySelector(".wr");
	let te=document.querySelector(".title");
	let se=document.querySelector(".side");
	document.title+=" "+window._dt.name;
	document.querySelector(".t").innerText=window._dt.name;
	document.querySelector(".img").src=window._dt.img;
	window.onresize=()=>{
		be.style.height="initial";
		wre.style.height="initial";
		let h=Math.max(document.querySelector(".main").getBoundingClientRect().height+140,document.body.getBoundingClientRect().height-70);
		be.style.height=`${h+70}px`;
		wre.style.height=`${h}px`;
	};
	window.onresize();
	setTimeout(window.onresize,10);
	setTimeout(window.onresize,100);
	document.querySelector(".icon").onclick=()=>{
		window.location.href="/";
	};
	document.querySelector(".txt").onclick=()=>{
		window.location.href=`/login?r=${encodeURIComponent(window.location.href)}`;
	};
	te.innerHTML=te.innerText.split("").map((e)=>{
		return `<span class="c">${e}</span>`;
	}).join("");
	fetch("/api/v1/popular",{}).then((e)=>e.json()).then((e)=>e.forEach((k)=>{
		se.innerHTML+=`<div class="elem" onclick="window.location.href='${k.url}'">${k.name}</div>`;
	}));
	fetch("/api/v1/user_data",{headers:{"authorization":`bearer ${localStorage._tk}`}}).then((e)=>e.json()).then((e)=>{
		if (e.status!=0){
			localStorage._tk=null;
		}
		else{
			document.querySelector(".account").classList.add("l");
			document.querySelector(".icn").onclick=()=>{
				window.location.href=`/user/${e.username}`;
			};
		}
	});
},false);
