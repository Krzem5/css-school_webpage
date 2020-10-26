document.addEventListener("DOMContentLoaded",()=>{
	if (!window.location.href.startsWith("https://krzem5.github.io/Css-School_Webpage/")){
		console.log(window.location.href);
		// window.location.href="https://krzem5.github.io/Css-School_Webpage/";
	}
	document.querySelectorAll(".bg .wr .top .icon").onclick=()=>{
		window.location.href="/";
	};
},false);
