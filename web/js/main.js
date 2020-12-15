document.addEventListener("DOMContentLoaded",()=>{
	let te=document.querySelector(".title");
	let bge=document.querySelector(".bg");
	let wre=document.querySelector(".wr");
	let le=document.querySelector(".list");
	window.onresize=()=>{
		bge.style.height="initial";
		wre.style.height="initial";
		let h=Math.max(le.getBoundingClientRect().height+305,document.body.getBoundingClientRect().height-70);
		bge.style.height=`${h+70}px`;
		wre.style.height=`${h}px`;
	};
	window.onresize();
	document.querySelector(".icon").onclick=()=>{
		window.location.href="/";
	};
	document.querySelector(".txt").onclick=()=>{
		window.location.href=`/login?r=${encodeURIComponent(window.location.href)}`;
	};
	te.innerHTML=te.innerText.split("").map((e)=>{
		return `<span class="c">${e}</span>`;
	}).join("");
	fetch("/api/v1/popular?count=50").then((e)=>e.json()).then((e)=>{
		e.forEach((k)=>{
			le.innerHTML+=`<div class="e"><div class="e-wr"><div class="t" onclick="window.location.href='${k.url}'">${k.name}</div><div class="a" onclick="window.location.href='/user/${k.author}'">By <span>@${k.author}</span></div></div></div>`;
		});
		window.onresize();
		setTimeout(window.onresize,10);
		setTimeout(window.onresize,100);
		setTimeout(window.onresize,200);
		setTimeout(window.onresize,300);
		setTimeout(window.onresize,400);
		setTimeout(window.onresize,500);
	});
	fetch("/api/v1/user_data").then((e)=>e.json()).then((e)=>{
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
