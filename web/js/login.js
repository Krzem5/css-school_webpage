document.addEventListener("DOMContentLoaded",()=>{
	let te=document.querySelectorAll(".bg-r .bg .wr .top")[0];
	te.innerHTML=te.innerText.split("").map((e)=>{
		return `<span class="c">${e}</span>`;
	}).join("");
	let em=document.querySelectorAll(".bg-r .bg .wr .email #em-inp")[0];
	let pw=document.querySelectorAll(".bg-r .bg .wr .pwd #pw-inp")[0];
	let le=document.querySelectorAll(".bg-r .bg .wr .main .login")[0];
	le.onclick=()=>{
		if (le.classList.contains("r")){
			fetch("/api/v1/auth/login",{method:"POST",body:JSON.stringify({email:em.value,password:pw.value})}).then((e)=>e.json()).then((e)=>{
				if (e.status!=0){
					console.error(`Login Failed (status=${e.status})`);
				}
				else{
					localStorage._tk=e.token;
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
		}
	};
},false);
