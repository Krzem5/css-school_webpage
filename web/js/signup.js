document.addEventListener("DOMContentLoaded",()=>{
	let te=document.querySelector(".top");
	let un=document.querySelector("#un-inp");
	let em=document.querySelector("#em-inp");
	let pw=document.querySelector("#pw-inp");
	let pwr=document.querySelector("#pwr-inp");
	let le=document.querySelector(".signup");
	let ee=document.querySelector(".err");
	function _check_btn(){
		if (le.r==15){
			le.classList.add("r");
		}
		else{
			le.classList.remove("r");
		}
	}
	te.innerHTML=te.innerText.split("").map((e)=>{
		return `<span class="c">${e}</span>`;
	}).join("");
	un.onkeydown=un.onkeyup=()=>{
		if (3<=un.value.length&&un.value.length<=24){
			le.r|=1;
		}
		else{
			le.r&=~1;
		}
		_check_btn();
	};
	em.onkeydown=em.onkeyup=()=>{
		if (/^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/.test(em.value)==true){
			le.r|=2;
		}
		else{
			le.r&=~2;
		}
		_check_btn();
	};
	pw.onkeydown=pw.onkeyup=()=>{
		pwr.onkeyup();
		if (6<=pw.value.length&&pw.value.length<=64){
			le.r|=4;
		}
		else{
			le.r&=~4;
		}
		_check_btn();
	};
	pwr.onkeydown=pwr.onkeyup=()=>{
		if (6<=pwr.value.length&&pwr.value.length<=64&&pwr.value==pw.value){
			le.r|=8;
		}
		else{
			le.r&=~8;
		}
		_check_btn();
	};
	le.onclick=()=>{
		if (le.classList.contains("r")){
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
				}
				else{
					window.location.pathname="/login";
				}
			});
		}
	};
},false);
