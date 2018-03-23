# git 子模块学习笔记


## 前言 

我们一般为我们的一个项目创建一个git仓库．  

但是我们的项目会引用很多其他项目的库或者工具．  

通常的做法是把那些库或工具直接复制到自己项目下．  

这样做之后，我们的项目的代码量看起来就很大了，但是很多都是第三方库和第三方工具．  

另一方面，如果第三方库和工具有重大更新了，我们也需要更新，这个时候再去复制什么的代价是很大的．  

这个时候子模块站出来了，　如果我们直接像创建一个软链接指向我们引用的库和工具的话，直接更新库和工具就行了，还不会影响到我们的项目．  

所以，简单的说，子模块可以理解为软链接，只不过这个是git仓库之间的链接，而不是文件之间的链接．  


## 准备工作

假设你已经有两个git仓库了．  

如果没有，可以到[git 使用笔记][tiankonguse-git-study] 和 [tiankonguse 的小工具与学习笔记][tiankonguse-empty] 来fork两个项目．  

然后把 [第二个][tiankonguse-empty] 先 clone 下来．  

```
git clone https://github.com/tiankonguse/empty.git
```

然后进入这个项目，创建一个 test 目录,并进入．  


## 基本命令

### 子模块配置文件

理论上说你增加子模块后自动会创建子模块配置文件．  

但是为了保证有这个文件，你先自己创建一个吧．  

```
touch .gitmodules
```


### 增加子模块


既然要使用，第一件事自然是增加子模块了．  

我们假设增加的就是那个 [git学习笔记项目][tiankonguse-git-study]吧．  

```
tiankonguse@tiankonguse:~/github/empty/test$ git submodule add https://github.com/tiankonguse/git-study.git gittest
正克隆到 'test/gittest'...
remote: Counting objects: 26, done.
remote: Total 26 (delta 0), reused 0 (delta 0), pack-reused 26
Unpacking objects: 100% (26/26), done.
检查连接... 完成。

tiankonguse@tiankonguse:~/github/empty/test$ ls
gittest

tiankonguse@tiankonguse:~/github/empty/test$ cat ../.gitmodules 
[submodule "vim"]
	path = vim
	url = https://github.com/tiankonguse/VIM-study.git
[submodule "test/gittest"]
	path = test/gittest
	url = https://github.com/tiankonguse/git-study.git
```

最后面那个就是我刚才新增的子模块了．  

命令的组成是　`git submodule add gitmodulesLink gitmodulesName`.  


### 提交

提交的时候，你会发现你的子模块里面的内容不会被提交，只是把这个目录提交了．  

```
tiankonguse@tiankonguse:~/github/empty/test$ git status
位于分支 master
您的分支与上游分支 'origin/master' 一致。

要提交的变更：
  （使用 "git reset HEAD <file>..." 撤出暂存区）

	修改:         ../.gitmodules
	新文件:       gittest
```

### 更新子模块

既然我们使用子模块是为了方便更新引进的子项目，那就需要知道怎么更新这些子模块了．  

下面这个命令是更新这个项目所有的子模块．  

```
tiankonguse@tiankonguse:~/github/empty/test$ git submodule update
子模组路径 '../vim'：检出 '3cba4fcd1e25d328a3a9d68e1029fd6d84d7b241'
```

如果你想更新指定的子模块，　就指定那个子模块的名字吧．  

```
tiankonguse@tiankonguse:~/github/empty/test$ git submodule update gittest
```

### 删除子模块


删除子模块虽然我们很少用，但是有时候不想使用一个库了，还是需要删除的.  

当然我们不能使用暴力手段来删除，　那样再操作git会报错的．  

我们需要使用　git 的删除功能．  

```
tiankonguse@tiankonguse:~/github/empty/test$ git rm -rf gittest
rm 'test/gittest'

tiankonguse@tiankonguse:~/github/empty/test$ cat ../.gitmodules
[submodule "vim"]
	path = vim
	url = https://github.com/tiankonguse/VIM-study.git
```

然后我们就可以提交了．  

```
tiankonguse@tiankonguse:~/github/empty/test$ git status 
位于分支 master
您的分支与上游分支 'origin/master' 一致。

无文件要提交，干净的工作区
```

### clone带子模块的项目


我们如果clone一个有子模块的项目时，会发现那些子项目的空的．  


```
tiankonguse@tiankonguse:~/github/test$ git clone https://github.com/tiankonguse/empty.git
正克隆到 'empty'...
remote: Counting objects: 985, done.
remote: Total 985 (delta 0), reused 0 (delta 0), pack-reused 985
接收对象中: 100% (985/985), 3.19 MiB | 645.00 KiB/s, done.
处理 delta 中: 100% (391/391), done.
检查连接... 完成。

tiankonguse@tiankonguse:~/github/test$ ll empty/bash/
总用量 8
drwxrwxr-x  2 tiankonguse tiankonguse 4096  4月 19 12:29 ./
drwxrwxr-x 31 tiankonguse tiankonguse 4096  4月 19 12:29 ../
```

这是因为这些子模块需要我们手动拉去．  

```
tiankonguse@tiankonguse:~/github/test/empty$ git submodule update
正克隆到 'bash'...
remote: Counting objects: 108, done.
remote: Total 108 (delta 0), reused 0 (delta 0), pack-reused 108
接收对象中: 100% (108/108), 33.57 KiB | 0 bytes/s, done.
处理 delta 中: 100% (44/44), done.
检查连接... 完成。
子模组路径 'bash'：检出 '351efed632e650e4ebc6009f2922fd0f85fff474'
正克隆到 'git'...
remote: Counting objects: 26, done.
remote: Total 26 (delta 0), reused 0 (delta 0), pack-reused 26
Unpacking objects: 100% (26/26), done.
检查连接... 完成。
子模组路径 'git'：检出 '838d2c26d4d106d30a8dacb4dd7fe3fc6a0c02d5'
正克隆到 'link'...
remote: Counting objects: 27, done.
remote: Compressing objects: 100% (25/25), done.
remote: Total 27 (delta 8), reused 21 (delta 2), pack-reused 0
Unpacking objects: 100% (27/27), done.
检查连接... 完成。
子模组路径 'link'：检出 '7c73be594c56f0384fc0df7b5b971072b342ab99'
正克隆到 'vim'...
remote: Counting objects: 81, done.
remote: Total 81 (delta 0), reused 0 (delta 0), pack-reused 81
Unpacking objects: 100% (81/81), done.
检查连接... 完成。
子模组路径 'vim'：检出 '3cba4fcd1e25d328a3a9d68e1029fd6d84d7b241'

tiankonguse@tiankonguse:~/github/test/empty$ ls bash/
ask          awk-manual.md  base.md  command.md  edite.md  guid.md          process.md  readme.md  start.bat           test     variable.md
awk-base.md  awk.md         bat.md   du.md       env.md    introduction.md  python.md   source     startSecureCRT.bat  type.md
```

### 结束语

好了，现在我们可以轻松的使用git的子模块了．  

当然，这个子模块还有很多其他的坑，这里就不介绍了．  

### 参考资料

* [git 使用笔记][tiankonguse-git-study]  
* [6.6 Git 工具 - 子模块][git-book-sub]  


[git-book-sub]: http://git-scm.com/book/zh/v1/Git-%E5%B7%A5%E5%85%B7-%E5%AD%90%E6%A8%A1%E5%9D%97
[tiankonguse-git-study]: https://github.com/tiankonguse/git-study
[tiankonguse-empty]: https://github.com/tiankonguse/empty
