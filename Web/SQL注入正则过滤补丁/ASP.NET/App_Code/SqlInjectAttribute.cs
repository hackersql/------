using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.SessionState;

/// <summary>
/// SqlInjectAttribute 的摘要说明
/// </summary>
public class SqlInjectAttribute:IHttpModule
{
    public String ModuleName
    {

        get { return "MyExampleFilter"; }

    }

    public void Dispose()
    {
        //此处放置清除代码。  
    } 


    // In the Init function, register for HttpApplication 

    // events by adding your handlers.

    public void Init(HttpApplication application)
    {

        application.AcquireRequestState += new EventHandler(Application_AcquireRequestState);

    }



    private void Application_AcquireRequestState(Object source,

        EventArgs e)
    {

        HttpApplication application = (HttpApplication)source;

        HttpContext context = application.Context;

        HttpSessionState session = context.Session;

        HttpRequest request = context.Request;

        HttpResponse response = context.Response;

        String contextPath = request.ApplicationPath;
        String paramStr = "";
        String method = request.HttpMethod;
        String xforwardfor = "X-Forwarded-For=" + request.Params["HTTP_X_FORWARDED_FOR"];
        if (!string.IsNullOrEmpty(request.Form.ToString()))
        {
            for (int i = 0; i < request.Form.Count; i++)
            {
                paramStr += request.Form.Keys[i].ToString().ToLower().Trim() + " = " + request.Form[i].ToString().ToLower().Trim()+"&";
            }
        }
        if (!string.IsNullOrEmpty(request.QueryString.ToString()))
        {
            paramStr += request.QueryString.ToString().ToLower().Trim()+"&";
        };
        paramStr += xforwardfor;
        if (sqlValidate(paramStr))
        {
            response.Redirect("~");
        }
        
    }

    public Boolean sqlValidate(String param)
    {
        if (string.IsNullOrEmpty(param)) { return false; }
        param = param.Trim().ToLower();
        String badStr = "'|and|exec|execute|insert|select|delete|update|count|drop|chr|mid|master|truncate|" +
                "char|declare|sitename|xp_cmdshell|like'|" +
                "table|from|grant|group_concat|column_name|" +
                "information_schema.columns|table_schema|union|where|order|by|count(|(|)|{";//过滤掉的sql关键字，可以自行增删
        String[] badStrs = badStr.Split('|');
        foreach(string b in badStrs){
            if (param.IndexOf(b)>=0)
            {
                return true;
            }
        }

        return false;
    }
}