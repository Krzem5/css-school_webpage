document.addEventListener("DOMContentLoaded",()=>{
	let be=document.querySelector(".bg");
	let wre=document.querySelector(".wr");
	let te=document.querySelector(".title");
	let ce=document.querySelector(".e");
	let pe=document.querySelector(".preview");
	window.onresize=()=>{
		be.style.height="initial";
		wre.style.height="initial";
		let h=Math.max(document.querySelector(".code").getBoundingClientRect().height+310,document.querySelector(".preview").getBoundingClientRect().height+310,document.body.getBoundingClientRect().height-70);
		be.style.height=`${h+70}px`;
		wre.style.height=`${h}px`;
	};
	window.onresize();
	setTimeout(window.onresize,10);
	setTimeout(window.onresize,100);
	document.querySelector(".icon").onclick=()=>{
		window.location.href="/";
	};
	te.innerHTML=te.innerText.split("").map((e)=>{
		return `<span class="c">${e}</span>`;
	}).join("");
	ce.onkeyup=()=>{
		let v=ce.value;
		let id=v.match(/^\s*\/\*\s*id\s*:\s*([a-z0-9\-]+?)\s*\*\/\s*$/m)[1];
		let title=v.match(/^\s*\/\*\s*title\s*:\s*([a-zA-Z0-9_\- ]+?)\s*\*\/\s*$/m)[1];
		let desc=v.match(/^\s*\/\*\s*description\s*:\s*([a-zA-Z0-9_\- \.\!\(\)\?\%]+?)\s*\*\/\s*$/m)[1];
		pe.innerHTML=`<div class="title">${title}</div><div class="desc">${desc}</div>`;
		v.replace(/\/\*[\s\S]*?\*\/|([^:]|^)\/\/.*$/gm,"").split("\n\n").forEach((k)=>{
			if (k.length){
				k=k.replace(/\n/gm,"<br>");
				pe.innerHTML+=`<p class="p">${k}</p>`;
			}
		});
	}
	ce.onkeyup();
},false);
