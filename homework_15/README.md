### Задание

#### Protobuf Serializer  

Задание: дописать extension (pb.c):

deviceapps_xwrite_pb должна принимать на вход iterable со словарями и путь до файла, писать запакованные в protobuf словари в файл, сжав gzip'ом. Каждая protobuf сообщенька должна идти вместе с заголовком, 
определенным pbheader_t. Функция возвращает количество записанных байт.
[опционально] deviceapps_xread_pb читает записанные deviceapps_xwrite_pb сообщеньки из файла в виде словарей. Возвращает генератор со словарями. 
https://eli.thegreenplace.net/2012/04/05/implementing-a-generatoryield-in-a-python-c-extension

расширить и дописать тесты соответствующим образом.

С чего начать:

$ docker run -ti --rm -v /Users/s.stupnikov/Coding/otus/lection14/:/tmp/otus/ centos /bin/bash
[root@309dadf4ada2 /]# cd tmp/otus/
[root@309dadf4ada2 otus]# sh start.sh

### Запуск:  

Docker: docker run -ti --rm -v "Project_folder\homework_15":/tmp/otus/ centos /bin/bash  

Модифицированный скрипт start.sh для Python3.8 и корректного пути для пакетов CentOS:  
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



