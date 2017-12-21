/*
 *对话框类。
 *使用举例：
 *@example
 new PwMenu('boxID').guide();
 *
 */
/**
 * @param String
 *            id 对话框的id，若不传递，则默认为pw_box
 */
 //add by ranisiwei 去空格
function rtrim(s){
	return s.replace( /(\s*|　*)$/, "");
}
function ltrim(s){
	return s.replace( /^(\s*|　*)/, "");
}
function trim(s){
	return ltrim(rtrim(s));
}
var __win = window;
var __doc = document;
PWMENU_ZINDEX=1001;

function PwMenu(id){
	this.pid	= null;
	this.obj	= null;
	this.w		= null;
	this.h		= null;
	this.t		= 0;
	this.menu	= null;
	this.mid	= id;
	this.oCall  = null;
	this.init(id);
}

PwMenu.prototype = {

	init : function(id) {
		this.menu = getPWBox(id);
		var _ = this;
		document.body.insertBefore(this.menu,document.body.firstChild);
		_.menu.style.zIndex=PWMENU_ZINDEX+10+"";
		PWMENU_ZINDEX+=10;
	},

	guide : function() {
		this.menu=this.menu||getPWBox(this.mid);
		this.menu.className = '';
		this.menu.innerHTML = '<div class="popout"><table border="0" cellspacing="0" cellpadding="0"><tbody><tr><td class="bgcorner1"></td><td class="pobg1"></td><td class="bgcorner2"></td></tr><tr><td class="pobg4"></td><td><div class="popoutContent" style="padding:20px;"><img src="'+imgpath+'/loading.gif" align="absmiddle" alt="loading" /> 正在加载数据...</div></td><td class="pobg2"></td></tr><tr><td class="bgcorner4"></td><td class="pobg3"></td><td class="bgcorner3"></td></tr></tbody></table></div>';
		this.menupz(this.obj);
	},

	close : function() {
		var _=this;
		read.t = setTimeout(function() {
			_.menu?0:_.menu=read.menu;
			if (_.menu) {
				_.menu.style.display = 'none';
				_.menu.className = '';
				if (_.oCall && _.oCall.close) _.oCall.close();
			}
		}, 100);
	},

	setMenu : function(element,type,border,oCall) {
		if (this.IsShow() && this.oCall && this.oCall.close) {
			this.oCall.close();
		}
		if (type) {
			this.menu=this.menu||getPWBox(this.mid);
			var thisobj = this.menu;
		} else {
			var thisobj = getPWContainer(this.mid,border);
		}
		if (typeof(element) == 'string') {
			thisobj.innerHTML = element;
		} else {
			while (thisobj.hasChildNodes()) {
				thisobj.removeChild(thisobj.firstChild);
			}
			thisobj.appendChild(element);
		}
		this.oCall = null;
		if (typeof oCall == 'object' && oCall.open) {
			this.oCall = oCall;
			oCall.open();
		}
	},

	move : function(e) {
		if(is_ie){document.body.onselectstart = function(){return false;}}
		var e  = is_ie ? __win.event : e;
		var o  = this.menu||getPWBox(this.mid);
		var x  = e.clientX;
		var y  = e.clientY;
		this.w = e.clientX - parseInt(o.offsetLeft);
		this.h = e.clientY - parseInt(o.offsetTop);
		var _=this;
		_.menu=_.menu||getPWBox(_.mid);
		document.body.setCapture && _.menu.setCapture();
		document.onmousemove = function(e) {
			var e  = is_ie ? __win.event : e;
			var x  = e.clientX;
			var y  = e.clientY;
			_.menu.style.left = x - _.w + 'px';
			_.menu.style.top  = y - _.h + 'px';
		};
		document.onmouseup   = function() {
			if(is_ie){document.body.onselectstart = function(){return true;}}
			document.body.releaseCapture && _.menu.releaseCapture();// IE释放鼠标监控
			document.onmousemove = null;
			document.onmouseup = null;
		};
	},


	open : function(idName, object, type, pz, oCall) {
		if (typeof idName == 'string') {
			idName = getObj(idName);
		}
		if (idName == null) return false;
		this.menu=this.menu||getPWBox(this.mid);
		clearTimeout(read.t);
		if (typeof type == "undefined" || !type) type = 1;
		if (typeof pz == "undefined" || !pz) pz = 0;

		this.setMenu(idName.innerHTML, 1, 1, oCall);
		this.menu.className = idName.className;
		this.menupz(object,pz);

		if (type == 3) {
			this.closeByClick();
		} else if (type != 2) {
			this.closeByMove(object);
		}
	},

	closeByClick : function() {
		document.onmousedown = function (e) {
			var o = is_ie ? __win.event.srcElement : e.target;
			if (!issrc(o)) {
				read.close();
				document.onmousedown = '';
			}
		}
	},

	closeByMove : function(id) {
		var _=this;
		getObj(id).onmouseout = function() {_.close();getObj(id).onmouseout = '';};
		_.menu.onmouseout = function() {_.close();}
		_.menu.onmouseover = function() {clearTimeout(read.t);}
	},

	menupz : function(obj,pz) {
		this.menu=this.menu||getPWBox(this.mid);
		this.menu.onmouseout = '';
		this.menu.style.display = '';
		// this.menu.style.zIndex = 3000;
		this.menu.style.left	= '-500px';
		this.menu.style.visibility = 'visible';

		if (typeof obj == 'string') {
			obj = getObj(obj);
		}
		if (obj == null) {
			if (is_ie) {
				this.menu.style.top  = (ietruebody().offsetHeight - this.menu.offsetHeight)/3 + getTop() +($('upPanel')?$('upPanel').scrollTop:0)+ 'px';
				this.menu.style.left = (ietruebody().offsetWidth - this.menu.offsetWidth)/2 + 'px';
			} else {
				this.menu.style.top  = (document.documentElement.clientHeight - this.menu.offsetHeight)/3 + getTop() + 'px';
				this.menu.style.left = (document.documentElement.clientWidth - this.menu.offsetWidth)/2 + 'px';
			}
		} else {
			var top  = findPosY(obj);
			var left = findPosX(obj);
			var pz_h = Math.floor(pz/10);
			var pz_w = pz % 10;
			if (is_ie) {
				var offsetheight = ietruebody().offsetHeight;
				var offsethwidth = ietruebody().offsetWidth;
			} else {
				var offsetheight = ietruebody().clientHeight;
				var offsethwidth = ietruebody().clientWidth;
			}
			/*
			 * if (IsElement('upPanel') && is_ie) { var gettop = 0; } else { var
			 * gettop = ; }
			 */
			var show_top = IsElement('upPanel') ? top - getObj('upPanel').scrollTop : top;

			if (pz_h!=1 && (pz_h==2 || show_top < offsetheight/2)) {
				top += getTop() + obj.offsetHeight;
			} else {
				top += getTop() - this.menu.offsetHeight;
			}
			if (pz_w!=1 && (pz_w==2 || left > (offsethwidth)*3/5)) {
				left -= this.menu.offsetWidth - obj.offsetWidth - getLeft();
			}
			this.menu.style.top = top+ 'px';
			if (top < 0) {
				this.menu.style.top  = 0  + 'px';
			}
			this.menu.style.left = left + 'px';
			if (pz_w != 1 && left + this.menu.offsetWidth > document.body.offsetWidth+ietruebody().scrollLeft) {
				this.menu.style.left = document.body.offsetWidth+ietruebody().scrollLeft-this.menu.offsetWidth-30 + 'px';
			}
		}
	},

	InitMenu : function() {
		var _=this;
		function setopen(a,b) {
			if (getObj(a)) {
				var type = null,pz = 0,oc;
				if (typeof __win[a] == 'object') {
					oc = __win[a];
					oc.type ? type = oc.type : 0;
					oc.pz ? pz = oc.pz : 0;
				}
				getObj(a).onmouseover = function(){_.open(b, a, type, pz, oc);};
				// getObj(a).onmouseover=function(){_.open(b,a);callBack?callBack(b):0};
				// try{getObj(a).parentNode.onfocus =
				// function(){_.open(b,a);callBack?callBack(b):0};}catch(e){}
			}
		}
		for (var i in openmenu) {
			try{setopen(i,openmenu[i]);}catch(e){}
		}
	},

	IsShow : function() {
		this.menu=this.menu||getPWBox(this.mid);
		return (this.menu.hasChildNodes() && this.menu.style.display != 'none') ? true : false;
	}
};
var read = new PwMenu();

function closep() {
	read.menu.style.display = 'none';
	read.menu.className = '';
}
function cancelping(url) {
	ajax.send(url,'',function(){
	var in_text=ajax.request.responseText;
	TINY.box.show(in_text,1,700,630,1);
	})
}
function findPosX(obj) {
	var curleft = 0;
	if (obj.offsetParent) {
		while (obj.offsetParent) {
			curleft += obj.offsetLeft
			obj = obj.offsetParent;
		}
	} else if (obj.x) {
		curleft += obj.x;
	}
	return curleft - getLeft();
}
function findPosY(obj) {
	var curtop = 0;
	if (obj.offsetParent) {
		while (obj.offsetParent) {
			curtop += obj.offsetTop
			obj = obj.offsetParent;
		}
	} else if (obj.y) {
		curtop += obj.y;
	}
	return curtop - getTop();
}
function in_array(str,a){
	for (var i=0; i<a.length; i++) {
		if(str == a[i])	return true;
	}
	return false;
}
function loadjs(path, code, id, callBack) {
	if (typeof id == 'undefined') id = '';
	if (id != '' && IsElement(id)) {
		try{callBack?callBack():0;}catch(e){}
		return false;
	}
	var header = document.getElementsByTagName("head")[0];
	var s = document.createElement("script");
	if (id) s.id = id;
	if (path) {
		// bug fix
		if(is_webkit && path.indexOf(' ')>-1)
		{
			var reg = /src="(.+?)"/ig;
			var arr = reg.exec(path);
			if(arr){
				path = arr[1];
			}
		}
		s.src=path;
	} else if (code) {
		s.text = code;
	}
	if (document.all) {
		s.onreadystatechange = function() {
			if (s.readyState == "loaded" || s.readyState == "complete") {
				s.onreadystatechange = null;
				if(callBack){
					callBack();
				}
			}
		};
	} else {
		try{s.onload = callBack?callBack:null;}catch(e){callBack?callBack():0;}
	}
	header.appendChild(s);
	return true;
}
function keyCodes(e) {
	if (read.menu.style.display == '' && e.keyCode == 27) {
		read.close();
	}
}

function opencode(menu,td,id) {
	document.body.onclick = null;
	document.body.onmousedown=null;
	var id = id || 'ckcode';
	if (read.IsShow() && read.menu.firstChild.id == id) return;
	read.open(menu,td,2,11);
	getObj(id).src = 'ck.php?nowtime=' + new Date().getTime();

	document.body.onmousedown=function(e) {
		var o = is_ie ? __win.event.srcElement : e.target;
        var f = is_ie ? false : true;// firefox e.type = click by lh

		if( o!=getObj(id) && o!=td )
		{
			closep();
		}
		if (o == td || (f && e.type == "click")) {
			return;
		} else if (o.id == id) {
			getObj(id).src = 'ck.php?nowtime=' + new Date().getTime();
		} else {
			closep();
			document.body.onmousedown = null;
			document.body.onmousedown=null;
		}
	};

}

function getPWBox(type){
	if (getObj(type||'pw_box')) {
		return getObj(type||'pw_box');
	}
	var pw_box	= elementBind('div',type||'pw_box','','position:absolute;left:-10000px');

	document.body.appendChild(pw_box);
	return pw_box;
}

function getPWContainer(id,border){
	if (typeof(id)=='undefined') id='';
	if (getObj(id||'pw_box')) {
		var pw_box = getObj(id||'pw_box');
	} else {
		var pw_box = getPWBox(id);
	}
	if (getObj(id+'box_container')) {
		return getObj(id+'box_container');
	}

	if (border == 1) {
		pw_box.innerHTML = '<div class="popout"><div id="'+id+'box_container"></div></div>';
	} else {
		pw_box.innerHTML = '<div class="popout"><table border="0" cellspacing="0" cellpadding="0"><tbody><tr><td class="bgcorner1"></td><td class="pobg1"></td><td class="bgcorner2"></td></tr><tr><td class="pobg4"></td><td><div class="popoutContent" id="'+id+'box_container"></div></td><td class="pobg2"></td></tr><tr><td class="bgcorner4"></td><td class="pobg3"></td><td class="bgcorner3"></td></tr></tbody></table></div>';
	}
	var popoutContent = getObj(id+'box_container');
	return popoutContent;
}
function elementBind(type,id,stylename,csstext){
	var element = document.createElement(type);
	if (id) {
		element.id = id;
	}
	if (typeof(stylename) == 'string') {
		element.className = stylename;
	}
	if (typeof(csstext) == 'string') {
		element.style.cssText = csstext;
	}
	return element;
}

function addChild(parent,type,id,stylename,csstext){
	parent = objCheck(parent);
	var child = elementBind(type,id,stylename,csstext);
	parent.appendChild(child);
	return child;
}

function delElement(id){
	id = objCheck(id);
	id.parentNode.removeChild(id);
}

function pwForumList(isLink,isPost,fid,handle,ifblank) {
	if (isLink == true) {
		if (isPost == true){
			if(ifblank == true) {
				__win.open('post.php?fid='+fid);
			} else {
				__win.location.href = 'post.php?fid='+fid;
			}
			if (is_ie) {
				__win.event.returnValue = false;
			}
		} else {
			return true;
		}
	} else {
		if (gIsPost != isPost || read.menu.style.display=='none' || read.menu.innerHTML == '') {
			read.menu.innerHTML = '';
			if (isPost == true) {
				if (getObj('title_forumlist') == null) {
					showDialog('error','没有找到版块列表信息');
				}
				getObj('title_forumlist').innerHTML = '选择你要发帖的版块';
			} else {
				if (getObj('title_forumlist') == null) {
					showDialog('error','没有找到版块列表信息');
				}
				getObj('title_forumlist').innerHTML = '快速跳转';
			}
			gIsPost = isPost;
			if (handle.id.indexOf('pwb_')==-1) {
				read.open('menu_forumlist', handle, 3);
			}
		} else {
			read.close();
		}
	}
	return false;
}
function char_cv(str){
	if (str != ''){
		str = str.replace(/</g,'&lt;');
		str = str.replace(/%3C/g,'&lt;');
		str = str.replace(/>/g,'&gt;');
		str = str.replace(/%3E/g,'&gt;');
		str = str.replace(/'/g,'&#39;');
		str = str.replace(/"/g,'&quot;');
	}
	return str;
}

/*function showDialog(type,message,autohide,callback) {
	if (!type) type = 'warning';
	var tar = '<div class="popBottom" style="text-align:right;">';
	if (type == 'confirm' && typeof(callback) == 'function') {
		temp = function () {
			closep();
			if (typeof(callback)=='function') {
				callback();
			}
		}
		var button = typeof(callback)=='function' ? '<span class="btn2"><span><button onclick="temp();" type="button">确定</button></span></span>' : '<span class="btn2"><span><button type="button">确定</button></span></span>';

		tar += button+'</span></span>';
	}
	if (autohide) {
		tar += '<div class="fl gray">本窗口'+autohide+'秒后关闭</div>';
	}
	tar += '<span class="bt2"><span><button onclick="closep();" type="button">关闭</button></span></span>';
	var container = '<div style="width:350px;"><div class="popTop">提示</div><div class="popCont"><img src="'+imgpath+'/'+type+'_bg.gif" class="mr10" align="absmiddle" />'+message+'</div>'+tar+'</div>';
	read.setMenu(container);
	read.menupz();
	if (autohide) {
		window.setTimeout("closep()", (autohide * 1000));
	}
}*/

function checkFileType() {
	var fileName = getObj("uploadpic").value;
	if (fileName != '') {
		var regTest = /\.(jpe?g|gif|png)$/gi;
		var arrMactches = fileName.match(regTest);
		if (arrMactches == null) {
			getObj('fileTypeError').style.display = '';
			return false;
		} else {
			getObj('fileTypeError').style.display = 'none';
		}
	}
	return true;
}
var searchTxt = '搜索其实很简单！ (^_^)';
function searchFocus(e){
	if(e.value == searchTxt){
		e.value='';
		e.className = '';
	}
	//e.parentNode.className += ' inputFocus';
}
function searchBlur(e){
	if(e.value == ''){
		e.value=searchTxt;
		e.className = 'gray';
	}
	//e.parentNode.className = 'ip';
}
function getSearchType(event){
	if (is_ie){
		var n = __win.event.srcElement;
    } else {
    	var n = event.target;
    }
	if(n && n.tagName!='LI') return;
	n.parentNode.parentNode.getElementsByTagName('h6')[0].innerHTML = n.innerHTML;
	var lis = n.parentNode.getElementsByTagName('li');
	for(var i = 0,j=lis.length;i < j;i++){
		lis[i].style.display = '';
	}
	n.style.display='none';
	getObj('search_type').value=n.getAttribute('type');
	n.parentNode.style.display='none';
}

function searchInput() {
	if(getObj('search_input').value==searchTxt)
		getObj('search_input').value='';
	return true;
}


/*
 * searchInput 修改by ransiwei 0418
 *搜索跳转到官网搜索
*/
/*
function searchInput() {
	var _val = trim(getObj('search_input').value);
	if(_val==searchTxt || _val==''){
		return false;
	}
		//getObj('search_input').value='';
	var suffix = __win.location.host.replace(/^.*\.aliyun/i,''),
		q = encodeURIComponent(_val),
//		url = "http://www.aliyun" +suffix+ '/s?'+"k="+q+"&c=b";
                url = "https://www.aliyun.com/ss/?k="+q;//更换新的阿里云搜索链接
		__win.open(url);
		return false;
	//return true;
}
*/

(function() {
    if (__win.showDlg) return;
    var win = window,doc = win.document,
        isIE = !+'\v1', // IE浏览器
	    isCompat = doc.compatMode == 'CSS1Compat',	// 浏览器当前解释模式
	    IE6 = isIE && /MSIE (\d)\./.test(navigator.userAgent) && parseInt(RegExp.$1) < 7, // IE6以下需要用iframe来遮罩
	    useFixed = !isIE || (!IE6 && isCompat), // 滚动时，IE7+（标准模式）及其它浏览器使用Fixed定位
        Typeis = function(o,type) {
		    return Object.prototype.toString.call(o)==='[object ' + type + ']';
	    }, // 判断元素类型
        $ = function(o) {
            return Typeis(o,'String') ? doc.getElementById(o) : o;
        },
        $height = function(obj) {return parseInt(obj.style.height) || obj.offsetHeight}, // 获取元素高度
        $width = function(obj) {return parseInt(obj.style.width) || obj.offsetWidth}, // 获取元素高度
        getWinSize = function() {
            var rootEl = doc.body;
			return [Math.max(rootEl.scrollWidth, rootEl.clientWidth), Math.max(Math.max(doc.body.scrollHeight,rootEl.scrollHeight), Math.max(rootEl.clientHeight,doc.body.clientHeight || window.clientHeight))]
		},
		/* 获取scrollLeft和scrollTop */
		getScrollPos = function() {
		    var body = doc.body,docEl = doc.documentElement;
			return {
			    left:body.scrollLeft || docEl.scrollLeft, top:body.scrollTop || docEl.scrollTop
			}
		},
		getElementsByClassName = function(className, element) {
		    var children = (element || document).getElementsByTagName('*');
		    var elements = new Array();
		    for (var i = 0; i < children.length; i++) {
			    var child = children[i];
			    var classNames = child.className.split(' ');
			    for (var j = 0; j < classNames.length; j++) {
				    if (classNames[j] == className) {
					    elements.push(child);
					    break;
				    }
			    }
		    }
		    return elements;
	    },
        empty = function(){},
        defaultCfg = {   // 默认配置
            id:         'pw_dialog',
            type:       'warning',
            message:    '',// 弹出提示的文字
            showObj:    null,// 要显示的本地元素,在ajax提示是常用
            width:      350,// 弹出框高度
            isMask:     1,
            autoHide:   0,// 是否自动关闭
		    zIndex:		9999, // 层叠值
		    onShow:		empty,// 显示时执行
		    onOk:       empty,
		    onClose:	empty, // 关闭时执行
		    left:       '50%',// 绝对位置
		    top:        '50%',
		    alpha:      0.2,// 遮罩的透明度
		    backgroundColor:'#000',// 遮罩的背景色
		    titleText:  '提示',// 提示标题
		    okText:      '确定',// 确定按钮文字
		    cancelText:  '取消',// 取消文字，确认时用
		    closeText:  '关闭',// 关闭文字
		    button:     null// 默认不显示按钮
        },
		icoPath = 'images/';

    var Dialog = function(options) {// 构造函数
        var self = this;
        this.options = options;
        if (!(self instanceof Dialog)) {
            return new Dialog(options);
        }
        this._initialize();
    }
    Dialog.prototype = {
        _initialize:function() {
            for(var i in defaultCfg) {
                if(!(i in options)){
                    options[i] = defaultCfg[i];
                }
            }
            this.show();
        },
        show:function(options) {
            var self = this,
                opt = self.options,
                box = opt.showObj;
            	closep();
                createButton = function(){// 创建按钮
                    var html = [],btn = opt.button;
                    if(opt.autoHide){ html.push('<div class="fl gray">本窗口<span class="spanTime">'+ opt.autoHide +'</span>秒后关闭</div>');}
                    if(btn){
                        for(var i = 0,j = btn.length;i < j;i++ ) {
                            html.push('<span class="bt2"><span><button class="pw_dialoag_button" type="button">'+ btn[i][0] +'</button></span></span>');
                        }
                    }else {
                        if(opt.type === 'confirm') {
                            html.push('<span class="btn2"><span><button type="button" class="pw_dialoag_ok">'+ opt.okText +'</button></span></span>');
                        }
                        html.push('<span class="bt2"><span><button type="button" class="pw_dialoag_close">'+ opt.closeText +'</button></span></span>');
                    }
                    return html.join('');
                }
                // timeout;
            if(!opt.showObj) {
                var divStyle = 'z-index:'+ (opt.zIndex + 1) +';position:'+ (useFixed ? 'fixed' : 'absolute')+';';
                    maskStyle = (!opt.isMask ? 'display:none':'') + 'width:'+ getWinSize()[0] +'px;height:'+ getWinSize()[1] +'px;z-index:'+ opt.zIndex +';position:absolute;top:0;left:0;text-align:center;filter:alpha(opacity='+ opt.alpha*100 + ');opacity:'+ opt.alpha +';background-color:'+opt.backgroundColor;
                    if(!$(opt.id)) {
                        box = document.createElement('div');
                        box.id = opt.id;
                    }else {
                        box = $(opt.id);
                    }
                    if (!opt.type) opt.type = defaultCfg.type;
		            box.innerHTML = [
		            /* 遮罩 */
		            '<div style="' + maskStyle + '"></div>', IE6 ? ("<iframe id='maskIframe' src='about:blank' style='" + maskStyle + "'></iframe>") : '',
		            /* 窗体 */
		            // IE6 ? "<iframe src='javascript:false'
					// style='width:100%;height:999px;position:absolute;top:0;left:0;z-index:-1;opacity:1;filter:alpha(opacity=100)'></iframe>":
					// '',
		            '<div style="'+ divStyle +'" class="popout">\
		            <table cellspacing="0" cellpadding="0" border="0">\
		                <tbody>\
		                <tr><td class="bgcorner1"></td><td class="pobg1"></td><td class="bgcorner2"></td></tr><tr><td class="pobg4"></td>\
		                    <td>\
		                        <div id="box_container" class="popoutContent">\
		                            <div style="width:'+ opt.width +'px;">\
		                                <div class="popTop">'+ opt.titleText +'</div>\
		                                <div class="popCont"><img align="absmiddle" class="mr10" src="'+ icoPath + opt.type +'_bg.gif">'+ opt.message +'</div>\
		                                <div style="text-align: right;" class="popBottom">\
		                                '+ createButton() + '\
		                                </div>\
		                            </div>\
		                        </div>\
		                    </td><td class="pobg2"></td></tr><tr><td class="bgcorner4"></td><td class="pobg3"></td><td class="bgcorner3"></td></tr>\
		                </tbody>\
		            </table>\
		            </div>',
		            /* 阴影 */
		            isIE ? "<div id='ym-shadow' style='position:absolute;z-index:10000;background:#808080;filter:alpha(opacity=80) progid:DXImageTransform.Microsoft.Blur(pixelradius=5);'></div>": ''].join('');
		        doc.body.insertBefore(box, doc.body.childNodes[0]);
		        var popout = getElementsByClassName('popout',box)[0];
                popout.style.left = Typeis(opt.left,'Number') ? opt.left + 'px' : opt.left
                popout.style.top = Typeis(opt.top,'Number') ? opt.top + 'px' : opt.top;
                var h = $height(popout),w = $width(popout);
                if(!Typeis(opt.left,'Number')) {
				    popout.style.marginLeft = useFixed ? - w / 2 + "px" : getScrollPos().left - w / 2 + "px";
				}else {
				    popout.style.left = ''+opt.left + 'px';
				}
				if(!Typeis(opt.top,'Number')) {
				    popout.style.marginTop = useFixed ? - h / 2 + "px" : getScrollPos().top - h / 2 + "px";
				}else {
				    popout.style.top = ''+opt.top + 'px';
				}
				var closeTime = function() {
					if(interval){
						clearInterval(interval);
						interval = null;
					}
                };
				if(opt.button) {
				    var customBtn = getElementsByClassName('pw_dialoag_button',box),buttons = opt.button;
				    if(customBtn.length){
                        for(var i = 0,j = customBtn.length;i < j;i++) {
                            (function(i){
                                customBtn[i].onclick = function() {
                                   buttons[i][1] && buttons[i][1]();
                                }
                            })(i)

                        }
                    }
				}else{
		            var closeBtn = getElementsByClassName('pw_dialoag_close',box),
                        okBtn = getElementsByClassName('pw_dialoag_ok',box);
                   if(closeBtn.length){
                        closeBtn[0].onclick = function() {
                            self.close();
                        }
                    }
                    if(okBtn.length) {
                        okBtn[0].onclick = function() {
                            self.options.onOk && self.options.onOk();
							//self.options.onClose && self.options.onClose();
                            self.close();
                        }
                    }
                }

            }else{
                var obj = $(opt.showObj);
                if(obj.nodeType !== 1) {// 如果传进来的不是元素,直接return
                    return;
                }
                obj.style.display = '';
                var msgObj = getElementsByClassName('message',obj),
                    msgClose = getElementsByClassName('close',obj);
                if( !msgObj.length ) { return false; }
                msgObj[0].innerHTML = opt.message;
                if( msgClose.length ) { msgClose[0].onclick = function() {obj.style.display = 'none'; }}
            }
            opt.onShow && opt.onShow();
            if(opt.autoHide) {
                var spanTime = getElementsByClassName('spanTime',popout)[0];
		        interval = setInterval(function() {
		                var time = --opt.autoHide;
		                if(spanTime){ spanTime.innerHTML = time;}
		                if(time === 0){
		                    clearInterval(interval);
		                    self.close();
		                }
		        },1000);
		    }
        },
        close:function() {
            var opt = this.options;
            if(!opt.showObj && $(opt.id)) {
                doc.body.removeChild($(opt.id));
            }else if($(opt.showObj)) {
                $(opt.showObj).style.display = 'none';
            }
            opt.onClose && opt.onClose();
        }
    }
    win['showDlg'] = function(type,message,autohide,callback){
		var isMask = type === 'confirm' ? 0 : 1,
			onClose = type !== 'confirm' ? callback : null,
			options = arguments.length === 1 ? arguments[0] : { type:type,message:message,autoHide:autohide,onOk:callback,onClose:onClose,isMask:isMask };
        Dialog(options);
    }
	win['showDialog'] = win['showDlg'];
})();
//回到顶部
var addLoadEvent =function( func){
       var oldonload =window .onload ;
       if(typeof oldonload !="function"){
             window.onload=func;
       }else{
             window.onload=function (){
                   if ( oldonload) {
                         oldonload();
                   }
                   func();
             }
       }
}
var Tween={
	Quad:{
			easeOut: function(t,b,c,d){
						return -c *(t/=d)*(t-2) + b;
					},
			easeInOut: function(t,b,c,d){
						if ((t/=d/2) < 1) return c/2*t*t + b;
						return -c/2 * ((--t)*(t-2) - 1) + b;
					}
		}
}

// var scrollBar=function(){
// 	var that=this;
// 	if(!document.getElementById("scrollBar")){
// 		var ele=document.createElement("div");
// 		ele.id="scrollBar";
// 		ele.innerHTML='<a hideFocus="true" href="javascript:void(0)">回到顶部</a>';
// 		document.body.appendChild(ele);
// 	}else{
// 		var ele=document.getElementById("scrollBar");
// 	}
// 	var barTxt="回到顶部";
// 	var distance=100;//限定范围
// 	var dd=document.documentElement;
// 	var db=document.body;
// 	var scrollTop;//顶部距离
// 	this.setStyle=function(){
// 		scrollTop=db.scrollTop||dd.scrollTop;//顶部距离
// 		var sw=dd.scrollWidth;
// 		var pos='right:50%;margin-right:-610px;';
// 		var fullscreen=document.getElementById('fullscreenStyle');//判断屏幕状态
// 		if((fullscreen&&!fullscreen.disabled)||sw<1020){//宽屏或者窗口宽度小于可见值时 1020=960+20*2+10*2
// 				pos='right:5px;';
// 		}
// 		var ctxt=scrollTop>=distance?'':'display:none';
// 		ele.style.cssText='position:fixed;'+pos+'bottom:50px;'+ctxt;
// 	}
// 	this.update=function(){//控制滑块显示 并修正IE6定位
// 			scrollTop=db.scrollTop||dd.scrollTop;
// 			ele.style.display=(scrollTop>=distance)?"block":"none";
// 		if(!window.XMLHttpRequest){//如果IE6
// 			var h=ele.offsetHeight;
// 			var ch=document.documentElement.clientHeight;
// 			ele.style.position="absolute";
// 			ele.style.top=ch+scrollTop-h-50+"px";
// 		}
// 	}
// 	that.b=0;//初始值
// 	that.c=0;//变化量
// 	var d=10,t=0;//持续时间和增量
// 	this.run=function(){
// 		if(dd.scrollTop){
// 			dd.scrollTop=Math.ceil(Tween.Quad.easeOut(t,that.b,that.c,d));
// 		}else{
// 			db.scrollTop = Math.ceil(Tween.Quad.easeOut(t,that.b,that.c,d));
// 		}
// 		if(t<d){ t++; setTimeout(that.run, 10); }else{t=0;}
// 	}
// 	ele.onclick=function(){
// 		that.b=scrollTop;
// 		that.c=-scrollTop;
// 		that.run();
// 		return false;
// 	}
// 	this.init=function(){
// 		this.setStyle();
// 		window.onscroll=function(){
// 			that.update();
// 		}
// 		window.onresize=function(){
// 			that.setStyle();
// 			that.update();
// 		}
// 	}
// }

//新版scrollBar
var scrollBar = function(){
	var distance = 100, ele, scrollTop,
		that = this;

	//create dom
	ele=document.createElement("a");
	ele.id="to-top";
	ele.title = "回到顶部";
	ele.style.display = "none";
	ele.innerHTML="<span class='icon-up2'></span>";
	document.body.appendChild(ele);

	this.updateScrollTop = function(){
		scrollTop = document.body.scrollTop || document.documentElement.scrollTop;
	};

	this.init = function(){
		var that = this;
		window.onscroll = function(){
			that.updateScrollTop();
			if(scrollTop > distance){
				ele.style.display = "";
			}else{
				ele.style.display = "none";
			}
		}

		ele.onclick = function(){
			var back = setInterval(function(){
				that.updateScrollTop();
				if(scrollTop>0){
					document.body.scrollTop ? document.body.scrollTop -= 100 :
											  document.documentElement.scrollTop -= 100;
				}else{
					clearInterval(back);
				}
			},1);
		}
	}
};


var goTop;
addLoadEvent(function(){
	goTop=new scrollBar();
	goTop.init();
});

//本地存储 From pw87 by rickyleo 20120810
(function(){
	var UserData = {
        userData : null,
        name : location.hostname,
        init:function(){
            if (!UserData.userData) {
                try {
                    UserData.userData = document.createElement('INPUT');
                    UserData.userData.type = "hidden";
                    UserData.userData.style.display = "none";
                    UserData.userData.addBehavior ("#default#userData");
                    document.body.appendChild(UserData.userData);
                    var expires = new Date();
                    expires.setDate(expires.getDate()+365);
                    UserData.userData.expires = expires.toUTCString();
                } catch(e) {
                    return false;
                }
            }
            return true;
        },
        setItem : function(key, value) {
            if(UserData.init()){
                UserData.userData.load(UserData.name);
                UserData.userData.setAttribute(key, value);
                UserData.userData.save(UserData.name);
            }
        },
        getItem : function(key) {
            if(UserData.init()){
            UserData.userData.load(UserData.name);
            return UserData.userData.getAttribute(key)
            }
        },
        removeItem : function(key) {
            if(UserData.init()){
            UserData.userData.load(UserData.name);
            UserData.userData.removeAttribute(key);
            UserData.userData.save(UserData.name);
            }

        }
    };
	if(!window.localStorage){
		window.localStorage=UserData;
	}
})();
