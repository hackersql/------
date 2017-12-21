var agt = navigator.userAgent.toLowerCase();
var is_ie = ((agt.indexOf("msie") != -1) && (agt.indexOf("opera") == -1));
var is_gecko= (navigator.product == "Gecko");
var is_webkit=agt.indexOf('webkit')>-1;
var is_safari = (agt.indexOf('chrome')==-1)&&is_webkit;
if(!window.opera){
	is_ie||is_safari||document.write("<script src='js/desktop/Compatibility.js'></sc"+"ript>");
}
document.write("<script src='js/lang/zh_cn.js'></sc"+"ript>");
var gIsPost = true;
window.getObj?0:getObj=function(s){return document.getElementById(s)};
$=getObj;

if (location.href.indexOf('/simple/') != -1) {
	getObj('headbase')?getObj('headbase').href = location.href.substr(0,location.href.indexOf('/simple/')+1):0;
} else if (location.href.indexOf('.html')!=-1 && 0) {
	var base = location.href.replace(/^(http(s)?:\/\/(.*?)\/)[^\/]*\/[0-9]+\/[0-9]{4,6}\/[0-9]+\.html$/i,'$1');
	if (base != location.href) {
		getObj('headbase')?getObj('headbase').href = base:0;
	}
}
~function()
{
	var FNArray=[];
	var D = document;
	/**
	 * 使用举例：
		window.onReady(FunctionName[,argu1,[argu2,[....]]]);
	 */
    window.onReady = function(fallBackFunction)
    {
		var argu=[];
		for (var i=1,len=arguments.length; i<len; i++)
		{
			argu.push(arguments[i]);
		}
		if (window.readyBound) return fallBackFunction.apply(this,argu);
		if(!is_ie) return 	fallBackFunction.apply(this,argu);
		FNArray.push(fallBackFunction);
        readyBound = true;
        var ready = 0;
        // Mozilla, Opera and webkit nightlies currently support this event
        if (D.addEventListener)
        {
            // Use the handy event callback
            D.addEventListener("DOMContentLoaded",
            function()
            {
                D.removeEventListener("DOMContentLoaded", arguments.callee, false);
                if (ready) return;
                ready = 1;
				for (var i=0,len=FNArray.length; i<len; i++)
				{
					FNArray[i] ? FNArray[i].apply(this,argu) : 0;
				}

            },
            false);

            // If IE event model is used
        } else if (D.attachEvent)
        {
            // ensure firing before onload,
            // maybe late but safe also for iframes
            D.attachEvent("onreadystatechange",
            function()
            {
                if (D.readyState === "complete")
                {
                    D.detachEvent("onreadystatechange", arguments.callee);

                    if (ready) return;
                    ready = 1;
                    for (var i=0,len=FNArray.length; i<len; i++)
					{
						FNArray[i] ? FNArray[i].apply(this,argu) : 0;
					}
                }
            });

            // If IE and not an iframe
            // continually check to see if the D is ready
            if (D.documentElement.doScroll && window == window.top)(function()
            {
                if (ready) return;
                try
                {
                    // If IE is used, use the trick by Diego Perini
                    // http://javascript.nwbox.com/IEContentLoaded/
                    D.documentElement.doScroll("left");
                } catch(error)
                {
                    setTimeout(arguments.callee, 0);
                    return;
                }
                ready = 1;
                for (var i=0,len=FNArray.length; i<len; i++)
				{
					FNArray[i] ? FNArray[i].apply(this,argu) : 0;
				}

            })();
        }
    };
}();
/**
 *验证码的，点其他地方消失的事件添加。
 */
function PW_popEvent (obj)
{
	if (typeof(obj) != 'object'){
		return false;
	}
	var a=obj.getElementsByTagName("*");
	for (var i=0,len=a.length; i<len; i++)
	{
		a[i].setAttribute("s",1);
	}
   document.body.onmousedown=function()
	{
		var e = window.event || event,
			elem = e.srcElement || e.target;
	   if(!elem.getAttribute("s") && elem.id != 'showpwd' && elem.id != 'header_reg_ckcode_img' && elem.id != 'changeGdCode' && elem.id != 'changeGdCode_a' && elem.tagName!=='OBJECT')
		{
		   obj.style.display="none";
		   try{getObj('header_ckcode').style.display="none";}catch(e){}
		}
	};

}
function getObj(id) {
	return document.getElementById(id);
}
function getElementsByClassName (className, parentElement){
	if (parentElement && typeof(parentElement)=='object') {
		var elems = parentElement.getElementsByTagName("*");
	} else {
		var elems = (document.getElementById(parentElement)||document.body).getElementsByTagName("*");
	}
	var result=[];
	for (i=0; j=elems[i]; i++) {
	   if ((" "+j.className+" ").indexOf(" "+className+" ")!=-1) {
			result.push(j);
	   }
	}
	return result;
}

function ietruebody() {
	/*
	if (getObj('upPanel')) {
		return getObj('upPanel');
	}
	*/
	return (document.compatMode && document.compatMode!="BackCompat" && !is_webkit)? document.documentElement : document.body;
}
function getTop() {
	return typeof window.pageYOffset != 'undefined' ? window.pageYOffset:ietruebody().scrollTop;
}
function getLeft() {
	return (typeof window.pageXOffset != 'undefined' ? window.pageXOffset:ietruebody().scrollLeft)
}
function IsElement(id) {
	return document.getElementById(id) != null ? true : false;
}
function CopyCode(obj) {
	if (typeof obj != 'object') {
		if (is_ie) {
			if(window.clipboardData.setData("Text",obj)){
				alert('复制成功！');
			}
		} else {
			prompt('按Ctrl+C复制内容', obj);
		}
	} else if (is_ie) {
		var lis = obj.getElementsByTagName('li'), ar = [];
		for(var i=0,l=lis.length; i<l; i++){
			ar.push(lis[i].innerText);
		}
		if(window.clipboardData.setData('Text', ar.join("\r\n") ) ){
			alert('复制成功！');
		}
	} else {
		function openClipWin(){
			var lis = obj.getElementsByTagName('li'), ar = [];
			for(var i=0,l=lis.length; i<l; i++){
				ar.push(lis[i].textContent);
			}
			window.clip = new ZeroClipboard.Client();
			clip.setHandCursor( true );
			
			clip.addEventListener('complete', function (client, text) {
				alert("复制成功!" );
				closep();
			});
			clip.setText(ar.join("\r\n"));
			var clipEle = getObj('clipWin');
			if (!clipEle){
				var clipEle = document.createElement('div');
				clipEle.innerHTML = '<div class="popout"><table border="0" cellspacing="0" cellpadding="0"><tbody><tr><td class="bgcorner1"></td><td class="pobg1"></td><td class="bgcorner2"></td></tr><tr><td class="pobg4"></td><td><div class="popoutContent">\
<div class="p10"><a href="javascript:closep();" class="adel">关闭</a>提示</div><div class="popBottom"><span class="btn2"><span><button type="button">点击这里复制代码</button></span></span></div></div></td><td class="pobg2"></td></tr><tr><td class="bgcorner4"></td><td class="pobg3"></td><td class="bgcorner3"></td></tr></tbody></table></div>';
				//clipEle.innerHTML = '<p id="d_clip_button">提示</p>';
				clipEle.style.display = 'none';
				document.body.appendChild(clipEle);
			}
			read.open(clipEle, null, 2);
			var btn = getObj('pw_box').getElementsByTagName('button')[0];
			clip.glue(btn);
			//clip.glue( 'd_clip_button', 'd_clip_container' );
		}//彈窗
		
		if (!window.clip){
			var script = document.createElement('script');
			script.src = 'js/ZeroClipboard.js';
			script.onload = function(){
				ZeroClipboard.setMoviePath( 'js/ZeroClipboard.swf' );
				openClipWin();
			};
			document.body.appendChild(script);
		}else{
			openClipWin();
		}
	}
	return false;
}
function Addtoie(value,title) {
	try
	  {
		is_ie ? window.external.AddFavorite(value,title) : window.sidebar.addPanel(title,value,"");
	  }
	catch(err)
	  {
	    txt = "1、抱歉，您的IE注册表值被修改，导致不支持收藏，您可按照以下方法修改。\n\n"
	    txt += "2、打开注册表编辑器，右键点击HKEY_CLASSES_ROOT查找'C:/\WINDOWS/\system32/\shdocvw.dll'。 \n\n"
	    txt += "3、点击(默认)，把'C:/\WINDOWS/\system32/\shdocvw.dll'修改为'C:/\WINDOWS/\system32/\ieframe.dll'，重启IE浏览器。\n\n"
		is_ie ? alert(txt) : alert("抱歉，您的浏览器不支持，请使用Ctrl+D进行添加\n\n")
	  }
}
~function() {
	var ifcheck = true;
	CheckAll = function (form,match) {
		for (var i = 0; i < form.elements.length; i++) {
			var e = form.elements[i];
			if (e.type == 'checkbox' && (typeof match == 'undefined' || e.name.match(match))) {
				e.checked = ifcheck;
			}
		}
		ifcheck = ifcheck == true ? false : true;
	}
}();

function showcustomquest(qid,id){
	var id = id ? id : 'customquest';
	getObj(id).style.display = qid==-1 ? '' : 'none';
}
function showCK(){
	getObj('ckcode').style.display="";
	getObj('ckcode').style.zIndex="1000000";
	if (getObj('ckcode').src.indexOf('ck.php') == -1) {
		getObj('ckcode').src = 'ck.php?nowtime=' + new Date().getTime();
	}
}
function setTab(m,n){
	var tli=document.getElementById("menu"+m).getElementsByTagName("li");
	var mli=document.getElementById("main"+m).getElementsByTagName("div");
	for(i=0;i<tli.length;i++){
		tli[i].className=i==n?"hover":"";
		mli[i].style.display=i==n?"block":"none";
	}
}
function changeState() {
	var msg = ajax.request.responseText;
	if (msg == 1) {
		getObj('stealth').className = '';
		getObj('iconimg').title = HEADER_HIDE;
		getObj('online_state').innerHTML = '<img src="'+IMG_PATH+'/stealth.png" align="absmiddle" alt="隐身" />隐身';
	} else {
		getObj('stealth').className = 'hide';
		getObj('iconimg').title = HEADER_ONLINE;
		getObj('online_state').innerHTML = '<img src="'+IMG_PATH+'/online.png" align="absmiddle" alt="在线" />在线';
	}
}
function showcustomquest_l(qid){
	getObj('customquest_l').name = 'customquest';
	getObj('customquest_l').style.display = qid==-1 ? '' : 'none';
}

function checkinput(obj,val){
	if (obj.className.indexOf('gray')!=-1) {
		obj.value = '';
		obj.className = obj.className.replace('gray', 'black');
	} else if (val && obj.value=='') {
		obj.value = obj.defaultValue = val;
		if (obj.className.indexOf('black') == -1) {
			obj.className += ' gray';
		} else {
			obj.className = obj.className.replace('black', 'gray');
		}
	}
}
var mt;
function showLoginDiv(){
	mt = setTimeout('read.open(\'user-login\',\'show-login\',2,26);getObj(\'pwuser\').focus();',200);
	document.onmousedown = function (e) {
		var o = is_ie ? window.event.srcElement : e.target;
		if (!issrc(o)) {
			read.close();
			document.onmousedown = '';
		}
	}
}
function issrc(o) {
	var k = 0;
	while (o) {
		if (o == read.menu) {
			return true;
		}
		if (o.tagName.toLowerCase() == 'body' || ++k>10) {
			break;
		}
		o = o.parentNode;
	}
	return false;
}

function imgResize(o, size) {
	if (o.width > o.height) {
		if (o.width > size) o.width = size;
	} else {
		if (o.height > size) o.height = size;
	}
	try{
		var next = getObj('next');
		var pre = getObj('pre');
		next.coords = '0 0 ' + ',' + o.width/2 + ',' + o.height;
		pre.coords = o.width/2 + ' 0 ' + ',' + o.width + ',' + o.height;
	}catch(e){}
}
function ajaxurl(o, ep) {
	if (typeof o == 'object') {var url = o.href;read.obj = o;} else {var url = o;}
	ajax.send(url + ((typeof ep == 'undefined' || !ep) ? '' : ep), '', ajax.get);
	return false;
}

function sendurl(o,id) {
	read.obj = o;
	sendmsg(o.href,'',id);
	return false;
}
function showAnnouce(){
	var annouce = getObj('annouce_div');
	if (annouce.style.display == 'none') {
		annouce.style.display = '';
	} else {
		annouce.style.display = 'none';
	}
}

function showCK(){
	var a = getObj('ckcode2');
	if (!a) {
		a = getObj('ckcode');
	}
	a.style.display="";
	if (a.src.indexOf('ck.php') == -1) {
		a.src = 'ck.php?nowtime=' + new Date().getTime();
	}
}
function showConInfo(uid,cyid){
	ajax.send('apps.php?q=group&a=uintro&cyid='+cyid+'&uid='+uid,'',ajax.get);
}

/*
userCard = {
	t1	 : null,
	t2	 : null,
	menu : null,
	//uids : '',
	data : {},
	init : function() {
		var els = getElementsByClassName('userCard');
		for (i = 0; i < els.length; i++) {
			if (els[i].id) {
				var sx = els[i].id.split('_');
				//userCard.uids += (userCard.uids ? ',' : '') + sx[3];
				els[i].onmouseover = function() {
					var _ = this;
					clearTimeout(userCard.t2);
					userCard.t1 = setTimeout(function(){userCard.show(_.id);}, 800);
				}
				els[i].onmouseout = function() {
					clearTimeout(userCard.t1);
					if (userCard.menu) userCard.t2 = setTimeout(function(){userCard.menu.close();},500);
				}
			}
		}
	},
	show : function(id) {
		var sx = id.split('_');
		if (typeof userCard.data[sx[3]] == 'undefined') {
			try {
				ajax.send($('headbase').href + 'pw_ajax.php?action=showcard&uid=' + sx[3]+ '&rnd='+Math.random(), '', function() {
					userCard.data[sx[3]] = ajax.runscript(ajax.request.responseText);
					userCard.show(id);
				})
			} catch(e){}
			return;
		}
		userCard.menu ? 0 : userCard.menu = new PwMenu('userCard');
		userCard.menu.menu.style.zIndex = 9;
		userCard.menu.obj = $(sx[1] + '_' + sx[2]) || $(id);
		userCard.menu.setMenu(userCard.data[sx[3]], '', 1);
		userCard.menu.menupz(userCard.menu.obj,21);
	}
}
*/

Class = function(aBaseClass, aClassDefine) {
	function class_() {
		this.Inherit = aBaseClass;
		for (var member in aClassDefine) {
			try{this[member] = aClassDefine[member];}catch(e){}		//针对opera,safri浏览器的只读属性的过滤
		}
	}
	class_.prototype = aBaseClass;
	return  new class_();
};
New = function(aClass, aParams) {
	function new_()	{
		this.Inherit = aClass;
		if (aClass.Create) {
			aClass.Create.apply(this, aParams);
		}
	}
	new_.prototype = aClass;
	return  new new_();
};
/* end */

function imgLoopClass(){
	this.timeout   = 2000;
	this.currentId = 0;
	this.tmp       = null;
	this.wrapId    = 'x-pics';
	this.tag       = 'A';
	this.wrapNum   = 0;
	this.total     = 10;
}
imgLoopClass.prototype = {
	/*对象选择器*/
	$ : function(id){
		return document.getElementById(id);
	},
	/*图片显示*/
	display : function(pics,currentId){
		for(i=0;i<pics.length;i++){
			if(i==currentId){
				var current = pics[i];
			}
			pics[i].style.display = "none";
		}
		current.style.display = "";
	},
	/*获取所有标签对象*/
	gets : function(){
		var wrapId = this.wrapId+this.wrapNum;
		var obj = this.$(wrapId);
		if(!obj){
			return false;
		}
		return this.$(wrapId).getElementsByTagName(this.tag);
	},
	/*轮显*/
	alternate : function(){
		var pictures = this.gets();
		if(!pictures){
			return false;
		}
		var length = pictures.length;
		this.currentId = this.currentId ? this.currentId : 0;
		if(this.currentId+1>length){
			this.currentId = 0;
		}
		this.display(pictures,this.currentId);
		this.currentId = this.currentId+1;
	},
	/*循环器*/
	loop : function(){
		this.alternate();
		var _this = this;
		t = setTimeout(function(){
			_this.loop();
		},this.timeout);
	},

	/*单页面多个图片轮播，最多十个*/
	imginit : function(){
		for(i=0;i<this.total;i++){
			var obj = this.$(this.wrapId+i);
			if(!obj){
				continue;
			}
			imgloop(i);/*调用外部通用接口*/
		}
	},

	init : function(){

	}
}
/*图片轮播调用接口*/
var imgloops = new imgLoopClass();
/*特殊图片轮播调用*/
function imgloop(num){
	var imgloops = new imgLoopClass();
	imgloops.wrapNum = num;
	imgloops.loop();
}
/*任务中心弹出控制*/
showJobPOP = function(){
	var pop = getObj("jobpop") || 0;
	var newjob = getObj("newjob");
	if(newjob){
		var num = newjob.getAttribute("num");
		if(!num){
			window.location.href = "jobcenter.php";
			return false;
		}
	}
	if(pop){
		pop.style.display='';
	}else{
		openjobpop("&job=show");/*必须显示*/
	}
	return false;
}
/*弹出任务中心界面*/
function openjobpop(param){
	var param = param ? param : '';
	ajax.send('pw_ajax.php?action=jobpop',param,function(){
		jobCenterRun(ajax.request.responseText);
	});
}
//所有的删除确定
function checkDel(sub,str){
	if(confirm(str))
		sub.form.submit();
}

function insertContentToTextArea(textAreaObj, codeText) {
	var startPostionOffset = codeText.length;
	textAreaObj.focus();
	if (document.selection) {
		var selection = document.selection.createRange();
		selection.text = codeText.replace(/\\r?\\n/g, '\\r\\n');
		selection.moveStart('character', - codeText.replace(/\\r/g,'').length + startPostionOffset);
		selection.moveEnd('character', - codeText.length + startPostionOffset);
		selection.select();
	} else if (typeof textAreaObj.selectionStart != 'undefined') {
		var prepos = textAreaObj.selectionStart;
		textAreaObj.value = textAreaObj.value.substr(0,prepos) + codeText + textAreaObj.value.substr(textAreaObj.selectionEnd);
		textAreaObj.selectionStart = prepos + startPostionOffset;
		textAreaObj.selectionEnd = prepos + startPostionOffset;
	}
}

function displayElement(elementId, isDisplay) {
	if (undefined == isDisplay) {
		getObj(elementId).style.display = getObj(elementId).style.display == 'none' ? '' : 'none';
	} else {
		getObj(elementId).style.display = isDisplay ? '' : 'none';
	}
}
function preview_img(id){
	var photype = getObj('p_'+id);
	if(getObj('q_'+id)){
		getObj('q_'+id).value = "";
	}
	var patn = /\.jpg$|\.jpeg$|\.png|\.bmp|\.gif$/i;
	if(patn.test(photype.value)){
		var Preview = getObj('preview_'+id);

		if (is_gecko || is_webkit) {
			Preview.src = photype.files[0].getAsDataURL();
		} else if (is_ie) {
			Preview.src="images/90.png";
			photype.select();
			var val = document.selection.createRange().text;
			Preview.filters.item("DXImageTransform.Microsoft.AlphaImageLoader").src = val;
			Preview.filters.item("DXImageTransform.Microsoft.AlphaImageLoader").sizingMethod = 'scale';
		}
	} else {
		showDialog('error','您选择的似乎不是图像文件。',2);
	}
}

var Attention = {
	add : function(obj, touid, recommend) {
		ajax.send('pw_ajax.php?action=addattention&touid=' + touid + (recommend ? '&recommend=' + recommend : ''), '', function() {
			var rText = ajax.request.responseText.split('\t');
			if (rText[0] == 'success') {
				obj.innerHTML = '关注中';
				obj.className = obj.className.replace('follow', 'following gray');
				obj.onclick = '';
				
				if (obj.name) {
					getObj(obj.name+'_'+touid).innerHTML = parseInt(getObj(obj.name+'_'+touid).innerHTML) + 1;
				}
				
			} else {
				ajax.guide();
			}
		});
		return false;
	},
	del : function(touid) {
		ajax.send('pw_ajax.php?action=delattention&touid=' + touid, '', function() {
			var rText = ajax.request.responseText.split('\t');
			if (rText[0] == 'success') {
				window.location.reload();
			} else {
				ajax.guide();
			}
		});
		return false;
	}
};

(function(){
    var win = window,doc = win.document,
        defaultCfg = {
            container :win,
            srcAttr : 'data-src',
            delay : 100,            //resize时和socrll时延迟处理,以免频繁触发,100毫秒基本无视觉问题
            placeholder :'images/blank.gif'         //图片占位符
        },
        addEvent = function( obj, type, fn ) {  
            if (obj.addEventListener)  
                obj.addEventListener( type, fn, false );  
            else if (obj.attachEvent) {  
                obj["e"+type+fn] = fn;  
                obj.attachEvent( "on"+type, function() { obj["e"+type+fn](); } );  
            }  
        };
        
    function ImgLazyLoad(options) {
        var self = this;
        this.options = options || {};
        if (!(self instanceof ImgLazyLoad)) {
            return new ImgLazyLoad(options);
        }
        this._initialize();
    }
    
    ImgLazyLoad.prototype = {
        _initialize:function() {
            var self = this,
                lazyImgs = doc.getElementsByTagName('img');
            for(var i in defaultCfg) {
                if(!(i in self.options)) {//合并参数
                    self.options[i] = defaultCfg[i];
                }
            }
            for(var i = 0,j = lazyImgs.length;i < j;i++) {
                var img = lazyImgs[i];
                if(!img.getAttribute(self.options.srcAttr)) {
                    img.setAttribute(self.options.srcAttr,img.src);
                }
                if(self.options.placeholder) {
                    img.src = self.options.placeholder;
                }else {
                    img.removeAttribute('src');
                }
                //img.style.display = 'none';
            }
            var $ = function(elem) { return typeof elem === 'string' ? document.getElementById(elem) : elem; },
                container = self.options.container.nodeType === 1 ? $(self.options.container) :win,
                
                threshold = function() {//计算图片加载入口
		            if(container===win) {
		                var scrollTop =  win.pageYOffset || container.scrollTop || doc.documentElement.scrollTop || doc.body.scrollTop,
		                    eHeight = doc.documentElement.clientHeight || doc.body.clientHeight || window.innerHeight;
		                return scrollTop + eHeight;
		            }
		            return container.getBoundingClientRect().top + container.clientHeight;
		        },
		        
		        eHeight = function() { return container.innerHeight || container.clientHeight; },//元素的高度
		        
		        loadImgs = function() {
		            for(var i = 0,j = lazyImgs.length;i < j;i++) {
		                var img = lazyImgs[i],src = img.getAttribute('src');
		                if(!src || src.indexOf(self.options.placeholder) > -1) {
	                        if(img.getBoundingClientRect().top <= threshold()) {
	                            var src = img.getAttribute(self.options.srcAttr);
								if(src){
	                            	img.src = src.indexOf('javascript') > -1 ? '' : src;
								}//IE8不允许img.src="javascript://",拒绝访问的错误
	                            img.style.display = '';
	                        }
		                }
		            }
		        };
		    loadImgs();
		    addEvent(container,'scroll',function() {
		        setTimeout(function() {
		            loadImgs();
		        },self.options.delay);
		    });
        }
    }
    
    win['ImgLazyLoad'] = function(option) {
        ImgLazyLoad(option);
    }
})();

function getBaseUrl() {
	var baseURL = document.baseURI || getHeadBase() || document.URL;
	if (baseURL && baseURL.match(/(.*)\/([^\/]?)/)) {
		baseURL = RegExp.$1 + "/";
	}
	return baseURL;
}
function getHeadBase() {
	return getObj('headbase') ? getObj('headbase').href : null;
}