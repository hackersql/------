
function AjaxObj() {
	this.responseText = null;
	var s = document.createElement('div');
	s.style.display = 'none';
	var n = 'iframe' + new Date().getTime();
	s.innerHTML = '<iframe src="about:blank" id="' + n + '" name="' + n + '"></iframe>';
	document.body.appendChild(s);
	this.iframe = s.firstChild;

	this.post = function(url,data) {
		if (typeof data == 'string' && data != '') {
			var f = document.createElement('form');
			f.name	 = 'ajaxform';
			//f.target = 'ajaxiframe';
			f.target = n;
			f.method = 'post';
			f.action = url;
			var ds = data.split("&");
			for (var i = 0; i < ds.length; i++) {
				if (ds[i]) {
					var v	 = ds[i];
					var el	 = document.createElement('input');
					el.type  = 'hidden';
					el.name  = v.substr(0,v.indexOf('='));
					el.value = v.substr(v.indexOf('=')+1);
					f.appendChild(el);
				}
			}
			document.body.insertBefore(f,document.body.childNodes[0]);
			f.submit();
			document.body.removeChild(f);
		} else if (typeof data == 'object') {
			var s = data.getAttribute('action');
			if (typeof s == 'object') {
				var p = s.parentNode;
				p.removeChild(s);
				data.setAttribute('action', url);
				p.appendChild(s);
			} else {
				data.setAttribute('action', url);
			}
			data.target = n;
			data.submit();
		} else {
			window.frames[n].location.replace(url);//让iframe没有浏览历史
			//self.frames[n].location.replace(url);//让iframe没有浏览历史
			//this.iframe.src=url;
		}
	}
	this.clearhistroy = function() {
		window.frames[n].location.replace('about:blank');
		//self.frames[n].location.replace('about:blank');
	}
}
function XMLhttp() {
	this.request = null;
	this.recall	 = null;
	this.time    = null;
	this.t       = null;
	this.sArray  = new Array();
	this.last	 = 0;
}

XMLhttp.prototype = {

	send : function(url,data,callback) {
		if (this.request == null) {
			this.request = new AjaxObj();
		}
		this.request.responseText = '';

		var nowtime	= new Date().getTime();
		if (nowtime - this.last < 1500) {
			clearTimeout(this.t);
			this.t = setTimeout(function(){ajax.send(url,data,callback)},1500+this.last-nowtime);
			return;
		}
		this.last = nowtime;
		url	+= (url.indexOf("?") >= 0) ? "&nowtime=" + nowtime : "?nowtime=" + nowtime;
		if (typeof verifyhash != 'undefined') {
			url += '&verify=' + verifyhash;
		}
		this.request.post(url,data);
		this.recall = callback;
		if (typeof this.recall == "function") {
			if (this.request.iframe.attachEvent) {
				this.request.iframe.detachEvent('onload',ajax.load);
				this.request.iframe.attachEvent('onload',ajax.load);
			} else {
				this.request.iframe.addEventListener('load',ajax.load,true);
			}
		}
	},

	load : function() {
		if(!ajax.request.iframe.contentWindow){
			return false;
		}
		var _innerText=ajax.request.iframe.contentWindow.document.documentElement.innerText;
		var _textContent=ajax.request.iframe.contentWindow.document.documentElement.textContent;
		if(_innerText==undefined&&_textContent==undefined){
			return false;
		}
		if(-[1,]){
				ajax.request.responseText=_textContent;
		}else{
				var rules = /<!\[CDATA\[([\s\S]+)\]\]>/.exec(_innerText);
				if(rules && rules[1]){
					ajax.request.responseText=rules[1].replace(/^\s+|\s+$/g,'');
				}else{
					var xmlDoc=ajax.request.iframe.contentWindow.document.XMLDocument;
					if(xmlDoc){
						ajax.request.responseText=xmlDoc.text;
					}else{
						ajax.request.responseText=_innerText;
					}
				}
		}
		
		if (ajax.request.iframe.detachEvent) {
			ajax.request.iframe.detachEvent('onload',ajax.load);
		} else {
			ajax.request.iframe.removeEventListener('load',ajax.load,true);
		}
		//try{if (ajax.request.iframe.location.href == 'about:blank'){return '';}}catch(e){}
		if (typeof(ajax.recall) == 'function') {
			ajax.recall();
			ajax.doscript();
		}
		//fixed for tt browser (register page)
		if (typeof ajaxclearhistory == 'undefined')ajax.request.clearhistroy();
	},

	XmlDocument : function(obj) {
		return (!-[1,]) ? ajax.request.iframe.contentWindow.document.XMLDocument : ajax.request.iframe.contentWindow.document;
	},

	submit : function(obj,recall) {
		if (typeof recall == 'undefined' || typeof recall != 'function') {
			recall = ajax.guide;
		}
		ajax.send(obj.getAttribute('action'), obj, recall);
		closep();
	},

	get : function(newread,border) {
		var temp = newread ? newread : read;
		if (ajax.request.responseText != null && ajax.request.responseText.indexOf('<') != -1) {
			temp.setMenu(this.runscript(ajax.request.responseText), '', border);
			temp.menupz(temp.obj);
			try{temp.menu.getElementsByTagName("input")[1].focus();}catch(e){}
		} else {
			closep();
			ajax.guide();
		}
	},

	runscript : function (html) {
		if (html.indexOf('<script') == -1) return html;
		var _=this;
		html = html.replace(/<script(.*?)>([^\x00]*?)<\/script>/ig, function($1, $2, $3) {
			_.sArray.push({'attribute' : $2, 'code' : $3});
			return '';
		});
		return html;
	},

	doscript : function() {
		for (var i = 0; i < this.sArray.length; i++) {
			var id = path = code = '';
			if (this.sArray[i]['attribute'].match(/\s*id\="([\w\_]+?)"/i)) {
				id = RegExp.$1;
			}
			if (this.sArray[i]['attribute'].match(/\s*src\="(.+?)"/i)) {
				path = RegExp.$1;
			} else {
				code = this.sArray[i]['code'];
			}
			loadjs(path, code, id);
		}
		this.sArray = new Array();
	},
	
	showError : function(message,time){
		var control = document.getElementById('pw_box'),
			popout = getElementsByClassName('popout',control)[0],
			msgBoxs = getElementsByClassName('wrongTip',popout),
			box = msgBoxs.length ? msgBoxs[0] : null;
			popBottom = getElementsByClassName('popBottom',control);
			if(!box) {	
				
				box = document.createElement('div');
				box.className = 'wrongTip';
				box.innerHTML = message;
				popBottom[0].parentNode.insertBefore(box,popBottom[0]);
			}
			box.style.display = '';
			box.innerHTML = message;
			if(time == undefined) time = 3;	
			clearTimeout(this.showTime);
			this.showTime = setTimeout(function(){box.style.display = 'none';},time * 1000);
			return false;
	},

	guide : function(callback) {
		if (ajax.request.responseText == null) {
			ajax.request.responseText = '您请求的页面出错啦!';
		}
		var rText = ajax.request.responseText.split('\t');

		/*主题印戳*/
		if(operateOverPrint(rText)){
			return false;
		}
		if (rText[1] != 'nextto') {
			showDialog('', rText[0], 2, callback ? callback : null);
		}
		if (typeof(rText[1]) != 'undefined' && in_array(rText[1],['jump','nextto','reload'])) {
			if (rText[1] == 'jump') {
				setTimeout("window.location.href='"+rText[2]+"';",200);
			} else if (rText[1] == 'nextto') {
				sendmsg(rText[2],rText[3],rText[4]);
			} else if (rText[1] == 'reload') {
				setTimeout("window.location.reload();",2000);
			}
		}
	},

	clear : function() {
		if (IsElement('ajax_guide')) document.body.removeChild(getObj('ajax_guide'));
	},

	convert : function(str) {
		if (typeof(str)=='string') {
			return str.replace(/\&/g,'%26');
		}
		return str;
	},

	quickpost : function(event,obj) {
		if ((event.ctrlKey && event.keyCode == 13) || (event.altKey && event.keyCode == 83)) {
			try{obj.ajaxsubmit.click();}catch(e){}
		}
	}
}

var ajax = new XMLhttp();

function sendmsg(url,data,id) {
	read.obj = (typeof id == 'undefined' || !id) ? null : getObj(id);
	read.guide();
	setTimeout(function(){ajax.send(url,data,ajax.get);},100);
}
function getObj(id) {
	return document.getElementById(id);
}
$=getObj;
function objCheck(obj) {
	if (typeof(obj)=='string') {
		obj	= getObj(obj);
	}
	return obj;
}

function setCurrent(src,dst,css) {
	var o = null;
	if (IsElement(src)) {
		o = getObj(src);
	} else if (dst && IsElement(dst)) {
		o = getObj(dst);
	}
	if (o) o.className += ' ' + css;
}

function strlen(str){
	var len = 0;
	var s_len = str.length = (is_ie && str.indexOf('\n')!=-1) ? str.replace(/\r?\n/g, '_').length : str.length;
	window.charset?0:charset="";
	var c_len = charset == 'utf-8' ? 3 : 2;
	for(var i=0;i<s_len;i++){
		len += str.charCodeAt(i) < 0 || str.charCodeAt(i) > 255 ? c_len : 1;
	}
	return len;
}

function substr(str, len) {
	if(!str || !len) {
		return '';
	}
	var a = 0;
	var i = 0;
	var temp = '';
	var c_len = charset == 'utf-8' ? 3 : 2;
	for (i=0;i<str.length;i++) {
		if (str.charCodeAt(i)>255) {
			a+=c_len;
		} else {
			a++;
		}
		if(a > len) {
			return temp;
		}
		temp += str.charAt(i);
	}
	return str;
}

function initCheckTextNum(textareaid,warnid,num,nodisplay) {
	var textareaobj = getObj(textareaid);
	var nodisplay = nodisplay ? false : true;/* if choose true the limit nums will not display else will display*/
	try{if (document.addEventListener) {
		textareaobj.addEventListener("input",function(){checkTextNum(textareaobj,warnid,num,nodisplay);},false);
	} else if (document.attachEvent){
		textareaobj.attachEvent("onpropertychange",function(){checkTextNum(textareaobj,warnid,num,nodisplay);});
	}}catch(e){}
}

function checkTextNum(textareaid,warnid,num,nodisplay) {

	if (typeof(textareaid) == 'string') {
		var textareaobj = getObj(textareaid);
	} else {
		var textareaobj = textareaid;
	}
	var str_length = strlen(textareaobj.value);
	if (!objCheck(getObj(warnid))) {
		return false;
	}
	var warn = getObj(warnid);
	if (str_length > num) {
		warn.style.display = '';
		warn.style.color = '';
		warn.innerHTML = '已超出'+(str_length-num)+'字节';
	} else {
		if(nodisplay){
			warn.style.display = '';
			warn.innerHTML = '剩余'+(num-str_length)+'字节';
		}else if(warn.style.display == ''){
			warn.style.display = 'none';
		}
	}
}

function JSONParse(text){
	var cx = /[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g;
	var j;
	if (cx.test(text)) {
		text = text.replace(cx, function (a) {
			return '\\u' + ('0000' + a.charCodeAt(0).toString(16)).slice(-4);
		});
	}
	if (/^[\],:{}\s]*$/.
test(text.replace(/\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g, '@').
replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g, ']').
replace(/(?:^|:|,)(?:\s*\[)+/g, ''))) {
		j = eval('(' + text + ')');
		return j;
	}
	showDialog('error','数据格式错误，无法解析');
}

function SetCookie(name,value) {
	expires = new Date();
	expires.setTime(expires.getTime()+(86400*365));
	document.cookie=name+"="+escape(value)+"; expires="+expires.toGMTString()+"; path=/";
}

function FetchCookie(name) {
	var start = document.cookie.indexOf(name);
	var end = document.cookie.indexOf(";",start);
	return start==-1 ? null : unescape(document.cookie.substring(start+name.length+1,(end>start ? end : document.cookie.length)));
}

function showOverPrint(obj,isMulti){
	var url = obj.getAttribute("url");
	if (!isMulti) {
		sendmsg(url,'',obj.id);
		return false;
	}
	var overprintTids = getObj('overprinttids').value;
	sendmsg(url,'tidarray=' + overprintTids,obj.id);
	return false;
}

function operateOverPrint(text){
	/*主题印戳*/
	if (typeof(text[1]) != 'undefined' && in_array(text[1],['overprint'])) {
		var overprint = getObj("read_overprint");
		if(overprint && typeof(text[2]) != 'undefined'){
			var img = overprint.getElementsByTagName("img")[0];
			if(!img){
				img = document.createElement("img");
				img.src = text[2];
				overprint.appendChild(img);
			}else{
				img.src = text[2];/*图标切换*/
			}
			if(text[2] == ""){
				overprint.removeChild(img);
			}
		}
		/*是否存在后续操作*/
		if(typeof(text[3]) == 'undefined'){
			showDialog('',text[0],2);
		}
		if(typeof(text[3]) != 'undefined' && text[3] == "nextto"){
			sendmsg(text[4],text[5],text[6]);
		}
		return true;;
	}else{
		return false;
	}
}
function showViewLog(url,data,id){
	read.obj = (typeof id == 'undefined' || !id) ? null : getObj(id);
	read.guide();
	setTimeout(function(){ajax.send(url,data,function(){
		ajax.get();
		document.body.onmousedown = function(event){
			closep();
			document.body.onmousedown = function(){};
		}
		var box = getObj("pw_box");
		if(box){
			box.onmousedown = function(evt){
				if(evt){
		    		evt.stopPropagation();
		    	}else{
		    		event.cancelBubble = true;
		    	}
			}
		}
	});},100);
}
function uploadFile(ajaxForm,callback)
{
	ajax.send(url, ajaxForm.cloneNode(true), callback);
}