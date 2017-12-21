var Account = function(){
    var ua = navigator.userAgent.toLowerCase();
    var isIE = ua.match(/msie ([\d.]+)/);
    var isIE6 = isIE && isIE[1] && parseInt(isIE[1]) == 6 ? true : false;
    var onDOMReady = function(fn){
        var isReady=false;
        var readyList= [];
        var timer;
        var ready = function(fn) {
            if (isReady)
                fn.call( document);
            else
                readyList.push( function() { return fn.call(this);});
                return this;
            };
            var onDOMReady=function(){
            for(var i=0;i<readyList.length;i++){
                readyList[i].apply(document);
            }
            readyList = null;
        };
        var bindReady = function(evt){
            if(isReady) return;
                isReady=true;
                onDOMReady.call(window);
            if(document.removeEventListener){
                document.removeEventListener("DOMContentLoaded", bindReady, false);
            }else if(document.attachEvent){
                document.detachEvent("onreadystatechange", bindReady);
                if(window == window.top){
                    clearInterval(timer);
                    timer = null;
                }
            }
        };
        if(document.addEventListener){
            document.addEventListener("DOMContentLoaded", bindReady, false);
        }else if(document.attachEvent){
            document.attachEvent("onreadystatechange", function(){
                if((/loaded|complete/).test(document.readyState)){
                    bindReady();
                }
            });
            if(window == window.top){
                timer = setInterval(function(){
                    try{
                        isReady||document.documentElement.doScroll('left');
                    }catch(e){
                        return;
                    }
                    bindReady();
                },5);
            }
        };
        
        return ready;
    }();
    
    
    
    var suffix = function(){
        if(window.location.host.indexOf('aliyun.') == -1)return '.com';
        var output =  window.location.host.replace(/^.*\.aliyun/i,'');
        if(!output)output = '.com';
        return output;
    }();
    
    var staticServer = function(){
        var protocol = window.location.protocol;
        if(protocol != 'https:'){
            protocol = 'http:';
            return protocol + '//static-img4.cdn.aliyuncs' + suffix;
        }else{
            return protocol + '//static.aliyun' + suffix;
        }
        
    }();
    
    var loginProtocol = 'https://';
    var currentURL = encodeURIComponent(window.location.href);
    var API = {
        url:'http://www.aliyun' + suffix + '/user?m=ajaxcomm&ac=getuserstatus&reurl=' + currentURL,
        getLoginInfo:loginProtocol + 'account.aliyun' + suffix + '/login/aliyun_login_page2.js?oauth_callback=' + currentURL,
        loginSubmitURL:loginProtocol + 'account.aliyun' + suffix + '/login/doLogin.htm?oauth_callback=' + currentURL,
        popupLoginSubmitURL:loginProtocol + 'login.aliyun' + suffix + '/loginJs',
        alipayLoginURL:loginProtocol + 'account.aliyun' + suffix + '/login/alipay_quick_login.htm?oauth_callback=' + currentURL,
        forgetPwdURL:loginProtocol + 'account.aliyun' + suffix + '/forget/forget.htm',
        loginURL:loginProtocol + 'account.aliyun' + suffix + '/login/login.htm?oauth_callback=' + currentURL,
        regURL:loginProtocol + 'account.aliyun' + suffix + '/register/register.htm?oauth_callback=' + currentURL,
        sendVerifyCodeURL:loginProtocol + 'member.aliyun' + suffix + '/ajaxcommon/sendMobileVerifyCode',
        bindMobileSubmitURL:loginProtocol + 'member.aliyun' + suffix + '/ajaxcommon/bindMobile',
        swm:'http://www.aliyun' + suffix + '/promotion/swm',
        links:{
            goldenMetal:'http://promotion.aliyun.com/act/jpfw.html',
            userLession:'http://help.aliyun.com/manual?spm=0.0.0.32.CdpeRJ&lastSortId=236',
            userTask:'http://bbs.aliyun.com/read.php?tid=128287',
            userAct:'http://bbs.aliyun.com/read.php?spm=5176.383338.11.4.L1aaci&tid=129272',
            userDirection:'http://help.aliyun.com/guide?spm=0.0.0.39.pV8Wee&lastSortId=428'
        }
    };
    
    function loadScript(params){
        var url = params.url;
        var successFn = params.success;
        var head = document.getElementsByTagName("head")[0];
        var script = document.createElement("script");
        script.setAttribute("type", "text/javascript");
        script.setAttribute("src", url);
        if(isIE){
            script.onreadystatechange = function(){
                if(script.readyState == "complete" || script.readyState == "loaded"){
                    if(successFn instanceof Function){
                        successFn.call();
                    }

                }
            };
        }else{
            script.onload = function(){
                if(successFn instanceof Function){

                    successFn.call();
                }
            };
        };
        head.appendChild(script);
        return script;
    }
    
    function trimString(string){
        return string.replace(/^\s+|\s+$/g,'');
    }
    
    function trimUserName(string,length){
        if(string.length <= length){
            return string;
        }else{
            return string.substr(0,length - 6) + '...' + string.substr(string.length - 3,3);
        }
    }
    
    function getCookie(){
        var info = new Object();
        var values = document.cookie.split(';');
        var pair;
        var key;
        for(var i=0,len=values.length;i<len;i++){
            values[i] = values[i].replace(/\s/,'');
            var pair = values[i].split('=');
            info[pair[0]] = pair[1];
        }
        return info;
    }
    
    function addStyle(cssText){
        if(isIE){
            document.createStyleSheet().cssText = cssText;
        }else{
            var style = document.createElement("style");
            style.type = "text/css";
            style.textContent = cssText;
            document.getElementsByTagName("head").item(0).appendChild(style);
        }
    }
    
    function findCls(cls,el){
        if(!el)el = document.body;
        var elements = el.getElementsByTagName("*");
        var results = [];
        for(var i=0,len=elements.length;i<len;i++){
            if((" " + elements[i].className + " ").indexOf(" " + cls + " ") > -1){
                results.push(elements[i]);
            }
        }
        return results;
    }
    
    function addCls(el,cls){
        var clsName = el.className.replace(/\s+/g,' ');
        clsNames = clsName.split(' ');
        for(var i=0,len=clsNames.length;i<len;i++){
            if(clsNames[i] == cls){
                return;
            }
        }
        clsNames.push(cls);
        el.className = clsNames.join(' ');
    }
    
    function removeCls(el,cls){
        var clsName = el.className.replace(/\s+/g,' ');
        clsNames = clsName.split(' ');
        for(var i=0,len=clsNames.length;i<len;i++){
            if(clsNames[i] == cls){
                clsNames.splice(i,1);
                len = clsNames.length;
                i--;
            }
        }
        el.className = clsNames.join(' ');
    }
    
    function addListener(el,type,fn){
        if(isIE){
            el.attachEvent("on" + type,fn);
        }else{
            el.addEventListener(type,fn,false);
        }
    }
    
    function removeListener(el,type,fn){
        if(isIE){
            el.detachEvent("on" + type,fn);
        }else{
            el.removeEventListener(type,fn,false);
        }
    }
    
    function getRandom(){
        return parseInt((Math.random() * 1000000000)).toString();
    }
    
    function waitForIframeData(iframe,fn){
        var originalWindowName = iframe.contentWindow.name;
        
        var fn1 = function(){
            removeListener(iframe,'load',fn1);
            addListener(iframe,'load',fn2);
            iframe.contentWindow.location.href = 'about:blank';
        };
        
        var fn2 = function(){
            var data = iframe.contentWindow.name;
            fn(data);
            iframe.contentWindow.name = originalWindowName;
            removeListener(iframe,'load',fn2);
        };
        
        addListener(iframe,'load',fn1);
    };
    
    function updatePageToken(token){
        var elements = document.getElementsByTagName('input');
        for(var i=0,len=elements.length;i<len;i++){
            if(elements[i].getAttribute('type') == 'hidden' && elements[i].getAttribute('name') == 'sec_token'){
                elements[i].value = token;
            }
        }
    }
    
/*=============================================================================================================*/   
    
    
    var renderUserPanel = function(type){
        if(typeof(type) == 'undefined' || type == null)type = 1;
        
        var html;
        var elid = 'aylogin_' + getRandom();
        
        var cssText = [
            '.ayaccount-login{ font:12px/18px "\\5FAE\\8F6F\\96C5\\9ED1", Helvetica, Arial, Verdana, "\\5B8B\\4F53"; color:#666666; width:220px; height:232px;}',
            '.ayaccount-login-nolinks{ height:190px;}',
            '.ayaccount-login-btns{ overflow:hidden; *zoom:1; padding-bottom:10px; clear:both;}',
            '.ayaccount-login-btn-login,',
            '.ayaccount-login-btn-reg{ display:block; float:left; width:110px; height:41px; background-image:url(' + staticServer + '/images/account/sprite_login_new.gif); background-repeat:no-repeat;}',
            '.ayaccount-login-btn-reg{ background-position:0 0;}',
            '.ayaccount-login-btn-reg:hover{ background-position:0 -42px;}',
            '.ayaccount-login-btn-login{ background-position:right 0;}',
            '.ayaccount-login-btn-login:hover{ background-position:right -42px;}',
            
            '.ayaccount-login-ad{ clear:both; overflow:hidden; *zoom:1;}',
            '.ayaccount-login-ad-header{ height:28px; background:#F5F5F5; padding:0 2px 0 2px; border:1px solid #E7E7E7; border-bottom-width:2px;}',
            '.ayaccount-login-ad-header a{ display:block; float:left; color:#333!important; padding:4px 0 5px 0; width:105px; text-align:center; border-width:1px 1px 0 1px; border-style:solid; border-color:#F5F5F5; position:relative; bottom:-2px; text-decoration:none!important;}',
            '.ayaccount-login-ad-header a.ayaccount-login-ad-header-on{ background:#FFF; border-color:#E7E7E7; font-weight:bold;}',
            '.ayaccount-login-ad-body{ border:1px solid #E7E7E7; border-top:none; height:97px; text-align:center;}',
            
            '.ayaccount-login-ad-goldenmetal{ text-align:left; clear:both;}',
            '.ayaccount-login-ad-goldenmetal span{ display:block; float:left; height:55px; width:55px;  background:url(' + staticServer + '/images/account/sprite_login_new.gif?v=20130423) right -130px no-repeat;margin:20px 15px}',
            '.ayaccount-login-ad-goldenmetal ul{margin:0; float:left; width:115px;margin-top:10px;}',
            //'.ayaccount-login-ad-goldenmetal p font{ color:#E0AB0A; font-size:14px;}',
            '.ayaccount-login-ad-goldenmetal ul li{ height:25px;line-height:25px;border-bottom:1px dashed #e7e7e7;font-family:"Microsoft YaHei";}',
            '.ayaccount-login-ad-goldenmetal ul li.a,.ayaccount-login-ad-goldenmetal ul li.b,.ayaccount-login-ad-goldenmetal ul li.c{background:url(' + staticServer + '/images/account/goldservice-icon.png?v=20130423) 0 5px no-repeat;text-indent:22px;}',
            '.ayaccount-login-ad-goldenmetal ul li.b{background-position:0 -24px;}',
            '.ayaccount-login-ad-goldenmetal ul li.c{background-position:0 -51px;}',
            '.ayaccount-login-ad-goldenmetal ul li a{color:#333333}',
            '.ayaccount-login-ad-userguide{}',
            '.ayaccount-login-ad-userguide-row{ padding:14px 0; border-bottom:1px dotted #E7E7E7;}',
            '.ayaccount-login-ad-userguide-row-noline{ border-bottom:none;}',
            '.ayaccount-login-ad-userguide-row a{ display:inline-block; *display:inline; *zoom:1; padding-left:25px; padding-right:10px; color:#333!important; background-image:url(' + staticServer + '/images/account/sprite_login_new.gif?v=20130423); background-repeat:no-repeat; height:20px;}',
            '.ayaccount-login-userguid-lesson{ background-position:-5px -209px;}',
            '.ayaccount-login-userguid-task{ background-position:-5px -289px;}',
            '.ayaccount-login-userguid-act{ background-position:-5px -250px;}',
            '.ayaccount-login-userguid-direction{ background-position:-5px -329px;}',
            
            '.ayaccount-login-links{ overflow:hidden;margin-top:10px; height:40px; clear:both;}',
            '.ayaccount-login-links .ayaccount-login-links-price{display:block;*zoom:1;height:38px; width:220px; background:url(http://oss.aliyuncs.com/aliyun_portal_storage/1366775003_70_346.png) 0 0px;text-indent:-10000px;}',
            '.ayaccount-login-links a.ayaccount-login-links-price:hover{background-position:0px -39px;}',
            '.ayaccount-login-nolinks .ayaccount-login-links{ display:none;}',
            '.ayaccount-login-nolinks .ayaccount-login-ad-body{ padding:5px 0;}',
            '.ayaccount-login a{ color:#0066cc; text-decoration:none;}',
            '.ayaccount-login a:hover{ text-decoration:underline;}',
            '.ayaccount-login-header{ border:#E5E5E5 solid 1px; padding:10px 15px; overflow:hidden; *zoom:1; background:#F5F5F5;}',
            '.ayaccount-login-header h1{ font-weight:bold; display:block; float:left; margin:0; font-size:12px;}',
            '.ayaccount-login-header a{ display:inline-block; *display:inline; *zoom:1; vertical-align:middle; float:right;}',
            '.ayaccount-login-body{ padding:10px 15px 15px 15px; border:solid #E5E5E5; border-width:0 1px 1px 1px; height:166px; overflow:hidden;}',
            '.ayaccount-login-body input{ width:125px; border: 1px solid #CFCFCF; border-radius: 3px; box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.1) inset; font: 12px/15px Microsoft YaHei,Tahoma,Geneva,sans-serif,SimSun; height: 15px; padding: 4px 5px; vertical-align: middle; *margin:-1px 0; outline:none;}',
            '.ayaccount-login-body label{ display:inline-block; *display:inline; *zoom:1; width:47px; vertical-align:middle;}',
            '.ayaccount-login-body input.ayaccount-login-input-focus{ border-color:#999;}',
            '.ayaccount-login-body input.ayaccount-login-input-error{ border-color:#F30; background-color:#FFC; color:#F30;}',
            '.ayaccount-login-body input.ayaccount-login-input-tip{ color:#CCC;}',
            '.ayaccount-login-body .ayaccount-row{ padding:5px 0; overflow:hidden; *zoom:1;}',
            '.ayaccount-login-userinfo .ayaccount-row{ padding:8px 0; border-bottom:1px dotted #E4E4E4;}',
            '.ayaccount-login-buttons-row{ padding-left:47px; padding-top:3px;}',
            '.ayaccount-login-loginbtn{ display:inline-block; *display:inline; *zoom:1; width:77px; height:27px; vertical-align:middle; background:url(' + staticServer + '/images/account/sprite_login.gif) 0 0 no-repeat; overflow:hidden; margin-right:10px;}',
            '.ayaccount-login-loginbtn:hover{ background-position:0 -200px;}',
            '.ayaccount-login-others-row{ padding:6px 0; text-align:center;}',
            '.ayaccount-login-others-row label{ width:auto; vertical-align:middle;}',
            '.ayaccount-login-others-row a{ display:inline-block; *display:inline; *zoom:1; height:16px; width:16px; background:url(' + staticServer + '/images/account/sprite_login.gif) -9999px -9999px no-repeat; vertical-align:middle; overflow: hidden; text-indent: -9999px;}',
            '.ayaccount-login-others-row .ayaccount-login-alipay{ background-position: -6px -93px; margin-left:8px;}',
            '.ayaccount-login-links-row{ overflow:hidden; *zoom:1;}',
            '.ayaccount-login-links-row a,.ayaccount-login-links-row a:hover{ text-decoration:none;}',
            '.ayaccount-login-nolinks .ayaccount-login-links-row{ display:none;}',
            '.ayaccount-login-nolinks .ayaccount-login-body{ height:133px; padding-bottom:6px;}',
            '.ayaccount-login-price,',
            '.ayaccount-login-magazine{ display:block; width:92px; height:31px; float:left; background:url(' + staticServer + '/images/account/sprite_login.gif) 0 -30px repeat-x; text-align:center;}',
            '.ayaccount-login-price{ border-top:1px solid #D5D5D5; border-right:1px solid #E5E5E5; border-bottom:1px solid #BFBFBF; border-left:1px solid #C9C9C9;}',
            '.ayaccount-login-magazine{ border-top:1px solid #D5D5D5; border-right:1px solid #BFBFBF; border-bottom:1px solid #BFBFBF;}',
            '.ayaccount-login-price:hover,.ayaccount-login-magazine:hover{ background:#FFF;}',
            '.ayaccount-login-price span,',
            '.ayaccount-login-magazine span{ display:inline-block; *display:inline; *zoom:1; height:18px; vertical-align:middle; padding-left:25px; color:#333333; margin-top:6px; background-image:url(' + staticServer + '/images/account/sprite_login.gif); text-decoration:none; cursor:pointer;}',
            '.ayaccount-login-price span{ background-position: -7px -166px;}',
            '.ayaccount-login-magazine span{ background-position: -5px -130px;}',
            '.ayaccount-login-loading{ background:url(' + staticServer + '/images/account/loading_32.gif) center center no-repeat}',
            '.ayaccount-login i{ display:inline-block; *display:inline; *zoom:1; font-size:0; overflow:hidden; line-height:0; width:1px; height:12px; margin:7px 0; background:#C8C8D0; margin:0 6px; vertical-align:middle;}',
            '.ayaccount-orange{ color:#F60!important;}'
        ].join('');
        
        html = [
            '<div class="ayaccount-login' + (type=='1'?' ayaccount-login-nolinks':'') + ' ayaccount-login-loading" id=' + elid + '>',
                
            '</div>'
        ].join('');
        
        addStyle(cssText);
        document.writeln(html);
        var loginEl = document.getElementById(elid);
        var loginBodyEl = loginEl;
        
        var renderUserInfo = function(uname,msgNum,expiringVMNum){
            addCls(loginEl,' ayaccount-login-userinfo');
            loginBodyEl.innerHTML = [
                '<div class="ayaccount-login-header">',
                    '<h1 class="ayaccount-login-title">会员登录</h1>',
                    '<a class="ayaccount-login-reg" style="display:none;" href="#" >注册帐号</a>',
                '</div>',
                '<div class="ayaccount-login-body">',
                
                    '<div class="ayaccount-row" style="padding-top:0;">',
                        '<a style="color:#666;" href="http://i.aliyun' + suffix + '/pm"  target="_blank">消息中心</a> ',
                        (msgNum=='0'?
                        '<span style="color:#999">(0)</span>':
                        '<a href="http://i.aliyun' + suffix + '/pm" style="color:#F30;"  target="_blank">(' + msgNum + ')</a>'),
                    '</div>',
                    '<div class="ayaccount-row">',
                        //'云服务器即将到期 ',
                        //(expiringVMNum=='0'?
                        //'<span style="color:#999">(' + expiringVMNum + ')</span>':
                        //'<a href="http://i.aliyun' + suffix + '/dashboard?type=vm&outdate=1" style="color:#F30;">(' + expiringVMNum + ')</a> <a href="http://i.aliyun' + suffix + '/dashboard?type=vm&outdate=1" style="margin-left:10px;">马上续费</a>'),
                        '<a href="' + SWM.get('account_login_plugin','console_link') + '" target="' + SWM.get('account_login_plugin','console_target') + '">' + SWM.get('account_login_plugin','console_text') + '</a>',
                    '</div>',
                    '<div class="ayaccount-row">',
                        '去 <a href="http://i.aliyun' + suffix + '" target="_blank">用户中心</a> 查看',
                    '</div>',
                    '<div class="ayaccount-row" style="border-bottom:none; margin-bottom:2px;">',
                        '<a href="http://i.aliyun.com/faq" target="_blank" style="vertical-align:middle;">售后支持</a>',
                        '<i></i>',
                        '<a href="http://bbs.aliyun.com/thread.php?fid=157" target="_blank" style="vertical-align:middle;">意见反馈</a>',
                        '<i></i>',
                        '<a href="http://my.aliyun.com" target="_blank" style="vertical-align:middle;">手机云空间</a>',
                    '</div>',
                    '<div class="ayaccount-login-links-row">',
                        '<a class="ayaccount-login-price" href="http://help.aliyun.com/manual?helpId=744" target="_blank"><span>价格总览</span></a>',
                        '<a class="ayaccount-login-magazine" href="http://lingyun.aliyun.com" target="_blank"><span>凌云杂志</span></a>',
                    '</div>',
                
                '</div>'
            ].join('');
            
            var topbarUnameEl = findCls('aysw-topbar-uname',document.body)[0];
            if(topbarUnameEl){
                topbarUnameEl.innerHTML = uname;
                topbarUnameEl.className = 'aysw-topbar-uname';
            };
            var headerTextEl = findCls('ayaccount-login-title',loginEl)[0];
            headerTextEl.innerHTML = '欢迎您，<span class="ayaccount-orange" title="' + uname + '">' + trimUserName(uname,18) + '</span>';
        };
        
        var renderLogin = function(oauthToken,server,token,alipayURL){
            removeCls(loginBodyEl,'ayaccount-login-loading');
            loginBodyEl.innerHTML = [
                '<div class="ayaccount-login-btns">',
                    '<a hidefocus="on" href="' + API.regURL + '" class="ayaccount-login-btn-reg"></a>',
                    '<a hidefocus="on" href="' + API.loginURL + '" class="ayaccount-login-btn-login"></a>',
                '</div>',
                '<div class="ayaccount-login-ad">',
                    '<div class="ayaccount-login-ad-header">',
                        '<a href="#" hidefocus="on" class="ayaccount-login-ad-header-on">金牌服务</a>',
                        '<a href="#" hidefocus="on">新手专区</a>',
                    '</div>',
                    '<div class="ayaccount-login-ad-body">',
                        '<div class="ayaccount-login-ad-goldenmetal">',
                            '<a href="' + API.links.goldenMetal + '" target="_blank"><span></span></a>',
                            '<ul><li class="a"><a href="http://promotion.aliyun.com/act/jpfw.html?czclac=65a1d80a0bc368dc8873ba3a6d5f5e23#4">免费快速备案</a></li><li class="b"><a href="http://promotion.aliyun.com/act/jpfw.html?czclac=b974fe41cc2653560b10fdd898c111b6#6">免费数据迁移</a></li><li class="c"><a href="http://promotion.aliyun.com/act/jpfw.html?czclac=3cd5adf7d4e07bde5905da0f3045efb1#2">故障100倍赔偿</a></li></ul>',
                        '</div>',
                        '<div class="ayaccount-login-ad-userguide" style="display:none;">',
                            '<div class="ayaccount-login-ad-userguide-row">',
                                '<a href="' + SWM.get('account_login_plugin','lessons_link') + '" target="_blank" class="ayaccount-login-userguid-lesson">' + SWM.get('account_login_plugin','lessons_text') + '</a>',
                                '<a href="' + SWM.get('account_login_plugin','tasks_link') + '" target="_blank" class="ayaccount-login-userguid-task">' + SWM.get('account_login_plugin','tasks_text') + '</a>',
                            '</div>',
                            '<div class="ayaccount-login-ad-userguide-row ayaccount-login-ad-userguide-row-noline">',
                                '<a href="' + SWM.get('account_login_plugin','act_link') + '" target="_blank" class="ayaccount-login-userguid-act">' + SWM.get('account_login_plugin','act_text') + '</a>',
                                '<a href="' + SWM.get('account_login_plugin','directions_link') + '" target="_blank" class="ayaccount-login-userguid-direction">' + SWM.get('account_login_plugin','directions_text') + '</a>',
                            '</div>',
                        '</div>',
                    '</div>',
                    '<div class="ayaccount-login-links">',
                        '<a href="http://mail.aliyun.com" target="_blank"   class="ayaccount-login-links-price">登录云邮箱</a>',
                    '</div>',
                '</div>'
            ].join('');
            
            var tabs = findCls('ayaccount-login-ad-header',loginEl)[0].getElementsByTagName('a');
            var tab_golden = tabs[0];
            var tab_golden_content = findCls('ayaccount-login-ad-goldenmetal',loginEl)[0];
            var tab_userguide = tabs[1];
            var tab_userguide_content = findCls('ayaccount-login-ad-userguide',loginEl)[0];
            addListener(tab_golden,'click',function(e){
                if(e.preventDefault){
                    e.preventDefault();
                }else{
                    e.returnValue = false;
                }
                
                addCls(tab_golden,'ayaccount-login-ad-header-on');
                removeCls(tab_userguide,'ayaccount-login-ad-header-on');
                tab_golden_content.style.display = '';
                tab_userguide_content.style.display = 'none';
            });
            
            addListener(tab_userguide,'click',function(e){
                if(e.preventDefault){
                    e.preventDefault();
                }else{
                    e.returnValue = false;
                }
                
                addCls(tab_userguide,'ayaccount-login-ad-header-on');
                removeCls(tab_golden,'ayaccount-login-ad-header-on');
                tab_golden_content.style.display = 'none';
                tab_userguide_content.style.display = '';
            });
            
            /*
            var loginBtn = findCls('ayaccount-login-loginbtn',loginEl)[0];
            var form = loginEl.getElementsByTagName('form')[0];
            var regLink = findCls('ayaccount-login-reg',loginEl)[0];
            var input_uid = findCls('ayaccount-login-uid',loginEl)[0];
            var input_pwd = findCls('ayaccount-login-pwd',loginEl)[0];
            
            regLink.href =  API.regURL;
            regLink.style.display = '';
            loginBtn.onclick = function(){
                submitLogin();
                return false;
            };
            
            if(input_uid.getAttribute('autotip') && input_uid.value == ''){
                input_uid.value = input_uid.getAttribute('autotip');
                addCls(input_uid,'ayaccount-login-input-tip');
            }
            addListener(input_uid,'focus',focusHandler);
            addListener(input_uid,'blur',blurHandler);
            addListener(input_pwd,'focus',focusHandler);
            addListener(input_pwd,'blur',blurHandler);
            
            addListener(input_uid,'keyup',function(e){
                if(!e)e = window.event;
                if(e.keyCode == '13'){
                    input_pwd.focus();
                };
            });
            
            addListener(input_pwd,'keypress',function(e){
                if(!e)e = window.event;
                var target = e.target?e.target:e.srcElement;
                target.className = 'ayaccount-login-input-focus';
                target.title = '';
                if(e.keyCode == '13'){
                    submitLogin();
                };
            });
            */
            
            function submitLogin(){
                if(checkFields()){
                    form.submit();
                }
            }
            
            function checkFields(){
                var result = true;
                if(!checkuid())result = false;
                if(!checkpwd())result = false;
                return result;
            }
            
            function checkuid(){
                input_uid.value = trimString(input_uid.value);
                var uid = input_uid.value;
                var correct = true;
                if(input_uid.className != 'ayaccount-login-input-error'){
                    if(uid == '' || uid == input_uid.getAttribute('autotip')){
                        addCls(input_uid,'ayaccount-login-input-error');
                        input_uid.title = '用户名不能为空';
                        correct = false;
                    }else if(!/^1\d{10}$|^[a-zA-Z][a-zA-Z0-9\._]{3,29}$|^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/.test(uid)){
                        addCls(input_uid,'ayaccount-login-input-error');
                        input_uid.title = '输入的用户名有误';
                        correct = false;
                    }
                }else{
                    correct = false;
                }
                
                return correct;
            }
            
            function checkpwd(){
                var pwd = input_pwd.value;
                var correct = true;
                
                if(input_pwd.className != 'ayaccount-login-input-error'){
                    if(pwd == ''){
                        input_pwd.className = 'ayaccount-login-input-error';
                        input_pwd.title = '密码不能为空';
                        correct = false;
                    }else if(!/^.{6,20}$/.test(pwd)){
                        input_pwd.className = 'ayaccount-login-input-error';
                        input_pwd.title = '输入的密码有误';
                        correct = false;
                    }
                }else{
                    correct = false;
                }
                
                return correct;
            }
            
            function focusHandler(e){
                if(!e)e = window.event;
                var target = e.target?e.target:e.srcElement;
                if(target.className == 'ayaccount-login-input-error'){
                    //target.value = '';
                }
                removeCls(target,'ayaccount-login-input-tip');
                removeCls(target,'ayaccount-login-input-error');
                target.title = '';
                addCls(target,'ayaccount-login-input-focus');
                
                if(target.getAttribute('autotip')){
                    if(target.value == target.getAttribute('autotip')){
                        target.value = '';
                    }
                }
            }
            
            function blurHandler(e){
                if(!e)e = window.event;
                var target = e.target?e.target:e.srcElement;
                removeCls(target,'ayaccount-login-input-focus');
                removeCls(target,'ayaccount-login-input-error');
                target.title = '';
                if(target.getAttribute('autotip')){
                    if(target.value == target.getAttribute('autotip') || target.value == ''){
                        target.value = target.getAttribute('autotip');
                        addCls(target,'ayaccount-login-input-tip');
                    }
                }
            }
        };
        
        if(window.__ay_topbar_requestCallback){
            var topbarCallback = window.__ay_topbar_requestCallback;
            window.__ay_topbar_requestCallback = undefined;
        }
        
        onDOMReady(function(){
            if(!window.SWM){
                loadScript({
                    url:API.swm,
                    success:function(){
                        startLoading();
                    }
                });
            }else{
                startLoading();
            }
            
            function startLoading(){
                var script = loadScript({
                    url:API.url + '&' + getRandom(),
                    success:function(){
                        script.parentNode.removeChild(script);
                        if(window.__ay_login_info && window.__ay_login_info.data){
                            var data = window.__ay_login_info.data;
                            window.__ay_login_info = undefined;
                            if(data.uname){
                                renderUserInfo(data.uname, data.pnum, data.vnum);
                                removeCls(loginBodyEl,'ayaccount-login-loading');
                            }else{
                                renderLogin();
                            }
                            if(topbarCallback){
                                topbarCallback(data);
                            }
                        }
                    }
                });
            }
        });
    };
    
    
    
/*=============================================================================================================*/   
    var login = function(){
        var popup = getPopup();
        popup.show();
        popup.showInfo('正在加载数据，请稍后...','ayaccount-popuplogin-infopanel-loading');
        popup.center();
        getUserStatus(function(response){
            if(response.data && response.data.uname){
                popup.showInfo('用户已登录！','ayaccount-popuplogin-infopanel-warning');
                setTimeout(function(){
                    popup.hide();
                    window.location.reload();
                },1000);
                
            }else{
                popup.reset();
                popup.showLogin(response.data.token,response.vcode);
                popup.setCallback(function(){
                    window.location.reload();
                });
                popup.center();
            }
        });
    };
    
    
    var doUserAction = function(callback,requireMobile){
        var popup = getPopup();
        popup.show();
        popup.reset();
        popup.showInfo('正在验证用户身份，请稍后...','ayaccount-popuplogin-infopanel-loading');
        popup.center();
        getUserStatus(function(response){
            if(response.data && response.data.uname){
                if(requireMobile && !response.data.mobile){
                    popup.show();
                    popup.reset();
                    popup.showBind(response.data.token);
                    popup.setCallback(callback);
                    
                    popup.center();
                }else{
                    popup.hide();
                    callback();
                }
            }else{
                popup.setData(response.data);
                popup.reset();
                popup.showLogin(response.data.token,response.vcode);
                popup.setCallback(function(){
                    doUserAction(callback,requireMobile);
                });
                popup.center();
            }
        });
    };
    
    var getUserStatus = function(callback){
        var script = loadScript({
            url:API.url + '&' + getRandom(),
            success:function(){
                script.parentNode.removeChild(script);
                if(window.__ay_login_info && window.__ay_login_info.data){
                    var data = window.__ay_login_info;
                    window.__ay_login_info = undefined;
                    if(callback instanceof Function){
                        callback(data);
                    }
                }
            }
        });
    };
    
    var popupWindow;
    var getPopup = function(){
        if(popupWindow){
            return popupWindow;
        }
        
        var userData,
        container,
        overlay,
        loginPanel,
        bindPanel,
        infoPanel,
        form,
        bindForm,
        loginBtn,
        bindBtn,
        vcodePic,
        changeVCodePic,
        input_username,
        input_password,
        input_vcode,
        input_token,
        input_mobile,
        input_mobile_vcode,
        input_bind_token,
        requireMobile,
        callback;
        
                        
        var setError = function(el,msg){
            if(el.nodeName == 'INPUT'){
                addCls(el.parentNode,'ayaccount-popuplogin-textbox-error');
            }else{
                addCls(el.parentNode,'ayaccount-popuplogin-buttons-error');
            }
            findCls('ayaccount-popuplogin-bubble-text',el.parentNode)[0].innerHTML = msg;
        };
        
        var clearError = function(el,msg){
            if(el.nodeName == 'INPUT'){
                removeCls(el.parentNode,'ayaccount-popuplogin-textbox-error');
            }else{
                removeCls(el.parentNode,'ayaccount-popuplogin-buttons-error');
            }
        };
        
        var popup = {
            init:function(){
                var cssText = [
                    '.ayaccount-popuplogin{ width:430px; background:#E2E2E2; border-radius:5px; padding:4px; position:fixed; _position:absolute; font:12px/18px "\\5FAE\\8F6F\\96C5\\9ED1", Helvetica, Arial, Verdana, "\\5B8B\\4F53"; color:#666666; z-index:10000;}',
                    '.ayaccount-popuplogin-loginpanel{ }',
                    '.ayaccount-popuplogin a{ color:#06C; text-decoration:none; outline:none;}',
                    '.ayaccount-popuplogin a:hover{ text-decoration:underline;}',
                    '.ayaccount-popuplogin input{ font-family:"\\5FAE\\8F6F\\96C5\\9ED1", Helvetica, Arial, Verdana, "\\5B8B\\4F53"; color:#666666; outline:none;}',
                    '.ayaccount-popuplogin form{ margin:0; padding:0;}',
                    '.ayaccount-popuplogin-inner{ border:1px solid #CCC; border-radius:3px; background:#FAFAFA; padding:20px;}',
                    '.ayaccount-popuplogin-blue{ color:#06C;}',
                    '.ayaccount-popuplogin-header{ padding:0 0 10px 0; border-bottom:2px solid #999; overflow:hidden; *zoom:1;}',
                    '.ayaccount-popuplogin-title{ display:block; float:left; width:74px; height:18px; background:url(' + staticServer + '/images/account/login_popup_sprite.gif) -15px -10px; text-indent:-10000px;}',
                    '.ayaccount-popuplogin-title-bind{ background-position:-15px -170px;}',
                    '.ayaccount-popuplogin-closebtn{ display:block; float:right; width:17px; height:17px; background:url(' + staticServer + '/images/account/login_popup_sprite.gif) -215px -14px;}',
                    '.ayaccount-popuplogin-closebtn:hover{ opacity:0.7; filter:alpha(opacity=70);}',
                    '.ayaccount-popuplogin-body{ padding:20px 5px 10px 5px;}',
                    '.ayaccount-popuplogin-row{ padding:2px 0; clear:both; *zoom:1;}',
                    '.ayaccount-popuplogin-row:after{content:".";display:block;height:0;clear:both;visibility:hidden;}',
                    '.ayaccount-popuplogin-caption{ float:left; width:60px; text-align:right; font-size:14px; margin-right:15px; padding-top:11px;}',
                    '.ayaccount-popuplogin-content{ float:left;}',
                    '.ayaccount-popuplogin-textbox{ padding:4px; border-radius:5px; float:left; position:relative;}',
                    '.ayaccount-popuplogin-textbox input{ border:1px solid #CCC; border-radius:3px; padding:7px 9px; width:230px; height:18px; font-size:14px; display:block; float:left; outline:none;}',
                    '.ayaccount-popuplogin-buttons .ayaccount-popuplogin-bubble,',
                    '.ayaccount-popuplogin-textbox .ayaccount-popuplogin-bubble{ display:none; position:absolute; left:20px; top:-28px; border:1px solid #FACC80; background:#FFFDF1; padding:4px 10px; border-radius:3px; color:#F00; font-weight:bold; *zoom:1;}',
                    '.ayaccount-popuplogin-buttons .ayaccount-popuplogin-bubble-arrow,',
                    '.ayaccount-popuplogin-textbox .ayaccount-popuplogin-bubble-arrow{ display:block; position:absolute; bottom:-9px; left:20px; width:16px; height:9px; background:url(' + staticServer + '/images/account/login_popup_sprite.gif) -146px -20px no-repeat; *zoom:1; font-size:0; overflow:hidden;}',
                    '.ayaccount-popuplogin-bubble-text{ white-space:nowrap;}',
                    '.ayaccount-popuplogin-textbox input.ayaccount-popuplogin-vcode{ width:123px;}',
                    '.ayaccount-popuplogin-textbox-focus{ background:#D7E6F6;}',
                    '.ayaccount-popuplogin-textbox-focus input{ border-color:#80A7D3;}',
                    '.ayaccount-popuplogin-textbox-error{ background:#FDEDD3;}',
                    '.ayaccount-popuplogin-textbox-error input{ border-color:#DCBA83;}',
                    '.ayaccount-popuplogin-textbox-tip input{ color:#CCC;}',
                    '.ayaccount-popuplogin-buttons-error .ayaccount-popuplogin-bubble,',
                    '.ayaccount-popuplogin-textbox-error .ayaccount-popuplogin-bubble{ display:block;}',
                    '.ayaccount-popuplogin-texttip{ display:block; clear:both; padding-left:5px;}',
                    '.ayaccount-popuplogin-vcodepic{ display:block; float:left; padding:4px 0 0 0;}',
                    '.ayaccount-popuplogin-vcodepic img{ width:100px; height:30px; border:1px solid #EEE; padding:1px 0 1px 1px; border-radius:3px;}',
                    '.ayaccount-popuplogin-vcodepic:hover{ filter:alpha(opacity=70); opacity:0.7}',
                    '.ayaccount-popuplogin-buttons{ position:relative; padding:8px 10px 8px 80px;}',
                    '.ayaccount-popuplogin-buttons span,',
                    '.ayaccount-popuplogin-buttons a{ vertical-align:middle;}',
                    '.ayaccount-popuplogin-buttons .ayaccount-popuplogin-bubble{ left:105px;}',
                    '.ayaccount-popuplogin-loginbtn,',
                    '.ayaccount-popuplogin-btn-sendvcode,',
                    '.ayaccount-popuplogin-bindbtn{ display:inline-block; *display:inline; *zoom:1; width:103px; height:35px; background:url(' + staticServer + '/images/account/login_popup_sprite.gif) -9999px -9999px no-repeat; overflow:hidden; margin-right:10px;}',
                    '.ayaccount-popuplogin-loginbtn{ background-position: -15px -116px}',
                    '.ayaccount-popuplogin-bindbtn{ background-position: -15px -200px}',
                    '.ayaccount-popuplogin-btn-sendvcode{ background-position: -15px -251px; width:99px; height:27px; display:block; float:right; margin:4px 0 0 7px; color:#666!important; text-align:center; padding-top:7px; font-size:14px;}',
                    '.ayaccount-popuplogin-loginbtn:hover,',
                    '.ayaccount-popuplogin-btn-sendvcode:hover,',
                    '.ayaccount-popuplogin-bindbtn:hover{ filter:alpha(opacity=80); opacity:0.8}',
                    '.ayaccount-popuplogin-btn-sendvcode-disabled,',
                    '.ayaccount-popuplogin-btn-sendvcode-disabled:hover{ color:#999!important; cursor:default; text-decoration:none!important; filter:alpha(opacity=60); opacity:0.6}',
                    '.ayaccount-popuplogin-loginbtn-logging,',
                    '.ayaccount-popuplogin-loginbtn-logging:hover{ background-position:-135px -116px; opacity:1; filter:alpha(opacity=100); cursor:default;}',
                    '.ayaccount-popuplogin-bindbtn-binding,',
                    '.ayaccount-popuplogin-bindbtn-binding:hover{ background-position:-135px -200px; opacity:1; filter:alpha(opacity=100); cursor:default;}',
                    '.ayaccount-popuplogin-btn-register{ display:block; margin-left:-3px; width:221px; height:48px; background:url(' + staticServer + '/images/account/login_popup_sprite.gif) -15px -49px no-repeat; text-indent:-9999px; overflow:hidden;}',
                    '.ayaccount-popuplogin-btn-register:hover{ filter:alpha(opacity=70); opacity:0.7}',
                    '.ayaccount-popuplogin-alipay,',
                    '.ayaccount-popuplogin-taobao{ display:inline-block; *display:inline; *zoom:1; width:16px; height:16px; text-indent:-9999px; overflow:hidden; background:url(' + staticServer + '/images/account/login_popup_sprite.gif) -9999px -9999px; vertical-align:middle; margin-left:8px;}',
                    '.ayaccount-popuplogin-alipay{ background-position:-170px -15px;}',
                    '.ayaccount-popuplogin-taobao{ background-position:-192px -15px;}',
                    '.ayaccount-popuplogin-infopanel{ text-align:center;}',
                    '.ayaccount-popuplogin-infopanel span{ display:inline-block; *display:inline; *zoom:1; padding:10px 0; font-size:14px;}',
                    '.ayaccount-popuplogin-infopanel span.ayaccount-popuplogin-infopanel-loading{ padding-left:40px; background:url(' + staticServer + '/images/account/loading_32_1.gif) 0 center no-repeat;}',
                    '.ayaccount-popuplogin-overlay{ background:#000; overflow:hidden; position:fixed; top:0; left:0; height:100%; width:100%; bottom:0; right:0; _position:absolute; opacity:0.3; filter:alpha(opacity=30); z-index:9999;}'
                ].join('');
                addStyle(cssText);
                
                
                overlay = document.createElement('div');
                overlay.className = 'ayaccount-popuplogin-overlay';
                if(isIE6){
                    overlay.innerHTML = '<iframe style="filter:alpha(opacity=0);" frameborder="0"></div>';
                    var iframe = overlay.getElementsByTagName('iframe')[0];
                    var adjustOverlay = function(){
                        var width = document.documentElement.clientWidth || document.body.clientWidth;
                        var height = document.documentElement.clientHeight || document.body.clientHeight;
                        var scrollLeft = document.documentElement.scrollLeft || document.body.scrollLeft;
                        var scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
                        
                        overlay.style.width = width + 'px';
                        overlay.style.height = height + 'px';
                        iframe.setAttribute('width',width); 
                        iframe.setAttribute('height',width);
                        overlay.style.left = scrollLeft + 'px';
                        overlay.style.top = scrollTop + 'px';
                    };
                    adjustOverlay();
                    addListener(window,'resize',adjustOverlay);
                    addListener(window,'scroll',adjustOverlay);
                }
                document.body.appendChild(overlay);
                
                container = document.createElement('div');
                container.className = 'ayaccount-popuplogin';
                container.innerHTML = [
                    '<div class="ayaccount-popuplogin-inner">',
                        '<div class="ayaccount-popuplogin-loginpanel ayaccount_id_loginpanel">',
                            '<form action="' + API.popupLoginSubmitURL + '" method="post" target="ay_login_popup_sunmit_iframe">',
                                '<input type="hidden" class="ayaccount_id_token" name="sec_token" />',
                                '<div class="ayaccount-popuplogin-header">',
                                    '<span class="ayaccount-popuplogin-title">会员登录</span>',
                                    '<a href="#" class="ayaccount-popuplogin-closebtn ayaccount_id_closebtn"></a>',
                                '</div>',
                                '<div class="ayaccount-popuplogin-body">',
                                    '<div class="ayaccount-popuplogin-row">',
                                        '<div class="ayaccount-popuplogin-caption">用户名</div>',
                                        '<div class="ayaccount-popuplogin-content">',
                                            '<div class="ayaccount-popuplogin-textbox">',
                                                '<input autotip="会员帐号/手机号" class="ayaccount_id_user_name" type="text" name="user_name" value=""/>',
                                                '<div class="ayaccount-popuplogin-bubble">',
                                                    '<span class="ayaccount-popuplogin-bubble-arrow"></span>',
                                                    '<span class="ayaccount-popuplogin-bubble-text">请输入用户名</span>',
                                                '</div>',
                                            '</div>',
                                        '</div>',
                                    '</div>',
                                    '<div class="ayaccount-popuplogin-row">',
                                        '<div class="ayaccount-popuplogin-caption">密　码</div>',
                                        '<div class="ayaccount-popuplogin-content">',
                                            '<div class="ayaccount-popuplogin-textbox">',
                                                '<input class="ayaccount_id_password" type="password" name="password" />',
                                                '<div class="ayaccount-popuplogin-bubble">',
                                                    '<span class="ayaccount-popuplogin-bubble-arrow"></span>',
                                                    '<span class="ayaccount-popuplogin-bubble-text">请输入密码</span>',
                                                '</div>',
                                            '</div>',
                                        '</div>',
                                    '</div>',
                                    '<div class="ayaccount-popuplogin-row ayaccount_id_vcode">',
                                        '<div class="ayaccount-popuplogin-caption">验证码</div>',
                                        '<div class="ayaccount-popuplogin-content">',
                                            '<div class="ayaccount-popuplogin-textbox ayaccount-popuplogin-vcode ">',
                                                '<input class="ayaccount-popuplogin-vcode ayaccount_id_input_vcode" type="text" name="vcode" />',
                                                '<div class="ayaccount-popuplogin-bubble">',
                                                    '<span class="ayaccount-popuplogin-bubble-arrow"></span>',
                                                    '<span class="ayaccount-popuplogin-bubble-text">请输入验证码</span>',
                                                '</div>',
                                            '</div>',
                                            '<a href="#" title="点击更换" class="ayaccount_id_vcodepic ayaccount-popuplogin-vcodepic"><img /></a>',
                                            '<span class="ayaccount-popuplogin-texttip">看不清？<a class="ayaccount_id_changevcodepic" href="#">换一张</a></span>',
                                        '</div>',
                                    '</div>',
                                    '<div class="ayaccount-popuplogin-row ayaccount-popuplogin-buttons ">',
                                        '<a href="#" class="ayaccount_id_btn_login ayaccount-popuplogin-loginbtn"></a><a href="' + API.forgetPwdURL + '" target="_blank">忘记密码？</a>',
                                        '<div class="ayaccount-popuplogin-bubble">',
                                            '<span class="ayaccount-popuplogin-bubble-arrow"></span>',
                                            '<span class="ayaccount-popuplogin-bubble-text">用户名或密码错误</span>',
                                        '</div>',
                                    '</div>',
                                    '<div class="ayaccount-popuplogin-row ayaccount-popuplogin-buttons ">',
                                        '<span class="ayaccount-popuplogin-blue">其它登录方式</span>',
                                        '<a class="ayaccount-popuplogin-alipay" title="支付宝登录" href="' + API.alipayLoginURL + '">支付宝登录</a>',
                                        //'<a class="ayaccount-popuplogin-taobao" title="淘宝登录" href="#">淘宝登录</a>',
                                    '</div>',
                                    '<div class="ayaccount-popuplogin-row ayaccount-popuplogin-buttons ">',
                                        '<a href="' + API.regURL + '" target="_blank" class="ayaccount-popuplogin-btn-register">免费注册云帐号</a>',
                                    '</div>',
                                '</div>',
                                '<iframe class="ayaccount_id_loginiframe" name="ay_login_popup_sunmit_iframe" style="position:absolute; left:-9999px; top:-9999px;"></iframe>',
                            '</form>',
                        '</div>',
                        '<div class="ayaccount-popuplogin-loginpanel ayaccount_id_bindmobilepanel">',
                            '<form action="' + API.bindMobileSubmitURL + '" method="post" target="ay_login_popup_bind_sunmit_iframe">',
                                '<input type="hidden" class="ayaccount_id_bind_token" name="sec_token" />',
                                '<div class="ayaccount-popuplogin-header">',
                                    '<span class="ayaccount-popuplogin-title ayaccount-popuplogin-title-bind">手机绑定</span>',
                                    '<a href="#" class="ayaccount-popuplogin-closebtn ayaccount_id_closebtn"></a>',
                                '</div>',
                                '<div class="ayaccount-popuplogin-body">',
                                    '<div class="ayaccount-popuplogin-row">',
                                        '<div class="ayaccount-popuplogin-caption">手机号</div>',
                                        '<div class="ayaccount-popuplogin-content">',
                                            '<div class="ayaccount-popuplogin-textbox">',
                                                '<input class="ayaccount_id_mobile" type="text" name="mobile" value=""/>',
                                                '<div class="ayaccount-popuplogin-bubble">',
                                                    '<span class="ayaccount-popuplogin-bubble-arrow"></span>',
                                                    '<span class="ayaccount-popuplogin-bubble-text">请输入手机号</span>',
                                                '</div>',
                                            '</div>',
                                        '</div>',
                                    '</div>',
                                    '<div class="ayaccount-popuplogin-row">',
                                        '<div class="ayaccount-popuplogin-caption">验证码</div>',
                                        '<div class="ayaccount-popuplogin-content">',
                                            '<div class="ayaccount-popuplogin-textbox">',
                                                '<input class="ayaccount_id_mobilevcode" style="width:120px" type="text" name="vcode" />',
                                                '<div class="ayaccount-popuplogin-bubble">',
                                                    '<span class="ayaccount-popuplogin-bubble-arrow"></span>',
                                                    '<span class="ayaccount-popuplogin-bubble-text">请输入验证码</span>',
                                                '</div>',
                                            '</div>',
                                            '<a href="#" class="ayaccount-popuplogin-btn-sendvcode ayaccount_id_btn_sendvcode">发送验证码</a>',
                                        '</div>',
                                    '</div>',
                                    '<div class="ayaccount-popuplogin-row ayaccount-popuplogin-buttons ">',
                                        '<a href="#" class="ayaccount_id_btn_bind ayaccount-popuplogin-bindbtn"></a>',
                                        '<div class="ayaccount-popuplogin-bubble">',
                                            '<span class="ayaccount-popuplogin-bubble-arrow"></span>',
                                            '<span class="ayaccount-popuplogin-bubble-text">验证码错误</span>',
                                        '</div>',
                                    '</div>',
                                '</div>',
                                '<iframe class="ayaccount_id_bindmobileiframe" name="ay_login_popup_bind_sunmit_iframe" style="position:absolute; left:-9999px; top:-9999px;"></iframe>',
                            '</form>',
                        '</div>',
                        '<div class="ayaccount_id_infopanel ayaccount-popuplogin-infopanel">',
                            '<span>提示信息</span>',
                        '</div>',
                    '</div>'
                ].join('');
                
                loginPanel = findCls('ayaccount_id_loginpanel',container)[0];
                bindPanel = findCls('ayaccount_id_bindmobilepanel',container)[0];
                infoPanel = findCls('ayaccount_id_infopanel',container)[0];
                input_username = findCls('ayaccount_id_user_name',container)[0];
                input_password = findCls('ayaccount_id_password',container)[0];
                input_vcode = findCls('ayaccount_id_input_vcode',container)[0];
                input_mobile = findCls('ayaccount_id_mobile',container)[0];
                input_mobile_vcode = findCls('ayaccount_id_mobilevcode',container)[0];
                form = container.getElementsByTagName('form')[0];
                bindForm = container.getElementsByTagName('form')[1];
                loginBtn = findCls('ayaccount_id_btn_login',container)[0];
                bindBtn = findCls('ayaccount_id_btn_bind',container)[0];
                vcodeBtn = findCls('ayaccount_id_btn_sendvcode',container)[0];
                vcodeRow = findCls('ayaccount_id_vcode',container)[0];
                vcodePic = findCls('ayaccount_id_vcodepic',container)[0];
                changeVCodePic = findCls('ayaccount_id_changevcodepic',container)[0];
                input_token = findCls('ayaccount_id_token',container)[0];
                input_bind_token = findCls('ayaccount_id_bind_token',container)[0];
                iframe_login =  findCls('ayaccount_id_loginiframe',container)[0];
                iframe_bind =  findCls('ayaccount_id_bindmobileiframe',container)[0];
                
                var closeBtns = findCls('ayaccount_id_closebtn',container);
                document.body.appendChild(container);
                
                var closeHandler = function(e){
                    if(e.preventDefault){
                        e.preventDefault();
                    }else{
                        e.returnValue = false;
                    }
                    popup.hide();
                };
                addListener(closeBtns[0],'click',closeHandler);
                addListener(closeBtns[1],'click',closeHandler);
                
                addListener(vcodePic,'click',function(e){
                    if(e.preventDefault){
                        e.preventDefault();
                    }else{
                        e.returnValue = false;
                    }
                    popup.reloadVCode();
                });
                addListener(changeVCodePic,'click',function(e){
                    if(e.preventDefault){
                        e.preventDefault();
                    }else{
                        e.returnValue = false;
                    }
                    popup.reloadVCode();
                });
                
                var inputFocusHandler = function(e){
                    if(!e)e = window.event;
                    var target = e.target?e.target:e.srcElement;
                    removeCls(target.parentNode,'ayaccount-popuplogin-textbox-tip');
                    addCls(target.parentNode,'ayaccount-popuplogin-textbox-focus');
                    if(!target.nonuseraction){
                        clearError(target);
                        clearError(loginBtn);
                        clearError(bindBtn);
                    }else{
                        target.nonuseraction = false;
                    }
                    
                    if(target.getAttribute('autotip')){
                        if(target.value == target.getAttribute('autotip')){
                            target.value = '';
                        }
                    }
                };
                
                var inputKeyPressHandler = function(e){
                    if(!e)e = window.event;
                    var target = e.target?e.target:e.srcElement;
                    removeCls(target.parentNode,'ayaccount-popuplogin-textbox-tip');
                    addCls(target.parentNode,'ayaccount-popuplogin-textbox-focus');
                    clearError(target);
                    clearError(loginBtn);
                    clearError(bindBtn);
                };
                
                var inputBlurHandler = function(e){
                    if(!e)e = window.event;
                    var target = e.target?e.target:e.srcElement;
                    removeCls(target.parentNode,'ayaccount-popuplogin-textbox-focus');
                    
                    if(target.getAttribute('autotip')){
                        if(target.value == target.getAttribute('autotip') || target.value == ''){
                            target.value = target.getAttribute('autotip');
                            addCls(target.parentNode,'ayaccount-popuplogin-textbox-tip');
                        }
                    }
                };
                
                addListener(input_username,'focus',inputFocusHandler);
                addListener(input_username,'blur',inputBlurHandler);
                addListener(input_username,'keypress',inputKeyPressHandler);
                addListener(input_username,'keyup',function(e){
                    if(!e)e = window.event;
                    if(e.keyCode == '13'){
                        if(e.preventDefault){
                            e.preventDefault();
                        }else{
                            e.returnValue = false;
                        }
                        input_password.focus();
                    };
                });
                addListener(input_password,'focus',inputFocusHandler);
                addListener(input_password,'blur',inputBlurHandler);
                addListener(input_password,'keypress',inputKeyPressHandler);
                addListener(input_password,'keyup',function(e){
                    if(!e)e = window.event;
                    if(e.keyCode == '13'){
                        if(e.preventDefault){
                            e.preventDefault();
                        }else{
                            e.returnValue = false;
                        }
                        if(vcodeRow.style.display != 'none'){
                            input_vcode.focus();
                        }else{
                            popup.submit();
                        }
                    };
                });
                
                addListener(input_vcode,'focus',inputFocusHandler);
                addListener(input_vcode,'blur',inputBlurHandler);
                addListener(input_vcode,'keypress',inputKeyPressHandler);
                addListener(input_vcode,'keyup',function(e){
                    if(!e)e = window.event;
                    if(e.keyCode == '13'){
                        if(e.preventDefault){
                            e.preventDefault();
                        }else{
                            e.returnValue = false;
                        }
                        popup.submit();
                    };
                });
                
                addListener(input_mobile,'focus',inputFocusHandler);
                addListener(input_mobile,'blur',inputBlurHandler);
                addListener(input_mobile,'keypress',inputKeyPressHandler);
                addListener(input_mobile,'keyup',function(e){
                    if(!e)e = window.event;
                    if(e.keyCode == '13'){
                        if(e.preventDefault){
                            e.preventDefault();
                        }else{
                            e.returnValue = false;
                        }
                        input_mobile_vcode.focus();
                    };
                });
                
                addListener(input_mobile_vcode,'focus',inputFocusHandler);
                addListener(input_mobile_vcode,'blur',inputBlurHandler);
                addListener(input_mobile_vcode,'keypress',inputKeyPressHandler);
                addListener(input_mobile_vcode,'keyup',function(e){
                    if(!e)e = window.event;
                    if(e.keyCode == '13'){
                        if(e.preventDefault){
                            e.preventDefault();
                        }else{
                            e.returnValue = false;
                        }
                        popup.submitBind();
                    };
                });
                
                addListener(loginBtn,'click',function(e){
                    if(e.preventDefault){
                        e.preventDefault();
                    }else{
                        e.returnValue = false;
                    }
                    popup.submit();
                });
                
                addListener(bindBtn,'click',function(e){
                    if(e.preventDefault){
                        e.preventDefault();
                    }else{
                        e.returnValue = false;
                    }
                    popup.submitBind();
                });
                
                var verifyCodeTimer;
                var startVerifyCodeTimer = function(){
                    var timeout = 60;
                    
                    vcodeBtn.isPending = true;
                    addCls(vcodeBtn,'ayaccount-popuplogin-btn-sendvcode-disabled');
                    vcodeBtn.innerHTML = timeout + ' 秒后重发';
                    verifyCodeTimer = setInterval(function(){
                        timeout --;
                        vcodeBtn.innerHTML = timeout + ' 秒后重发';
                        if(timeout <=0){
                            stopVerifyCodeTimer();
                        }
                    },1000);
                };
                
                var stopVerifyCodeTimer = function(){
                    clearInterval(verifyCodeTimer);
                    removeCls(vcodeBtn,'ayaccount-popuplogin-btn-sendvcode-disabled');
                    vcodeBtn.innerHTML = '发送验证码';
                    vcodeBtn.isPending = false;
                };
                
                addListener(vcodeBtn,'click',function(e){
                    if(e.preventDefault){
                        e.preventDefault();
                    }else{
                        e.returnValue = false;
                    }
                    
                    if(vcodeBtn.isPending == true)return;
                    
                    clearError(input_mobile_vcode);
                    if(input_mobile.value == ''){
                        setError(input_mobile,'请输入手机号');
                        return;
                    }
                    
                    if(!input_mobile.value.match(/^1\d{10}$/)){
                        setError(input_mobile,'手机号输入有误');
                        return;
                    }
                    
                    startVerifyCodeTimer();
                    loadScript({
                        url:API.sendVerifyCodeURL + '?mobile=' + input_mobile.value,
                        success:function(){
                            if(window.__ay_sendmobileverifycode){
                                var data = window.__ay_sendmobileverifycode;
                                window.__ay_sendmobileverifycode = undefined;

                                if(data.status != 1){
                                    setError(bindBtn,data.msg || '手机验证码发送失败');
                                    if(data.status == 0){
                                        stopVerifyCodeTimer();
                                    }
                                };
                            }
                        }
                    });
                });
                
                
                addListener(window,'resize',function(){
                    popup.center();
                });
                if(isIE6){
                    addListener(window,'scroll',function(){
                        popup.center();
                    });
                }
            },
            setData:function(data){
                userData = data;
            },
            show:function(){
                container.style.display = 'block';
                overlay.style.display = 'block';
            },
            hide:function(){
                container.style.display = 'none';
                overlay.style.display = 'none';
            },
            reset:function(){
                clearError(input_username);
                clearError(input_password);
                clearError(input_vcode);
                clearError(input_mobile);
                clearError(input_mobile_vcode);
                input_username.value = '';
                if(input_username.getAttribute('autotip')){
                    input_username.value = input_username.getAttribute('autotip');
                    addCls(input_username.parentNode,'ayaccount-popuplogin-textbox-tip');
                }
                input_password.value = '';
                input_vcode.value = '';
                input_mobile.value = '';
                input_mobile_vcode.value = '';
            },
            reloadVCode:function(){
                var img = vcodePic.getElementsByTagName('img')[0];
                if(img.src){
                    img.src = img.src.replace(/\&timestamp\=\d*/,'&timestamp=' + (new Date()).getTime());
                }
            },
            setCallback:function(fn){
                callback = fn;
                //form.setAttribute('action',API.loginSubmitURL + '?reurl=' + encodeURIComponent(url));
            },
            center:function(){
                var winWidth = document.documentElement.clientWidth || document.body.clientWidth;
                var winHeight = document.documentElement.clientHeight || document.body.clientHeight;
                var winScrollLeft = document.documentElement.scrollLeft || document.body.scrollLeft;
                var winScrollTop = document.documentElement.scrollTop || document.body.scrollTop;
                
                var popupWidth = container.offsetWidth;
                var popupHeight = container.offsetHeight;
                if(!isIE6){
                    container.style.left = parseInt((winWidth - popupWidth)/2) + 'px';
                    container.style.top = parseInt((winHeight - popupHeight)/2) + 'px';
                }else{
                    container.style.left = (parseInt((winWidth - popupWidth)/2) + winScrollLeft) + 'px';
                    container.style.top = (parseInt((winHeight - popupHeight)/2) + winScrollTop) + 'px';
                }
            },
            showInfo:function(msg,iconCls){
                if(!iconCls)iconCls = '';
                if(!msg)msg = '数据读取中，请稍后...';
                var span = infoPanel.getElementsByTagName('span')[0];
                span.innerHTML = msg;
                span.className = iconCls;
                loginPanel.style.display = 'none';
                loginPanel.style.visibility = 'hidden';
                bindPanel.style.display = 'none';
                bindPanel.style.visibility = 'hidden';
                infoPanel.style.display = 'block';
                infoPanel.style.visibility = 'visible';
            },
            showLogin:function(token,vcodeURL){
                loginPanel.style.display = 'block';
                loginPanel.style.visibility = 'visible';
                bindPanel.style.display = 'none';
                bindPanel.style.visibility = 'hidden';
                infoPanel.style.display = 'none';
                infoPanel.style.visibility = 'hidden';
                if(token){
                    input_token.value = token;
                }
                if(vcodeURL){
                    vcodeRow.style.display = 'block';
                    vcodeRow.style.visibility = 'visible';
                    var img = vcodePic.getElementsByTagName('img')[0];
                    img.src = vcodeURL + '&timestamp=' + (new Date()).getTime();
                }else{
                    vcodeRow.style.display = 'none';
                    vcodeRow.style.visibility = 'hidden';
                }
                input_username.nonuseraction = true;
                input_username.focus();
            },
            showBind:function(token){
                loginPanel.style.display = 'none';
                loginPanel.style.visibility = 'hidden';
                bindPanel.style.display = 'block';
                bindPanel.style.visibility = 'visible';
                infoPanel.style.display = 'none';
                infoPanel.style.visibility = 'hidden';
                if(token){
                    input_bind_token.value = token;
                }
                input_mobile.nonuseraction = true;
                input_mobile.focus();
            },
            submit:function(){
                if(loginBtn.isLogging == true)return;
                
                clearError(loginBtn);
                
                input_username.value = trimString(input_username.value);
                if(input_username.value == '' || input_username.value == input_username.getAttribute('autotip')){
                    setError(input_username,'请输入用户名');
                    return;
                }
                
                if(!input_username.value.match(/^1\d{10}$|^[a-zA-Z][a-zA-Z0-9\._]{3,29}$|^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/)){
                    setError(input_username,'用户名输入有误');
                    return;
                }
                
                if(input_password.value == ''){
                    setError(input_password,'请输入密码');
                    return;
                }
                
                if(!input_password.value.match(/^.{6,20}$/)){
                    setError(input_password,'密码输入有误');
                    return;
                }
                
                if(vcodeRow.style.display != 'none' && input_vcode.value == ''){
                    setError(input_vcode,'请输入验证码');
                    return;
                }
                
                addCls(loginBtn,'ayaccount-popuplogin-loginbtn-logging');
                loginBtn.isLogging = true;
                
                waitForIframeData(iframe_login,function(data){
                    var data = eval('(' + data + ')');
                    removeCls(loginBtn,'ayaccount-popuplogin-loginbtn-logging');
                    loginBtn.isLogging = false;
                    if(data && data.status == 1){
                        if(callback instanceof Function){
                            popup.hide();
                            callback();
                        }else if(typeof(callback) == 'string'){
                            popup.hide();
                            window.location.href = callback;
                        }
                    }else{
                        if(data._vcode){
                            popup.showLogin(null,data._vcode);
                            popup.center();
                        }
                        popup.reloadVCode();
                        setError(loginBtn,data.msg || '登录失败');
                    }
                });
                
                form.submit();
            },
            submitBind:function(){
                if(bindBtn.isPending == true)return;
                
                clearError(bindBtn);
                
                if(input_mobile.value == ''){
                    setError(input_mobile,'请输入手机号');
                    return;
                }
                
                if(!input_mobile.value.match(/^1\d{10}$/)){
                    setError(input_mobile,'手机号输入有误');
                    return;
                }
                
                if(input_mobile_vcode.value == ''){
                    setError(input_mobile_vcode,'请输入验证码');
                    return;
                }
                
                if(!input_mobile_vcode.value.match(/^\d{6}$/)){
                    setError(input_mobile_vcode,'验证码输入有误');
                    return;
                }
                
                addCls(bindBtn,'ayaccount-popuplogin-bindbtn-binding');
                bindBtn.isPending = true;
                
                waitForIframeData(iframe_bind,function(data){
                    var data = eval('(' + data + ')');
                    removeCls(bindBtn,'ayaccount-popuplogin-bindbtn-binding');
                    bindBtn.isPending = false;
                    if(data && data.status == 1){
                        if(callback instanceof Function){
                            popup.hide();
                            callback();
                        }else if(typeof(callback) == 'string'){
                            popup.hide();
                            window.location.href = callback;
                        }
                    }else{
                        setError(bindBtn,data.msg || '绑定失败');
                    }
                });
                
                bindForm.submit();
            }
        };
        popup.init();
        
        popupWindow = popup;
        return popupWindow;
    };
/*=============================================================================================================*/       
    
    
    var pub = {
        login:login,
        renderUserPanel:renderUserPanel,
        doUserAction:doUserAction
    };
    
    return pub;
}();