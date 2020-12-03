fetch.loop=(n,url,p)=>{
	return fetch(url,p).catch((r)=>{
		r.ok=false;
		return r;
	}).then((r)=>{
		if (!r.ok){
			if (n==1){
				throw new Error("API Request Error");
			}
			return fetch.loop(n-1,url,p);
		}
		return r;
	});
}
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
			fetch.loop(3,"/api/v1/auth/login",{method:"POST",body:JSON.stringify({email:em.value,password:pw.value})}).then((e)=>e.json()).then((e)=>{
				if (e.status!=0){
					console.error(`Login Failed (status=${e.status})`);
				}
				else{
					localStorage._tk=e.token;
				}
			});
		}
	};
},false);
