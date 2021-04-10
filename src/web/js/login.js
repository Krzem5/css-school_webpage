document.addEventListener("DOMContentLoaded",()=>{
	let em=document.querySelector("#em-inp");
	let pw=document.querySelector("#pw-inp");
	let le=document.querySelector(".login");
	let ee=document.querySelector(".err");
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
				window.location.href="/";
			}
		});
	};
},false);
