package com.filter;

import javax.servlet.*;
import javax.servlet.annotation.WebFilter;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Enumeration;
import java.util.Map;
import java.util.Set;

@WebFilter(filterName = "SQLFilter")
public class SQLFilter implements Filter {
    private static String denyWord = "";
    public void destroy() {
    }

    public void doFilter(ServletRequest req, ServletResponse resp, FilterChain chain) throws ServletException, IOException {

        HttpServletRequest httpRequest = (HttpServletRequest) req;
        Enumeration<String> params = httpRequest.getParameterNames();
        StringBuilder sb = new StringBuilder();
        String xforwardedfor = "";
        while (params.hasMoreElements()){
            String paramName = params.nextElement();
            String paramValue = httpRequest.getParameter(paramName);
            sb.append(paramName);
            sb.append("=");
            sb.append(paramValue);
            sb.append("&");

        }
        xforwardedfor = "x-forwarded-for="+httpRequest.getHeader("x-forwarded-for");
        sb.append(xforwardedfor);
        if (sqlValidate(sb.toString())) {
            throw new ServletException("您发送请求中的参数中含有非法字符"+denyWord);
        } else {
            chain.doFilter(req, resp);
        }

    }

    public void init(FilterConfig config) throws ServletException {

        System.out.println("start");
    }

    //校验
    protected static boolean sqlValidate(String str) {
        str = str.toLowerCase();//统一转为小写
        String badStr = "'|and|exec|execute|insert|select|delete|update|count|drop|chr|mid|master|truncate|" +
                "char|declare|sitename|xp_cmdshell|like'|" +
                "table|from|grant|group_concat|column_name|" +
                "information_schema.columns|table_schema|union|where|order|by|count(";//过滤掉的sql关键字，可以自行增删//过滤掉的sql关键字，可以自行增删
        String[] badStrs = badStr.split("\\|");
        for (int i = 0; i < badStrs.length; i++) {
            if (str.indexOf(badStrs[i]) >= 0) {
                denyWord = badStrs[i];
                return true;
            }
        }
        return false;
    }

}
