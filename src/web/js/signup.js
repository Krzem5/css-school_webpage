document.addEventListener("DOMContentLoaded",()=>{
	let un=document.querySelector("#un-inp");
	let em=document.querySelector("#em-inp");
	let pw=document.querySelector("#pw-inp");
	let pwr=document.querySelector("#pwr-inp");
	let le=document.querySelector(".signup");
	let ee=document.querySelector(".err");
	le.onclick=()=>{
		if (pwr.value!=pw.value){
			ee.innerText="Password doesn't match";
			if (ee.t){
				clearTimeout(ee.t);
			}
			ee.classList.add("e");
			ee.t=setTimeout(()=>{
				ee.classList.remove("e");
			},5e3);
			pwr.value="";
			return;
		}
		fetch("/api/v1/auth/signup",{method:"POST",body:JSON.stringify({username:un.value,email:em.value,password:pw.value})}).catch((e)=>0).then((e)=>(e?e.json():0)).then((e)=>{
			if (!e||e.status){
				if (!e){
					ee.innerText="An Unknown Error Occured";
				}
				else{
					ee.innerText=["Username Too Short","Username Too Long","Username Contains Invalid Characters","Username Already Used","Invalid Email","Email Already Used","Password Too Short","Password Too Long","Password Contains Invalid Characters"][e.status-1];
				}
				if (ee.t){
					clearTimeout(ee.t);
				}
				ee.classList.add("e");
				ee.t=setTimeout(()=>{
					ee.classList.remove("e");
				},5e3);
				pw.value="";
				pwr.value="";
				return;
			}
			window.location.pathname="/login";
		});
	};
},false);
