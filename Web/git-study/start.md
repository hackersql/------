
## 在命令行中创建一个新的项目

假设你的这个项目在 github 上的地址是 https://github.com/tiankonguse/DocManageSystem

首先创建该项目的文件夹

然后执行

````
touch README.md
git init
git add README.md
git commit -m "first commit"
git remote add origin git@github.com:tiankonguse/DocManageSystem.git
git push -u origin master
````


## 把已经存在的项目添加到 github 上

执行下面的命令

````
git remote add origin git@github.com:tiankonguse/DocManageSystem.git
git push -u origin master
````



