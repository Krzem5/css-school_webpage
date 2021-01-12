document.addEventListener("DOMContentLoaded",()=>{
	let LOCATION_ARR=["accounts","pages","logs"];
	let te=document.querySelector(".title");
	let mne=document.querySelector(".main");
	let aie=document.querySelector(".a-s-inp");
	let ae=document.querySelector(".a-list");
	let aue=document.querySelector(".user-wr");
	let pie=document.querySelector(".p-s-inp");
	let pe=document.querySelector(".p-list");
	let ppe=document.querySelector(".page-wr");
	let le=document.querySelector(".logs");
	let s=null;
	let t;
	let t2;
	let t3;
	function _pad_num(n){
		n=Number(n).toString();
		if (n.length<2){
			n="0"+n;
		}
		return n;
	}
	function _start_socket(){
		fetch("/api/v1/admin/logs").catch((e)=>0).then((e)=>(e?e.json():0)).then((e)=>{
			if (!e||e.status||e.code){
				location.hash="";
				location.href="/";
				return;
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
						le.innerHTML+=`<div class="l-msg"><span class="l-msg-t">${t2}] </span><span class="l-msg-m">${e.substring(t2.length+2)}</span></div>`;
						le.removeChild(le.children[0]);
					}
					else{
						for (t of e.split("\n")){
							t2=t.split("] ")[0];
							le.innerHTML+=`<div class="l-msg"><span class="l-msg-t">${t2}] </span><span class="l-msg-m">${t.substring(t2.length+2)}</span></div>`;
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
		pie.value=""
		ae.innerHTML="";
		pe.innerHTML="";
		le.innerHTML="";
		aue.classList.remove("s");
		if (window.s){
			mne.children[window.s].classList.remove("main-v");
		}
		mne.children[id].classList.add("main-v");
		window.s=id;
		if (s){
			t=s;
			s=null;
			t.close();
		}
		if (id==0){
			aie.onkeyup();
		}
		if (id==1){
			pie.onkeyup();
		}
		else{
			_start_socket();
		}
	}
	window.change_tag=(t,id)=>{
		if (id<0){
			return;
		}
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
		aue.innerHTML=`<div class="user"><div class="u-elem"><span class="u-elem-k">Name:</span><span class="u-elem-v u-nm" onclick="window.copy(this)">${nm}</span></div><div class="u-elem"><span class="u-elem-k">Email:</span><span class="u-elem-v u-em" onclick="window.copy(this)">${em}</span></div><div class="u-elem"><span class="u-elem-k">ID:</span><span class="u-elem-v u-id" onclick="window.copy(this)">${id}</span></div><div class="u-elem"><span class="u-elem-k">Join Date:</span><span class="u-elem-v u-tm" onclick="window.copy(this)">${tm}</span></div><div class="u-elem"><span class="u-elem-k">Join IP:</span><span class="u-elem-v u-ip" onclick="window.copy(this)">${ip}</span></div><div class="u-elem"><span class="u-elem-k">Log-In Token:</span><span class="u-elem-v u-tk" onclick="window.copy(this)">${(tk?tk+" ("+tke+")":"none")}</span></div><div class="u-elem"><span class="u-elem-k">Image:</span><span class="u-elem-v u-img" onclick="window.copy(this)">${img}</span></div><div class="u-elem"><span class="u-elem-k">Password:</span><span class="u-elem-v u-pwd" onclick="window.copy(this)">${pwd}</span></div><div class="u-elem"><span class="u-elem-k">Tags:</span><span class="u-elem-v u-tg" onclick="window.copy(this)"><span class="${(d?"u-tg-s":"")}">disabled</span> <span class="${(tk?"u-tg-s":"")}">logged-in</span> <span class="${(ev?"u-tg-s":"")}">verified-email</span> <span class="${(a?"u-tg-s":"")}">admin</span></span></div><input class="u-ch-nm" type="text" placeholder="Name" value="${nm}" minlength="3" maxlength="24"><div class="u-ch-t"><span class="${(d?"u-ch-t-s":"")}" onclick="window.change_tag(0,'${id}')">disabled</span> <span class="${(tk?"u-ch-t-s":"")}" onclick="window.change_tag(${(tk?1:-1)},'${id}')">logged-in</span> <span class="${(ev?"u-ch-t-s":"")}" onclick="window.change_tag(2,'${id}')">verified-email</span> <span class="${(a?"u-ch-t-s":"")}" onclick="window.change_tag(3,'${id}')">admin</span></div></div>`;
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
	window.show_pg=(id,t,d,tm,a)=>{
		location.hash="pages-"+id;
		ppe.classList.add("s");
		ppe.innerHTML=`<div class="page"><div class="p-elem"><span class="p-elem-k">ID:</span><span class="p-elem-v p-id" onclick="window.copy(this)">${id}</span></div><div class="p-elem"><span class="p-elem-k">Title:</span><span class="p-elem-v p-t" onclick="window.copy(this)">${t}</span></div><div class="p-elem"><span class="p-elem-k">Desc:</span><span class="p-elem-v p-d" onclick="window.copy(this)">${d}</span></div><div class="p-elem"><span class="p-elem-k">Creation Date:</span><span class="p-elem-v p-tm" onclick="window.copy(this)">${tm}</span></div><div class="p-elem"><span class="p-elem-k">Author:</span><span class="p-elem-v p-a" onclick="window.copy(this)">${a}</span></div></div>`;
	}
	window.copy=(e)=>{
		navigator.clipboard.writeText(e.innerText);
	}
	document.body.onkeydown=(e)=>{
		if (e.keyCode==27){
			if (!window.s){
				aue.classList.remove("s");
				location.hash="accounts";
			}
			else if (window.s==1){
				ppe.classList.remove("s");
				location.hash="pages";
			}
		}
	}
	aie.onkeyup=(oe)=>{
		if (!oe||oe.keyCode==13){
			fetch("/api/v1/admin/users",{method:"POST",body:JSON.stringify({query:aie.value})}).catch((e)=>0).then((e)=>(e?e.json():0)).then((e)=>{
				if (!e||e.status||e.code){
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
						t2=new Date(t.time*1e3);
						t3=new Date(t.token_end*1e3);
						ae.innerHTML+=`<div class="a-l-elem" onclick="window.show('${t.username}','${t.email}','${t.id}','${_pad_num(t2.getMonth()+1)}/${_pad_num(t2.getDate())}/${t2.getFullYear()} ${_pad_num(t2.getHours())}:${_pad_num(t2.getMinutes())}:${_pad_num(t2.getSeconds())} (${t.time})','${t.ip}',${(t.token?"\'"+t.token+"\'":null)},'${_pad_num(t3.getMonth()+1)}/${_pad_num(t3.getDate())}/${t3.getFullYear()} ${_pad_num(t3.getHours())}:${_pad_num(t3.getMinutes())}:${_pad_num(t3.getSeconds())} (${t.token_end})','${t.image}','${t.password}',${t.email_verified},${t.admin},${t.disabled})"><div class="a-l-elem-pr"><span class="a-l-elem-pr-nm">${t.username}</span><span class="a-l-elem-pr-em">${t.email}</span></div></div>`;
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
	pie.onkeyup=(oe)=>{
		if (!oe||oe.keyCode==13){
			fetch("/api/v1/admin/pages",{method:"POST",body:JSON.stringify({query:pie.value})}).catch((e)=>0).then((e)=>(e?e.json():0)).then((e)=>{
				if (!e||e.status||e.code){
					location.hash="";
					location.href="/";
				}
				else{
					pe.innerHTML="";
					oe=(!oe?location.hash.split("-"):null);
					if (oe&&oe.length>1){
						oe=oe.slice(1).join("-");
					}
					for (t of e.users){
						t2=new Date(t.time*1e3);
						pe.innerHTML+=`<div class="p-l-elem" onclick="window.show_pg('${t.id}','${t.title}','${t.desc}','${_pad_num(t2.getMonth()+1)}/${_pad_num(t2.getDate())}/${t2.getFullYear()} ${_pad_num(t2.getHours())}:${_pad_num(t2.getMinutes())}:${_pad_num(t2.getSeconds())} (${t.time})','${t.author}')"><div class="p-l-elem-pr"><span class="p-l-elem-pr-id">${t.id}</span><span class="p-l-elem-pr-tt">${t.title}</span></div></div>`;
						if (oe==t.id){
							pe.childNodes[pe.childElementCount-1].onclick();
							oe=-1;
						}
					}
					if (oe!=-1){
						location.hash="pages";
					}
				}
			});
		}
	}
	window.switch(Math.max(LOCATION_ARR.indexOf(location.hash.substring(1).split("-")[0].toLowerCase()),0),location.hash);
},false);
