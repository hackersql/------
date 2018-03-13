//<!--网站参数begin

var site = new Object();
site.Name = '榆林市统计局';
site.Url = 'http://192.168.7.99:9617';
site.Dir = '/';
site.CookieDomain = '';
site.CookiePrev = 'netstar';


//-->网站参数end


//<!--模型begin

var ___JSON_Modules = {recordcount: 6, table: [{no: 0, id: 1, title: '文章', type: 'article', fieldvalues: 'title,summary', fieldtexts: '标题,简介'},{no: 1, id: 2, title: '图片', type: 'photo', fieldvalues: 'title,summary', fieldtexts: '标题,简介'},{no: 2, id: 3, title: '下载', type: 'soft', fieldvalues: 'title,summary', fieldtexts: '标题,简介'},{no: 3, id: 4, title: '视频', type: 'video', fieldvalues: 'title,summary', fieldtexts: '标题,简介'},{no: 4, id: 5, title: '文档', type: 'document', fieldvalues: 'title,summary', fieldtexts: '标题,简介'},{no: 5, id: 6, title: '文库', type: 'paper', fieldvalues: 'title,summary', fieldtexts: '标题,简介'}]}

//-->模型end

var _jcms_DialogUrl		= site.Dir + "style/dialog/";
/*------------------------------------------------------------------*/
function $OBJ(el)
{
	if(typeof el=='string')
		return document.getElementById(el);
	else if(typeof el=='object')
		return el;
}
var JumbotCms=new Object();
JumbotCms.Cookie={//
	set:function(name,value,expires,path,domain){
		if(typeof expires=="undefined"){
			expires=new Date(new Date().getTime()+24*3600*100);
		}
		document.cookie=name+"="+_jcms_UrlEncode(value)+((expires)?"; expires="+expires.toGMTString():"")+((path)?"; path="+path:"; path=/")+((domain!=null && domain.length>0)?";domain="+domain:"");
	},
	get:function(name, subname){
		var re = new RegExp((subname ? name + "=(.*?&)*?" + subname + "=(.*?)(&|;)" : name + "=([^;]*)(;|$)"), "i");
		return _jcms_UrlDecode(re.test(document.cookie) ? (subname ? RegExp["$2"] : RegExp["$1"]) : ""); 
	}, 
	clear:function(name,path,domain){
		if(this.get(name)){
			document.cookie=name+"="+((path)?"; path="+path:"; path=/")+((domain)?"; domain="+domain:"")+";expires=Fri, 02-Jan-1970 00:00:00 GMT";
		}
	}
};
//追加/删除事件
JumbotCms.Event={
	add:function(obj, evType, fn){
		if (obj.addEventListener){obj.addEventListener(evType, fn, false);return true;}
		else if (obj.attachEvent){var r = obj.attachEvent("on"+evType, fn);return r;}
		else {return false;}
	},
	remove:function(obj, evType, fn, useCapture){
		if (obj.removeEventListener){obj.removeEventListener(evType, fn, useCapture);return true;}
		else if (obj.detachEvent){var r = obj.detachEvent("on"+evType, fn);return r;}
		else {alert("Handler could not be removed");}
	}
};
//追加onload事件
JumbotCms.addOnloadEvent=function(fnc) {
	if ( typeof window.addEventListener != "undefined" )
		window.addEventListener( "load", fnc, false );
	else if ( typeof window.attachEvent != "undefined" )
	{
		window.attachEvent( "onload", fnc );
	}
	else
	{
		if ( window.onload != null )
		{
			var oldOnload = window.onload;
			window.onload = function (e) {
				oldOnload(e);
				window[fnc]();
			};
		} else
			window.onload = fnc;
	}
};
JumbotCms.isFunction=function(variable) {
	return typeof variable == 'function' ? true : false;
};
JumbotCms.isUndefined=function(variable) {
	return typeof variable == 'undefined' ? true : false;
};
JumbotCms.Length=function(variable) {
	var len = 0;
	var val = variable;
	for (var i = 0; i < val.length; i++) 
	{
		if (val.charCodeAt(i) >= 0x4e00 && val.charCodeAt(i) <= 0x9fa5){ 
			len += 2;
		}else {
			len++;
		}
	}
	return len;
};
JumbotCms.Eval=function(data) {
	JumbotCms.Loading.hide();
	try {
		eval(data);
	}
	catch(e) {
		alert(data);	
	}
};
/////////////////////////////
//弹出消息框
/////////////////////////////
JumbotCms.Message=function(errstr, success, returnFunc){
	new _jcms_Dialog().reset();
	var MSG = $.message;
	MSG.lays(200, 24);
	//MSG.anim('fade', 'slow');
	MSG.anim('fade', 'slow', site.Dir+'_libs/jquery.messager/');
	if(returnFunc) MSG.doafter(returnFunc);
	MSG.show(success, errstr, 3000);
};
/////////////////////////////
//弹出提示框
/////////////////////////////
JumbotCms.Alert=function(errstr, success, returnFunc){
	var oDialog = new _jcms_Dialog('2', '', 360, 180, success, true);
	oDialog.init();
	oDialog.event(errstr,'');
	if (returnFunc == null)
		oDialog.button('dialogSubmit', '');
	else
		oDialog.button('dialogSubmit', returnFunc);
};
/////////////////////////////
//弹出确认框
//例如:
//1、JumbotCms.Confirm("是否操作", act, null) //函数不加()
//2、JumbotCms.Confirm("是否操作", "alert('yes')", "alert('no')")
/////////////////////////////
JumbotCms.Confirm=function(errstr, returnSubmitFunc, returnCancelFunc)
{
	var oDialog = new _jcms_Dialog('2', '', 360, 180, null, true);
	oDialog.init();
	oDialog.event(errstr,'');
	oDialog.button('dialogSubmit', returnSubmitFunc);
	if (returnCancelFunc == null)
		oDialog.button('dialogCancel', '');
	else
		oDialog.button('dialogCancel', returnCancelFunc);
};
/////////////////////////////
//弹出模拟窗口
/////////////////////////////
JumbotCms.Popup={
	show:function(url, width, height, showCloseBox, showTitle, returnFunc)
	{
		new _jcms_Dialog().reset();
		if(showTitle==null) showTitle="&nbsp;";
		var oDialog = new _jcms_Dialog('2', showTitle, width, height, null, showCloseBox);
		if (url.indexOf("?") == -1)
			oDialog.open(url+"?windowCode="+(new Date().getTime()), returnFunc, "auto");
		else
			oDialog.open(url+"&windowCode="+(new Date().getTime()), returnFunc, "auto");
	},
	hide:function(callReturnFunc){
		new _jcms_Dialog().reset(callReturnFunc);
	}
};
/////////////////////////////
//弹出加载层
/////////////////////////////
JumbotCms.Loading={
	show:function(msgstr, width, height)
	{
		if(width==null) width=280;
		if(height==null) height=100;
		var oDialog = new _jcms_Dialog('0', '友情提示', width, height, null, false);
		oDialog.init(true);
		oDialog.html("<div style='text-align:center;padding-top:20px;'>"+msgstr+"<br /><br /><img src='" + _jcms_DialogUrl + "loading.gif' align='absmiddle'></div>");
	},
	hide:function(callReturnFunc){
		new _jcms_Dialog().reset(callReturnFunc);
	}
};
JumbotCms.Event.add(window,"load",_jcms_OperatorPlus);
JumbotCms.Event.add(window,"scroll",_jcms_OperatorPlus);
JumbotCms.Event.add(window,"resize",_jcms_OperatorPlus);

////////////////////////////////////////////////////////////////////////////////////////////
//标题栏跑马灯
////////////////////////////////////////////////////////////////////////////////////////////
var _jcms_ScrollTitle__Oldtitle		= top.document.title;
var _jcms_ScrollTitle__i		= 0;
var _jcms_ScrollTitle__Speed		= 200;
var _jcms_ScrollTitle__Timer		= function(message){
	if(_jcms_ScrollTitle__i == message.length)
	{
		top.document.title = _jcms_ScrollTitle__Oldtitle;
		_jcms_ScrollTitle__i = 0;
		return;
	}
	else{
		top.document.title = message.substring(_jcms_ScrollTitle__i);
		_jcms_ScrollTitle__i++;
		setTimeout("_jcms_ScrollTitle__Timer('"+message+"')",_jcms_ScrollTitle__Speed);
	}
}

////////////////////////////////////////////////////////////////////////////////////////////

var _jcms_HideSelects			= false;
var _jcms_DialogIsShown			= false;
var _jcms_WindowMask			= null;
////////////////////////////////////////////////////////////////////////////////////////////
//以下为弹出窗口的类
////////////////////////////////////////////////////////////////////////////////////////////
function _jcms_Dialog(styletype, title, width, height, iswhat, showCloseBox){
	//半透明边框宽度
	var shadowBorderBoth=0;
	var oWidth = width;
	var oHeight = height;
	if(oWidth==-1 || oWidth>_jcms_GetViewportWidth()-15)
	{
		oWidth=_jcms_GetViewportWidth()-15;
		shadowBorderBoth = 0;
	}
	if(oWidth<-1)
	{
		oWidth=_jcms_GetViewportWidth()+oWidth;
		shadowBorderBoth = 0;
	}
	if(oHeight==-1 || oHeight>_jcms_GetViewportHeight()-44)
	{
		oHeight=_jcms_GetViewportHeight()-44;
		shadowBorderBoth = 0;
	}
	if(oHeight<-1)
	{
		oHeight=_jcms_GetViewportHeight()+oHeight;
		shadowBorderBoth = 0;
	}
	var sTitle = "友情提示";
	if (iswhat == "0")
		sTitle = "错误提示";
	else if (iswhat == "1")
		sTitle = "成功提示";
	else
		if (title!='') sTitle = title;
	var src = "";
	var path = _jcms_DialogUrl + styletype + "/";
	var gReturnFunc;
	var gReturnVal = null;
	var sButtonFunc = '<input id="dialogSubmit" class="dialogSubmit' + styletype + '" type="button" value="确 认" onclick="new _jcms_Dialog().reset();" /> <input id="dialogCancel" class="dialogCancel' + styletype + '" type="button" value="取 消" onclick="new _jcms_Dialog().reset();" />';
	var sClose = '';
	if (showCloseBox == null || showCloseBox == true)
		sClose = '<img alt="关闭" style="cursor:pointer;" id="dialogBoxClose" onclick="new _jcms_Dialog().reset();" src="' + path + 'dialogCloseOut.gif" border="0" onmouseover="this.src=\'' + path + 'dialogCloseOver.gif\';" onmouseout="this.src=\'' + path + 'dialogCloseOut.gif\';" align="absmiddle" />';
	var sSuccess = '';
	if (iswhat != null)
		sSuccess = '<td width="80" align="center" valign="middle"><img id="dialogBoxFace" class="dialogBoxFace' + styletype + '" src="' + path + iswhat + '.gif" valign="absmiddle" /></td>';
	else
		sSuccess = '<td width="80" align="center" valign="middle"><img id="dialogBoxFace" class="dialogBoxFace' + styletype + '" src="' + path + '0.gif" valign="absmiddle" /></td>';
	var sBody = '\
		<table id="dialogBodyBox" class="dialogBodyBox' + styletype + '" border="0" align="center" cellpadding="0" cellspacing="0" width="100%" height="100%" >\
			<tr height="' + (oHeight - 60) + '">\
				<td width="10"></td>' + sSuccess + '<td id="dialogMsg" class="dialogMsg' + styletype + '"></td>\
				<td width="10"></td>\
			</tr>\
			<tr height="30"><td id="dialogFunc" class="dialogFunc' + styletype + '" colspan="4">' + sButtonFunc + '</td></tr>\
		</table>\
	';
	var sBox = '\
		<div style="display:none;" id="dialogBox" class="dialogBox' + styletype + '">\
			<div id="dialogTitleDiv" class="dialogTitleDiv' + styletype + '" style="width:' + oWidth + 'px;">\
				<span id="dialogBoxTitle" class="dialogBoxTitle' + styletype + '">' + sTitle + '</span>\
				<span id="dialogBoxClose" class="dialogBoxClose' + styletype + '">' + sClose + '</span>\
			</div>\
			<div id="dialogHeight" style="width:' + oWidth + 'px;height:' + oHeight + 'px;">\
				<div id="dialogBody" class="dialogBody' + styletype + '" style="height:' + oHeight + 'px;">' + sBody + '</div>\
			</div>\
		</div>\
		<div id="dialogBoxShadow" style="display:none;"></div>\
	';
	this.init = function(_showTitleBar){
		document.body.oncontextmenu=function(){return false;};
		document.body.onselectstart=function(){return false;};
		document.body.ondragstart=function(){return false;};
		document.body.onsource=function(){return false;};
		$OBJ('dialogFrame') ? $OBJ('dialogFrame').src='' : function(){};
		$OBJ('dialogCase') ? $OBJ('dialogCase').parentNode.removeChild($OBJ('dialogCase')) : function(){};
		$OBJ('windowMask') ? $OBJ('windowMask').parentNode.removeChild($OBJ('windowMask')) : function(){};
		var oDiv = document.createElement('span');
		oDiv.id = "dialogCase";
		oDiv.innerHTML = sBox;
		document.body.appendChild(oDiv);
		var oMask = document.createElement('div');
		oMask.id = 'windowMask';
		document.body.appendChild(oMask);
		_jcms_WindowMask = $OBJ("windowMask");
		_jcms_WindowMask.style.display="block";
		var brsVersion = parseInt(window.navigator.appVersion.charAt(0), 10);
		if (brsVersion <= 6 && window.navigator.userAgent.indexOf("MSIE") > -1) {
			_jcms_HideSelects = true;
		}
		if (_jcms_HideSelects == true) {
			HideSelectBoxes();
		}
		if (_showTitleBar == true || _showTitleBar == null)
			$OBJ("dialogTitleDiv").style.display = "block";
		else
			$OBJ("dialogTitleDiv").style.display = "none";
		_jcms_OperatorPlus();
	}
	//this.show = function(){$OBJ('dialogBox') ? function(){} : this.init();_jcms_DialogIsShown=true;this.middle('dialogBox');}
	this.show = function(){$OBJ('dialogBox') ? function(){} : this.init();_jcms_DialogIsShown=true;this.middle('dialogBox');this.shadow();this.middle('dialogBoxShadow');_jcms_OperatorPlus();}
	this.html = function(_sHtml){
		this.show();
		$OBJ('dialogBody').innerHTML = _sHtml;
	}
	this.button = function(_sId, _sFuc){
		if($OBJ(_sId)){
			$OBJ(_sId).style.display = '';
			if($OBJ(_sId).addEventListener){
				if($OBJ(_sId).act){$OBJ(_sId).removeEventListener('click', function(){eval($OBJ(_sId).act);}, false);}
				$OBJ(_sId).act = _sFuc;
				$OBJ(_sId).addEventListener('click', function(){eval(_sFuc);this.reset();}, false);
			}else{
				if($OBJ(_sId).act){$OBJ(_sId).detachEvent('onclick', function(){eval($OBJ(_sId).act);});}
				$OBJ(_sId).act = _sFuc;
				$OBJ(_sId).attachEvent('onclick', function(){eval(_sFuc);});
			}
		}
	}
	this.shadow = function(){
		if(shadowBorderBoth>0){
			var oShadow = $OBJ('dialogBoxShadow');
			var oDialogDiv = $OBJ('dialogBox');
			oShadow.style.position = "absolute";
			oShadow.style.background = "#000";
			oShadow.style.display = "";
			oShadow.style.opacity = "0.25";
			oShadow.style.filter = "alpha(opacity=25)";
			oShadow.style.width = (oDialogDiv.offsetWidth + shadowBorderBoth)+"px";
			oShadow.style.height = (oDialogDiv.offsetHeight + shadowBorderBoth)+"px";
		}
	}
	this.open = function(_sUrl, _returnFunc, _sMode){
		this.show();
		gReturnFunc = _returnFunc;
		//if(!_sMode || _sMode == "no" || _sMode == "yes"){
			$OBJ("dialogBody").innerHTML = "<iframe id='dialogFrame' name='dialogFrame' src='"+_sUrl+"' width='" + oWidth + "' height='" + oHeight + "' frameborder='no' border='0' marginwidth='0' marginheight='0' scrolling='" + _sMode + "'></iframe>";
			$OBJ("dialogFrame").src = _sUrl;
		//}
	}
	this.reset = function(callReturnFunc){$OBJ('dialogCase') ? this.dispose(callReturnFunc) : function(){};}
	this.dispose = function(callReturnFunc){
		_jcms_DialogIsShown = false;
		document.body.oncontextmenu=function(){return true;};
		document.body.onselectstart=function(){return true;};
		document.body.ondragstart=function(){return true;};
		document.body.onsource=function(){return true;};
		$OBJ('dialogFrame') ? $OBJ('dialogFrame').src='' : function(){};
		$OBJ('dialogCase').parentNode.removeChild($OBJ('dialogCase'));
		$OBJ('windowMask').parentNode.removeChild($OBJ('windowMask'));
		_jcms_WindowMask=null;
		if (callReturnFunc == true && gReturnFunc != null) {
			gReturnVal = window.dialogFrame.returnVal;
			window.setTimeout('gReturnFunc(gReturnVal);', 1);
		}
		if (_jcms_HideSelects == true) {
			ShowSelectBoxes();
			_jcms_HideSelects = false;
		}
		//$OBJ('dialogBoxShadow').style.display = "none";
	}
	this.event = function(_sMsg, _sSubmit, _sCancel, _sClose){
		this.show();
		$OBJ('dialogFunc').innerHTML = sButtonFunc;
		$OBJ('dialogBoxClose').innerHTML = sClose;
		$OBJ('dialogBodyBox') == null ? $OBJ('dialogBody').innerHTML = sBody : function(){};
		$OBJ('dialogMsg') ? $OBJ('dialogMsg').innerHTML = _sMsg  : function(){};
		_sSubmit ? this.button('dialogSubmit', _sSubmit) | $OBJ('dialogSubmit').focus() : $OBJ('dialogSubmit').style.display = "none";
		_sCancel ? this.button('dialogCancel', _sCancel) : $OBJ('dialogCancel').style.display = "none";
		_sClose ? this.button('dialogBoxClose', _sClose) : function(){};
	}
	this.set = function(_oAttr, _sVal){
		var oDialogDiv = $OBJ('dialogBox');
		var oHeight = $OBJ('dialogHeight');
		if(_sVal != ''){
			switch(_oAttr){
				case 'title':
					$OBJ('dialogBoxTitle').innerHTML = _sVal;
					title = _sVal;
					break;
				case 'width':
					oDialogDiv.style.width = _sVal;
					width = _sVal;
					this.middle('dialogBox');
					this.shadow();
					this.middle('dialogBoxShadow');
					_jcms_OperatorPlus();
					break;
				case 'height':
					oHeight.style.height = _sVal;
					height = _sVal;
					this.middle('dialogBox');
					this.shadow();
					this.middle('dialogBoxShadow');
					_jcms_OperatorPlus();
					break;
				case 'src':
					if(parseInt(_sVal) > 0){
						$OBJ('dialogBoxFace') ? $OBJ('dialogBoxFace').src = path + _sVal + '.png' : function(){};
					}else{
						$OBJ('dialogBoxFace') ? $OBJ('dialogBoxFace').src = _sVal : function(){};
					}
					src = _sVal;
					break;
				case 'url':
					this.open(_sVal);
					break;
			}
		}
	}
	this.middle = function(_sId){	
		var theWidth;
		var theHeight;
		if (document.documentElement && document.documentElement.clientWidth) { 
			theWidth = document.documentElement.clientWidth+document.documentElement.scrollLeft*2;
			theHeight = document.documentElement.clientHeight+document.documentElement.scrollTop*2; 
		} else if (document.body) { 
			theWidth = document.body.clientWidth;
			theHeight = document.body.clientHeight; 
		}else if(window.innerWidth){
			theWidth = window.innerWidth;
			theHeight = window.innerHeight;
		}
		$OBJ(_sId).style.display = '';
		$OBJ(_sId).style.position = "absolute";
		$OBJ(_sId).style.left = (theWidth / 2) - ($OBJ(_sId).offsetWidth / 2)+"px";
		if(document.all||$OBJ("user_page_top")){
			$OBJ(_sId).style.top = (theHeight / 2 + document.body.scrollTop) - ($OBJ(_sId).offsetHeight / 2)+"px";
		}else{
			var sClientHeight = parent ? parent.document.body.clientHeight : document.body.clientHeight;
			var sScrollTop = parent ? parent.document.body.scrollTop : document.body.scrollTop;
			var sTop = -80 + (sClientHeight / 2 + sScrollTop) - ($OBJ(_sId).offsetHeight / 2);
			$OBJ(_sId).style.top = (theHeight / 2 + document.body.scrollTop) - ($OBJ(_sId).offsetHeight / 2)+"px";
		}
	}
	BtnOver=function(obj,path){obj.style.backgroundImage = "url("+path+"button2.gif)";}
	BtnOut=function(obj,path){obj.style.backgroundImage = "url("+path+"button1.gif)";}
	ShowSelectBoxes=function(){var x = document.getElementsByTagName("SELECT");for (i=0;x && i < x.length; i++){x[i].style.visibility = "visible";}}
	HideSelectBoxes=function(){var x = document.getElementsByTagName("SELECT");for (i=0;x && i < x.length; i++) {x[i].style.visibility = "hidden";}}

}
///////////////////////////////////////////////////////////////////////////
function _jcms_OperatorPlus() {
	if (_jcms_DialogIsShown == true) {
		var oDialogDiv = $OBJ("dialogBox");
		var oShadow = $OBJ("dialogBoxShadow");
		var oWidth = oDialogDiv.offsetWidth;
		var oHeight = oDialogDiv.offsetHeight;
		var theBody = document.getElementsByTagName("BODY")[0];
		var scTop = parseInt(_jcms_GetScrollTop(),10);
		var scLeft = parseInt(theBody.scrollLeft,10);
		var fullHeight = _jcms_GetViewportHeight();
		var fullWidth = _jcms_GetViewportWidth();
		oDialogDiv.style.top = (scTop + ((fullHeight - oHeight) / 2)) + "px";
		oDialogDiv.style.left = (scLeft + ((fullWidth - oWidth) / 2)) + "px";
		oShadow.style.top = (scTop + ((fullHeight - oShadow.offsetHeight) / 2)) + "px";
		oShadow.style.left = (scLeft + ((fullWidth - oShadow.offsetWidth) / 2)) + "px";
		if (_jcms_WindowMask != null) {
			var popHeight = theBody.scrollHeight;
			var popWidth = theBody.scrollWidth;
			if (fullHeight > theBody.scrollHeight) popHeight = fullHeight;
			if (fullWidth > theBody.scrollWidth) popWidth = fullWidth;
			_jcms_WindowMask.style.height = popHeight + "px";
			_jcms_WindowMask.style.width = popWidth + "px";
		}
	}
}
function _jcms_GetViewportHeight() {
	if (window.innerHeight!=window.undefined)//FF
	{
		return window.innerHeight;
	}
	if (document.compatMode=='CSS1Compat')//IE
	{
		return document.documentElement.clientHeight;
	}
	if (document.body)//other
	{
		return document.body.clientHeight; 
	}
	return window.undefined; 
}
function _jcms_GetViewportWidth() {
	var offset = 17;
	var width = null;
	if (window.innerWidth!=window.undefined)//FF
	{
		//return window.innerWidth-offset; 
		return window.innerWidth; 
	}
	if (document.compatMode=='CSS1Compat')//IE
	{
		return document.documentElement.clientWidth; 
	}
	if (document.body)//other
	{
		return document.body.clientWidth; 
	}
	return window.undefined; 
}
function _jcms_GetScrollTop() {
	if (self.pageYOffset){return self.pageYOffset;}
	else if (document.documentElement && document.documentElement.scrollTop){return document.documentElement.scrollTop;}
	else if (document.body){return document.body.scrollTop;}
}
function _jcms_GetScrollLeft() {
	if (self.pageXOffset){return self.pageXOffset;}
	else if (document.documentElement && document.documentElement.scrollLeft){return document.documentElement.scrollLeft;}
	else if (document.body){return document.body.scrollLeft;}
}
function _jcms_SetDialogTitle(){
	if(window.document.title!=""){
		try {
			$OBJ('dialogBoxTitle').innerHTML = window.document.title;
		}
		catch(e) {
			try {
				parent.$OBJ('dialogBoxTitle').innerHTML = window.document.title;
			}
			catch(e) {
			}	
		}
	}
}
function _jcms_SetDialogSize(w,h){
	try {
		if(w>0) $OBJ('dialogBox').style.width = w;
		if(h>0) $OBJ('dialogHeight').style.height = h;
		_jcms_OperatorPlus();
	}
	catch(e) {
		try {
			if(w>0) parent.$OBJ('dialogBox').style.width = w;
			if(h>0) parent.$OBJ('dialogHeight').style.height = h;
			parent._jcms_OperatorPlus();
		}
		catch(e) {
		}	
	}	
}
/* Url编码 */ 
_jcms_UrlEncode = function(unzipStr){ 
	var zipstr=""; 
	var strSpecial="!\"#$%&'()*+,/:;<=>?[]^`{|}~%"; 
	var tt= ""; 
	for(var i=0;i<unzipStr.length;i++){ 
		var chr = unzipStr.charAt(i); 
		var c=_jcms_StringToAscii(chr); 
		tt += chr+":"+c+"n"; 
		if(parseInt("0x"+c) > 0x7f){ 
			zipstr+=encodeURI(unzipStr.substr(i,1)); 
		}else{ 
		if(chr==" ") 
			zipstr+="+"; 
		else if(strSpecial.indexOf(chr)!=-1) 
			zipstr+="%"+c.toString(16); 
		else 
			zipstr+=chr; 
		} 
	} 
	return zipstr; 
} 
/* Url解码 */ 
_jcms_UrlDecode=function(zipStr){ 
	var uzipStr=""; 
	for(var i=0;i<zipStr.length;i++){ 
		var chr = zipStr.charAt(i); 
		if(chr == "+"){ 
			uzipStr+=" "; 
		}else if(chr=="%"){ 
			var asc = zipStr.substring(i+1,i+3); 
			if(parseInt("0x"+asc)>0x7f){ 
				uzipStr+=decodeURI("%"+asc.toString()+zipStr.substring(i+3,i+9).toString()); 
				i+=8; 
			}else{ 
				uzipStr+=_jcms_AsciiToString(parseInt("0x"+asc)); 
				i+=2; 
			} 
		}else{ 
			uzipStr+= chr; 
		} 
	} 
	return uzipStr; 
} 
var _jcms_StringToAscii = function(str){
	return str.charCodeAt(0).toString(16);
}
var _jcms_AsciiToString = function(asccode){
	return String.fromCharCode(asccode);
}

////////////////////////////////////////////////////////////////////////////////////////////
function _jcms_SetUrlRefresh(url)
{
	if(url.indexOf("?") > 0)
    		return url+"&t="+(new Date().getTime());   
	else
    		return url+"?t="+(new Date().getTime());   
}
/*当前网站访问者信息*/
var user = new Object();
if(JumbotCms.Cookie.get(site.CookiePrev + "user", "id") == ""){//游客
	user.id = "0";
	user.name = "guest";
	user.nickname = "游客";
	user.password = "666666";
	user.userkey = "666666";
	user.groupid = "0";
	user.adminid = "0";
	user.groupname = "游客组";
	user.setting = "";
	user.cookies = "88888888";
}
else{
	user.id = JumbotCms.Cookie.get(site.CookiePrev + "user", "id");
	user.name = JumbotCms.Cookie.get(site.CookiePrev + "user", "name");
	user.nickname = JumbotCms.Cookie.get(site.CookiePrev + "user", "nickname");
	user.password = JumbotCms.Cookie.get(site.CookiePrev + "user", "password");
	user.userkey = JumbotCms.Cookie.get(site.CookiePrev + "user", "password").substring(4,12);
	user.groupid = JumbotCms.Cookie.get(site.CookiePrev + "user", "groupid");
	user.adminid = JumbotCms.Cookie.get(site.CookiePrev + "user", "adminid");
	user.groupname = JumbotCms.Cookie.get(site.CookiePrev + "user", "groupname");
	user.setting = JumbotCms.Cookie.get(site.CookiePrev + "user", "setting");
	user.cookies = JumbotCms.Cookie.get(site.CookiePrev + "user", "cookies");
}

var _jcms_StuHover = function() {
	var cssRule;
	var newSelector;
	for (var i = 0; i < document.styleSheets.length; i++)
		for (var x = 0; x < document.styleSheets[i].rules.length ; x++)
			{
			cssRule = document.styleSheets[i].rules[x];
			if (cssRule.selectorText.indexOf("LI:hover") != -1)
			{
				 newSelector = cssRule.selectorText.replace(/LI:hover/gi, "LI.iehover");
				document.styleSheets[i].addRule(newSelector , cssRule.style.cssText);
			}
		}
	var topnavbar = $OBJ("topnavbar");
	if(topnavbar != null)
	{
		var getElm = topnavbar.getElementsByTagName("LI");
		for (var i=0; i<getElm.length; i++) {
			getElm[i].onmouseover=function() {
				this.className+=" iehover";
			}
			getElm[i].onmouseout=function() {
				this.className=this.className.replace(new RegExp(" iehover\\b"), "");
			}
		}
	}
}
/*切换输入法*/
function _jcms_ChangeIEM(n){
	if(n == 1)
	{
		JumbotCms.Cookie.set('ime_qqweb','1');
		_jcms_LoadIEM();
	}
	else{
		JumbotCms.Cookie.set('ime_qqweb','0');
		location.reload();
	}
}
/*加载输入法*/
function _jcms_LoadIEM(){
	if(JumbotCms.Cookie.get('ime_qqweb') != '1')
	{
		$('#ime_local').show();
		$('#ime_qqweb').hide();
	}
	else{
		$('#ime_local').hide();
		$('#ime_qqweb').show();
		//$("input[@type='text']").addClass('nochinese');
		(function(q){!!q?q.toggle():(function(d,j){j=d.createElement('script');j.src='//ime.qq.com/fcgi-bin/getjs';j.setAttribute('ime-cfg','lt=2');d.getElementsByTagName('head')[0].appendChild(j)})(document)})(window.QQWebIME)
	}

}
/*HTML标签小写*/
function HTML2LowerCase(html)
{
	return html.replace(/(<\/?)([a-z\d\:]+)((\s+.+?)?>)/gi,function(s,a,b,c){return a+b.toLowerCase()+c;});
}
/*获取指定字符串的长度*/
function GetLength(id)
{
	var srcjo = $("#"+id);
	sType = srcjo.get(0).type;
	var len = 0;
	switch(sType)
	{
		case "text":
		case "hidden":
		case "password":
		case "textarea":
		case "file":
			var val = srcjo.val();
			for (var i = 0; i < val.length; i++) 
			{
				if (val.charCodeAt(i) >= 0x4e00 && val.charCodeAt(i) <= 0x9fa5){ 
					len += 2;
				}else {
					len++;
				}
			}
			break;
		case "checkbox":
		case "radio": 
			len = $("input[@type='"+sType+"'][@name='"+srcjo.attr("name")+"'][@checked]").length;
			break;
		case "select-one":
			len = srcjo.get(0).options ? srcjo.get(0).options.selectedIndex : -1;
			break;
		case "select-more":
			break;
	}
	return len;
}
function InsertUnit(text, obj) {
	if(!obj) {
		obj = 'jstemplate';
	}
	var o = $OBJ(obj);
	o.focus();
	if(!JumbotCms.isUndefined(o.selectionStart)) {
		var opn = o.selectionStart + 0;
		o.value = o.value.substr(0, o.selectionStart) + text + o.value.substr(o.selectionEnd);
	} else if(document.selection && document.selection.createRange) {
		var sel = document.selection.createRange();
		sel.text = text.replace(/\r?\n/g, '\r\n');
		//sel.moveStart('character', -strlen(text));
	} else {
		o.value += text;
	}
}
function JoinSelect(selectName)
{
	var selectIDs="";
	$("input[@name='" + selectName + "']").each(function(){
   		if($(this).attr("checked")==true){
			if(selectIDs=="")
    				selectIDs = $(this).attr("value");
			else
				selectIDs += ","+$(this).attr("value");
   		}
	})
	return selectIDs;
}

function ajaxAddMessage(userid,username){
	window.open(site.Dir + 'user/pmsend_default.aspx?touserid='+userid+'&tousername='+encodeURIComponent(username));
}
function ajaxAddFriend(userid){
	$.ajax({
		type:		"post",
		dataType:	"json",
		data:		"id="+userid+"&time="+(new Date().getTime()),
		url:		site.Dir + "user/friendadd_ajax.aspx?oper=ajaxAddFriend",
		error:		function(XmlHttpRequest,textStatus, errorThrown){if(XmlHttpRequest.responseText!=""){alert(XmlHttpRequest.responseText);}},
		success:	function(d){
			switch (d.result)
			{
			case '0':
				alert(d.returnval);
				break;
			case '1':
				alert(d.returnval);
				break;
			}
		}
	});
}




/*显示个人主页*/
function ShowUserPage(userid){
	//alert(userid);
}


/*========================================================================================*/
function UrlSearch(){ //重复时只取最后一个
	var name,value; 
	var str=window.location.href; //取得整个地址栏
	var num=str.indexOf("?") 
	str=str.substr(num+1); //取得所有参数
	var arr=str.split("&"); //各个参数放到数组里
	for(var i=0;i < arr.length;i++){ 
		num=arr[i].indexOf("="); 
		if(num>0){ 
			name=arr[i].substring(0,num);
			value=arr[i].substr(num+1);
			this[name]=value;
		} 
	}
	this["getall"]=str;
}
var RQ=new UrlSearch(); //实例化
function formatStr(s){
	if(typeof(s) == "string")
		return s;
	else
		return "";
}
function joinValue(parameter){
	eval("var temp=RQ."+parameter);
	if((typeof(temp) == "string") && (typeof(temp) != null))
	{
		return "&"+parameter+"="+temp.replace(/(^\s*)|(\s*$)/g, "");
	}
	else
		return "";
}
/*
function q(parameter){
	eval("var temp=RQ."+parameter);
	if((typeof(temp) == "string") && (typeof(temp) != null))
	{
		return temp.replace(/(^\s*)|(\s*$)/g, "");
	}
	else
		return "";
}
*/
function q(pname){
	var query = location.search.substring(1);
	var qq = "";
	params = query.split("&");
	if(params.length>0){
		for(var n in params){
			var pairs = params[n].split("=");
			if(pairs[0]==pname){
				qq = pairs[1];
				break;
			}
		}
	}
	return qq;
}
function anchor(){
	var str=window.location.href; //取得整个地址栏
	var num=str.indexOf("#") 
	str=str.substr(num+1);
	return str;
}
/*获取当前页页码*/
function thispage(){
	var r = /^\+?[1-9][0-9]*$/;
	if(r.test(q('page')))
		return q('page');
	else
		return "1";
}
/*全选*/
function CheckAll(form)
{
	var f;
	if(form==null)
		f = document.getElementsByTagName('FORM')[0];
	else
		f = $OBJ(form);
	for (var i=0;i<f.elements.length;i++)
	{
		var e = f.elements[i];
		if (e.name != 'chkall' && e.type == "checkbox")
			e.checked = $OBJ("chkall").checked;
	}
}
/*全不选*/
function CheckNo(form)
{
	var f;
	if(form==null)
		f = document.getElementsByTagName('FORM')[0];
	else
		f = $OBJ(form);
	for (var i=0;i<f.elements.length;i++)
	{
		var e = f.elements[i];
		if (e.type == "checkbox")
			e.checked = false;
	}
}
function WinFullOpen(url){
	var newwin=window.open(url,"","scrollbars");
	if(document.all){
		newwin.moveTo(0,0);
		newwin.resizeTo(screen.width,screen.height);
	}
}
function WindowOpen(url,iWidth,iHeight,name)
{
	if(name==null) name='';
	var iTop = (window.screen.availHeight-30-iHeight)/2;
	var iLeft = (window.screen.availWidth-10-iWidth)/2;
	window.open(url,name,'height='+iHeight+',,innerHeight='+iHeight+',width='+iWidth+',innerWidth='+iWidth+',top='+iTop+',left='+iLeft+',toolbar=no,menubar=no,scrollbars=auto,resizeable=no,location=no,status=no');
}
/*字符串格式化*/
String.prototype.Trim = function(){return this.replace(/(^\s*)|(\s*$)/g, "");}
String.prototype.LTrim = function(){return this.replace(/(^\s*)/g, "");}
String.prototype.RTrim = function(){return this.replace(/(\s*$)/g, "");}

/*日期格式化(2009-06-30+++)*/
function formatDate(strDate, format){
	return parseDate(strDate).format(format);
} 
Date.prototype.format = function(format)
{
	if(format == null) format = "yyyy-MM-dd hh:mm:ss";
	var o = 
	{
		"M+" : this.getMonth()+1, //month
		"d+" : this.getDate(),    //day
		"h+" : this.getHours(),   //hour
		"m+" : this.getMinutes(), //minute
		"s+" : this.getSeconds(), //second
		"q+" : Math.floor((this.getMonth()+3)/3), //quarter
		"S" : this.getMilliseconds() //millisecond
	}
		
	if(/(y+)/.test(format)) 
		format=format.replace(RegExp.$1,(this.getFullYear()+"").substr(4 - RegExp.$1.length));
	for(var k in o)
		if(new RegExp("("+ k +")").test(format))
			format = format.replace(RegExp.$1,RegExp.$1.length==1 ? o[k] : ("00"+ o[k]).substr((""+ o[k]).length));
	return format;
}
function parseDate(str){   
	if(typeof str == 'string'){   
		var results = str.match(/^ *(\d{4})-(\d{1,2})-(\d{1,2}) *$/);   
		if(results && results.length>3)   
			return new Date(parseInt(results[1]),parseInt(results[2]) -1,parseInt(results[3]));    
		results = str.match(/^ *(\d{4})-(\d{1,2})-(\d{1,2}) +(\d{1,2}):(\d{1,2}):(\d{1,2}) *$/);   
		if(results && results.length>6)   
			return new Date(parseInt(results[1]),parseInt(results[2]) -1,parseInt(results[3]),parseInt(results[4]),parseInt(results[5]),parseInt(results[6]));    
		results = str.match(/^ *(\d{4})-(\d{1,2})-(\d{1,2}) +(\d{1,2}):(\d{1,2}):(\d{1,2})\.(\d{1,9}) *$/);   
		if(results && results.length>7)   
			return new Date(parseInt(results[1]),parseInt(results[2]) -1,parseInt(results[3]),parseInt(results[4]),parseInt(results[5]),parseInt(results[6]),parseInt(results[7]));    
	}   
	return null;   
}
/**
 * 将数值四舍五入(保留2位小数)后格式化成金额形式
 *
 * @param num 数值(Number或者String)
 * @return 金额格式的字符串,如'1,234,567.45'
 * @type String
 */
function formatCurrency(num) {
	num = num.toString().replace(/\$|\,/g,'');
	if(isNaN(num))
	num = "0";
	sign = (num == (num = Math.abs(num)));
	num = Math.floor(num*100+0.50000000001);
	cents = num%100;
	num = Math.floor(num/100).toString();
	if(cents<10)
		cents = "0" + cents;
	for (var i = 0; i < Math.floor((num.length-(1+i))/3); i++)
	num = num.substring(0,num.length-(4*i+3))+','+
	num.substring(num.length-(4*i+3));
	return (((sign)?'':'-') + num + '.' + cents);
}
/*预览HTML代码*/
function PreviewHTML(txt)
{
	var win = window.open("", "win");
	win.document.open("text/html", "replace"); 
	win.document.write(txt); 
	win.document.close();
}
function formatIsPass(ispass) {
	if(ispass == "-1")return "已删";
	return ispass == "1" ? "已审" : "未审";
}
function formatIsImg(isimg) {
	return isimg == "1" ? "有索引图" : "无索引图";
}
function formatIsTop(istop) {
	return istop == "1" ? "置顶" : "不置顶";
}
function formatIsFocus(isfocus) {
	return isfocus == "1" ? "焦点" : "非焦点";
}
/*格式化列表*/
function FormatListValue(id)
{
	var _val = $('#'+id).val();
	if(_val=='') return;
	_val =_val.replace(/[，]/g,",");
	_val =_val.replace(/ /g,",");
	_val =_val.replace(/[,]+/g,",");
	$('#'+id).val(_val);
}
function PlayCodeVoice(wmpid)
{
	if(!wmpid) wmpid="player";
	var _voicewmp2 = $OBJ(wmpid);
	var _voicecode = JumbotCms.Cookie.get("ValidateCode");
	_voicewmp2.innerHTML = "<embed   id='sound_play' name='sound_play' src='" + site.Dir + "style/flash/sound_play.swf?"+(new Date().getTime())+"' FlashVars='isPlay=1&url=" + site.Dir + "plus/codevoice.aspx&code=" + _voicecode + "' width='0' height='0' allowScriptAccess='always' type='application/x-shockwave-flash' pluginspage='http://www.macromedia.com/go/getflashplayer' /></embed>";
	//alert(_voicewmp2.innerHTML);
}




function get_user_status(w)
{
	//参数说明:w=0,1分别指"初始化"和"登陆"
	var uName="";
	var uPass="";
	if(w==null) w=0;
	if(w==1)
	{
		uName=$("#loginBarName").val();
		uPass=$("#loginBarPass").val();
		if(!uName || !uPass)
		{
			window.location.href = site.Dir+"passport/login.aspx";
			return;
		}
		$("btnLoginbar").attr("disabled","disabled");
	}
	$.ajax({
		type:		"post",
		dataType:	"json",
		data:		"name="+encodeURIComponent(uName)+"&pass="+encodeURIComponent(uPass)+"&state="+w,
		url:		site.Dir + "ajax/user.aspx?oper=ajaxLoginbar&time="+(new Date().getTime()),
		success:	function(d){
			if(d.result!="1" && w==1)
				alert(d.returnval);
			else
			{
				if(d.result == "1"){//成功登录
					var _adminBar = '';
					if(d.adminid != "0")
						_adminBar = '<li class="hr">|</li><li><a href="' + site.Dir + 'admin/login.aspx?adminid=' + d.adminid + '" target="_blank">管理中心</a></li>';
					var _messageBar = '';
					if(d.newpmcount > 0)
						_messageBar = '<li class="pm1"><a href="' + site.Dir + 'user/pmlist_default.aspx" title="' + d.newpmcount + '条未读消息" target="_blank">消息<span style="color:red;">(' + d.newpmcount + ')</span></a></li>';
					else
						_messageBar = '<li class="pm0"><a href="' + site.Dir + 'user/pmlist_default.aspx" title="0条未读消息" target="_blank">消息</a></li>';
					var _ajaxLoginbar = '\
						<ul>\
							<li class="user"><a href="' + site.Dir + 'user/index_default.aspx" title="进入个人中心" target="_blank"><b>' + d.username + '</b></a></li>\
							<li><a href="' + site.Dir + 'passport/logout.aspx?userkey=' + d.userkey + '">[退出]</a></li>\
							<li class="points"><a href="' + site.Dir + 'customer/buypoints_default.aspx?mod=customer" target="_blank" title="当前剩余点数' + d.points + '，点击马上充值">点数</a></li>' + _messageBar + '\
							<li class="hr">|</li><li><a href="' + site.Dir + 'user/index_default.aspx" target="_blank">进入我的中心</a></li>' + _adminBar + '\
						</ul>\
					';
					$("#user_status").html(_ajaxLoginbar);
				}
			}
			$("#user_status").show();
			ajaxShowWeather('search_bar_weather');//显示天气(2011.03.6)
		}
	});
}
// 显示当前日期，时间
function setCurrentDateTime(o){
	var d = new Date();
	var da = d.getDate();
	var mo = d.getMonth() + 1;
	var y = d.getFullYear();
	var h = d.getHours();
	if(h<10){h='0'+h}
	var m = d.getMinutes();
	if(m<10){m='0'+m}
	var s = d.getSeconds();
	if(s<10){s='0'+s}
	var week = ['天','一','二','三','四','五','六'];
	if(typeof(o) != 'object'){o=$OBJ(o)}
	o.innerHTML = "今天是:"+y+'年'+mo+'月'+da+'日 星期'+week[d.getDay()];//+' '+h+':'+m+':'+s;
	//window.setTimeout(function(){setCurrentDateTime(o)}, 1000);	
}

// 显示当前日期，时间
function setCurrentDateTime2() {
    var d = new Date();
    var da = d.getDate();
    var mo = d.getMonth() + 1;
    var y = d.getFullYear();
    var h = d.getHours();
    if (h < 10) { h = '0' + h }
    var m = d.getMinutes();
    if (m < 10) { m = '0' + m }
    var s = d.getSeconds();
    if (s < 10) { s = '0' + s }
    var week = ['天', '一', '二', '三', '四', '五', '六'];
    var _document = y + '年' + mo + '月' + da + '日 星期' + week[d.getDay()];
    return _document;
}

function CheckSearchData() {
	var type = $("#search_channeltype").val();
	if ($("#search_keywords").val() == "" || $("#search_keywords").val() == "请输入关键字")
	{
	    alert("请输入关键字");
	    $("#search_keywords").val('');
		return;
	}
	window.open(site.Dir + 'search/default.aspx?type='+type+'&k='+encodeURIComponent($("#search_keywords").val()));
}

function CheckSearchData2()
{
	var type = $("#search_channeltype").val();
	if($("#search_keywords").val()=="")
	{
		alert("请输入关键字");
		return;
	}
	window.open(site.Dir + 'search/default.aspx?type='+type+'&k='+encodeURIComponent($("#search_keywords").val()));
}
function BindModuleRadio(spanId,selecdType)
{
	var data = ___JSON_Modules;
	var html = "";
	for (i=0;i<data.table.length;i++) {
		html += "<span style=\"padding-right:6px;\"><input id=\"RaChannelType_" + data.table[i].type + "\" type=\"radio\" name=\"type\" value=\"" + data.table[i].type + "\"";
		if(data.table[i].type == selecdType)
			html += " checked=\"checked\"";
		html += " /><label for=\"RaChannelType_" + data.table[i].type + "\">&nbsp;" + data.table[i].title + "</label></span>";
	}
	html += "<span style=\"padding-right:6px;\"><input id=\"RaChannelType_all\" type=\"radio\" name=\"type\" value=\"all\"";
	if(selecdType == "all")
		html += " checked=\"checked\"";
	html += " /><label for=\"RaChannelType_all\">&nbsp;所有</label></span>";
	$("#"+spanId).html(html);
}
var ___JSON_Modes = {
	recordcount: 2, 
	table: [
		{no: 0, title: '普通检索'},
		{no: 1, title: '智能检索'}
	]
}
function BindModeRadio(spanId,selecdMode)
{
	var data = ___JSON_Modes;
	var html = "";
	for (i=0;i<data.table.length;i++) {
		html += "<span style=\"padding-right:6px;\"><input id=\"RaSearchMode_" + data.table[i].no + "\" type=\"radio\" name=\"mode\" value=\"" + data.table[i].no + "\"";
		if(data.table[i].no == selecdMode)
			html += " checked=\"checked\"";
		html += " /><label for=\"RaSearchMode_" + data.table[i].no + "\">&nbsp;" + data.table[i].title + "</label></span>";
	}
	$("#"+spanId).html(html);
}
function ajaxGo2View(ccId,id)
{
	$.ajax({
		type:		"post",
		dataType:	"json",
		data:		"contentid="+id+"&channelid="+ccId+"&time="+(new Date().getTime()),
		url:		site.Dir + "ajax/content.aspx?oper=ajaxGo2View",
        	error:		function(XmlHttpRequest,textStatus, errorThrown){if(XmlHttpRequest.responseText!=""){alert(XmlHttpRequest.responseText);}},
		success:	function(d){
			window.open(d.returnval);
		}
	});
}

/*将会被抛弃*/
function ajaxViewCount(cType,id,randomid,needadd)
{
	var addit = needadd == false ? 0 : 1;
	$.ajax({
		type:		"get",
		dataType:	"json",
		data:		"oper=ajaxViewCount&id="+id+"&addit="+addit+"&cType="+cType+"&time="+(new Date().getTime()),
		url:		site.Dir + "ajax/content.aspx",
		error:		function(XmlHttpRequest,textStatus, errorThrown){if(XmlHttpRequest.responseText!=""){alert(XmlHttpRequest.responseText);}},
		success:	function(d){
			$("#ajaxViewCount_"+id+"_"+randomid).text(d.count);
		}
	});
}
var _closeTimer = -1;
function Go2PageForm(url)
{
	if(user.adminid != "0")
		window.open(site.Dir + "plus/"+url+"&userkey="+user.userkey);
	else{
		var oDialog = new _jcms_Dialog('1', '确认框', 350, 130, null, false);
		oDialog.init();
		var sHtml = '<form id="Go2PageForm"><table width="100%" border="0" align="center" cellpadding="0" cellspacing="0">\
				<tr><td height="30" align="left"><span id="closetimer"></span></td></tr>\
				<tr><td height="60" align="left">确定要下载该资源吗？<br /><br />同一资源只扣除一次点数。</td></tr>\
				<tr><td height="20" align="left"><input type="button" value="开始下载" onclick="Go2PageCheck(\''+url+'\');" />&nbsp;&nbsp;<input type="button" value="稍后再说" onclick="Go2PageStop();" /></td></tr>\
			</table></form>\
		';
		oDialog.event(sHtml,'');
		Go2PageStart();
	}
}
function Go2PageCheck(url){
	window.open(site.Dir + "plus/"+url+"&userkey="+user.userkey);
	Go2PageStop();
}
function Go2PageStart(){
	_closeTimer = 30;
	Go2PageAutoClose(_closeTimer, "closetimer");
}
function Go2PageStop(){
	_closeTimer = - 1;
	Go2PageAutoClose(_closeTimer, "closetimer");
}
function Go2PageAutoClose(secs, spanid){
	if($OBJ(spanid) == null)
		return;
	if(secs > 0) 
	{
		_closeTimer = secs - 1;
		$('#'+spanid).html('还有 <span style="color:red;">' + _closeTimer + '</span> 秒自动关闭');
		window.setTimeout("Go2PageAutoClose(" + _closeTimer + ",'" + spanid + "')", 1000);
	} 
	else if(secs == 0) 
	{
		_closeTimer = -1;
		Go2PageAutoClose(_closeTimer,spanid);
	} 
	else
		new _jcms_Dialog().reset();
}
function addFavorite(ccid,cType,id)
{
	$.ajax({
		type:		"get",
		dataType:	"html",
		data:		"oper=addFavorite&id="+id+"&ccid="+ccid+"&cType="+cType+"&time="+(new Date().getTime()),
		url:		site.Dir + "ajax/content.aspx",
		error:		function(XmlHttpRequest,textStatus, errorThrown){if(XmlHttpRequest.responseText!=""){alert(XmlHttpRequest.responseText);}},
		success:	function(d){
			alert(d);
		}
	});
}

function replaceContentTags(ccid,cType,taglist,bodyid)
{
	try{
		var elms1 = $("#"+bodyid+" a");
		for (i = 0; i < elms1.length; i++){elms1[i].title="";}
		var elms2 = $("#"+bodyid+" img");
		for (i = 0; i < elms2.length; i++){elms2[i].alt="";}
        	if (taglist.length == 0) return;
        	var keys = taglist.split(",");
        	var element = $OBJ(bodyid);
        	for (var i = 0; i < keys.length; i++) {
                	highlightWord(element, keys[i], site.Dir + 'search/default.aspx?ch='+ccid+'&type='+cType+'&k=');
        	}
	}
	catch(e){}

}
function highlightWord(node, word, linkurl) {
        // Iterate into this nodes childNodes 
        if (node.hasChildNodes) {
                var hi_cn;
                for (hi_cn = 0; hi_cn < node.childNodes.length; hi_cn++) {
                        highlightWord(node.childNodes[hi_cn], word, linkurl);
                }
        }
        // And do this node itself 
        if (node.nodeType == 3) { // text node 
                tempNodeVal = node.nodeValue.toLowerCase();
                tempWordVal = word.toLowerCase();
                if (tempNodeVal.indexOf(tempWordVal) > -1) {
                        pn = node.parentNode;
                        if (pn.className != "highlight") {
                                nv = node.nodeValue;
                                ni = tempNodeVal.indexOf(tempWordVal);
                                before = document.createTextNode(nv.substr(0, ni));
                                docWordVal = nv.substr(ni, word.length);
                                after = document.createTextNode(nv.substr(ni + word.length));
                                hiwordtext = document.createTextNode(docWordVal);
                                hiword = document.createElement("A");
                                hiword.className = "highlight";
				if(linkurl)
					hiword.href = linkurl + encodeURIComponent(tempWordVal);
                                hiword.appendChild(hiwordtext);
                                pn.insertBefore(before, node);
                                pn.insertBefore(hiword, node);
                                pn.insertBefore(after, node);
                                pn.removeChild(node);
                        }
                }
        }

}
/*选项卡*/
function jTab(Id, tId, EclassName, iBeHavior){
	if(!document.getElementById(Id))return;
	if(iBeHavior==null)iBeHavior='mouseover';
	if(EclassName==null)EclassName='more';
	var self=this;
	var links=document.getElementById(Id).getElementsByTagName('a');
	if(links.length==0)return;

	this.init=function(){
		for(var i=0;i<links.length;i++){
			eval("links[i].on"+iBeHavior+"=function(e){return self.itab(this);};");
			links[i].onclick=function(){
				return (this.href.indexOf('javascript:')>-1 || this.href.indexOf('#')<0 || this.className==EclassName);
			};
			links[i].onfocus=function(e){
				this.blur();
			};
		}
		self.itab(links[0]);
	};
	this.itab=function(o){
		if(o.href.indexOf('javascript:')>-1 || o.href.indexOf('#')<0 || o.className==EclassName){return true;}
		for(var i=0;i<links.length;i++){
			if(links[i].className!=EclassName)links[i].className='';
		}
		o.className='s';
		var url=o.href.substring(o.href.indexOf('#')+1);
		this.showDiv(url);
		return false;
	};
	this.showDiv=function(tDiv){
		if(document.getElementById(tId) && document.getElementById(tDiv)){
			document.getElementById(tId).innerHTML=document.getElementById(tDiv).innerHTML;
			jTab_img_border(document.getElementById(tId));
			//jTab_blank_link(document.getElementById(tId));
			jTab_set_className(document.getElementById(tId));
		}
	};
	this.createDiv=function(id){
		var div=document.createElement('div');
		div.style.display='none';
		div.id=id;
		document.body.appendChild(div);
		return div;
	};
	this.init();
}

function jTab_img_border(obj){
	var li = obj.getElementsByTagName('li');
	var img = null;
	var bc = '#333';
	for(var i=0;i<li.length;i++){
		img = li[i].getElementsByTagName('img');
		for(var j=0;j<img.length;j++){
			bc = img[j].style.borderColor;
			img[j].onmouseover=function(){this.style.borderColor='#f60';};
			img[j].onmouseout=function(){this.style.borderColor=bc;};
		}
	}
}

function jTab_blank_link(obj){
	obj=obj==null?document:obj;
	var links = obj.getElementsByTagName('a');
	for(var j=0;j<links.length;j++){
		links[j].setAttribute('target','_blank');
	}
}

function jTab_set_className(obj){
	obj=obj==null?document:obj;
	this.initialize=function(){
		var ename='';
		var links=obj.getElementsByTagName('a');
		for(var i=0;i<links.length;i++){
			ename=links[i].className;
			if(ename=='new' || ename=='hot'){
				links[i].style.position='relative';
				this.createDiv(links[i],ename);
			}
		}
	};
	this.createDiv=function(ilink, en){
		var a=document.createElement('div');
		a.className='icon_'+en;
		a.style.left=parseInt(ilink.offsetLeft-15)+'px';
		a.style.top=parseInt(ilink.offsetTop-15)+'px';
		ilink.parentNode.appendChild(a);
		return a;
	};
	this.initialize();
}
/*内容滚动*/
function jScrollText(content,btnPrevious,btnNext,autoStart,timeout,isSmoothScroll)
{
	this.Speed = 10;
	this.Timeout = timeout;
	this.stopscroll =false;//是否停止滚动的标志位
	this.isSmoothScroll= isSmoothScroll;//是否平滑连续滚动
	this.LineHeight = 20;//默认高度。可以在外部根据需要设置
	this.NextButton = this.$(btnNext);
	this.PreviousButton = this.$(btnPrevious);
	this.ScrollContent = this.$(content);
	if(!this.ScrollContent) return;
	this.ScrollContent.innerHTML += this.ScrollContent.innerHTML;//为了平滑滚动再加一遍

	if(this.PreviousButton)

	{
		this.PreviousButton.onclick = this.GetFunction(this,"Previous"); 
		this.PreviousButton.onmouseover = this.GetFunction(this,"MouseOver");
		this.PreviousButton.onmouseout = this.GetFunction(this,"MouseOut");
	}
	if(this.NextButton){
		this.NextButton.onclick = this.GetFunction(this,"Next");
		this.NextButton.onmouseover = this.GetFunction(this,"MouseOver");
		this.NextButton.onmouseout = this.GetFunction(this,"MouseOut");
	}
	this.ScrollContent.onmouseover = this.GetFunction(this,"MouseOver");
	this.ScrollContent.onmouseout = this.GetFunction(this,"MouseOut");

	if(autoStart)
	{
		this.Start();
	}
}

jScrollText.prototype = {

	$:function(element)
	{
		return document.getElementById(element);
	},
	Previous:function()
	{
		this.stopscroll = true;
		this.Scroll("up");
	},
	Next:function()
	{
		this.stopscroll = true;
		this.Scroll("down");
	},
	Start:function()
	{
		if(this.isSmoothScroll)
		{
			this.AutoScrollTimer = setInterval(this.GetFunction(this,"SmoothScroll"), this.Timeout);
		}
		else
		{		
			this.AutoScrollTimer = setInterval(this.GetFunction(this,"AutoScroll"), this.Timeout);
		}
	},
	Stop:function()
	{
		clearTimeout(this.AutoScrollTimer);
		this.DelayTimerStop = 0;
	},
	MouseOver:function()
	{	
		this.stopscroll = true;
	},
	MouseOut:function()
	{
		this.stopscroll = false;
	},
	AutoScroll:function()
	{
		if(this.stopscroll) 
		{
			return;
		}
		this.ScrollContent.scrollTop++;
		if(parseInt(this.ScrollContent.scrollTop) % this.LineHeight != 0)
		{
			this.ScrollTimer = setTimeout(this.GetFunction(this,"AutoScroll"), this.Speed);
		}
		else
		{
			if(parseInt(this.ScrollContent.scrollTop) >= parseInt(this.ScrollContent.scrollHeight) / 2)
			{
				this.ScrollContent.scrollTop = 0;
			}
			clearTimeout(this.ScrollTimer);
			//this.AutoScrollTimer = setTimeout(this.GetFunction(this,"AutoScroll"), this.Timeout);
		}
	},
	SmoothScroll:function()
	{
		if(this.stopscroll) 
		{
			return;
		}
		this.ScrollContent.scrollTop++;
		if(parseInt(this.ScrollContent.scrollTop) >= parseInt(this.ScrollContent.scrollHeight) / 2)
		{
			this.ScrollContent.scrollTop = 0;
		}
	},
	Scroll:function(direction)
	{

		if(direction=="up")
		{
			this.ScrollContent.scrollTop--;
		}
		else
		{
			this.ScrollContent.scrollTop++;
		}
		if(parseInt(this.ScrollContent.scrollTop) >= parseInt(this.ScrollContent.scrollHeight) / 2)
		{
			this.ScrollContent.scrollTop = 0;
		}
		else if(parseInt(this.ScrollContent.scrollTop)<=0)
		{
			this.ScrollContent.scrollTop = parseInt(this.ScrollContent.scrollHeight) / 2;
		}
		
		if(parseInt(this.ScrollContent.scrollTop) % this.LineHeight != 0)
		{
			this.ScrollTimer = setTimeout(this.GetFunction(this,"Scroll",direction), this.Speed);
		}
	},
	GetFunction:function(variable,method,param)
	{
		return function()
		{
			variable[method](param);
		}
	}
}

var isIE=!-[1,];
//JS图片播放器
function renderPicPlayer(id){
	var interv=4000; //切换间隔时间
	var intervSpeed=10; //切换速度
	var cpic=0;
	var tpic=1;
	var timer, timer1, timer2;
	
	var list=$OBJ(id + '-list');
	if(list){list=list.getElementsByTagName('li')}
	var change = $OBJ(id + '-change');
	if(!list || !list.length || list.length < 2 || !change){return}
	
	var lis = cls = '';
	var picnum = list.length;
	for(var i=0;i<picnum;i++){cls=i==0?' class="active"':'';lis+='<li'+cls+'>'+(i+1)+'</li>'}
	change.innerHTML = lis;
	change = change.getElementsByTagName('li');
	var div = list[0].getElementsByTagName('div')[0];
	var img_fit_with = div.offsetWidth, img_fit_height = div.offsetHeight;
	for(var i=0;i<picnum;i++){
		change[i].index = i;
		var img = list[i].getElementsByTagName('img');
		if(img && img[0]){
			//img[0].onload = function(){resizeImage(this, img_fit_with, img_fit_height, true)}
		}
		if(i>0){
			list[i].opacity = 0;
			alpha(list[i]);
		}else{
			list[i].opacity = 100;
		}
		change[i].onmouseover = function(){
			list[cpic].opacity = 0;
			alpha(list[cpic]);
			setActive(cpic);
			cpic = tpic = this.index;
			list[tpic].opacity = 100;
			alpha(list[tpic]);
			setActive(tpic,true);
			tpic = tpic == (picnum - 1) ? 0 : tpic + 1;
			window.clearInterval(timer);
			timer = window.setInterval(loop, interv);
		}
	}
	function setActive(n,f){change[n].className=f?'active':''}
	if(picnum < 2){return}
	//控制图层透明度
	function alpha(o){if(isIE){o.style.filter="alpha(opacity="+o.opacity+")";}else{o.style.opacity=(o.opacity/100)}o.style.display=o.opacity>0?'':'none'}
	//渐显
	var fadeon=function(){setActive(tpic,true);var o=list[tpic];o.opacity+=5;alpha(o);if(o.opacity<100){window.clearTimeout(timer1);timer1=setTimeout(fadeon,intervSpeed)}else{cpic=tpic;tpic=tpic==(picnum-1)?0:tpic+1;}}
	//渐隐
	var fadeout=function(){setActive(cpic);var o=list[cpic];o.opacity-=10;alpha(o);if(o.opacity>0){window.clearTimeout(timer2);timer2=setTimeout(fadeout,intervSpeed)}else{o.opacity=0;}}
	//循环
	var loop = function(){fadeout();setTimeout(fadeon,intervSpeed+50)}
	timer = window.setInterval(loop, interv);
}

function _jcms_SearchBar(){
	var _document = "<div class=\"search_bar\">";
	_document +="    <div id=\"search_bar_date\" class=\"search_bar_left\"></div>";
	_document +="    <script type=\"text/javascript\">setCurrentDateTime('search_bar_date');<\/script>";
	_document +="    <form id=\"searchform\" target=\"_blank\" action=\"" + site.Dir + "search/default.aspx\"><input type=\"hidden\" name=\"ch\" value=\"0\" />";
	_document +="<ul class=\"tab\" id=\"sotypetab\">";
	_document +="<li class=\"new\"><span id=\"ajaxChannelType\"></span><script>BindModuleRadio('ajaxChannelType','article');</script></li>";
	_document +="</ul>";
	_document +="        <div class=\"sokey\">";
	_document +="            <input type=\"text\" name=\"k\" id=\"search_keywords\" class=\"keywords\" value=\"\" />";
	_document +="            <input type=\"submit\" id=\"searchsubmit\" class=\"submit\" value=\"搜索\" />";
	_document +="        </div>";
	_document +="    </form>";
	_document +="    <div id=\"search_bar_weather\" class=\"search_bar_right\"></div>";
	_document +="</div>";
	return _document;
}
// <table width="100%" border="0" cellspacing="0" cellpadding="0">
//                <tr>
//                  <td>站内搜索</td>
//                  <td><input class="input_in_120" name=" " type="text" value=" " /></td>
//                  <td><input name=" " type="image" value=" " src="/images/icon_search.jpg" alt="查询" /></td>
//                </tr>
//              </table>
function _page_SearchBar(){
    var _document = "<form id=\"searchform\" target=\"_blank\" action=\"/search/default.aspx\"><input type=\"hidden\" name=\"ch\" value=\"0\" />";
    _document+="<table width=\"204\">";
    _document+="<td><input type=\"text\" name=\"k\" id=\"search_keywords\"  class=\"input_in_120\"  value=\"请输入关键字\"    onfocus=\"if (this.value == '请输入关键字') {this.value = '';}\" onblur=\"if (this.value == '') {this.value = '请输入关键字';}\"  /></td>";
    _document += "<td><input type=\"submit\" id=\"searchsubmit\" class=\"button\" value=\"搜索\" /></td>";
    _document+="</tr></table>";
    _document+="</form>";
    return _document;
}

function p_search() {
    var keywords = $("#search_keywords").val();
    window.location = "/search/default.aspx?ch=0&k=" + keywords;
}

function _page_SearchBar2() {
    var _document = "<table width=\"204\">";
    _document += "     <td><input type=\"text\" name=\"k\" id=\"search_keywords\"  class=\"input_in_120\"  value=\"请输入关键字\"    onfocus=\"if (this.value == '请输入关键字') {this.value = '';}\" onblur=\"if (this.value == '') {this.value = '请输入关键字';}\"  /></td>";
    _document += "     <td><input type=\"button\" id=\"searchsubmit2\" class=\"button\" value=\"搜索\" onclick=\"p_search()\"/></td>";
    _document += "</tr></table>";
    return _document;
}

function ShowEditDiv(channeltype,channelid,contentid){
    var masterid = JumbotCms.Cookie.get(site.CookiePrev + "admin", "id");
    if(masterid != ""){
	    JumbotCms.Popup.show(site.Dir+'modules/'+channeltype+'_admin_edit.aspx?ccid='+channelid+'&id='+contentid,-1,-1,true);
	}
}

//<!--插件开关begin


var PluginVote	= true;//投票调查插件
var PluginReview	= true;//内容评论插件
var PluginPlacard	= true;//网站公告插件
var PluginLink	= true;//友情链接插件
var PluginFeedback	= true;//用户留言插件
var PluginDigg	= true;//内容顶客插件
var PluginQQOnline    = true;//QQ在线客服插件
//-->插件开关end
/*--内容顶客插件--*/

function ajaxPluginDiggAdd(cType,id)
{
	$.ajax({
		type:		"get",
		dataType:	"json",
		data:		"oper=ajaxPluginDiggAdd&id="+id+"&cType="+cType+"&time="+(new Date().getTime()),
		url:		site.Dir + "extends/digg/ajax.aspx",
		error:		function(XmlHttpRequest,textStatus, errorThrown){if(XmlHttpRequest.responseText!=""){alert(XmlHttpRequest.responseText);}},
		success:	function(d){
			$("#ajaxPluginDigg_"+id).text(d.count);
			$("#DiggSpan"+id).html("<a>谢谢支持</a>");

		}
	});
}

/*--用户留言插件--*/

function ajaxPluginFeedbackTopList(classid,pagesize,elementid)
{
	$.ajax({
		type:		"get",
		dataType:	"html",
		data:		"oper=ajaxPluginFeedbackTopList&classid="+classid+"&page=1&pagesize="+pagesize+"&time="+(new Date().getTime()),
		url:		site.Dir + "extends/feedback/ajax.aspx",
		error:		function(XmlHttpRequest,textStatus, errorThrown){if(XmlHttpRequest.responseText!=""){alert(XmlHttpRequest.responseText);}},
		success:	function(d){
			$('#'+elementid).html(d);
		}
	});
}

/*--内容评论插件--*/

function ajaxPluginReviewTopList(ccid,id,pagesize,elementid)
{
	$.ajax({
		type:		"get",
		dataType:	"html",
		data:		"oper=ajaxPluginReviewTopList&ccid="+ccid+"&id="+id+"&page=1&pagesize="+pagesize+"&time="+(new Date().getTime()),
		url:		site.Dir + "extends/review/ajax.aspx",
		error:		function(XmlHttpRequest,textStatus, errorThrown){if(XmlHttpRequest.responseText!=""){alert(XmlHttpRequest.responseText);}},
		success:	function(d){
			$('#'+elementid).html(d);
		}
	});
}

/*--投票调查插件--*/

function ajaxPluginVoteAdd(id,mtype,btn)
{
	btn="#"+btn;
//	$(btn).attr("disabled","disabled");
	var voteNum;
	var rbVote=$("#voteform input");
	for(var i=0;i<rbVote.length;i++)
	{
		if(rbVote[i].checked && (rbVote[i].type=="radio" || rbVote[i].type=="checkbox")){
			if(!voteNum)
				voteNum=rbVote[i].value;
			else
				voteNum += "," + rbVote[i].value;
		}
	}
	if(!voteNum){
		alert("请先选择一项!");
		$(btn).attr("disabled","");
		return;
	}
	$.ajax({
		type:		"get",
		dataType:	"html",
		data:		"id="+id+"&mtype="+mtype+"&vote="+voteNum+"&time="+(new Date().getTime()),
		url:		site.Dir + "extends/vote/ajax.aspx?oper=ajaxPluginVoteAdd",
		error:		function(XmlHttpRequest,textStatus, errorThrown){if(XmlHttpRequest.responseText!=""){alert(XmlHttpRequest.responseText);}},
		success:	function(d){
			if(d=="ok")
			{
				alert("成功,谢谢你的投票!");
			}
			else
			{
				alert(d);
				$(btn).attr("disabled","");
			}
		}
	});
}
/*用户登录*/
function ajaxUserLogin(uname,upwd)
{
    if(uname=="")
    {
        alert("请输入帐号");
        return;
    }
    if(upwd=="")
    {
        alert("请输入密码");
        return;
    }
    $.ajax({
		type:		"post",
		dataType:	"html",
		data:		"name="+uname+"&pass="+upwd+"&time="+(new Date().getTime()),
		url:		site.Dir + "passport/ajax.aspx?oper=login",
		error:		function(XmlHttpRequest,textStatus, errorThrown){if(XmlHttpRequest.responseText!=""){alert(XmlHttpRequest.responseText);}},
		success:	function(d){
		    if(d=="ok")
			{
			    var name = JumbotCms.Cookie.get(site.CookiePrev + "user", "name");
			    $("#lguname").html(name);
			    $("#yeslogin").css("display","block");
			    $("#nologin").css("display","none");
			    window.location.href="/default.aspx";
			}else
			{
			    alert(d);
			}
		}
	});
}

$(function(){
    document.onkeydown = keyDown;//网站纠错方法调用
    var id = JumbotCms.Cookie.get(site.CookiePrev + "user", "id");
    if(id=="")
    {
       $("#yeslogin").css("display","none");
	   $("#nologin").css("display","block");
	   $(".color_green_text").css("display","none");
	   $(".rightfloat").css("display","none");
    }else
    {
       var name = JumbotCms.Cookie.get(site.CookiePrev + "user", "name");
	   $("#lguname").html("<a href='"+site.Dir + "exit.aspx?userkey="+ id + "'>退出</a>&nbsp;["+name+"]");
//	   var str = "<a href='"+site.Dir + "main.aspx'><img src='/images/jr_btn.jpg' width='49' height='17' /></a> &nbsp;";
//	   str+="<a href='"+site.Dir + "exit.aspx?userkey="+ id + "'><img src='/images/tc_btn.jpg' width='49' height='17' /></a>";
       $("#yeslogin").css("display","block");
	   $("#nologin").css("display","none"); 
	   $(".color_green_text").css("display","block");
	   $(".rightfloat").css("display","block");
//	   $("#lg").html(str);
    }
});

/*--投票问题调查插件--*/

function ajaxPluginQuestionAdd(msg)
{
	if(msg==""){
		alert("请填写信息!");
		return;
	}
	if(msg.length>150)
	{
	   alert("输入必须在150个字符以内!");
	   return; 
	}
	$.ajax({
		type:		"post",
		dataType:	"html",
		data:		"msg="+msg+"&time="+(new Date().getTime()),
		url:		site.Dir + "extends/vote/ajax.aspx?oper=ajaxPluginQuestionAdd",
		error:		function(XmlHttpRequest,textStatus, errorThrown){if(XmlHttpRequest.responseText!=""){alert(XmlHttpRequest.responseText);}},
		success:	function(d){
		    if(d=="ok")
			{
			    alert("提交成功,谢谢!");
			    $("#msg").val("");
			}
		}
	});
}
function ajaxShowWeather(id)//显示天气(2011.03.6)
{
	$.ajax({
		type:		"get",
		dataType:	"json",
		data:		"time="+(new Date().getTime()),
		url:		site.Dir + "tools/weather/json.aspx",
		success:	function(d){
			$('#'+id).html(d.cityname + " <br /><span style='vertical-align:text-bottom;'><img alt='" + d.weather + "' title='" + d.weather + "' src='"+site.Dir+"tools/weather/icon/" + d.img + ".gif' /></span> " + d.temperature);
		}
	});
}

/*--纪检信箱--*/

function ajaxPluginQuestionAddss(uname,utel,utitle,utxt,code)
{
	if(utel==""){
		alert("请填写联系方式!");
		return;
	}
	if(utitle==""){
		alert("请填写标题名称!");
		return;
	}
	if(utxt.length>350)
	{
	   alert("输入必须在350个字符以内!");
	   return; 
	}
	if(code==""){
		alert("请填写验证码!");
		return;
	}
	$.ajax({
		type:		"post",
		dataType:	"html",
		data:		"uname="+encodeURIComponent(uname)+"&tel="+encodeURIComponent(utel)+"&tit="+encodeURIComponent(utitle)+"&txt="+encodeURIComponent(utxt)+"&code="+code+"&time="+(new Date().getTime()),
		url:		site.Dir + "admin/sanyuan_feedback_ajax.aspx?oper=add",
		error:		function(XmlHttpRequest,textStatus, errorThrown){if(XmlHttpRequest.responseText!=""){alert(XmlHttpRequest.responseText);}},
		success:	function(d){
		    if(d=="ok")
			{
			    alert("提交成功,谢谢!");
			}else if(d=="error")
			{
			    alert("验证码错误!");
			}
		}
	});
}
/*<a href="javascript:void(0);" onclick="return SetHome(window.location);">设为首页</a>*/
function SetHome(vrl)
{
	var obj=document.createElement("shewei_shouye");
	try
	{
		obj.style.behavior='url(#default#homepage)';obj.setHomePage(vrl);
	}
	catch(e)
	{
		if(window.netscape) 
		{
			try{
				netscape.security.PrivilegeManager.enablePrivilege("UniversalXPConnect"); 
			}catch (e){ 
				alert("此操作被浏览器拒绝！\n请在浏览器地址栏输入“about:config”并回车\n然后将[signed.applets.codebase_principal_support]设置为'true'"); 
			}
			var prefs = Components.classes['@mozilla.org/preferences-service;1'].getService(Components.interfaces.nsIPrefBranch);
			prefs.setCharPref('browser.startup.homepage',vrl);
		}
	}
	return false;
}
/*<a href="javascript:void(0);" onclick="return AddFavorite(window.location,document.title);">加入收藏</a>*/
function AddFavorite(sURL, sTitle)
{
	try
	{
		window.external.addFavorite(sURL, sTitle);
	}
	catch (e)
	{
		try
		{
			window.sidebar.addPanel(sTitle, sURL, "");
		}
		catch (e)
		{
			alert("加入收藏失败，请使用Ctrl+D进行添加");
		}
	}
	return false;
}

/*自适应iframe高度window.setInterval("reinitIframe()", 1000);*/
function reinitIframe(){
    var iframe = document.getElementById("frame_content");
    try{
        var bHeight = iframe.contentWindow.document.body.scrollHeight;
        var dHeight = iframe.contentWindow.document.documentElement.scrollHeight;
        var height = Math.max(bHeight, dHeight);
        iframe.height = height;
    }catch (ex){}
}


/*网站纠错 调用代码:document.onkeydown = keyDown;*/
function keyDown(e)
{
    var e = (typeof event != "undefined") ? window.event : e;   // IE : Firefox
    var s = (document.getSelection) ? document.getSelection() : document.selection.createRange().text;
    if (e.ctrlKey && e.keyCode == 13) {
        if (s != "")
        {
            window.open("/plus/correction.htm", "", "width=400,height=300");
        } else {
            alert("请先用鼠标选择出错的内容片断！");
            return false;
        }
    }
}

///*漂浮广告*/
//var xPos = 300;
//var yPos = 200; 
//var step = 1;
//var delay = 30; 
//var height = 0;
//var Hoffset = 0;
//var Woffset = 0;
//var yon = 0;
//var xon = 0;
//var pause = true;
//var interval;
//img1.style.top = yPos;
//function changePos() 
//{
//	width = document.body.clientWidth;
//	height = document.body.clientHeight;
//	Hoffset = img1.offsetHeight;
//	Woffset = img1.offsetWidth;
//	img1.style.left = xPos + document.body.scrollLeft;
//	img1.style.top = yPos + document.body.scrollTop;
//	if (yon) 
//		{yPos = yPos + step;}
//	else 
//		{yPos = yPos - step;}
//	if (yPos < 0) 
//		{yon = 1;yPos = 0;}
//	if (yPos >= (height - Hoffset)) 
//		{yon = 0;yPos = (height - Hoffset);}
//	if (xon) 
//		{xPos = xPos + step;}
//	else 
//		{xPos = xPos - step;}
//	if (xPos < 0) 
//		{xon = 1;xPos = 0;}
//	if (xPos >= (width - Woffset)) 
//		{xon = 0;xPos = (width - Woffset);}
//}
//	
//function start()
//{
//	img1.visibility = "visible";
//	interval = setInterval('changePos()', delay);
//}
//function pause_resume() 
//{
//	if(pause) 
//	{
//		clearInterval(interval);
//		pause = false;}
//	else 
//	{
//		interval = setInterval('changePos()',delay);
//		pause = true; 
//	}
//}