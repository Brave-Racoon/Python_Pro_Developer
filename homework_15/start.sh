#!/bin/sh

sed -i s/mirror.centos.org/vault.centos.org/g /etc/yum.repos.d/CentOS-*.repo
sed -i s/^#.*baseurl=http/baseurl=http/g /etc/yum.repos.d/CentOS-*.repo
sed -i s/^mirrorlist=http/#mirrorlist=http/g /etc/yum.repos.d/CentOS-*.repo

yum install -y  gcc \
				make \
				protobuf \
				protobuf-c \
				protobuf-c-compiler \
				protobuf-c-devel \
				python38-devel \
				python3-setuptools \
				gdb 

ulimit -c unlimited
cd /tmp/otus/
protoc-c --c_out=. deviceapps.proto
protoc -I . --python_out=. deviceapps.proto
python3.8 setup.py test
