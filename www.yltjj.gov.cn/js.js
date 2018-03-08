function register() {
    var isNull = /^[\s'　']*$/
    var reg = new RegExp("^([a-zA-Z0-9]+[_|\-|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\-|\.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$");
    var passReg = new RegExp("^[a-zA-Z0-9]{6,12}$");
    var cardReg = /^(\d{18,18}|\d{15,15}|\d{17,17}x)$/
    var loginid = $("#txtLoginID").val();
    var pwd = $("#txtPwd").val();
    var okpwd = $("#txtOkPwd").val();
    var realname = $("#txtRealname").val();
    var cardno = $("#txtCardNo").val();
    var email = $("#txtEmail").val();
    var tel = $("#txtTel").val();
    var question = $("#txtQuestion").val();
    var answer = $("#txtAnswer").val();
    var ispass = $("#hdCheckReg").val();
    if (isNull.test(loginid)) {
        alert("请输入登录用户名！");
        $("#txtLoginID").focus();
        return false;
    }
    if (isNull.test(pwd) || !passReg.test(pwd)) {
        alert("请输入密码，密码长度为6-12位数字或字母任意组合！");
        $("#txtPwd").focus();
        return false;
    }
    if (pwd != okpwd) {
        alert("密码输入不一致，请重新输入！");
        $("#txtOkPwd").focus();
        return false;
    }
    if(isNull.test(realname))
    {
        alert("请收入真实姓名！");
        $("#txtRealname").focus();
        return false;
    }
    if(!isNull.test(cardno) & !cardReg.test(cardno))
    {
        alert("请收入有效的身份证号(15位或18位)！");
        $("#txtCardNo").focus();
        return false;
    }
    if (!isNull.test(email) & !reg.test(email)) {
        alert("请输入正确格式的邮箱！");
        $("#txtEmail").focus();
        return false;
    }
    if(isNull.test(question))
    {
        alert("请收入密码提示问题！");
        $("#txtQuestion").focus();
        return false;
    }
    if(isNull.test(answer))
    {
        alert("请收入密码提示答案！");
        $("#txtAnswer").focus();
        return false;
    }
    if (isNull.test(ispass) || ispass == "1") {
        $("#msg").html("<font color=\"red\">该账号已经被注册！</font>");
        $("#txtLoginID").focus();
        return false;
    }
    $.ajax({
        type: "get",
        datatype: "html",
        data: "oper=register&LoginID=" + escape(loginid) + "&Pwd=" + pwd +"&RealName="+escape(realname)+"&CardNo="+cardno+"&Email=" + email +"&Tel="+tel+"&Question="+escape(question)+"&Answer="+escape(answer)+ "&date=" + (new Date().getDate()),
        url: "/ajax.aspx",
        success: function(d) {
            if (d == "success") {
                alert("注册成功！");
                location = "/login.aspx";
            } else if (d == "fail") {
                alert("注册失败！");
            } else {
                alert("注册异常！");
                location = "/register.aspx";
            }
        }
    });
}

function checkRegister() {
    var isNull = /^[\s'　']*$/
    var loginid = $("#txtLoginID").val();
    if (isNull.test(loginid)) {
        return false;
    } else {
    $.ajax({
        type: "get",
        datatype: "html",
        data: "oper=checkRegister&LoginID=" + escape(loginid) + "&date=" + (new Date().getDate()),
        url: "/ajax.aspx",
        success: function(d) {
            if (d == "success") {
                $("#msg").html("<font color=\"blue\">√</font>");
                $("#hdCheckReg").val("0");
            } else {
                $("#msg").html("<font color=\"red\">该账号已经被注册！</font>");
                $("#hdCheckReg").val("1");
            }
        }
    });
    }
}


     $(document).ready(function(){
        if(getCookie("ULogin")!=null)
        {
            var _htm="<table width=\"413\">";
            _htm+="        <tr>";
            _htm+="           <td>欢迎"+getNetCookie("ULogin","LoginID")+"，登录</td>";
            _htm+="           <td>[<a href=\"javascript:void(0)\" onclick=\"login_out()\">退出]</a></td>";
            _htm +="      </tr>";
            _htm+="</table>";
            $("#d_login").html(_htm);
        }
     });  

function checkLogin()
{
    var isNull = /^[\s'　']*$/
    var uloginid=$("#txtULoginID").val();
    var upass = $("#txtPass").val();
    if(isNull.test(uloginid) & isNull.test(upass)){
        alert("请输入登录帐号！");
        $("#txtULoginID").focus();
        return false;
    }
    if(isNull.test(uloginid)){
         alert("请输入登录密码！");
        $("#txtPass").focus();
        return false;
    }
    $.ajax({
        type:       "get",
        datatype:   "html",
        data:       "oper=login&uloginid="+escape(uloginid)+"&upass="+upass+"&date="+(new Date().getDate()),
        url:        "/ajax.aspx",
        success:    function(d){
            if (d == "success") {
                var _html="<table width=\"413\">";
                _html+="        <tr>";
                _html+="           <td>欢迎 "+getNetCookie("ULogin","LoginID")+"，登录！</td>";
                _html+="           <td>[<a href=\"javascript:void(0)\" onclick=\"login_out()\">退出]</a></td>";
                _html +="      </tr>";
                _html+="</table>";
               $("#d_login").html(_html);
            } else if(d=="fail"){
                alert("用户名或密码错误！");
            }else if(d=="nopass"){
                alert("该帐号也被禁用！");
            }
        }
    });
}

function checkLogin2()
{
    var isNull = /^[\s'　']*$/
    var uloginid=$("#txtULoginID").val();
    var upass = $("#txtPass").val();
    if(isNull.test(uloginid) & isNull.test(upass)){
        alert("请输入登录帐号！");
        $("#txtULoginID").focus();
        return false;
    }
    if(isNull.test(uloginid)){
         alert("请输入登录密码！");
        $("#txtPass").focus();
        return false;
    }
    $.ajax({
        type:       "get",
        datatype:   "html",
        data:       "oper=login&uloginid="+escape(uloginid)+"&upass="+upass+"&date="+(new Date().getDate()),
        url:        "/ajax.aspx",
        success:    function(d){
            if (d == "success") {
                location="/";
            } else if(d=="fail"){
                alert("用户名或密码错误！");
            }else if(d=="nopass"){
                alert("该帐号不可用！");
            }
        }
    });
}

function login_out()
{
    var url = window.location.href;
    if(getCookie("ULogin")!=null)
    {
        delCookie("ULogin")
    }
    window.location.href=url;
}

function getQuestion()
{
    var isNull = /^[\s'　']*$/
    var uid = $("#txtUserID").val();
    $.ajax({
        type:         "get",
        datatype:  "html",
        data:         "oper=ajaxGetQuestion&LoginID="+escape(uid)+"&cdate="+(new Date().getDate()),
        url:            "/ajax.aspx",
        success:    function(d){
            if(d=="error")
            {
                alert("该用户名不存在");
                return false;
            }
            else if(d=="error_1")
            {
                alert("对不起您没有设置密保");
            }
            else{
                $("#txtQuestion").val(d);
            }
        }
    })
}

function findPass()
{
    var isNull = /^[\s'　']*$/
    var uid = $("#txtUserID").val();
    var question = $("#txtQuestion").val();
    var answer = $("#txtAnswer").val();
    var newpass = $("#txtPwd").val();
    var newp = $("#txtP").val();
    if(isNull.test(uid))
    {
        alert("请先输入用户名！");
        $("#txtUserID").focus();
        return false;
    }
    if(isNull.test(question))
    {
        alert("密保问题不能为空！");
        return false;
    }
    if(isNull.test(answer))
    {
        alert("请输入问题答案！");
        $("#txtAnswer").focus();
        return false;
    }
    if(isNull.test(newpass))
    {
        alert("请输入新密码！");
        $("#txtPwd").focus();
        return false;
    }
    if(newp!=newpass)
    {
        alert("新密码输入不一致！");
        $("#txtP").focus();
        return false;
    }
    $.ajax({
        type:         "get",
        datatype:  "html",
        data:         "oper=ajaxUpdatePass&LoginID="+escape(uid)+"&Answer="+escape(answer)+"&Pass="+newpass+"&cdate="+(new Date().getDate()),
        url:            "/ajax.aspx",
        success:    function(d){
            if(d=="true")
            {
                alert("密码修改成功！");
                $("#d_pass").toggle("slow");
            }else if(d=="error"){
                alert("密保答案错误！");
            }else{
                alert("密码修改失败！");
            }
        }
    })
}


function getCookie(name) {
    var bikky = document.cookie;
    name += "=";
    var i = 0;
    while (i < bikky.length) {
        var offset = i + name.length;
        if (bikky.substring(i, offset) == name) {
            var endstr = bikky.indexOf(";", offset);
            if (endstr == -1) endstr = bikky.length;
            return unescape(bikky.substring(offset, endstr));
        }
        i = bikky.indexOf(" ", i) + 1;
        if (i == 0) break;
    }
    return null;
}
//获取cookie集合中的cookie的值
function getNetCookie(bigname, smallname) {
    var re = new RegExp("(\;|^)[^;]*(" + bigname + ")\=([^;]*)(;|$)");
    var match = re.exec(document.cookie);
    if (match) {
        var cookieValue = match != null ? match[3] : null;
        var reg = new RegExp("(^|&*)" + smallname + "=([^&]*)(&|$)");
        var r = cookieValue.match(reg);
        if (r != null) return r[2];
    }
    return null;
}

//删除cookie
function delCookie(name)//删除cookie
{
    var exp = new Date();
    exp.setTime(exp.getTime() - 10000);
    var cval = getCookie(name);
    if (cval != null) document.cookie = name + "=" + cval + ";expires=" + exp.toGMTString() + ";path=/";
}