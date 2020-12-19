document.addEventListener("DOMContentLoaded",()=>{
	window.onresize=()=>{
		document.querySelector(".bg").style.height="initial";
		document.querySelector(".wr").style.height="initial";
		let h=Math.max(document.querySelector(".main").getBoundingClientRect().height+140,document.body.getBoundingClientRect().height-70);
		document.querySelector(".bg").style.height=`${h+70}px`;
		document.querySelector(".wr").style.height=`${h}px`;
	};
	window.onresize();
	setTimeout(window.onresize,10);
	setTimeout(window.onresize,100);
	setTimeout(window.onresize,200);
	setTimeout(window.onresize,300);
	setTimeout(window.onresize,400);
	setTimeout(window.onresize,500);
	document.querySelector(".icon").onclick=()=>{
		window.location.href="/";
	};
	document.querySelector(".txt").onclick=()=>{
		window.location.href=`/login?r=${encodeURIComponent(window.location.href)}`;
	};
	let te=document.querySelector(".title");
	te.innerHTML=te.innerText.split("").map((e)=>{
		return `<span class="c">${e}</span>`;
	}).join("");
	let se=document.querySelector(".side");
	fetch("/api/v1/popular?count=10").then((e)=>e.json()).then((e)=>e.forEach((k)=>{
		se.innerHTML+=`<div class="elem" onclick="window.location.href='${k.url}'">${k.name}</div>`;
	}));
	fetch("/api/v1/user_data").then((e)=>e.json()).then((e)=>{
		if (!e.error&&!e.status){
			document.querySelector(".account").classList.add("l");
			document.querySelector(".account-i").onclick=()=>{
				window.location.href=`/user/${e.username}`;
			};
		}
	});
},false);
