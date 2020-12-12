document.addEventListener("DOMContentLoaded",()=>{
	let te=document.querySelector(".title");
	let mne=document.querySelector(".main");
	let aie=document.querySelector(".s-inp");
	let ae=document.querySelector(".list");
	let aue=document.querySelector(".user-wr");
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
	window.switch(0);
	window.show=(nm,em,id,tm,ip,img,pwd,ev,a)=>{
		aue.classList.add("s");
		aue.innerHTML=`<div class="user"><div class="u-elem"><span class="k">Name:</span><span class="v nm" onclick="window.copy(this)">${nm}</span></div><div class="u-elem"><span class="k">Email:</span><span class="v em" onclick="window.copy(this)">${em}</span></div><div class="u-elem"><span class="k">ID:</span><span class="v id" onclick="window.copy(this)">${id}</span></div><div class="u-elem"><span class="k">Join Date:</span><span class="v tm" onclick="window.copy(this)">${tm}</span></div><div class="u-elem"><span class="k">Join IP:</span><span class="v ip" onclick="window.copy(this)">${ip}</span></div><div class="u-elem"><span class="k">Image:</span><span class="v img" onclick="window.copy(this)">${img}</span></div><div class="u-elem"><span class="k">Password:</span><span class="v pwd" onclick="window.copy(this)">${pwd}</span></div><div class="u-elem"><span class="k">Tags:</span><span class="v tg" onclick="window.copy(this)"><span class="${(ev?"s":"")}">verified-email</span> <span class="${(a?"s":"")}">admin</span></span></div></div>`;
	}
	window.copy=(e)=>{
		navigator.clipboard.writeText(e.innerText);
	}
	document.body.onkeydown=(e)=>{
		if (e.keyCode==27){
			aue.classList.remove("s");
		}
	}
	aie.onkeyup=(e)=>{
		function pad(n){
			n=Number(n).toString();
			if (n.length<2){
				n="0"+n;
			}
			return n;
		}
		if (e.keyCode==13){
			fetch("/api/v1/admin/users",{method:"POST",headers:{"authorization":`bearer ${localStorage._tk}`},body:JSON.stringify({query:aie.value})}).catch((e)=>0).then((e)=>(e?e.json():0)).then((e)=>{
				if (!e||e.status){
					console.log("FAIL FETCH");
				}
				else{
					ae.innerHTML="";
					for (let k of e.users){
						let d=new Date(k.time*1000);
						ae.innerHTML+=`<div class="l-elem" onclick="window.show('${k.username}','${k.email}','${k.id}','${pad(d.getMonth()+1)}/${pad(d.getDate())}/${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())} (${k.time})','${k.ip}','${k.image}','${k.password}',${k.email_verified},${k.admin})"><div class="pr"><span class="nm">${k.username}</span><span class="em">${k.email}</span></div></div>`;
					}
				}
			});
		}
	}
	fetch("/api/v1/admin",{headers:{"authorization":`bearer ${localStorage._tk}`}}).catch((e)=>0).then((e)=>(e?e.json():0)).then((e)=>{
		if (!e||e.status){
			// window.location.href="/";
		}
		// else{
			document.body.classList.remove("h");
		// }
	});
},false);
