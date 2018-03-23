<h1>git tag记录</h1>


标签

看别人的github上都有标签，一个标签可以代表在特定时间在项目里加入了重要的功能。
一般情况下，使用标签来标记发行版本，比如　v1.0 .

<h2>显示标签</h2>

输入　git tag 可以直接显示所有的标签。

<pre>
tiankonguse@tiankonguse:~/github/empty$ git tag
v1.0
</pre>

当标签很多的时候，可以使用　-l 参数搜索。

<pre>
tiankonguse@tiankonguse:~/github/empty$ git tag -l "v1.*"
v1.0
</pre>

<h2>添加简单的标签</h2>

直接添加即可

<pre>
tiankonguse@tiankonguse:~/github/empty$ git tag v1.1
tiankonguse@tiankonguse:~/github/empty$ git tag 
v1.0
v1.1
</pre>


<h2>添加有附注的标签</h2>

<pre>
tiankonguse@tiankonguse:~/github/empty$ git tag -a v1.2 -m "commit myssh v1.0"
tiankonguse@tiankonguse:~/github/empty$ git tag
v1.0
v1.1
v1.2
</pre>

有附注的标签和没附注的标签的区别：
    添加一个标签都相当于一次　commit, 有标签时可以储存更多的信息，如检查码，email,data等信息。


<h2>追加标签</h2>

我们想起使用标签时，项目可能已经更新了好几个版本了。
这是我们就需要向以前提交过的commit添加tag.

我们需要先找到那次　commit 的提交码

<pre>
tiankonguse@tiankonguse:~/github/empty$ git log --pretty=oneline
c50b89a055ab557019091bb04ab23201a6d26f27 update
1e79e2c8b051aace7db7a2a53a858449b3126260 update
07a6fe6cc115e85e3a91363c7f2f2336fcd734c1 update
4ff36040ae931719926ef04bd77dcf657954e476 \"$varupdate\"
f0a4327efd2edb11785cfeaf7dbde4a473401bba \"$1\"
04c1d4e612d3bdd78b5b69907f72bfb2f789f47a fix comment has add word
d9234f76ffb2b5ce4df314663b3aa191e3a9b924 add parame
303b0d1c1f08f50e030cdebf5eba68ddf30d0684 "test"
a9164347943c7ec49069c5e256d26d3c39b8dfab "test"
feb5c8683bde779b282ccb38d1d7b297861b499f "fix"
a5139c51e1efef7a5467958c79ac982f23ca238d "delete"
8ab803789489388275387826fec97ddc76f72a35 "update"
f6c5d7027b3b074356ababdeda3eb043621c9439 "update"
cfa6ee7ea753e4cc6551cd2bb51da7fbf98eb167 "update"
535d3ac43517ad041cb637bd736a152897217673 "update"
66c41b405ed6150553b99d12e0f73491744134d9 "update"
d27fe4fd25d949cff478209f945c999e02428482 update
af00f750df3c23800981e885577dedcb62aba7bc update
8065a4200f17c6e741629248d98eb19394176ccd update
8e60204acab33bca6d08965a30c26fe8fe37a473 update
c50c174442fcc7282869ba9fa2bc87ee69d1dae7 update
60752a14187ea7c988f2d0538726ea557815a9bb update
84b62ba490e8c43e7c7ff357be16a59aadc5694f add some thing
</pre>



悲剧的是我的commit都是　update, 太悲剧了。
这样我就不能区分哪次提交修改了什么了。


不过假设我是在 feb5c8683bde779b282ccb38d1d7b297861b499f "fix"　添加了第二个功能，所以我要给它添加一个标签。

<pre>
tiankonguse@tiankonguse:~/github/empty$ git tag -a v0.1 44a59b780cbec4b585fa400d72f789c2a51fdc61
tiankonguse@tiankonguse:~/github/empty$ git tag 
v0.1
v0.8
v0.9
v1.0
v1.1
v1.2
</pre>

<h2>提交标签</h2>

我们添加了标签，需要push给远程服务器。

提交一个　tag

<pre>
tiankonguse@tiankonguse:~/github/empty$ git push origin v0.1
Counting objects: 1, done.
Writing objects: 100% (1/1), 158 bytes | 0 bytes/s, done.
Total 1 (delta 0), reused 0 (delta 0)
To git@github.com:tiankonguse/empty.git
 * [new tag]         v0.1 -> v0.1
</pre>

提交所有的tag

<pre>
tiankonguse@tiankonguse:~/github/empty$ git push origin --tags 
Counting objects: 3, done.
Delta compression using up to 4 threads.
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 401 bytes | 0 bytes/s, done.
Total 3 (delta 0), reused 0 (delta 0)
To git@github.com:tiankonguse/empty.git
 * [new tag]         v0.8 -> v0.8
 * [new tag]         v0.9 -> v0.9
 * [new tag]         v1.1 -> v1.1
 * [new tag]         v1.2 -> v1.2
</pre>


