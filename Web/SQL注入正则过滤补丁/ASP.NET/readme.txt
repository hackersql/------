1.将App_Code文件夹复制到ASP.Net项目根目录
2.在Web.config中进行配置。先查看该文件中是否有modules标签，如果有，直接在其中添加<add name="MyExampleModule" type="SqlInjectAttribute"/>；
如果没有modules标签，在system.web标签中添加如下代码：
<modules>
      <add name="MyExampleModule" type="SqlInjectAttribute"/>
</modules>
3.过滤的关键字可以自己修改，response.Redirect("~")是返回到首页，可以自己修改重定向到其他页面。
