/*---------------蓝色导航下拉菜单*/
function topnavbarStuHover() {
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
	var getElm = document.getElementById("topnavbar").getElementsByTagName("LI");
	for (var i=0; i<getElm.length; i++) {
		getElm[i].onmouseover=function() {
			this.className+=" iehover";
		}
		getElm[i].onmouseout=function() {
			this.className=this.className.replace(new RegExp(" iehover\\b"), "");
		}
	}
}
function checkAll() { 
	if ($("#checkedAll").attr("checked") == true) { // 全选 
		$("input[@name='selectID']").each(function() { 
			$(this).attr("checked", true); 
		}); 
	} else { // 取消全选 
		$("input[@name='selectID']").each(function() { 
			$(this).attr("checked", false); 
		}); 
	}
}
function ActiveCoolTable() {
	$('.cooltable tbody tr:even').addClass('odd');
	$('.cooltable tbody tr').hover(
		function() {$(this).addClass('highlight');},
		function() {$(this).removeClass('highlight');}
	);

	// 如果复选框默认情况下是选择的，变色.
	$('.cooltable input[type="checkbox"]:checked').parents('tr').addClass('selected');
	// 复选框
	$('.cooltable tbody tr td').click(
		function() {
			if (!$(this).hasClass('oper')) {
				if ($(this).parents('tr').hasClass('selected')) {
					$(this).parents('tr').removeClass('selected');
					$(this).parents('tr').find('input[type="checkbox"]').removeAttr('checked');
				} else {
					$(this).parents('tr').addClass('selected');
					$(this).parents('tr').find('input[type="checkbox"]').attr('checked','checked');
				}
			}
		}
	);
}
function checkAllLine() { 
	if ($("#checkedAll").attr("checked") == true) { // 全选 
		$('.cooltable tbody tr').each(
			function() {
				$(this).addClass('selected');
				$(this).find('input[type="checkbox"]').attr('checked','checked');
			}
		);
	} else { // 取消全选 
		$('.cooltable tbody tr').each(
			function() {
				$(this).removeClass('selected');
				$(this).find('input[type="checkbox"]').removeAttr('checked');
			}
		);
	}
}