document.addEventListener("DOMContentLoaded",()=>{
	let be=document.querySelector(".bg");
	let wre=document.querySelector(".wr");
	let te=document.querySelector(".title");
	let se=document.querySelector(".side");
	let ie=document.querySelector(".img");
	document.title+=" "+window._dt.name;
	document.querySelector(".nm-t").innerText=window._dt.name;
	if (window._dt.img){
		document.querySelector(".a-img").classList.remove("a-img-h");
		ie.style.backgroundImage=`url(${window._dt.img})`;
	}
	if (window._dt.verified){
		document.querySelector(".v").classList.remove("v-h");
	}
	window.onresize=()=>{
		be.style.height="initial";
		wre.style.height="initial";
		let h=Math.max(document.querySelector(".list").getBoundingClientRect().height+310,document.body.getBoundingClientRect().height-70);
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
	fetch("/api/v1/popular?count=10").then((e)=>e.json()).then((e)=>e.forEach((k)=>{
		se.innerHTML+=`<div class="elem" onclick="window.location.href='${k.url}'">${k.name}</div>`;
	}));
	fetch("/api/v1/user_data").then((e)=>e.json()).then((e)=>{
		if (!e.status){
			document.querySelector(".account").classList.add("l");
			document.querySelector(".account-i").onclick=()=>{
				window.location.href=`/user/${e.username}`;
			};
		}
	});
},false);
