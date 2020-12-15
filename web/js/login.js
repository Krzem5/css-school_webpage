document.addEventListener("DOMContentLoaded",()=>{
	let te=document.querySelector(".top");
	let em=document.querySelector("#em-inp");
	let pw=document.querySelector("#pw-inp");
	let le=document.querySelector(".login");
	let ee=document.querySelector(".err");
	te.innerHTML=te.innerText.split("").map((e)=>{
		return `<span class="c">${e}</span>`;
	}).join("");
	le.onclick=()=>{
		fetch("/api/v1/auth/login",{method:"POST",body:JSON.stringify({email:em.value,password:pw.value})}).catch((e)=>0).then((e)=>(e?e.json():0)).then((e)=>{
			if (!e||e.status){
				if (ee.t){
					clearTimeout(ee.t);
				}
				ee.classList.add("e");
				ee.t=setTimeout(()=>{
					ee.classList.remove("e");
				},5e3);
				pw.value="";
			}
			else{
				let rd=false;
				if (window.location.search.split("?").length>1&&window.location.search.split("?")[1].length!=0){
					for (let e of window.location.search.split("?")[1].split("&")){
						if (e.split("=")[0]=="r"){
							window.location.href=decodeURIComponent(e.split("=")[1]);
							rd=true;
							break;
						}
					};
				}
				if (rd==false){
					window.location.href="/";
				}
			}
		});
	};
},false);
