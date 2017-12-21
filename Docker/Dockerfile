#用来指定一个基础镜像（第一层）
FROM debian

#
MAINTTAINER

#每条RUN指令执行完毕之后都会提交一个新的镜像层（第二层）
RUN apt-get update && apt-get install -y \
    curl \
    ruby1.9.1 \
    s3cmd=1.1.* \


RUN ["/bin/bash", "-c", "set -o pipefail && wget -O - https://some.site | wc -l > /number"]

#指定端口
EXPOSE

#环境变量
ENV PATH /usr/local/postgres-$PG_MAJOR/bin:$PATH


RUN mkdir -p /usr/src/things \
    && curl -SL http://example.com/big.tar.xz \
    | tar -xJC /usr/src/things \
    && make -C /usr/src/things all