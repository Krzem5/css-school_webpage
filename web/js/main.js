fetch.loop=(n,...a)=>{
	return fetch(...a).catch((r)=>{
		r.ok=false;
		return r;
	}).then((r)=>{
		if (!r.ok){
			if (n==1){
				throw new Error("API Request Error");
			}
			return fetch.loop(n-1,...a);
		}
		return r;
	});
}
document.addEventListener("DOMContentLoaded",()=>{
	window.onresize=()=>{
		document.querySelectorAll(".bg-r .bg")[0].style.height="initial";
		document.querySelectorAll(".bg-r .bg .wr")[0].style.height="initial";
		let h=document.querySelectorAll(".bg-r .bg .wr .main")[0].getBoundingClientRect().height+140;
		document.querySelectorAll(".bg-r .bg")[0].style.height=`${h+70}px`;
		document.querySelectorAll(".bg-r .bg .wr")[0].style.height=`${h}px`;
	};
	window.onresize();
	setTimeout(window.onresize,10);
	document.querySelectorAll(".bg-r .bg .wr .top .icon")[0].onclick=()=>{
		window.location.href="/";
	};
	document.querySelectorAll(".bg-r .bg .wr .top .account .txt")[0].onclick=()=>{
		window.location.href=`/login?r=${encodeURIComponent(window.location.href)}`;
	};
	let te=document.querySelectorAll(".bg-r .bg .wr .top .title")[0];
	te.innerHTML=te.innerText.split("").map((e)=>{
		return `<span class="c">${e}</span>`;
	}).join("");
	let se=document.querySelectorAll(".bg-r .bg .wr .side")[0];
	fetch.loop(3,"/api/v1/popular",{}).then((e)=>e.json()).then((e)=>e.forEach((k)=>{
		se.innerHTML+=`<div class="elem" onclick="window.location.href='${k.url}'">${k.name}</div>`;
	}));
	fetch.loop(3,"/api/v1/user_data",{headers:{"authorization":`bearer ${localStorage._tk}`}}).then((e)=>e.json()).then((e)=>{
		console.log(e);
	});
},false);
