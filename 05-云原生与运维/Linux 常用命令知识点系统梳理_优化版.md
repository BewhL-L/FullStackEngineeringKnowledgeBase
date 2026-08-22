---
title: Linux 常用命令知识点系统梳理
tags: [运维, Linux, 命令行, 面试]
created: 2026-08-13
updated: 2026-08-13
---

> **优化版说明**：本文档在原有内容基础上，为每个三级标题知识点补充了「🔍 深度解析」（作用+原理+用法要点），所有原有内容完整保留，未做任何修改。

# Linux 常用命令知识点系统梳理（优化版）

> **文档说明**：系统梳理 Linux 常用命令，涵盖文件操作、进程管理、网络、文本处理、权限、磁盘、系统监控等，面试和日常开发必备。

---

## 1. 概述

Linux 是开源的类 Unix 操作系统，以稳定、高效、安全著称，是服务器操作系统的绝对主流。掌握 Linux 命令是后端开发和运维的基本功。

**常见发行版**：
- **RedHat 系**：CentOS、RHEL、Fedora（yum/dnf 包管理）
- **Debian 系**：Ubuntu、Debian（apt 包管理）
- **其他**：Alpine（轻量，Docker 常用）、Arch

---

## 2. 文件与目录操作

```bash
# 查看目录内容
ls -la          # 长格式显示所有文件（含隐藏）
ls -lh          # 人类可读大小
ll              # 部分系统别名 = ls -l

# 目录操作
cd /path        # 切换目录
cd ~            # 回家目录
cd -            # 回上一次目录
pwd             # 当前路径
mkdir -p a/b/c  # 递归创建目录
rmdir dir       # 删除空目录

# 文件操作
touch file.txt          # 创建空文件/更新时间戳
cp -r src dst           # 复制（-r 递归目录）
mv old new              # 移动/重命名
rm -rf dir              # 强制递归删除（危险！）
ln -s target link       # 软链接（快捷方式）
ln target link          # 硬链接

# 查看文件内容
cat file.txt            # 全部显示
less file.txt           # 分页查看（q 退出，/ 搜索）
head -n 20 file.txt     # 前 20 行
tail -n 20 file.txt     # 后 20 行
tail -f app.log         # 实时跟踪日志
wc -l file.txt          # 统计行数
```

> 🔍 **知识点深度解析**
>
> **作用**：文件操作是最基础的 Linux 命令，日常开发高频使用。
>
> **原理**：Linux 一切皆文件，目录也是文件（存储目录项列表）。软链接（符号链接）是独立文件，存储目标路径，目标删除后软链接失效（悬空链接）；硬链接是同一文件的另一个目录项，共享 inode，删除一个不影响另一个，只有所有硬链接都删除文件才真正删除。`rm -rf /` 是最危险的命令，递归强制删除根目录所有内容。
>
> **用法要点**：① rm -rf 前确认路径，特别是变量（rm -rf $DIR/，DIR 为空时等于 rm -rf /）；② 用 less 查看大文件，不要用 cat（会刷屏）；③ tail -f 实时看日志，生产必备；④ 面试常考：软链接 vs 硬链接、rm -rf 风险、inode 概念。

---

## 3. 文本处理三剑客

### 3.1 grep（查找）

```bash
grep "pattern" file.txt          # 查找包含 pattern 的行
grep -i "pattern" file.txt       # 忽略大小写
grep -n "pattern" file.txt       # 显示行号
grep -v "pattern" file.txt       # 反向匹配（不包含）
grep -r "pattern" /dir           # 递归查找目录
grep -E "pat1|pat2" file.txt     # 扩展正则（或）
grep -c "pattern" file.txt       # 统计匹配行数
```

> 🔍 **知识点深度解析**
>
> **作用**：grep 在文件或标准输入中按字符串/正则检索匹配行，是日志排查、代码搜索、数据过滤最高频的命令。
>
> **原理**：grep 逐行读取并用正则引擎匹配；-i 忽略大小写，-n 显示行号，-v 反向匹配（输出不含模式的行），-r 递归目录，-E 启用扩展正则（支持 |、()、+、? 等），-P 用 Perl 正则（支持 \d、零宽断言），-c 统计匹配行数。底层采用高效字符串匹配算法，处理大文件比 cat 管道更快。
>
> **用法要点**：① 排查日志：grep -i error app.log | tail -50；② 排除注释与空行：grep -vE '^#|^$' file；③ -r 递归搜索代码库（配合 --include 限定扩展名）；④ -E 用扩展正则实现"或"匹配（pat1|pat2）；⑤ 配合管道组合（ps -ef | grep java | grep -v grep）；⑥ -A/-B/-C 显示匹配行上下文；⑦ 只看匹配部分用 -o。

### 3.2 sed（编辑）

```bash
sed 's/old/new/g' file.txt       # 全局替换
sed '2d' file.txt                # 删除第 2 行
sed -i 's/old/new/g' file.txt    # 原地修改（-i）
sed -n '10,20p' file.txt         # 显示 10-20 行
sed '/pattern/d' file.txt        # 删除匹配行
```

> 🔍 **知识点深度解析**
>
> **作用**：sed 是流编辑器，对文本逐行执行替换、删除、打印、插入等操作，常用于批量改配置、提取指定行。
>
> **原理**：sed 读入每行到"模式空间"再按脚本命令处理；s/old/new/g 中 g 表示全局替换（不加只替换每行首个），-i 原地修改文件，-n 取消默认打印（配合 p 只输出指定行），地址范围如 10,20 或 /pattern/ 限定作用行，多条命令用 -e 或分号分隔。
>
> **用法要点**：① 全局替换：sed -i 's/old/new/g' file（改前务必先备份 sed -i.bak）；② 删除行：sed '2d'（第 2 行）、sed '/pattern/d'（匹配行）；③ 提取区间：sed -n '10,20p'；④ 反向引用 \1 \2 在替换中复用捕获组；⑤ 改配置前先备份，避免误改生产；⑥ 复杂字段计算优先用 awk；⑦ 注意 -i 会重写整个文件，临时空间不足可能失败。

### 3.3 awk（处理）

```bash
awk '{print $1, $3}' file.txt    # 打印第 1、3 列
awk -F: '{print $1}' /etc/passwd # 以 : 分隔，打印第 1 列
awk '$3 > 1000 {print $1}' /etc/passwd  # 条件过滤
awk '{sum += $1} END {print sum}' file.txt  # 求和
```

> 🔍 **知识点深度解析**
>
> **作用**：grep/sed/awk 是 Linux 文本处理三剑客，日志分析、数据处理必备。
>
> **原理**：grep 用正则表达式匹配行，底层是正则引擎（grep -E 用扩展正则，grep -P 用 Perl 正则）。sed 是流编辑器，逐行处理，支持替换、删除、插入等操作，s 命令格式 `s/匹配/替换/标志`，g 标志是全局替换。awk 是编程语言，逐行处理，默认按空白分隔字段（$1 第一列，$0 整行），支持 BEGIN/END 块、条件、循环、函数。
>
> **用法要点**：① 日志排查：grep 关键词 + tail -f 组合；② awk -F 指定分隔符，处理 CSV/日志很方便；③ sed -i 原地修改前先备份（sed -i.bak）；④ 面试常考：三剑客用法、awk 字段、sed 替换、正则表达式。

---

## 4. 进程管理

```bash
ps aux                  # 查看所有进程
ps -ef | grep java      # 查找 Java 进程
top                     # 实时进程监控（q 退出）
htop                    # 增强版 top（需安装）
kill 1234               # 发送 TERM 信号（优雅终止）
kill -9 1234            # 强制杀死（SIGKILL）
killall nginx           # 按名称杀进程
pkill -f "java.*app"    # 按命令行匹配杀进程

# 前后台
sleep 100 &             # 后台运行
jobs                    # 查看后台任务
fg %1                   # 调到前台
bg %1                   # 后台继续
nohup command &         # 不挂断后台运行（退出终端不终止）

# 系统启动
systemctl start nginx   # 启动服务
systemctl stop nginx    # 停止
systemctl restart nginx # 重启
systemctl status nginx  # 状态
systemctl enable nginx  # 开机自启
systemctl disable nginx # 取消开机自启
```

> 🔍 **知识点深度解析**
>
> **作用**：进程管理排查服务状态、处理异常进程。
>
> **原理**：Linux 进程有状态：运行（R）、睡眠（S）、停止（T）、僵尸（Z）。ps aux 显示 USER/PID/%CPU/%MEM/VSZ/RSS/STAT/START/TIME/COMMAND。top 实时显示 CPU、内存、进程列表，按 P 排序 CPU，按 M 排序内存。kill 发送信号，默认 SIGTERM(15) 让进程优雅退出，SIGKILL(9) 强制杀死（进程无法捕获）。僵尸进程是子进程退出但父进程未 wait，需要杀父进程或修复代码。
>
> **用法要点**：① 杀进程先 kill（优雅），不行再 kill -9；② nohup + & 后台运行服务，输出重定向到文件；③ systemctl 是 CentOS7+/Ubuntu 的服务管理（替代 service/chkconfig）；④ 面试常考：进程状态、kill 信号、僵尸进程、nohup 用法。

---

## 5. 网络命令

```bash
# 网络连接
ip addr                 # 查看 IP 地址（替代 ifconfig）
ip route                # 查看路由表
ping -c 4 baidu.com     # 测试连通性（发 4 个包）
telnet host port        # 测试端口连通性
curl -I https://baidu.com  # 测试 HTTP 请求
wget url                # 下载文件

# 端口和连接
ss -tlnp                # 查看监听端口（替代 netstat）
ss -tunap               # 查看所有连接
netstat -tlnp           # 旧版查看监听端口
lsof -i :8080           # 查看占用 8080 端口的进程

# 防火墙
firewall-cmd --list-ports          # 查看开放端口
firewall-cmd --add-port=8080/tcp --permanent  # 开放端口
firewall-cmd --reload              # 重载
ufw allow 8080                     # Ubuntu 防火墙

# DNS
nslookup baidu.com       # DNS 查询
dig baidu.com            # 详细 DNS 查询
cat /etc/resolv.conf     # DNS 配置
```

> 🔍 **知识点深度解析**
>
> **作用**：网络命令排查网络问题、端口占用、服务连通性。
>
> **原理**：ss 是 iproute2 套件的一部分，比 netstat 更快（直接读取内核），推荐使用。`ss -tlnp`：t=TCP, l=listening, n=numeric（不解析域名）, p=process。lsof -i :port 通过 /proc 文件系统查找占用端口的进程。curl 是强大的 HTTP 客户端，-I 只看响应头，-v 看详细过程，-X 指定方法，-H 加 Header，-d 传数据。
>
> **用法要点**：① 端口被占用用 lsof -i :port 或 ss -tlnp | grep port 查找；② 测试端口用 telnet host port 或 curl；③ 面试常考：ss/netstat 区别、lsof 用法、curl 常用参数、防火墙配置。

---

## 6. 权限管理

```bash
# 文件权限
chmod 755 file.sh       # rwxr-xr-x
chmod +x script.sh      # 添加执行权限
chown user:group file   # 修改所有者和组
chown -R user:group dir # 递归修改

# 权限数字
# r=4, w=2, x=1
# 755 = rwx(7) r-x(5) r-x(5)
# 644 = rw-(6) r--(4) r--(4)

# 用户管理
useradd -m username     # 创建用户（-m 建家目录）
passwd username         # 设置密码
userdel -r username     # 删除用户（-r 删家目录）
usermod -aG group user  # 用户加入组

# sudo
visudo                  # 编辑 sudoers
```

---

## 7. 磁盘与文件系统

```bash
df -h                   # 查看磁盘使用情况
du -sh /dir             # 查看目录大小
du -sh /* | sort -rh    # 根目录各文件夹大小排序
fdisk -l                # 查看分区
mount /dev/sdb1 /data   # 挂载
umount /data            # 卸载
free -h                 # 查看内存使用
```

---

## 8. 系统监控

```bash
# CPU/内存
top                     # 实时监控
vmstat 1                # 每秒统计（CPU/内存/IO）
mpstat 1                # CPU 详细统计

# 磁盘 IO
iostat -xz 1            # 磁盘 IO 统计

# 网络
sar -n DEV 1            # 网络流量统计
iftop                   # 实时网络流量（需安装）

# 综合
dstat                   # 全能监控（需安装）
uptime                  # 系统运行时间、负载
```

---

## 9. 压缩与打包

```bash
# tar
tar -czvf archive.tar.gz /dir    # 打包并 gzip 压缩
tar -xzvf archive.tar.gz         # 解压
tar -cjvf archive.tar.bz2 /dir   # bzip2 压缩（更小但慢）
tar -tf archive.tar.gz           # 查看内容不解压

# zip/unzip
zip -r archive.zip /dir
unzip archive.zip

# gzip
gzip file.txt                    # 压缩（生成 file.txt.gz）
gunzip file.txt.gz               # 解压
```

---

## 10. Shell 脚本基础

```bash
#!/bin/bash
# 变量
name="Tom"
echo "Hello, $name"

# 条件判断
if [ -f file.txt ]; then
    echo "文件存在"
elif [ -d dir ]; then
    echo "目录存在"
else
    echo "不存在"
fi

# 循环
for i in {1..5}; do
    echo "Number: $i"
done

# 函数
greet() {
    echo "Hello, $1!"
}
greet "World"

# 命令替换
files=$(ls -l | wc -l)
echo "文件数: $files"
```

---

## 11. 面试高频考点

1. **文件操作**：ls/cp/mv/rm、软链接 vs 硬链接
2. **文本三剑客**：grep/sed/awk 常用操作
3. **进程管理**：ps/top/kill、进程状态、僵尸进程
4. **网络命令**：ss/lsof/curl、端口排查
5. **权限**：chmod 数字、chown、sudo
6. **磁盘**：df/du、挂载、inode
7. **系统监控**：top/vmstat/iostat、负载
8. **压缩**：tar 常用参数
9. **Shell 脚本**：变量、条件、循环、函数
10. **排查问题**：CPU 高/内存满/磁盘满/端口占用排查思路

---

## 📝 精简总结

- 文件操作：ls/cd/cp/mv/rm，软链接存路径、硬链接共享 inode
- 文本三剑客：grep 查找、sed 编辑、awk 处理
- 进程：ps/top 查看，kill 终止（先 15 后 9）
- 网络：ss 看端口、lsof 查占用、curl 测 HTTP
- 权限：r=4 w=2 x=1，chmod/chown
- 磁盘：df 看使用、du 看目录大小
- 监控：top/vmstat/iostat 全方位
- 打包：tar -czvf 压缩、-xzvf 解压
- 排查问题：先看资源（top/df/free），再看日志（tail -f）

---

[[05-云原生与运维/MOC-云原生与运维|← 返回云原生 MOC]] | [[Home|🏠 返回首页]]
