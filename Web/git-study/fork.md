# github 中 fork 项目简介

使用 github 时不可避免的会去 fork 别人的项目来学习或者使用。

在这个过程中，我们可能会对项目的代码进行一些改进，之后自然想着提交给项目的原作则，这样可以供大家使用了。

## 注册帐号

来到 [github](https://github.com/) 官网即可注册帐号。


## Fork A Repo

At some point you may find yourself wanting to contribute to someone else's project, or would like to use someone's project as the starting point for your own. 

在某些时候，你可能会发现自己想为别人的项目做贡献，或想用别人的项目作为你自己的项目的起点。

This is known as "forking". 

这就是所谓的分支(fork).

比如进入我的 [.vim](https://github.com/tiankonguse/.vim) 配置文件

To fork this project, click the "Fork" button in the GitHub.com repository.

在右上角可以看到 fork 这个单词，点击即可 fork 了。


## 修改 fork 的代码

一般我们都是把 github  上的代码 clone 到本地来修改的。

比如

````
git clone git@github.com:tiankonguse/.vim.git
````

当然，clone 之前，你需要在你的电脑上配置好 git.

注：这里有官网教程的翻译 [这里](http://tiankonguse.com/record/record.php?id=40)

修改后， push 到自己的 github 上。

## 配置 remotes

When a repository is cloned, it has a default remote called origin that points to your fork on GitHub, not the original repository it was forked from. 

当一个项目被 cloned 时，它有一个默认的 remote ，被成为 origin. 这个 origin 指向你github上的分支(fork),不是原始你 forked 的项目的分支。

To keep track of the original repository, you need to add another remote named upstream。

为了追踪原始的项目，你需要添加另外一个名字为 upstream 的 remote。

````
git remote add upstream https://github.com/tiankonguse/.vim
\# Assigns the original repository to a remote called "upstream"
git fetch upstream
\# Pulls in changes not present in your local repository, without modifying your files
````

## pull 到原作者

在你的项目里应该可以看到 Pull Request   这个词，点进去。

你可以看到你 push 的列表，每一行应该有三列，第一列是贡献着，第二列是comment 说明，第三列就是这个push 的id 了。点击这个 id.

然后可以在下面要填写标题和内容。
填写上然后点击 comment 即可。




