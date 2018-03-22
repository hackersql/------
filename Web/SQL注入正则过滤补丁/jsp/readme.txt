1.SQLFilter.java为过滤的源文件。可自行对SQL过滤的关键字进行修改。放在自己项目源码中进行编译。（路径不一致的时候请修改包名）
2.SQLFilter.class为编译后的文件，如果不想修改（修改的话对SQLFilter.java进行修改）放在项目web目录/WEB-INF/classes/com/filter/下。
3.修改web.xml。新增如下代码。
    <filter>
        <filter-name>SQLFilter</filter-name>
        <filter-class>com.filter.SQLFilter</filter-class>
    </filter>
    <filter-mapping>
        <filter-name>SQLFilter</filter-name>
        <url-pattern>/*</url-pattern><!-- 这里是针对所有的请求都进行过滤 -->
    </filter-mapping>
    <welcome-file-list>
