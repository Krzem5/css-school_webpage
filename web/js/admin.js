document.addEventListener("DOMContentLoaded",()=>{
	let LOCATION_ARR=["accounts","pages","logs"];
	let te=document.querySelector(".title");
	let mne=document.querySelector(".main");
	let aie=document.querySelector(".s-inp");
	let ae=document.querySelector(".list");
	let aue=document.querySelector(".user-wr");
	let le=document.querySelector(".logs");
	let s=null;
	let t;
	let t2;
	let t3;
	function _start_socket(){
		fetch("/api/v1/admin/logs").catch((e)=>0).then((e)=>(e?e.json():0)).then((e)=>{
			if (!e||e.status){
				location.reload();
			}
			s=new WebSocket(`wss://krzem.herokuapp.com/api/v1/admin/logs/${e.url}`);
			s.onclose=()=>{
				if (s){
					_start_socket();
				}
			}
			s.onmessage=(e)=>{
				e.data.text().then((e)=>{
					if (e=="null"){
						return;
					}
					t=e[0];
					e=e.substring(1);
					if (t==0){
						t2=e.split("] ")[0];
						le.innerHTML+=`<div class="msg"><span class="t">${t2}] </span><span class="m">${e.substring(t2.length+2)}</span></div>`;
						le.removeChild(le.children[0]);
					}
					else{
						for (t of e.split("\n")){
							t2=t.split("] ")[0];
							le.innerHTML+=`<div class="msg"><span class="t">${t2}] </span><span class="m">${t.substring(t2.length+2)}</span></div>`;
						}
					}
					le.scroll(0,le.scrollHeight);
				});
			}
			s.onerror=(e)=>{
				e.stopImmediatePropagation();
				e.stopPropagation();
				e.preventDefault();
			}
		});
	}
	te.innerHTML=te.innerText.split("").map((e)=>{
		return `<span class="c">${e}</span>`;
	}).join("");
	document.querySelector(".icon").onclick=()=>{
		location.hash="";
		location.href="/";
	}
	window.switch=(id,nh)=>{
		if (window.s==id){
			return;
		}
		location.hash=nh||LOCATION_ARR[id];
		aie.value="";
		ae.innerHTML="";
		le.innerHTML="";
		aue.classList.remove("s");
		mne.classList.remove(`id${window.s}`);
		mne.classList.add(`id${id}`);
		window.s=id;
		if (s){
			t=s;
			s=null;
			t.close();
		}
		if (id==0){
			aie.onkeyup();
		}
		if (id==2){
			_start_socket();
		}
	}
	window.change_tag=(t,id)=>{
		fetch("/api/v1/admin/flip_tag",{method:"PUT",body:JSON.stringify({tag:t,id:id})}).catch((e)=>0).then((e)=>(e?e.json():0)).then((e)=>{
			if (e&&!e.status){
				aue.classList.remove("s");
				aie.onkeyup();
			}
			else{
				location.hash="";
				location.href="/";
			}
		});
	}
	window.show=(nm,em,id,tm,ip,tk,tke,img,pwd,ev,a,d)=>{
		location.hash="accounts-"+id;
		aue.classList.add("s");
		aue.innerHTML=`<div class="user"><div class="u-elem"><span class="k">Name:</span><span class="v nm" onclick="window.copy(this)">${nm}</span></div><div class="u-elem"><span class="k">Email:</span><span class="v em" onclick="window.copy(this)">${em}</span></div><div class="u-elem"><span class="k">ID:</span><span class="v id" onclick="window.copy(this)">${id}</span></div><div class="u-elem"><span class="k">Join Date:</span><span class="v tm" onclick="window.copy(this)">${tm}</span></div><div class="u-elem"><span class="k">Join IP:</span><span class="v ip" onclick="window.copy(this)">${ip}</span></div><div class="u-elem"><span class="k">Log-In Token:</span><span class="v tk" onclick="window.copy(this)">${(tk?tk+" ("+tke+")":"none")}</span></div><div class="u-elem"><span class="k">Image:</span><span class="v img" onclick="window.copy(this)">${img}</span></div><div class="u-elem"><span class="k">Password:</span><span class="v pwd" onclick="window.copy(this)">${pwd}</span></div><div class="u-elem"><span class="k">Tags:</span><span class="v tg" onclick="window.copy(this)"><span class="${(d?"s":"")}">disabled</span> <span class="${(tk?"s":"")}">logged-in</span> <span class="${(ev?"s":"")}">verified-email</span> <span class="${(a?"s":"")}">admin</span></span></div><input class="ch-nm" type="text" placeholder="Name" value="${nm}" minlength="3" maxlength="24"><div class="ch-t"><span class="${(d?"s":"")}" onclick="window.change_tag(0,'${id}')">disabled</span> <span class="${(tk?"s\" onclick=\"window.change_tag(1,'"+id+"')":"")}">logged-in</span> <span class="${(ev?"s":"")}" onclick="window.change_tag(2,'${id}')">verified-email</span> <span class="${(a?"s":"")}" onclick="window.change_tag(3,'${id}')">admin</span></div></div>`;
		t=document.querySelector(".ch-nm");
		t.onkeyup=(e)=>{
			if (e.keyCode==13){
				fetch("/api/v1/admin/set_name",{method:"PUT",body:JSON.stringify({id:id,name:t.value})}).catch((e)=>0).then((e)=>(e?e.json():0)).then((e)=>{
					if (e&&!e.status){
						aue.classList.remove("s");
						aie.onkeyup();
					}
					else{
						location.hash="";
						location.href="/";
					}
				});
			}
		}
	}
	window.copy=(e)=>{
		navigator.clipboard.writeText(e.innerText);
	}
	document.body.onkeydown=(e)=>{
		if (e.keyCode==27&&window.s==0){
			aue.classList.remove("s");
			location.hash="accounts";
		}
	}
	aie.onkeyup=(oe)=>{
		function pad(n){
			n=Number(n).toString();
			if (n.length<2){
				n="0"+n;
			}
			return n;
		}
		if (!oe||oe.keyCode==13){
			fetch("/api/v1/admin/users",{method:"POST",body:JSON.stringify({query:aie.value})}).catch((e)=>0).then((e)=>(e?e.json():0)).then((e)=>{
				if (!e||e.status){
					location.hash="";
					location.href="/";
				}
				else{
					ae.innerHTML="";
					oe=(!oe?location.hash.split("-"):null);
					if (oe&&oe.length>1){
						oe=oe[1];
					}
					for (t of e.users){
						t2=new Date(t.time*1000);
						t3=new Date(t.token_end*1000);
						ae.innerHTML+=`<div class="l-elem" onclick="window.show('${t.username}','${t.email}','${t.id}','${pad(t2.getMonth()+1)}/${pad(t2.getDate())}/${t2.getFullYear()} ${pad(t2.getHours())}:${pad(t2.getMinutes())}:${pad(t2.getSeconds())} (${t.time})','${t.ip}',${(t.token?"\'"+t.token+"\'":null)},'${pad(t3.getMonth()+1)}/${pad(t3.getDate())}/${t3.getFullYear()} ${pad(t3.getHours())}:${pad(t3.getMinutes())}:${pad(t3.getSeconds())} (${t.token_end})','${t.image}','${t.password}',${t.email_verified},${t.admin},${t.disabled})"><div class="pr"><span class="nm">${t.username}</span><span class="em">${t.email}</span></div></div>`;
						if (oe==t.id){
							ae.childNodes[ae.childElementCount-1].onclick();
							oe=-1;
						}
					}
					if (oe!=-1){
						location.hash="accounts";
					}
				}
			});
		}
	}
	window.switch(Math.max(LOCATION_ARR.indexOf(location.hash.substring(1).split("-")[0].toLowerCase()),0),location.hash);
},false);
