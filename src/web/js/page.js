document.addEventListener("DOMContentLoaded",()=>{
	let bg=document.querySelector(".bg");
	let wr=document.querySelector(".wr");
	let se=document.querySelector(".side");
	window.onresize=()=>{
		bg.style.height="initial";
		wr.style.height="initial";
		let h=Math.max(document.querySelector(".main").getBoundingClientRect().height+140,document.body.getBoundingClientRect().height-70);
		bg.style.height=`${h+70}px`;
		wr.style.height=`${h}px`;
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
		window.location.href=`/login`;
	};
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
