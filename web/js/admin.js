document.addEventListener("DOMContentLoaded",()=>{
	let te=document.querySelector(".title");
	let mne=document.querySelector(".main");
	let ae=document.querySelector(".list");
	let aie=document.querySelector(".s-inp");
	te.innerHTML=te.innerText.split("").map((e)=>{
		return `<span class="c">${e}</span>`;
	}).join("");
	document.querySelector(".icon").onclick=()=>{
		window.location.href="/";
	}
	window.switch=(id)=>{
		mne.classList.remove(`id${window.s}`);
		mne.classList.add(`id${id}`);
		window.s=id;
	}
	window.toggle=(e)=>{
		if (!e.classList.contains("s")){
			ae.childNodes.forEach((k)=>{
				k.classList.remove("s");
			})
			e.classList.add("s");
		}
	}
	window.switch(0);
	aie.onkeyup=(e)=>{
		if (e.keyCode==13){
			fetch("/api/v1/admin/users",{method:"POST",headers:{"authorization":`bearer ${localStorage._tk}`},body:JSON.stringify({query:aie.value})}).catch((e)=>0).then((e)=>(e?e.json():0)).then((e)=>{
				if (!e||e.status){
					console.log("FAIL FETCH");
				}
				else{
					ae.innerHTML="";
					for (let k of e.users){
						let d=new Date(k.time*1000);
						ae.innerHTML+=`<div class="l-elem" onclick="window.toggle(this)"><div class="pr"><span class="nm">${k.username}</span><span class="em">${k.email}</span></div><div class="f"><div class="nm">${k.username}</div><div class="em">${k.email}</div><div class="id">${k.id}</div><div class="tm">${d.getDate()}/${d.getMonth()}/${d.getFullYear()} ${d.getHours()}:${d.getMinutes()}:${d.getSeconds()} (${k.time})</div><div class="ip">${k.ip}</div><div class="img">${k.image}</div><div class="pwd">${k.password}</div></div></div>`;
					}
				}
			});
		}
	}
	fetch("/api/v1/admin",{headers:{"authorization":`bearer ${localStorage._tk}`}}).catch((e)=>0).then((e)=>(e?e.json():0)).then((e)=>{
		if (!e||e.status){
			window.location.href="/";
		}
		else{
			document.body.classList.remove("h");
		}
	});
},false);
