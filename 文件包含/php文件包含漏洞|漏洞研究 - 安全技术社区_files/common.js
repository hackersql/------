var AYSW = new Object;
$(function(){
	if($.browser.msie && parseInt($.browser.version) == 6){
		$('.aysw-header nav ul li').hover(function(e){
			$(e.currentTarget).addClass('aysw-hover');
		},function(e){
			$(e.currentTarget).removeClass('aysw-hover');
		});

		$('.aysw-header-topnav-dropdown').hover(function(e){
			$(e.currentTarget).addClass('aysw-header-topnav-dropdown-hover');
		},function(e){
			$(e.currentTarget).removeClass('aysw-header-topnav-dropdown-hover');
		});
	}

	var suffix = window.location.host.replace(/^.*\.aliyun/i,'');
	var blackList = [
        'finance.aliyun',
        'bbs.aliyun',
        'event.aliyun',
        'lingyun.aliyun',
        'blog.aliyun',
        'os.aliyun',
        'i.aliyun',
        'cp.aliyun',
        'login.aliyun',
        'account.aliyun',
        'member.aliyun',
        'control.aliyun',
        'workorder.aliyun',
        'www.aliyun'+ suffix +'/about',
        'www.aliyun'+ suffix +'/law',
        'www.aliyun'+ suffix +'/sitemap',
        'www.aliyun'+ suffix +'/links',
        'www.aliyun'+ suffix +'/eco',
        'account.www.net.cn',
        'market.aliyun'+ suffix +'/user/',
        'buy.aliyun'+ suffix +'/trial'
    ];
	var inBlackList = false;
	var url = window.location.href.replace(/https\:\/\/|http\:\/\//,'');
	for(var i=0,len=blackList.length;i<len;i++){
		if(url.indexOf(blackList[i]) == 0){
			inBlackList = true;
		}
	}
	//ransiwei window.__preSales 为访问售前机器人的url
	//AYSW.renderPreSales();
	if(!inBlackList){
		AYSW.renderQuickSupport();
	}
});
AYSW.renderPreSales = {};
AYSW.renderQuickSupport = function(){
	
	var dockStatus = 'fold';//默认折叠, 小窗口生效
	var rendered = false;
	var win = $(window);
	var doc = $(document);
	var suffix = window.location.host.replace(/^.*\.aliyun/i,'');
	if(!suffix)suffix = '.dev';
	var pub = function(){
		if(rendered)return;
		rendered = true;
		var sec_key = window.location.href.match(/sec_key\=[^&]*/);
		if(!sec_key){
			sec_key = '?cache=20130626';
		}else{
			sec_key = '?' + sec_key+'&cache=20130626';
		}
		loadScript({
			url:'//www.aliyun' + suffix + '/user/livechat/gettaobaotools' + sec_key,
			success:function(){
				if(window.__ay_taobao_tools){
					render(window.__ay_taobao_tools.source,window.__ay_taobao_tools.html);
				}
			}
		});



	}
	AYSW.renderPreSales=function(){
                //根据不同的URL传递不同的参数

                var URL_CFG=[{
                            "url":new RegExp("(www\\.aliyun\\"+suffix+"\/$)","ig"),
                            "prm":"www_index"
                        },{
                            "url":new RegExp("(www\\.aliyun\\"+suffix+"\/product\/$)|(www\\.aliyun\\"+suffix+"\/product\/ecs\/$)","ig"),
                            "prm":"www_product_ecs"
                        },{
                            "url":new RegExp("(www\\.aliyun\\"+suffix+"\/product\/rds\/$)","ig"),
                            "prm":"www_product_rds"
                        },{
                            "url":new RegExp("(www\\.aliyun\\"+suffix+"\/product\/oss\/$)","ig"),
                            "prm":"www_product_oss"
                        },{
                            "url":new RegExp("(www\\.aliyun\\"+suffix+"\/product\/slb\/$)","ig"),
                            "prm":"www_product_slb"
                        },{
                            "url":new RegExp("(www\\.aliyun\\"+suffix+"\/product\/yundun\/$)","ig"),
                            "prm":"www_product_yundun"
                        },{
                            "url":new RegExp("(www\\.aliyun\\"+suffix+"\/product\/jiankong\/$)","ig"),
                            "prm":"www_product_jiankong"
                        },{
                            "url":new RegExp("(www\\.aliyun\\"+suffix+"\/act\/webbaindex\\.html$)","ig"),
                            "prm":"www_act_webbaindex"
                        },{
                            "url":new RegExp("(buy\\.aliyun\\"+suffix+"\/$)","ig"),
                            "prm":"buy_index"
                        },{
                            "url":new RegExp("(www\\.aliyun\\"+suffix+"\/product\/odps\/$)","ig"),
                            "prm":"www_product_odps"
                        },{
                            "url":new RegExp("(www\\.aliyun\\"+suffix+"\/product\/ots\/$)","ig"),
                            "prm":"www_product_ots"
                        },{
                            "url":new RegExp("(www\\.aliyun\\"+suffix+"\/product\/ace\/$)","ig"),
                            "prm":"www_product_ace"
                        },{
                            "url":new RegExp("(market\\.aliyun\\"+suffix+"\/$)","ig"),
                            "prm":"market_index"
                        },{
                            "url":new RegExp("(www\\.aliyun\\"+suffix+"\/partner\/index\\.html$)","ig"),
                            "prm":"www_partner_index"
                        },{
                            "url":new RegExp("(awdc\\.aliyun\\"+suffix+"\/$)","ig"),
                            "prm":"awdc_index"
                        }];
                    var params="";
                    for(var i=0,ii=URL_CFG.length;i<ii;i++){

                        if(URL_CFG[i].url.test(window.location.href.split("?")[0])){
                            params="?scence="+URL_CFG[i].prm ;
                            break;
                        }
                    }
					//当页面htpp协议为https则不执行，因为ie会弹出安全警告
				if(!window.__preSales && window.location.protocol!="https:"){

					loadScript({
					url:"http://help.aliyun"+suffix+"/robot/init"+params,
					success:function(){
						if(window.__retConfig && window.__retConfig.pre_sales && window.__retConfig.new_sales){
				 			window.__preSales = window.__retConfig.pre_sales.robotUrl;
				 			//增加一个售后咨询入口 ransiwei20130129
				 			window.__newSales = window.__retConfig.new_sales.robotUrl;
						}
							}
						})
					}
	}
	var render = function(status,html){
		return;//20130812 弃用快速帮助条
		if(!html)html = '';
		var baseY = 185;
		var pagebody = $('.aysw-body');
		var panel = $(html.presales?html.presales.content:'');

		panel.find('a[chatlink=true]').each(function(index,el){
			var sourceId = el.getAttribute('chatid');
			var $el = $(el);
			var online = status[sourceId];
			if(!online){
				if($el.hasClass('aysw-quicksupport-livechatbtn')){
					$el.addClass('aysw-quicksupport-livechatbtn-disabled');
				}else{
					$el.addClass('aysw-disabled');
				}
			}
			$el.click(function(e){
				e.preventDefault();
				AYSW.liveChat(sourceId);
			});
		});
		//点击事件
		panel.find('.aysw-quicksupport-header').click(function(e){
			e.preventDefault();
			if(!panel.hasClass('aysw-quicksupport-mini')){
				return;
			}
			dockStatus = dockStatus === 'fold' ? 'unfold' : 'fold';
			panel.toggleClass('aysw-quicksupport-fold');
		})

		$(document.body).append(panel);
		//ie6\7下iconfont
		if(($.browser.msie&&$.browser.version=="6.0")||($.browser.msie&&$.browser.version=="7.0")){

			var _addIcon= function(el, entity) {
				el.each(function(index,element){
						var html = element.innerHTML;
						element.innerHTML = '<span style="font-family: \'icomoon\'">' + entity + '</span>' + html;
					});


			}
			var el=$(".aysw-quicksupport-body .icon-dialog2");
			var el1=$(".aysw-quicksupport-body .icon-customers");
			_addIcon(el, "&#x65;");
			_addIcon(el1, "&#x5b;");

		}

		//setQSPosition(false);
		//win.bind('resize',windowChangeHandler);
		//win.bind('scroll',windowChangeHandler);

		var delayTimer;

		function windowChangeHandler(){
			clearTimeout(delayTimer);
			delayTimer = setTimeout(setQSPosition,50);
		}

		function setQSPosition(animated){
			if(animated !== false)animated = true;

			var bodyCoord = pagebody.offset();
			var bodyWidth = pagebody.outerWidth();
			var bodyHeight = pagebody.outerHeight();
			var panelWidth,panelHeight;

			if(dockStatus === 'fold'){
				panelWidth = 100;
				panelHeight = 377;
			}else{
				panelWidth = panel.outerWidth();
				panelHeight = panel.outerHeight();
			}
			var scrollTop = doc.scrollTop();
			var scrollLeft = doc.scrollLeft();
			var baseX = pagebody.innerWidth() + bodyCoord.left + 20;
			var baseY = bodyCoord.top;
			var maxX = win.width() - panelWidth + scrollLeft;
			var maxY = bodyCoord.top + bodyHeight - panelHeight;
			if(maxY < baseY){
				maxY = baseY;
			}
			var y;
			var x;
			if(scrollTop + 10 > baseY){
				y = scrollTop + 10 + 'px';
			}else{
				y = baseY + 'px';
			}

			if(scrollTop + 10 > maxY){
				y = maxY + 'px';
			}

			if(baseX < maxX){
				winDockHandler(panel, false);
				x = baseX + 'px';
			}else{
				winDockHandler(panel, true);
				x = maxX + 'px';
			}

			if(animated && jQuery.easing && jQuery.easing.easeOutCirc){
				panel.stop();
				panel.animate({
					top:y,
					left:x
				},500,'easeOutCirc');
			}else{
				panel.css({
					top:y,
					left:x
				});
			}
		}
	}

	function winDockHandler(panel, min){
		if(min){
			if(!panel.hasClass('aysw-quicksupport-mini')){
				panel.addClass('aysw-quicksupport-mini');
			}
			if(dockStatus === 'fold'){
				if(!panel.hasClass('aysw-quicksupport-fold')){
					panel.addClass('aysw-quicksupport-fold');
				}
			}else{
				if(panel.hasClass('aysw-quicksupport-fold')){
					panel.removeClass('aysw-quicksupport-fold');
				}
			}
		}else{
			if(panel.hasClass('aysw-quicksupport-mini')){
				panel.removeClass('aysw-quicksupport-mini');
			}
			if(panel.hasClass('aysw-quicksupport-fold')){
				panel.removeClass('aysw-quicksupport-fold');
			}
		}
	}
	function loadScript(params){
		var ua = navigator.userAgent.toLowerCase();
		var isIE = ua.match(/msie ([\d.]+)/);
		var isIE6 = isIE && isIE[1] && parseInt(isIE[1]) == 6 ? true : false;

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

	return pub;
}();



AYSW.liveChat = function(sourceId){
	var suffix = window.location.host.replace(/^.*\.aliyun/i,'');
	var _windowScreen = window.screen;
	if(!suffix)suffix = '.dev';

	var url = '//www.aliyun' + suffix + '/user/livechat/gettaobaotokenurl?sourceid=';
	var winWidth = 950;
	var winHeight = 500;
	var left = parseInt((_windowScreen.width - winWidth)/2);
	var top = parseInt((_windowScreen.height - winHeight)/2);
	// if(window.__preSales && sourceId=="1225141032"){
	// 	window.open(window.__preSales,'阿里云','height=' + winHeight + ',width=' + winWidth + ',left=' + left + ',top=' + top + ',toolbar=no,menubar=no,scrollbars=no, resizable=no,location=no, status=no')
	// }else 
	if(window.__newSales && sourceId=="1217141509"){//增加一个售后咨询入口 ransiwei20130129
		window.open(window.__newSales,'阿里云','height=' + winHeight + ',width=' + winWidth + ',left=' + left + ',top=' + top + ',toolbar=no,menubar=no,scrollbars=no, resizable=no,location=no, status=no')
	}
	else{
		window.open(url + sourceId,'dialog_' + sourceId + '_' + parseInt(Math.random()*10000000),'height=' + winHeight + ',width=' + winWidth + ',left=' + left + ',top=' + top + ',toolbar=no,menubar=no,scrollbars=no, resizable=no,location=no, status=no');
	}
}


AYSW.renderImageLazyLoad = function(){
	var rendered = false;

	var pub = function(){
		if(rendered)return;
		rendered = true;

		var images = $('img.c-lazyload');
		var loadedImageNum = 0;
		Alipw.getWin().bind('resize',checkImage);
		Alipw.getWin().bind('scroll',checkImage);
		checkImage();

		function checkImage(){
			if(loadedImageNum >= images.length){
				Alipw.getWin().unbind('resize',checkImage);
				Alipw.getWin().unbind('scroll',checkImage);
				return;
			}

			var scrollTop = Alipw.getDoc().scrollTop();
			var winHeight = Alipw.getWin().height();
			images.each(function(i,el){
				var $el = $(el);
				var src = $el.attr('image-src');
				if(src && $el.offset().top - scrollTop < winHeight){
					$el.attr('src',src);
					$el.removeAttr('image-src');
					loadedImageNum ++;
				};
			});
		}
	}

	return pub;
}();


AYSW.renderToolTip = function(){
	$(function(){
		var elements = $('.c-tooltip');
		if(elements[0]){
			Alipw.importClass('Alipw.ToolTip');
			Alipw.onReady(function(){
				elements.each(function(i,el){
					var $el = $(el);
					var width = $el.attr('tipwidth');
					if(width){
						width = parseInt(width);
					}else{
						width = null;
					}

					var html = $el.find('.tipcontent').html();
					var tooltip = new Alipw.ToolTip({
						target:el,
						html:html,
						width:width
					});
				});
			});
		}
	});
}

AYSW.hiliteNavItem = function(name){
	$('.aysw-header nav li.aysw-nav-' + name).addClass('aysw-current');
}





//11.11 promotion
/*
AYSW.renderPromotion1111 = function(){
	var whiteList = [
		'www.aliyun',
		'buy.aliyun',
		'i.aliyun',
		'market.aliyun'
	];
	var inWhiteList = false;
	var url = window.location.href.replace(/https\:\/\/|http\:\/\//,'');
	for(var i=0,len=whiteList.length;i<len;i++){
		if(url.indexOf(whiteList[i]) == 0){
			inWhiteList = true;
		}
	}
	if(!inWhiteList)return;

	var suffix = function(){
		if(window.location.host.indexOf('aliyun.') == -1)return '.com';
		var output =  window.location.host.replace(/^.*\.aliyun/i,'');
		if(!output)output = '.com';
		return output;
	}();
	var startTime = new Date('2012/11/10 23:00:00');
	var endTime = new Date('2012/11/12 23:59:59');

	loadScript({
		url:'http://www.aliyun' + suffix + '/promotion/ajaxcomm/getservertime?json=p',
		success:function(){
			if(window.__ay_server_time){
				render(new Date(parseInt(window.__ay_server_time) * 1000));
			}
		}
	});

	function render(currentTime){
		//currentTime = 1352559580000; //'2012/11/10 22:59:40'未开始
		//currentTime = 1352735980000; //'2012/11/12 23:59:40'已开始
		//currentTime = 1352736040000; //'2012/11/13 00:00:40'已结束

		if(currentTime >= endTime)return;

		var linkURL = 'http://www.aliyun.com/act/1111.html';
		if(window.location.host.indexOf('i.aliyun.') != -1){
			$('#header #logo').css('position','relative').css('padding','13px 0').append('<div id="aysw-counter-1111-i" style="position:absolute; left:130px; top:0; width:310px; height:70px; cursor:pointer; background:#FFF; text-align:left;"><div class="aysw-counter-1111"></div></div>');
			$('#header #logo a').attr({
				'href':linkURL,
				'target':'_blank'
			});
			$('#aysw-counter-1111-i').click(function(){
				$('#header #logo a')[0].click();
			});
			renderTo($('#header #logo .aysw-counter-1111'),currentTime);
			$('.aysw-logo').parent().attr({
				href:linkURL,
				target:'_blank'
			});
		}else{
			$('<a id="aysw-banner-1111" href="' + linkURL + '" target="_blank" style=" display:block; width:940px; height:40px; clear:both; margin:0 auto;"><img style="display:block; clear:both; margin:0 auto;" width="940" height="40" src="//static.aliyun' + suffix + '/images/www-summerwind/banner_11_11.jpg" /></a>').insertBefore($('.aysw-header'));
			$('.aysw-logo').css('position','relative').append('<div style="position:absolute; left:140px; top:0; width:310px; height:70px; cursor:pointer; background:#FFF; text-align:left;"><div class="aysw-counter-1111"></div></div>');
			renderTo($('.aysw-logo .aysw-counter-1111'),currentTime);
			//IE6/7 BUG
			$('<div style="clear:both; height:0; overflow:hidden; font-size:0; line-height:0;"></div>').insertBefore($('header nav ul'));
			$('.aysw-logo').parent().attr({
				href:linkURL,
				target:'_blank'
			});
		}
	}

	function renderTo(container,currentTime){
		var el = $('<div style="width:310px; height:70px;background:url(//static.aliyun' + suffix + '/images/www-summerwind/counter_11_11.jpg) 0 -5px"><div class="aysw-counter-1111-counter" style="position:absolute; left:190px; top:22px; width:70px; height:30px; text-align:center; font-size:12px; color:#333; font-weight:normal; line-height:120%;"></div></div>');
		var counterContainer = el.find('.aysw-counter-1111-counter');

		var counterTime;
		if(currentTime < startTime){
			counterTime = getHMS(startTime - currentTime);
			renderCounter(counterContainer,counterTime[0],counterTime[1],counterTime[2],function(){
				el.css('background-position','0 -100px');
				var hms = getHMS(endTime - startTime);
				counterContainer.empty();
				renderCounter(counterContainer,hms[0],hms[1],hms[2],removeCounter);
			});
		}else{
			el.css('background-position','0 -100px');
			counterTime = getHMS(endTime - currentTime);
			renderCounter(counterContainer,counterTime[0],counterTime[1],counterTime[2],removeCounter);
		}

		container.append(el);
	}

	function renderCounter(container,h,m,s,callback){
		var el = $('<span class="aysw-counter-1111-h" style="font-size:14px; color:red;"></span><span style="font-size:12px">小时</span><br /><span class="aysw-counter-1111-m" style="font-size:14px; color:red"></span><span style="font-size:12px">分</span><span class="aysw-counter-1111-s" style="font-size:12px; color:red"></span><span style="font-size:12px">秒</span>');
		var hEl = el.filter('.aysw-counter-1111-h');
		var mEl = el.filter('.aysw-counter-1111-m');
		var sEl = el.filter('.aysw-counter-1111-s');
		updateTime();

		container.append(el);

		var timer = setInterval(function(){
			var time = h * 3600000 + m * 60000 + s * 1000;
			var hms;
			time -= 1000;
			if(time == 0){
				clearInterval(timer);
				if(callback instanceof Function){
					callback.call();
				}
			}else{
				hms = getHMS(time);
				h = hms[0];
				m = hms[1];
				s = hms[2];
				updateTime();
			}
		},1000);

		function updateTime(){
			hEl.text(h);
			mEl.text(m);
			sEl.text(s);
		}
	}

	function removeCounter(){
		if(window.location.host.indexOf('i.aliyun.') != -1){
			$('#logo #aysw-counter-1111-i').remove();
			$('#logo').css({
				'padding':'',
				'position':''
			});
			$('#header #logo a').attr({
				'href':'//i.aliyun.com',
				'target':'_self'
			});
		}else{
			$('.aysw-logo').empty().parent().attr({
				href:'http://www.aliyun.com',
				target:'_self'
			});
			$('#aysw-banner-1111').remove();
		}
	}

	function getHMS(date){
		var h = parseInt(date/3600000);
		var m = parseInt((date % 3600000) / 60000);
		var s = parseInt((date - h * 3600000 - m * 60000)/1000);
		return [h,m,s];
	}

	function loadScript(params){
		var ua = navigator.userAgent.toLowerCase();
		var isIE = ua.match(/msie ([\d.]+)/);
		var isIE6 = isIE && isIE[1] && parseInt(isIE[1]) == 6 ? true : false;

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
};
*/
