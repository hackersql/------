
/**
 * cookie瀵硅薄
 * @class cookie瀵硅薄
 * @param 
 * @type object
 */
Cookie={};

/**
 * cookie瀵硅薄鐨剆et鏂规硶
 * @requires cookie
 * @param indexName,value,savedays
 * @type void
 */
Cookie.del=function(name)//鍒犻櫎cookie
{
var exp = new Date();
exp.setTime(exp.getTime() - 1);
var cval=Cookie.get(name);
if(cval) document.cookie= name + "="+cval+";expires="+exp.toGMTString();
};

Cookie.set=function(name, value,savedays){
try
{
if(!value)
{
	return Cookie.del(name);
}
if(value.toString().length>1000)
	{
	return '';
	}
if(!savedays)
{
savedays=365;
}
var exp   = new Date();
var ct=exp.getTime();
var pt=new Date(exp.getYear(),exp.getMonth(),exp.getDate()).getTime();
exp.setTime(exp.getTime() + savedays*24*60*60*1000-(ct-pt));
document.cookie = name + "="+ escape (value) + ";expires=" + exp.toGMTString();
}
catch(e)
{
}

};
/**
 * cookie瀵硅薄鐨刧et鏂规硶
 * @requires cookie
 * @param indexName
 * @type void
 */
Cookie.get=function(name){
try
{
var arr = document.cookie.match(new RegExp("(^| )"+name+"=([^;]*)(;|$)"));
    if(arr) return unescape(arr[2]); return '';
}
catch(e)
{
}
};