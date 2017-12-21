# docker

## 容器生命周期管理

### run

#### -a stdin: 指定标准输入输出内容类型，可选 STDIN/STDOUT/STDERR 三项；

#### -d: 后台运行容器，并返回容器ID；

#### -i: 以交互模式运行容器，通常与 -t 同时使用；

#### -t: 为容器重新分配一个伪输入终端，通常与 -i 同时使用；

#### --name="nginx-lb": 为容器指定一个名称；

#### --dns 8.8.8.8: 指定容器使用的DNS服务器，默认和宿主一致；

#### --dns-search example.com: 指定容器DNS搜索域名，默认和宿主一致；

#### -h "mars": 指定容器的hostname；

#### -e username="ritchie": 设置环境变量；

#### --env-file=[]: 从指定文件读入环境变量；

#### --cpuset="0-2" or --cpuset="0,1,2": 绑定容器到指定CPU运行；

#### -m :设置容器使用内存最大值；

#### --net="bridge": 指定容器的网络连接类型，支持 bridge/host/none/container: 四种类型；

#### --link=[]: 添加链接到另一个容器；

#### --expose=[]: 开放一个端口或一组端口；

### start/stop/restart

#### docker start :启动一个或多少已经被停止的容器

#### docker stop :停止一个运行中的容器

#### docker restart :重启容器

### kill

#### docker kill :杀掉一个运行中的容器。

#### -s :向容器发送一个信号

### rm

#### -f :通过SIGKILL信号强制删除一个运行中的容器

#### -l :移除容器间的网络连接，而非容器本身

#### -v :删除与容器关联的卷

### pause/unpause

#### docker pause :暂停容器中所有的进程。

#### docker unpause :恢复容器中所有的进程。

### create

#### docker create ：创建一个新的容器但不启动它

### exec

#### docker exec ：在运行的容器中执行命令

#### -d :分离模式: 在后台运行

#### -i :即使没有附加也保持STDIN 打开

#### -t :分配一个伪终端

## 容器操作

### ps

#### docker ps : 列出容器

#### -a :显示所有的容器，包括未运行的。

#### -f :根据条件过滤显示的内容。

#### --format :指定返回值的模板文件。

#### -l :显示最近创建的容器。

#### -n :列出最近创建的n个容器。

#### --no-trunc :不截断输出。

#### -q :静默模式，只显示容器编号。

#### -s :显示总的文件大小。

### inspect

#### docker inspect : 获取容器/镜像的元数据。

#### -f :指定返回值的模板文件。

#### -s :显示总的文件大小。

#### --type :为指定类型返回JSON。

### top

#### docker top :查看容器中运行的进程信息，支持 ps 命令参数。

### attach

#### docker attach :连接到正在运行中的容器。

### events

#### docker events : 从服务器获取实时事件

#### -f ：根据条件过滤事件；

#### --since ：从指定的时间戳后显示所有事件;

#### --until ：流水时间显示到指定的时间为止；

### logs

#### docker logs : 获取容器的日志

#### -f : 跟踪日志输出

#### --since :显示某个开始时间的所有日志

#### -t : 显示时间戳

#### --tail :仅列出最新N条容器日志

### wait

#### docker wait : 阻塞运行直到容器停止，然后打印出它的退出代码。

### export

#### docker export :将文件系统作为一个tar归档文件导出到STDOUT。

#### -o :将输入内容写到文件。

### port

#### docker port :列出指定的容器的端口映射，或者查找将PRIVATE_PORT NAT到面向公众的端口。

## 容器rootfs命令

### commit

#### docker commit :从容器创建一个新的镜像。

#### -a :提交的镜像作者；

#### -c :使用Dockerfile指令来创建镜像；

#### -m :提交时的说明文字；

#### -p :在commit时，将容器暂停。

### cp

#### docker cp :用于容器与主机之间的数据拷贝。

#### -L :保持源目标中的链接

### diff

#### docker diff : 检查容器里文件结构的更改。

## 镜像仓库

### login

#### docker login : 登陆到一个Docker镜像仓库，如果未指定镜像仓库地址，默认为官方仓库 Docker Hub

#### docker logout : 登出一个Docker镜像仓库，如果未指定镜像仓库地址，默认为官方仓库 Docker Hub

#### -u :登陆的用户名

#### -p :登陆的密码

### pull

#### docker pull : 从镜像仓库中拉取或者更新指定镜像

#### -a :拉取所有 tagged 镜像

#### --disable-content-trust :忽略镜像的校验,默认开启

### push

#### docker push : 将本地的镜像上传到镜像仓库,要先登陆到镜像仓库

#### --disable-content-trust :忽略镜像的校验,默认开启

### search

#### docker search : 从Docker Hub查找镜像

#### --automated :只列出 automated build类型的镜像；

#### --no-trunc :显示完整的镜像描述；

#### -s :列出收藏数不小于指定值的镜像。

## 本地镜像管理

### images

#### docker images : 列出本地镜像。

#### -a :列出本地所有的镜像（含中间映像层，默认情况下，过滤掉中间映像层）；

#### --digests :显示镜像的摘要信息；

#### -f :显示满足条件的镜像；

#### --format :指定返回值的模板文件；

#### --no-trunc :显示完整的镜像信息；

#### -q :只显示镜像ID。

### rmi

#### docker rmi : 删除本地一个或多个镜像。

#### -f :强制删除；

#### --no-prune :不移除该镜像的过程镜像，默认移除；

### tag

#### docker tag : 标记本地镜像，将其归入某一仓库。

### build

#### docker build : 使用Dockerfile创建镜像。

#### --build-arg=[] :设置镜像创建时的变量；

#### --cpu-shares :设置 cpu 使用权重；

#### --cpu-period :限制 CPU CFS周期；

#### --cpu-quota :限制 CPU CFS配额；

#### --cpuset-cpus :指定使用的CPU id；

#### --cpuset-mems :指定使用的内存 id；

#### --disable-content-trust :忽略校验，默认开启；

#### -f :指定要使用的Dockerfile路径；

#### --force-rm :设置镜像过程中删除中间容器；

#### --isolation :使用容器隔离技术；

#### --label=[] :设置镜像使用的元数据；

#### -m :设置内存最大值；

#### --memory-swap :设置Swap的最大值为内存+swap，"-1"表示不限swap；

#### --no-cache :创建镜像的过程不使用缓存；

#### --pull :尝试去更新镜像的新版本；

#### -q :安静模式，成功后只输出镜像ID；

#### --rm :设置镜像成功后删除中间容器；

#### --shm-size :设置/dev/shm的大小，默认值是64M；

#### --ulimit :Ulimit配置。

### history

#### docker history : 查看指定镜像的创建历史。

#### -H :以可读的格式打印镜像大小和日期，默认为true；

#### --no-trunc :显示完整的提交记录；

#### -q :仅列出提交记录ID。

### save

#### docker save : 将指定镜像保存成 tar 归档文件。

#### -o :输出到的文件。

### import

#### docker import : 从归档文件中创建镜像。

#### -c :应用docker 指令创建镜像；

#### -m :提交时的说明文字；

## info|version

### info

#### docker info : 显示 Docker 系统信息，包括镜像和容器数。

### version

#### docker version :显示 Docker 版本信息。

#### -f :指定返回值的模板文件。
