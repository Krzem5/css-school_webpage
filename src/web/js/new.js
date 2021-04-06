document.addEventListener("DOMContentLoaded",()=>{
	let bre=document.querySelector(".bg-r");
	let be=document.querySelector(".bg");
	let wre=document.querySelector(".wr");
	let ce=document.querySelector(".code-e");
	let pe=document.querySelector(".preview");
	let ee=document.querySelector(".e-err");
	window.onresize=()=>{
		let sc=bre.scrollTop;
		be.style.height="initial";
		wre.style.height="initial";
		let h=Math.max(ce.scrollHeight+310,pe.getBoundingClientRect().height+310,document.body.getBoundingClientRect().height-70);
		be.style.height=`${h+70}px`;
		wre.style.height=`${h}px`;
		bre.scroll(0,sc);
	};
	window.onresize();
	setTimeout(window.onresize,10);
	setTimeout(window.onresize,100);
	document.querySelector(".icon").onclick=()=>{
		window.location.href="/";
	};
	let u=true;
	document.body.onkeydown=(e)=>{
		if (e.key=="s"&&e.ctrlKey){
			if (u&&!window._ic){
				fetch("/api/v1/save",{method:"PUT",body:JSON.stringify(window._n)}).catch((e)=>0).then((e)=>(e?e.json():0)).then((e)=>{
					if (!e||e.status){
						ee.innerText=(e&&e.status?{11:"Invalid Login Credentials",17:"Page ID Already Used",18:"Page Title Already Used"}[e.status]:"Unable to Connect to the Server");
						if (ee.t){
							clearTimeout(ee.t);
						}
						ee.classList.add("e");
						ee.t=setTimeout(()=>{
							ee.classList.remove("e");
						},5e3);
					}
				});
			}
			u=false;
			e.stopImmediatePropagation();
			e.stopPropagation();
			e.preventDefault();
		}
	}
	window._le=0;
	window._e=(url,i)=>{
		if (i==window._le){
			pe.innerHTML=`<div class="err">Unable to Load Image '${url}'</div>`;
		}
	}
	window._l=(i)=>{
		if (i==window._le){
			window._ic--;
		}
	}
	ce.onkeydown=window.onresize;
	ce.onkeyup=(e)=>{
		if (e&&(!e.altKey&&!e.ctrlKey&&!e.metaKey&&!e.shiftKey&&e.key.length==1||e.key=="Backspace")){
			u=true;
			window.onresize();
		}
		let v=ce.value;
		let id=v.match(/^\s*\/\*\s*id\s*:\s*([a-z0-9\-]+?)\s*\*\/\s*$/m);
		if (id==null){
			pe.innerHTML=`<div class="err">Missing 'id' Value</div>`;
			return;
		}
		id=id[1].trim();
		let t=v.match(/^\s*\/\*\s*title\s*:\s*([a-zA-Z0-9_\- ]+?)\s*\*\/\s*$/m);
		if (t==null){
			pe.innerHTML=`<div class="err">Missing 'title' Value</div>`;
			return;
		}
		t=t[1].trim();
		let d=v.match(/^\s*\/\*\s*description\s*:\s*([a-zA-Z0-9_\-\.\!\(\)\?\% ]+?)\s*\*\/\s*$/m);
		if (d==null){
			pe.innerHTML=`<div class="err">Missing 'description' Value</div>`;
			return;
		}
		d=d[1].trim();
		pe.innerHTML=`<f-t>${t}</f-t><f-d>${d}</f-d>`;
		let j=0;
		let l;
		window._le=(window._le+1)%100;
		window._ic=0;
		window._n={id:id,title:t,desc:d,p:[]};
		if (!v.replace(/\/\*[\s\S]*?\*\/|([^:]|^)\/\/.*$/gm,"").trim().split(/\n{2,}/gm).every((k)=>{
			k=k.trim();
			if (k.length){
				window._ic++;
				window._n.p.push(k);
				j++;
				l=1;
				k=k.replace(/</gm,"&lt;").replace(/>/gm,"&gt;");
				let i=0;
				while (i<k.length){
					if (k[i]=="\n"){
						l++;
					}
					else if (k.substring(i,i+2)=="!["){
						let si=i;
						i+=2;
						while (k[i]!="]"){
							if (i>=k.length){
								pe.innerHTML="Square Brackets";
								return false;
							}
							i++;
						}
						i++;
						if (k[i]!="{"){
							i=si+1;
							continue;
						}
						i++;
						let si2=i;
						while (k[i]!="}"){
							if (i>=k.length){
								pe.innerHTML="Curly Brackets";
								return false;
							}
							i++;
						}
						window._ic++;
						let u=k.substring(si2,i);
						let ti=new Image();
						let le=window._le;
						ti.onload=()=>{
							window._l(le);
						};
						ti.onerror=()=>{
							window._e(u,le);
						};
						ti.src=u;
						k=k.substring(0,si)+`<img src="${u}" alt="${k.substring(si+2,si2-2)}"><br>`+k.substring(i+1);
						i+=18;
					}
					else if (k.substring(i,i+3)=="```"){
						let si=i;
						i+=3;
						while (k.substring(i,i+3)!="```"){
							if (i>=k.length){
								pe.innerHTML="Triple Quotes";
								return false;
							}
							i++;
						}
						k=k.substring(0,si)+`<f-c>${k.substring(si+3,i)}</f-c>`+k.substring(i+3);
						i+=7;
					}
					else if (k.substring(i,i+2)=="**"){
						let b=0;
						let si=i;
						i+=2;
						while (b%2!=0||k.substring(i,i+2)!="**"){
							if (i>=k.length){
								pe.innerHTML="Double Quotes";
								return false;
							}
							if (k[i]=="*"){
								b++;
							}
							i++;
						}
						k=k.substring(0,si)+`<f-b>${k.substring(si+2,i)}</f-b>`+k.substring(i+2);
						i=si+4;
					}
					else if (k[i]=="*"){
						let si=i;
						i++;
						while (k[i-1]=="*"||k[i]!="*"||(i+1>=k.length?false:k[i+1]=="*")){
							if (i>=k.length){
								pe.innerHTML="Single Quotes";
								return false;
							}
							i++;
						}
						k=k.substring(0,si)+`<f-i>${k.substring(si+1,i)}</f-i>`+k.substring(i+1);
						i=si+4;
					}
					i++;
				}
				window._ic--;
				pe.innerHTML+=`<p>${k.replace(/\n/gm,"<br>")}</p>`;
			}
			return true;
		})){
			pe.innerHTML=`<div class="err">Unterminated ${pe.innerHTML}<div class="ln">paragraph ${j}, line ${l}</div>`;
		}
	}
	ce.onkeyup();
},false);
