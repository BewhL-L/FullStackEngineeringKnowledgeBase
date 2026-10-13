---
title: Linux运维常用命令手册
tags: [Linux, DevOps, 命令手册, Shell, 系统管理, 性能监控, 网络排查, 安全, 枢纽笔记]
category: 云原生与运维
created: 2026-08-13
updated: 2026-08-28
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 核心
pre: ["[[Linux系统管理与常用命令]]"]
aliases: [Linux-运维常用命令手册]
---

# 🐧 Linux 运维常用命令手册

> **文档说明**：系统整理 Linux 运维工程师日常工作中最常用的命令与操作手册，涵盖系统信息查看、文件与目录操作、用户与权限管理、进程与服务管理、网络配置与排查、磁盘与文件系统管理、包管理与软件安装、日志查看与分析、性能监控与调优、安全与防火墙、文本处理与三剑客（grep/sed/awk）、压缩与归档、SSH 远程管理、定时任务（Cron）、系统启动与服务管理、常见故障排查流程、运维脚本示例、各发行版差异对比。
>
> **适用人群**：Linux 运维工程师、SRE、DevOps 工程师、后端开发者、云原生学习者
>
> **前置知识**：[[Linux系统管理与常用命令]] · [[PowerShell脚本自动化]]

---

## 一、系统信息与状态

### 1.1 系统基本信息

```bash
# 系统信息
uname -a                    # 内核版本、架构、主机名
uname -r                    # 内核版本
hostname                    # 主机名
hostnamectl                 # 系统信息（systemd 系统）
cat /etc/os-release         # 发行版信息（Ubuntu/CentOS 等）
cat /etc/redhat-release     # CentOS/RHEL 版本
lsb_release -a              # LSB 发行版信息
uptime                      # 系统运行时间、负载
date                        # 当前日期时间
date -s "2024-01-01 12:00:00"  # 设置时间
timedatectl                 # 时区和时间设置
timedatectl set-timezone Asia/Shanghai  # 设置时区
locale                      # 当前语言环境
localectl                   # 系统区域设置

# 硬件信息
lscpu                       # CPU 信息
cat /proc/cpuinfo           # CPU 详细信息
free -h                     # 内存使用（人类可读）
cat /proc/meminfo           # 内存详细信息
lsblk                       # 块设备列表
fdisk -l                    # 磁盘分区列表
df -h                       # 磁盘使用情况
du -sh /path                # 目录大小
lspci                       # PCI 设备列表
lsusb                       # USB 设备列表
dmidecode                   # DMI/SMBIOS 硬件信息（需 root）
```

### 1.2 系统负载与性能

```bash
# 负载
uptime                      # 1/5/15 分钟平均负载
cat /proc/loadavg           # 原始负载数据
w                           # 登录用户和负载

# 实时监控
top                         # 实时进程监控（q 退出）
htop                        # 增强版 top（需安装）
atop                        # 高级系统监控（需安装）
glances                     # 跨平台系统监控（需安装）

# 性能分析
vmstat 1 5                  # 虚拟内存统计（每秒1次，共5次）
iostat -xz 1                # IO 统计（sysstat 包）
mpstat -P ALL 1             # CPU 统计（每核）
pidstat 1                   # 进程级统计
sar -u 1 5                  # 历史性能数据（sysstat）
sar -r 1 5                  # 内存历史
sar -n DEV 1 5              # 网络历史
```

---

## 二、文件与目录操作

### 2.1 基本操作

```bash
# 目录操作
pwd                         # 当前目录
cd /path                    # 切换目录
cd ~                        # 回到主目录
cd -                        # 回到上一个目录
ls                          # 列出文件
ls -la                      # 详细列表（含隐藏文件）
ls -lh                      # 人类可读大小
ls -lt                      # 按修改时间排序
ls -R                       # 递归列出
mkdir dirname               # 创建目录
mkdir -p a/b/c              # 递归创建目录
rmdir dirname               # 删除空目录

# 文件操作
touch file.txt              # 创建空文件/更新时间戳
cp source dest              # 复制文件
cp -r source dest           # 递归复制目录
mv source dest              # 移动/重命名
rm file.txt                 # 删除文件
rm -r dirname               # 递归删除目录
rm -rf dirname              # 强制递归删除（危险！）
ln -s target linkname       # 创建软链接
ln target linkname          # 创建硬链接
readlink -f file            # 查看软链接真实路径
file file.txt               # 查看文件类型
stat file.txt               # 文件详细信息（inode/权限/时间）
```

### 2.2 查看文件内容

```bash
cat file.txt                # 查看全部内容
cat -n file.txt             # 显示行号
tac file.txt                # 反向显示（从最后一行开始）
more file.txt               # 分页查看（空格下页，q退出）
less file.txt               # 增强分页（上下键，/搜索，q退出）
head file.txt               # 查看前10行
head -n 20 file.txt         # 查看前20行
tail file.txt               # 查看后10行
tail -n 20 file.txt         # 查看后20行
tail -f file.txt            # 实时跟踪文件变化
tail -F file.txt            # 跟踪文件（文件重建后继续跟踪）
nl file.txt                 # 带行号显示
wc file.txt                 # 统计行数/单词数/字符数
wc -l file.txt              # 只统计行数
```

### 2.3 查找文件

```bash
# find 命令
find /path -name "*.log"            # 按名称查找
find /path -iname "*.log"           # 忽略大小写
find /path -type f                   # 只找文件
find /path -type d                   # 只找目录
find /path -size +100M               # 大于100MB的文件
find /path -size -10k                # 小于10KB的文件
find /path -mtime -7                 # 7天内修改的文件
find /path -mtime +30                # 30天前修改的文件
find /path -user username            # 属于某用户的文件
find /path -perm 644                 # 权限为644的文件
find /path -name "*.tmp" -delete    # 查找并删除
find /path -name "*.log" -exec ls -lh {} \;  # 对结果执行命令
find /path -name "*.log" | xargs ls -lh       # 同上（更高效）

# locate 命令（需 updatedb 建立索引）
locate filename               # 快速查找文件
updatedb                      # 更新文件索引数据库

# which/whereis
which command                 # 查找命令位置
whereis command               # 查找命令/源码/man 手册位置
type command                  # 查看命令类型（内置/外部/别名）
```

---

## 三、用户与权限管理

### 3.1 用户管理

```bash
# 用户操作
useradd username             # 创建用户
useradd -m -s /bin/bash username  # 创建用户并创建家目录、指定shell
useradd -u 1001 -g groupname username  # 指定UID和组
passwd username              # 设置/修改密码
usermod -aG groupname username  # 将用户添加到组（追加）
usermod -s /bin/zsh username    # 修改用户shell
usermod -l newname oldname      # 修改用户名
userdel username              # 删除用户（保留家目录）
userdel -r username           # 删除用户并删除家目录
id username                   # 查看用户UID/GID/所属组
whoami                        # 当前用户名
who                           # 当前登录用户
w                             # 登录用户详情
last                          # 最近登录记录
lastb                         # 失败登录记录
lastlog                       # 所有用户最后登录时间

# 组操作
groupadd groupname            # 创建组
groupmod -n newname oldname   # 修改组名
groupdel groupname            # 删除组
groups username               # 查看用户所属组
gpasswd -a username groupname # 添加用户到组
gpasswd -d username groupname # 从组移除用户
```

### 3.2 权限管理

```bash
# 权限查看
ls -l file.txt               # 查看文件权限
# 输出示例：-rw-r--r-- 1 user group 100 Jan 1 00:00 file.txt
# 类型(1) 所有者(3) 所属组(3) 其他(3) 链接数 所有者 组 大小 时间 名称

# chmod 修改权限
chmod 755 file.txt           # 数字方式：rwxr-xr-x
chmod u+x file.txt           # 所有者添加执行权限
chmod g-w file.txt           # 组移除写权限
chmod o+r file.txt           # 其他添加读权限
chmod a+x file.txt           # 所有人添加执行权限
chmod -R 755 /dir            # 递归修改目录权限

# 权限数字对照表
# r=4, w=2, x=1
# 7 = rwx (4+2+1)
# 6 = rw- (4+2)
# 5 = r-x (4+1)
# 4 = r-- (4)
# 0 = --- (无权限)

# chown 修改所有者
chown user:group file.txt    # 修改所有者和组
chown user file.txt          # 只修改所有者
chown :group file.txt        # 只修改组
chown -R user:group /dir     # 递归修改

# 特殊权限
chmod u+s file               # SUID（执行时以所有者身份运行）
chmod g+s dir                # SGID（目录中新建文件继承组）
chmod +t dir                 # Sticky Bit（只有所有者能删除文件，如 /tmp）

# ACL 访问控制列表（更细粒度权限）
getfacl file.txt             # 查看 ACL
setfacl -m u:username:rwx file.txt  # 给特定用户设置权限
setfacl -x u:username file.txt      # 删除特定用户 ACL
setfacl -b file.txt                 # 清除所有 ACL
```

---

## 四、进程与服务管理

### 4.1 进程管理

```bash
# 查看进程
ps                          # 当前shell进程
ps aux                      # 所有进程详细信息（BSD风格）
ps -ef                      # 所有进程（System V风格）
ps -ef --forest             # 进程树
ps aux --sort=-%cpu         # 按CPU使用率排序
ps aux --sort=-%mem         # 按内存使用率排序
pstree                      # 进程树（需安装 psmisc）
pgrep -u username           # 按用户查找进程PID
pgrep -f keyword            # 按命令行查找进程PID
pidof processname           # 按进程名查找PID

# 实时监控
top                         # 实时监控（P按CPU排序，M按内存排序，q退出）
htop                        # 增强版 top

# 终止进程
kill PID                    # 发送 SIGTERM（15）终止进程
kill -9 PID                 # 发送 SIGKILL（9）强制杀死
kill -l                     # 列出所有信号
killall processname         # 按进程名杀死所有进程
pkill -f keyword            # 按命令行匹配杀死进程
pkill -u username           # 杀死某用户的所有进程
xkill                       # 图形界面点击杀死（X11）

# 进程优先级
nice -n 10 command          # 以指定优先级运行（-20最高，19最低）
renice -n 5 -p PID          # 修改运行中进程的优先级
```

### 4.2 服务管理（systemd）

```bash
# systemctl 命令
systemctl start serviceName       # 启动服务
systemctl stop serviceName        # 停止服务
systemctl restart serviceName     # 重启服务
systemctl reload serviceName      # 重新加载配置（不中断服务）
systemctl status serviceName      # 查看服务状态
systemctl enable serviceName      # 设置开机自启
systemctl disable serviceName     # 取消开机自启
systemctl is-enabled serviceName  # 查看是否开机自启
systemctl is-active serviceName   # 查看是否运行中
systemctl list-units --type=service  # 列出所有服务
systemctl list-units --type=service --state=running  # 运行中的服务
systemctl list-unit-files --type=service  # 所有服务文件及自启状态
systemctl daemon-reload            # 重新加载 systemd 配置
systemctl mask serviceName         # 屏蔽服务（无法启动）
systemctl unmask serviceName       # 取消屏蔽

# 查看日志
journalctl -u serviceName          # 查看服务日志
journalctl -u serviceName -f       # 实时跟踪服务日志
journalctl -u serviceName --since "1 hour ago"  # 最近1小时日志
journalctl -u serviceName -n 100   # 最后100行
journalctl --boot                   # 本次启动以来的日志
journalctl -k                       # 内核日志
```

### 4.3 传统服务管理（SysVinit/Upstart）

```bash
# CentOS 6 / Ubuntu 14.04 等
service serviceName start
service serviceName stop
service serviceName restart
service serviceName status
chkconfig serviceName on            # 开机自启
chkconfig serviceName off           # 取消自启
chkconfig --list                    # 列出所有服务自启状态

# /etc/init.d/ 直接调用
/etc/init.d/serviceName start
/etc/init.d/serviceName stop
```

---

## 五、网络配置与排查

### 5.1 网络配置

```bash
# 查看网络信息
ip addr                     # 网络接口和IP地址（现代命令）
ip link                     # 网络接口状态
ip route                    # 路由表
ip neigh                    # ARP 表
ifconfig                    # 旧命令（需安装 net-tools）
route -n                    # 路由表（旧命令）
arp -a                      # ARP 表（旧命令）

# DNS
cat /etc/resolv.conf        # DNS 配置
nslookup domain.com         # DNS 查询（旧）
dig domain.com              # DNS 查询（推荐）
dig domain.com MX           # 查询 MX 记录
host domain.com             # DNS 查询
hostname -I                 # 本机所有IP

# 配置网络（临时）
ip addr add 192.168.1.100/24 dev eth0   # 添加IP
ip addr del 192.168.1.100/24 dev eth0   # 删除IP
ip link set eth0 up          # 启用接口
ip link set eth0 down        # 禁用接口
ip route add default via 192.168.1.1    # 添加默认网关

# 配置网络（永久，systemd-networkd/NetworkManager）
# Ubuntu/Debian: /etc/netplan/*.yaml
# CentOS/RHEL: /etc/sysconfig/network-scripts/ifcfg-eth0
# NetworkManager: nmcli
nmcli device status          # 设备状态
nmcli connection show       # 连接列表
nmcli connection up name    # 启用连接
```

### 5.2 网络连通性测试

```bash
# 基础连通性
ping google.com             # ping 测试（Ctrl+C停止）
ping -c 4 google.com        # 发送4个包
ping -i 0.5 google.com      # 间隔0.5秒
traceroute google.com       # 路由跟踪（需安装）
tracepath google.com        # 路由跟踪（内置）
mtr google.com              # 组合 ping+traceroute（需安装）

# 端口测试
telnet host port            # telnet 测试端口（需安装）
nc -zv host port            # netcat 测试端口
nc -zv host 1-1000         # 扫描端口范围
ss -tlnp                    # 监听的TCP端口（现代）
ss -ulnp                    # 监听的UDP端口
ss -tunap                   # 所有连接
netstat -tlnp               # 监听端口（旧命令）
netstat -an | grep ESTABLISHED  # 已建立连接

# HTTP 测试
curl -I https://example.com   # 只看响应头
curl -v https://example.com   # 详细输出
curl -X POST -d "data" https://api.example.com  # POST请求
curl -H "Authorization: Bearer token" https://api.example.com  # 带Header
wget https://example.com/file.zip  # 下载文件
wget -c https://example.com/file.zip  # 断点续传

# 域名/IP
whois domain.com            # 域名注册信息
dig -x 8.8.8.8              # 反向DNS查询
```

### 5.3 网络流量监控

```bash
# 实时流量
iftop                       # 按连接显示流量（需安装）
nethogs                     # 按进程显示流量（需安装）
vnstat                      # 网络流量统计（需安装）
bmon                        # 带宽监控（需安装）
slurm -i eth0               # 接口流量图（需安装）

# 抓包
tcpdump -i eth0             # 抓包（需root）
tcpdump -i eth0 port 80     # 抓80端口
tcpdump -i eth0 host 192.168.1.1  # 抓特定主机
tcpdump -i eth0 -w file.pcap  # 保存到文件
tcpdump -r file.pcap         # 读取文件
tcpdump -i eth0 -A port 80   # ASCII显示
```

---

## 六、磁盘与文件系统

### 6.1 磁盘管理

```bash
# 查看磁盘
lsblk                       # 块设备列表
fdisk -l                    # 分区列表
df -h                       # 磁盘使用（人类可读）
df -T                       # 显示文件系统类型
du -sh /path                # 目录大小
du -sh /* | sort -rh        # 根目录下各目录大小排序
du -h --max-depth=1 /path   # 一级目录大小

# 分区
fdisk /dev/sdb              # 交互式分区
parted /dev/sdb             # GNU分区工具（支持GPT）
partprobe                   # 通知内核重新读取分区表
partx -a /dev/sdb           # 添加分区

# 文件系统
mkfs.ext4 /dev/sdb1         # 格式化为ext4
mkfs.xfs /dev/sdb1          # 格式化为xfs
mkfs.btrfs /dev/sdb1        # 格式化为btrfs
mkfs.vfat /dev/sdb1         # 格式化为FAT32
e2label /dev/sdb1 label     # 设置ext4标签
xfs_admin -L label /dev/sdb1  # 设置xfs标签

# 挂载
mount /dev/sdb1 /mnt/data   # 挂载
mount -o remount,rw /       # 重新挂载为读写
umount /mnt/data             # 卸载
umount -l /mnt/data          # 延迟卸载（繁忙时）
mount -a                     # 挂载 /etc/fstab 中所有
cat /etc/fstab               # 开机挂载配置
findmnt                     # 查看挂载树
findmnt /mnt/data            # 查看特定挂载点

# 磁盘检查
fsck /dev/sdb1               # 文件系统检查（需卸载）
fsck -y /dev/sdb1            # 自动修复
badblocks /dev/sdb            # 检查坏道
smartctl -a /dev/sda          # SMART信息（需安装smartmontools）
```

### 6.2 LVM 逻辑卷管理

```bash
# 物理卷 PV
pvcreate /dev/sdb            # 创建物理卷
pvdisplay                    # 查看物理卷
pvs                          # 简要查看
pvremove /dev/sdb            # 删除物理卷

# 卷组 VG
vgcreate vgname /dev/sdb     # 创建卷组
vgextend vgname /dev/sdc     # 扩展卷组
vgdisplay                    # 查看卷组
vgs                          # 简要查看
vgreduce vgname /dev/sdc     # 从卷组移除
vgremove vgname              # 删除卷组

# 逻辑卷 LV
lvcreate -L 10G -n lvname vgname  # 创建10G逻辑卷
lvcreate -l 100%FREE -n lvname vgname  # 使用全部剩余空间
lvextend -L +5G /dev/vgname/lvname  # 扩展5G
lvextend -l +100%FREE /dev/vgname/lvname  # 扩展全部
resize2fs /dev/vgname/lvname  # ext4调整文件系统大小
xfs_growfs /mountpoint        # xfs调整（需挂载）
lvdisplay                    # 查看逻辑卷
lvs                          # 简要查看
lvremove /dev/vgname/lvname  # 删除逻辑卷
```

### 6.3 SWAP 交换空间

```bash
# 查看
free -h                     # 内存和swap
swapon --show               # swap详情
cat /proc/swaps             # swap列表

# 创建文件型swap
fallocate -l 4G /swapfile   # 创建4G文件
chmod 600 /swapfile         # 设置权限
mkswap /swapfile            # 格式化为swap
swapon /swapfile            # 启用
# 永久启用：/etc/fstab 添加
# /swapfile none swap sw 0 0

# 关闭和删除
swapoff /swapfile           # 关闭
rm /swapfile                # 删除文件

# swappiness（0-100，越小越少用swap）
cat /proc/sys/vm/swappiness # 查看当前值
sysctl vm.swappiness=10     # 临时设置
# 永久：/etc/sysctl.conf 添加 vm.swappiness=10
```

---

## 七、包管理与软件安装

### 7.1 Debian/Ubuntu（APT）

```bash
# 更新
apt update                  # 更新软件包索引
apt upgrade                 # 升级所有软件包
apt full-upgrade            # 智能升级（可能删除冲突包）

# 安装/卸载
apt install packageName     # 安装
apt install packageName=1.0  # 安装指定版本
apt remove packageName      # 卸载（保留配置）
apt purge packageName       # 卸载（删除配置）
apt autoremove              # 清理无用依赖
apt clean                   # 清理下载缓存
apt autoclean               # 清理无用缓存

# 查询
apt search keyword          # 搜索软件包
apt show packageName        # 查看软件包信息
apt list --installed        # 列出已安装包
apt list --upgradable       # 列出可升级包
dpkg -l                     # 列出所有已安装包
dpkg -l | grep keyword      # 搜索已安装包
dpkg -L packageName         # 查看包安装的文件
dpkg -i package.deb         # 安装 deb 包
dpkg -r packageName         # 卸载 deb 包
```

### 7.2 CentOS/RHEL（YUM/DNF）

```bash
# YUM（CentOS 7）
yum install packageName     # 安装
yum remove packageName      # 卸载
yum update                  # 升级所有
yum update packageName      # 升级指定包
yum search keyword          # 搜索
yum info packageName        # 查看信息
yum list installed          # 已安装列表
yum list updates            # 可更新列表
yum clean all               # 清理缓存
yum provides /path/to/file  # 查找文件属于哪个包
yum groupinstall "Group Name"  # 安装包组
yum localinstall package.rpm  # 安装本地rpm

# DNF（CentOS 8+/Fedora，命令与yum基本一致）
dnf install packageName
dnf remove packageName
dnf update
dnf search keyword
dnf info packageName
dnf list installed
dnf clean all

# RPM 包管理
rpm -ivh package.rpm        # 安装
rpm -e packageName          # 卸载
rpm -qa                     # 所有已安装包
rpm -qa | grep keyword      # 搜索
rpm -qi packageName         # 包信息
rpm -ql packageName         # 包安装的文件
rpm -qf /path/to/file       # 文件属于哪个包
rpm -V packageName          # 校验包文件完整性
```

### 7.3 其他包管理

```bash
# Alpine（apk）
apk update
apk add packageName
apk del packageName
apk search keyword
apk info packageName
apk upgrade

# Arch（pacman）
pacman -S packageName       # 安装
pacman -R packageName       # 卸载
pacman -Syu                 # 同步并升级
pacman -Ss keyword          # 搜索
pacman -Qi packageName      # 信息
pacman -Q                   # 已安装列表

# 源码编译安装
./configure --prefix=/usr/local
make
make install
# 卸载：make uninstall（如果支持）
```

---

## 八、日志管理

### 8.1 系统日志

```bash
# systemd journal
journalctl                    # 所有日志
journalctl -f                 # 实时跟踪
journalctl -n 100             # 最后100行
journalctl --since "2024-01-01" --until "2024-01-02"  # 时间范围
journalctl -u serviceName     # 指定服务
journalctl -u nginx -f        # 实时跟踪nginx
journalctl -p err             # 错误级别及以上
journalctl -p warning         # 警告级别及以上
journalctl -k                 # 内核日志
journalctl --boot             # 本次启动
journalctl --boot=-1          # 上一次启动
journalctl --disk-usage       # 日志占用空间
journalctl --vacuum-size=100M  # 清理到100M
journalctl --vacuum-time=7d    # 清理7天前

# 传统日志文件（/var/log/）
/var/log/messages             # 系统消息（CentOS）
/var/log/syslog               # 系统日志（Ubuntu）
/var/log/auth.log             # 认证日志（Ubuntu）
/var/log/secure               # 安全日志（CentOS）
/var/log/kern.log             # 内核日志
/var/log/cron                 # 定时任务日志
/var/log/boot.log             # 启动日志
/var/log/dmesg                # 内核启动信息
dmesg                         # 内核环形缓冲区日志
dmesg -T                      # 带时间戳
dmesg | grep -i error         # 过滤错误

# 应用日志
/var/log/nginx/               # Nginx日志
/var/log/apache2/             # Apache日志（Ubuntu）
/var/log/httpd/               # Apache日志（CentOS）
/var/log/mysql/               # MySQL日志
/var/log/redis/               # Redis日志
```

### 8.2 日志分析命令

```bash
# 实时查看
tail -f /var/log/nginx/access.log
tail -F /var/log/nginx/error.log  # 文件重建后继续跟踪
multitail /var/log/nginx/access.log /var/log/nginx/error.log  # 多文件（需安装）

# 统计分析
grep "404" /var/log/nginx/access.log | wc -l  # 404数量
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head 10  # TOP10 IP
awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -rn  # 状态码统计
awk '{sum += $10} END {print sum}' /var/log/nginx/access.log  # 总流量

# 日志切割（logrotate）
cat /etc/logrotate.conf       # 主配置
ls /etc/logrotate.d/          # 各服务配置
logrotate -d /etc/logrotate.d/nginx  # 调试模式（不实际执行）
logrotate -f /etc/logrotate.d/nginx  # 强制执行
```

---

## 九、性能监控与调优

### 9.1 CPU 性能

```bash
# 查看
top                          # 实时（1显示各核，P排序CPU）
mpstat -P ALL 1              # 每核统计（每秒）
vmstat 1                     # 系统整体（r队列、us/sy/id/wa/st）
sar -u 1 5                   # CPU历史统计

# 调优
# CPU调频
cpupower frequency-info      # 当前频率策略
cpupower frequency-set -g performance  # 性能模式
cpupower frequency-set -g powersave    # 节能模式

# 进程绑定CPU
taskset -c 0,1 command       # 绑定到CPU 0和1
taskset -cp 0,1 PID          # 修改运行中进程绑定

# 中断亲和性
cat /proc/interrupts          # 中断分布
```

### 9.2 内存性能

```bash
# 查看
free -h                      # 内存使用
cat /proc/meminfo            # 详细内存信息
vmstat 1                     # 虚拟内存（si/so交换、buff/cache）
sar -r 1 5                   # 内存历史
smem                        # 按进程内存（PSS，需安装）
pmap -x PID                  # 进程内存映射

# 调优
# 清理缓存（谨慎）
sync                         # 同步到磁盘
echo 1 > /proc/sys/vm/drop_caches   # 清理pagecache
echo 2 > /proc/sys/vm/drop_caches   # 清理dentries和inodes
echo 3 > /proc/sys/vm/drop_caches   # 全部清理

# OOM 调整
cat /proc/sys/vm/overcommit_memory  # 内存过量提交策略
# 0=启发式 1=总是过量 2=严格不超过swap+50%RAM
echo 2 > /proc/sys/vm/overcommit_memory

# 进程 OOM 优先级（-1000到1000，越小越不容易被杀）
cat /proc/PID/oom_score_adj
echo -500 > /proc/PID/oom_score_adj
```

### 9.3 磁盘 IO 性能

```bash
# 查看
iostat -xz 1                 # IO统计（%util、await、svctm）
iostat -d -x 1 /dev/sda      # 指定磁盘
iotop                        # 按进程IO（需安装，需root）
pidstat -d 1                 # 进程IO统计
sar -d 1 5                   # 磁盘历史
sar -b 1 5                   # IO传输历史

# 测试
dd if=/dev/zero of=testfile bs=1G count=1 oflag=direct  # 写速度测试
dd if=testfile of=/dev/null bs=1G iflag=direct           # 读速度测试
hdparm -Tt /dev/sda         # 硬盘读取速度（需安装）
fio --name=test --ioengine=libaio --rw=randread --bs=4k --size=1G --numjobs=4 --runtime=60  # 综合测试（需安装）

# 调优
# IO调度器
cat /sys/block/sda/queue/scheduler  # 当前调度器
echo deadline > /sys/block/sda/queue/scheduler  # 修改
# none/none(SSD), mq-deadline(通用), bfq(桌面), kyber(低延迟)

# 预读
cat /sys/block/sda/queue/read_ahead_kb  # 当前预读大小
echo 1024 > /sys/block/sda/queue/read_ahead_kb  # 增大预读
```

### 9.4 网络性能

```bash
# 查看
sar -n DEV 1 5              # 网络接口统计
sar -n TCP,ETCP 1 5         # TCP统计
ss -s                        # socket统计
cat /proc/net/snmp           # 网络协议统计
cat /proc/net/netstat        # 扩展网络统计

# 调优（sysctl）
# /etc/sysctl.conf
net.core.somaxconn = 65535           # 最大连接队列
net.core.netdev_max_backlog = 65535   # 网卡队列
net.ipv4.tcp_max_syn_backlog = 65535   # SYN队列
net.ipv4.tcp_fin_timeout = 30           # FIN超时
net.ipv4.tcp_tw_reuse = 1               # TIME_WAIT复用
net.ipv4.ip_local_port_range = 1024 65535  # 本地端口范围
net.core.rmem_max = 16777216            # 最大接收缓冲
net.core.wmem_max = 16777216            # 最大发送缓冲
# 应用：sysctl -p
```

---

## 十、安全与防火墙

### 10.1 防火墙

```bash
# firewalld（CentOS 7+/RHEL）
systemctl start firewalld
firewall-cmd --state                    # 状态
firewall-cmd --list-all                 # 所有规则
firewall-cmd --list-ports               # 开放端口
firewall-cmd --list-services            # 开放服务
firewall-cmd --permanent --add-port=8080/tcp    # 永久开放端口
firewall-cmd --permanent --remove-port=8080/tcp # 移除端口
firewall-cmd --permanent --add-service=http       # 开放服务
firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="192.168.1.0/24" accept'  # 富规则
firewall-cmd --reload                    # 重新加载（永久规则生效）
firewall-cmd --get-default-zone          # 默认区域
firewall-cmd --set-default-zone=public   # 设置默认区域

# iptables（通用）
iptables -L -n -v                         # 查看规则
iptables -L -n --line-numbers            # 带行号
iptables -A INPUT -p tcp --dport 80 -j ACCEPT  # 添加规则
iptables -I INPUT 1 -p tcp --dport 443 -j ACCEPT  # 插入到第1行
iptables -D INPUT 1                       # 删除第1行规则
iptables -F                                # 清空所有规则
iptables -P INPUT DROP                     # 默认策略DROP
iptables-save > /etc/iptables.rules       # 保存规则
iptables-restore < /etc/iptables.rules    # 恢复规则

# ufw（Ubuntu）
ufw status                                 # 状态
ufw enable                                 # 启用
ufw disable                                # 禁用
ufw allow 80/tcp                           # 允许端口
ufw deny 80/tcp                            # 拒绝端口
ufw allow from 192.168.1.0/24            # 允许IP段
ufw delete allow 80/tcp                    # 删除规则
ufw status verbose                         # 详细状态
```

### 10.2 SSH 安全

```bash
# 配置文件 /etc/ssh/sshd_config
Port 2222                                # 修改端口（非默认更安全）
PermitRootLogin no                       # 禁止root登录
PasswordAuthentication no                # 禁止密码登录（用密钥）
PubkeyAuthentication yes                 # 允许密钥登录
AllowUsers username                      # 只允许特定用户
MaxAuthTries 3                           # 最大尝试次数
ClientAliveInterval 300                  # 保活间隔
ClientAliveCountMax 2                    # 保活次数

# 重启服务
systemctl restart sshd                   # CentOS
systemctl restart ssh                    # Ubuntu

# 密钥登录
ssh-keygen -t ed25519 -C "email"        # 生成ed25519密钥
ssh-keygen -t rsa -b 4096 -C "email"    # 生成RSA密钥
ssh-copy-id user@host                    # 上传公钥到服务器
ssh -i /path/to/key user@host           # 指定密钥登录

# SSH 常用
ssh user@host                            # 登录
ssh -p 2222 user@host                    # 指定端口
ssh -L 8080:localhost:80 user@host       # 本地端口转发
ssh -R 8080:localhost:80 user@host       # 远程端口转发
ssh -D 1080 user@host                    # SOCKS代理
scp file.txt user@host:/path/            # 上传文件
scp user@host:/path/file.txt ./          # 下载文件
scp -r dir user@host:/path/              # 上传目录
rsync -avz ./dir user@host:/path/        # 同步目录（增量）
rsync -avz --delete user@host:/path/ ./  # 镜像同步（删除多余）
```

### 10.3 用户安全

```bash
# 密码策略
# /etc/login.defs
PASS_MAX_DAYS 90              # 密码最大有效期
PASS_MIN_DAYS 7               # 密码最小间隔
PASS_WARN_AGE 7               # 过期警告天数

# PAM 密码复杂度（/etc/pam.d/system-auth）
# password requisite pam_pwquality.so minlen=12 dcredit=-1 ucredit=-1 lcredit=-1 ocredit=-1

# 账户锁定（失败N次锁定）
# /etc/pam.d/system-auth 添加
# auth required pam_faillock.so preauth silent deny=5 unlock_time=300
# auth [default=die] pam_faillock.so authfail deny=5 unlock_time=300

faillock --user username      # 查看用户失败次数
faillock --user username --reset  # 重置

# sudo 权限
visudo                       # 编辑sudoers（安全编辑）
# username ALL=(ALL) ALL     # 全部权限
# username ALL=(ALL) NOPASSWD: ALL  # 免密码
# %groupname ALL=(ALL) ALL   # 组权限
sudo -l                      # 查看当前用户sudo权限
```

### 10.4 系统安全检查

```bash
# 登录审计
last                          # 登录历史
lastb                         # 失败登录
lastlog                       # 所有用户最后登录
who / w                       # 当前登录用户
users                         # 登录用户名列表

# 进程检查
ps aux --sort=-%cpu | head    # 高CPU进程
ps aux --sort=-%mem | head    # 高内存进程
ls -la /proc/*/exe 2>/dev/null | grep deleted  # 已删除但仍运行的程序（可疑）

# 网络检查
ss -tunap                     # 所有网络连接和监听
netstat -tunap                # 同上（旧）
lsof -i -P -n                 # 打开的网络连接
lsof -i :80                   # 占用80端口的进程

# 定时任务检查
crontab -l                    # 当前用户
crontab -u username -l        # 指定用户
ls -la /etc/cron.d/           # 系统cron目录
ls -la /etc/cron.daily/       # 每日任务
ls -la /var/spool/cron/       # 用户cron

# 系统服务
systemctl list-units --type=service --state=running  # 运行中服务
systemctl list-unit-files --type=service --state=enabled  # 开机自启服务

# 后门检查
chkrootkit                    # rootkit检测（需安装）
rkhunter --check              # rootkit检测（需安装）
clamscan -r /                 # 病毒扫描（ClamAV，需安装）

# 文件完整性
find / -perm -4000 2>/dev/null  # SUID文件
find / -perm -2000 2>/dev/null  # SGID文件
find / -nouser -o -nogroup 2>/dev/null  # 无属主文件
```

---

## 十一、文本处理三剑客

### 11.1 grep（查找）

```bash
# 基本用法
grep "pattern" file.txt       # 查找包含pattern的行
grep -i "pattern" file.txt    # 忽略大小写
grep -v "pattern" file.txt    # 反向匹配（不包含）
grep -n "pattern" file.txt    # 显示行号
grep -c "pattern" file.txt    # 统计匹配行数
grep -l "pattern" *.txt       # 只显示匹配的文件名
grep -r "pattern" /dir        # 递归搜索目录
grep -w "word" file.txt       # 匹配整个单词
grep -A 3 "pattern" file.txt  # 显示匹配行及后3行
grep -B 3 "pattern" file.txt  # 显示匹配行及前3行
grep -C 3 "pattern" file.txt  # 显示匹配行及前后各3行
grep -E "pat1|pat2" file.txt  # 扩展正则（或）
grep -E "[0-9]+" file.txt     # 正则匹配数字
grep -f patterns.txt file.txt  # 从文件读取模式
grep --color=auto "pattern" file.txt  # 高亮显示

# 常用正则
^pattern                      # 行首
pattern$                      # 行尾
.                             # 任意单个字符
*                             # 前一个字符0次或多次
+                             # 前一个字符1次或多次（需-E）
?                             # 前一个字符0次或1次（需-E）
[abc]                         # 字符集
[^abc]                        # 排除字符集
[a-z]                         # 范围
|                             # 或（需-E）
\                             # 转义
```

### 11.2 sed（编辑）

```bash
# 基本用法
sed 's/old/new/' file.txt     # 替换每行第一个old为new
sed 's/old/new/g' file.txt    # 全局替换
sed 's/old/new/2' file.txt    # 替换每行第2个
sed -i 's/old/new/g' file.txt # 直接修改文件（危险！）
sed -i.bak 's/old/new/g' file.txt  # 修改并备份.bak

# 行操作
sed -n '5p' file.txt          # 显示第5行
sed -n '5,10p' file.txt       # 显示5-10行
sed -n '5,$p' file.txt         # 显示第5行到末尾
sed '5d' file.txt              # 删除第5行
sed '5,10d' file.txt           # 删除5-10行
sed '/pattern/d' file.txt       # 删除匹配行
sed '/^$/d' file.txt            # 删除空行
sed '/^\s*$/d' file.txt         # 删除空白行（含空格）
sed -i '/^#/d' file.txt         # 删除注释行

# 插入/追加
sed '5i\new line' file.txt     # 第5行前插入
sed '5a\new line' file.txt     # 第5行后追加
sed '/pattern/a\new line' file.txt  # 匹配行后追加

# 替换高级
sed 's/old/new/gI' file.txt    # 忽略大小写替换
sed 's#old#new#g' file.txt     # 用#作分隔符（路径中有/时）
sed -E 's/([0-9]+)/\1/g' file.txt  # 分组引用
sed 's/^/prefix/' file.txt      # 行首添加
sed 's/$/suffix/' file.txt      # 行尾添加

# 多命令
sed -e 's/old/new/g' -e '5d' file.txt  # 多个命令
```

### 11.3 awk（处理）

```bash
# 基本用法
awk '{print $0}' file.txt      # 打印整行
awk '{print $1}' file.txt       # 打印第1列（默认空格分隔）
awk '{print $1, $3}' file.txt   # 打印第1和第3列
awk -F: '{print $1}' /etc/passwd  # 用:分隔
awk -F',' '{print $1}' file.csv   # 用,分隔（CSV）
awk '{print NF, $0}' file.txt   # NF=字段数
awk '{print NR, $0}' file.txt   # NR=行号

# 条件
awk '$3 > 100' file.txt         # 第3列大于100
awk '$1 == "root"' /etc/passwd  # 第1列等于root
awk '/pattern/' file.txt         # 匹配pattern的行
awk '$3 > 100 {print $1, $3}' file.txt  # 条件+动作

# 内置变量
NF                            # 字段数
NR                            # 行号（所有文件）
FNR                           # 行号（当前文件）
FS                            # 输入分隔符
OFS                           # 输出分隔符
RS                            # 输入记录分隔符
ORS                           # 输出记录分隔符
FILENAME                      # 当前文件名

# BEGIN/END
awk 'BEGIN {sum=0} {sum+=$3} END {print sum}' file.txt  # 求和
awk 'BEGIN {print "Header"} {print} END {print "Footer"}' file.txt
awk -F: 'BEGIN {count=0} {count++} END {print count}' /etc/passwd  # 统计行数

# 数组
awk '{count[$1]++} END {for (ip in count) print count[ip], ip}' access.log | sort -rn  # IP访问统计

# 常用示例
# 统计Nginx日志TOP10 IP
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head 10
# 统计状态码
awk '{print $9}' access.log | sort | uniq -c | sort -rn
# 计算总流量
awk '{sum += $10} END {print sum/1024/1024 " MB"}' access.log
# 打印大于1000字节的请求
awk '$10 > 1000 {print $7, $10}' access.log
```

---

## 十二、压缩与归档

```bash
# tar
tar -cvf archive.tar /dir       # 创建tar包
tar -xvf archive.tar             # 解压
tar -tvf archive.tar             # 查看内容
tar -czvf archive.tar.gz /dir    # 创建tar.gz（gzip压缩）
tar -xzvf archive.tar.gz         # 解压tar.gz
tar -cjvf archive.tar.bz2 /dir   # 创建tar.bz2（bzip2压缩，更小更慢）
tar -xjvf archive.tar.bz2         # 解压tar.bz2
tar -cJvf archive.tar.xz /dir     # 创建tar.xz（xz压缩，最小最慢）
tar -xJvf archive.tar.xz          # 解压tar.xz
tar -xzvf archive.tar.gz -C /tmp  # 解压到指定目录
tar -rvf archive.tar newfile      # 追加文件到tar
tar --exclude='*.log' -czvf archive.tar.gz /dir  # 排除文件

# gzip
gzip file.txt                     # 压缩（生成file.txt.gz，删除原文件）
gzip -d file.txt.gz               # 解压
gzip -k file.txt                  # 压缩但保留原文件
gzip -9 file.txt                  # 最高压缩比
gunzip file.txt.gz                # 解压（同gzip -d）
zcat file.txt.gz                  # 查看压缩文件内容

# bzip2
bzip2 file.txt                    # 压缩
bzip2 -d file.txt.bz2             # 解压
bunzip2 file.txt.bz2              # 解压
bzcat file.txt.bz2                # 查看内容

# xz
xz file.txt                       # 压缩
xz -d file.txt.xz                 # 解压
unxz file.txt.xz                  # 解压
xzcat file.txt.xz                 # 查看内容

# zip/unzip
zip archive.zip file1 file2       # 创建zip
zip -r archive.zip /dir           # 递归压缩目录
zip -e archive.zip file.txt       # 加密压缩（输入密码）
unzip archive.zip                 # 解压
unzip -l archive.zip              # 查看内容
unzip archive.zip -d /tmp         # 解压到指定目录
unzip -P password archive.zip     # 密码解压

# 7z（需安装p7zip）
7z a archive.7z /dir              # 创建7z
7z x archive.7z                   # 解压
7z l archive.7z                   # 查看内容
7z a -p archive.7z /dir           # 加密

# 其他
zcat /var/log/syslog.2.gz         # 查看压缩日志
zgrep "pattern" file.gz            # 在压缩文件中grep
zless file.gz                      # 分页查看压缩文件
```

---

## 十三、定时任务（Cron）

```bash
# 管理
crontab -l                        # 查看当前用户的cron
crontab -e                        # 编辑当前用户的cron
crontab -r                        # 删除当前用户的cron
crontab -u username -l            # 查看指定用户
crontab -u username -e            # 编辑指定用户（需root）

# 格式
# 分 时 日 月 周 命令
# * * * * * command
# */5 * * * * command    每5分钟
# 0 * * * * command      每小时整点
# 0 0 * * * command      每天凌晨
# 0 2 * * * command      每天凌晨2点
# 0 2 * * 0 command      每周日凌晨2点
# 0 2 1 * * command      每月1号凌晨2点
# 30 8 * * 1-5 command   周一到周五8:30

# 特殊字符串
@reboot        # 开机时执行
@yearly        # 每年（0 0 1 1 *）
@annually      # 每年（同@yearly）
@monthly       # 每月（0 0 1 * *）
@weekly        # 每周（0 0 * * 0）
@daily         # 每天（0 0 * * *）
@midnight      # 每天（同@daily）
@hourly        # 每小时（0 * * * *）

# 示例
# 每天凌晨2点备份数据库
0 2 * * * /usr/bin/mysqldump -u root -ppassword dbname > /backup/db_$(date +\%Y\%m\%d).sql
# 每5分钟检查服务状态
*/5 * * * * /usr/bin/systemctl is-active nginx || /usr/bin/systemctl start nginx
# 每周日凌晨3点清理7天前日志
0 3 * * 0 /usr/bin/find /var/log -name "*.log.*" -mtime +7 -delete

# 系统级cron（/etc/crontab 和 /etc/cron.d/）
# 格式多了用户名字段
# 分 时 日 月 周 用户名 命令
0 2 * * * root /backup/script.sh

# 日志
tail -f /var/log/cron            # CentOS
tail -f /var/log/syslog | grep CRON  # Ubuntu
```

---

## 十四、系统启动与引导

```bash
# 启动级别（systemd targets）
systemctl get-default            # 当前默认target
systemctl set-default multi-user.target  # 设置为命令行模式
systemctl set-default graphical.target   # 设置为图形模式

# 常用targets
poweroff.target                 # 关机
rescue.target                   # 救援模式（单用户）
multi-user.target               # 多用户命令行
graphical.target                # 图形界面
reboot.target                   # 重启

# 切换
systemctl isolate rescue.target  # 切换到救援模式
systemctl isolate multi-user.target  # 切换到命令行

# 启动项
systemctl list-unit-files --type=service --state=enabled  # 开机自启服务
systemd-analyze blame            # 分析启动耗时（各服务）
systemd-analyze critical-chain   # 关键启动链
systemd-analyze time             # 启动总时间

# GRUB
# /etc/default/grub
GRUB_TIMEOUT=5                  # 菜单等待时间
GRUB_DEFAULT=0                  # 默认启动项
update-grub                     # 更新GRUB配置（Ubuntu）
grub2-mkconfig -o /boot/grub2/grub.cfg  # CentOS

# 单用户模式（忘记密码）
# 重启 → GRUB菜单按e → 找到linux行 → ro改为rw init=/sysroot/bin/sh → Ctrl+X
# chroot /sysroot
# passwd root
# touch /.autorelabel
# exit
# reboot
```

---

## 十五、常见故障排查流程

### 15.1 系统无法启动

```text
1. 查看启动错误信息（屏幕输出）
2. 进入单用户/救援模式
3. 检查文件系统：fsck /dev/sda1
4. 检查/etc/fstab配置错误
5. 检查GRUB配置
6. 查看journalctl --boot=-1（上一次启动日志）
7. 救援模式chroot修复
```

### 15.2 系统变慢

```text
1. uptime → 查看负载
2. top/htop → 查看高CPU/内存进程
3. vmstat 1 → 查看整体（r队列、wa IO等待、si/so交换）
4. iostat -xz 1 → 查看磁盘IO
5. free -h → 查看内存（是否用swap）
6. df -h → 查看磁盘是否满
7. ss -s → 查看连接数
8. sar → 查看历史性能数据
```

### 15.3 服务无法访问

```text
1. 服务是否运行：systemctl status serviceName
2. 端口是否监听：ss -tlnp | grep port
3. 防火墙是否放行：firewall-cmd --list-ports / iptables -L
4. 本地能否访问：curl localhost:port
5. 远程能否访问：curl server_ip:port
6. DNS是否正常：nslookup/dig domain
7. 路由是否通：ping/traceroute
8. 查看服务日志：journalctl -u serviceName -n 100
```

### 15.4 磁盘满

```text
1. df -h → 哪个分区满
2. du -sh /* | sort -rh → 哪个目录大
3. du -h --max-depth=1 /var → 深入查找
4. 常见大文件：日志(/var/log)、数据库、Docker镜像、core dump、缓存
5. 清理日志：journalctl --vacuum-size=100M / truncate -s 0 /var/log/xxx
6. 清理Docker：docker system prune -a
7. 查找大文件：find / -size +100M -exec ls -lh {} \;
8. 注意：已删除但被进程占用的文件（lsof | grep deleted），需重启进程释放
```

### 15.5 内存不足/OOM

```text
1. free -h → 内存使用
2. top/htop → 高内存进程（M排序）
3. dmesg | grep -i oom → OOM kill记录
4. /var/log/messages 或 journalctl -k → 内核OOM日志
5. smem → 按进程PSS统计
6. 增加swap或内存
7. 调整swappiness
8. 限制进程内存（cgroups/systemd）
9. 优化应用内存使用
```

### 15.6 网络不通

```text
1. 网卡是否启用：ip link
2. IP是否正确：ip addr
3. 网关是否通：ping gateway_ip
4. DNS是否通：ping 8.8.8.8 / ping google.com
5. 路由表：ip route
6. 端口连通：nc -zv host port / telnet
7. 防火墙：iptables -L / firewall-cmd --list-all
8. 抓包：tcpdump -i eth0 port 80
9. 检查/etc/resolv.conf
10. 检查/etc/hosts
```

---

## 十六、运维脚本示例

### 16.1 系统巡检脚本

```bash
#!/bin/bash
# system_check.sh - 系统巡检脚本
echo "========== 系统巡检报告 =========="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "主机名: $(hostname)"
echo "系统: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "内核: $(uname -r)"
echo ""

echo "========== 1. 系统负载 =========="
uptime
echo ""

echo "========== 2. CPU 使用 =========="
top -bn1 | grep "Cpu(s)" | awk '{print "用户:"$2"% 系统:"$4"% 空闲:"$8"%"}'
echo ""

echo "========== 3. 内存使用 =========="
free -h | awk 'NR==2{printf "总计:%s 已用:%s 空闲:%s 缓存:%s\n",$2,$3,$4,$6}'
echo ""

echo "========== 4. 磁盘使用 =========="
df -h | awk 'NR>1{print $6": "$5" 已用 ("$3"/"$2")"}'
echo ""

echo "========== 5. 监听端口 =========="
ss -tlnp | awk 'NR>1{print $4" -> "$NF}'
echo ""

echo "========== 6. 关键服务状态 =========="
for svc in nginx mysql docker; do
  if systemctl is-active --quiet $svc; then
    echo "$svc: 运行中"
  else
    echo "$svc: 未运行!"
  fi
done
echo ""

echo "========== 7. 登录用户 =========="
who
echo ""

echo "========== 巡检完成 =========="
```

### 16.2 自动备份脚本

```bash
#!/bin/bash
# backup.sh - 自动备份脚本
BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d_%H%M%S)
KEEP_DAYS=7

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
echo "[$(date)] 开始备份数据库..."
mysqldump -u root -p'password' --all-databases | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# 备份配置文件
echo "[$(date)] 开始备份配置文件..."
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /etc/nginx /etc/mysql /etc/ssh

# 备份网站
echo "[$(date)] 开始备份网站..."
tar -czf $BACKUP_DIR/www_$DATE.tar.gz /var/www

# 清理旧备份
echo "[$(date)] 清理 $KEEP_DAYS 天前的备份..."
find $BACKUP_DIR -name "*.gz" -mtime +$KEEP_DAYS -delete

# 同步到远程（可选）
# rsync -avz $BACKUP_DIR/ user@backup-server:/backup/

echo "[$(date)] 备份完成!"
ls -lh $BACKUP_DIR/*$DATE*
```

### 16.3 日志切割脚本

```bash
#!/bin/bash
# log_rotate.sh - 手动日志切割
LOG_DIR="/var/log/myapp"
LOG_FILE="app.log"
KEEP_FILES=10

cd $LOG_DIR

# 如果日志文件存在且大于100M
if [ -f "$LOG_FILE" ] && [ $(stat -c%s "$LOG_FILE") -gt 104857600 ]; then
  echo "[$(date)] 开始切割日志..."
  
  # 重命名当前日志
  mv $LOG_FILE ${LOG_FILE}.$(date +%Y%m%d_%H%M%S)
  
  # 发送信号让应用重新打开日志（按实际应用调整）
  # kill -USR1 $(cat /var/run/myapp.pid)
  # 或重启应用
  systemctl reload myapp
  
  # 压缩旧日志
  gzip ${LOG_FILE}.* 2>/dev/null
  
  # 清理旧文件
  ls -t ${LOG_FILE}.*.gz | tail -n +$((KEEP_FILES+1)) | xargs rm -f
  
  echo "[$(date)] 日志切割完成"
fi
```

---

## 十七、各发行版差异

| 功能 | CentOS/RHEL | Ubuntu/Debian | Alpine |
|------|------------|--------------|--------|
| **包管理** | yum/dnf/rpm | apt/dpkg | apk |
| **服务管理** | systemctl | systemctl | openrc/rc-service |
| **网络配置** | /etc/sysconfig/network-scripts/ | /etc/netplan/ | /etc/network/interfaces |
| **主机名** | hostnamectl | hostnamectl | hostname |
| **系统日志** | /var/log/messages | /var/log/syslog | /var/log/messages |
| **安全日志** | /var/log/secure | /var/log/auth.log | /var/log/messages |
| **防火墙** | firewalld/iptables | ufw/iptables | iptables |
| **默认shell** | bash | bash | ash (BusyBox) |
| **默认编辑器** | vi | nano/vi | vi |
| **root默认** | 有root | sudo | 有root |
| **SELinux** | 默认启用 | 不安装 | 不安装 |
| **运行级别** | systemd targets | systemd targets | openrc runlevels |

---

## 十八、关联笔记

### Linux 与运维
- [[Linux系统管理与常用命令]] · [[PowerShell脚本自动化]] · [[Bash脚本编程]]
- [[Docker容器化]] · [[K8s-核心概念与架构]] · [[Ansible-配置管理]]

### 云原生
- [[Prometheus-指标采集]] · [[Grafana-可视化看板_backup_skeleton]] · [[ELK日志栈]]
- [[CI-CD流水线]] · [[Terraform-基础设施编排]]

### 导航
- [[MOC-云原生与运维]] · [[MOC-Linux]] · [[MOC-综合导航]] · [[Home]]

> 🔍 **知识点深度解析**
>
> **作用**：Linux 运维常用命令手册解决的是「Linux 服务器日常运维工作中命令查询和操作效率的问题」——Linux 系统管理涉及系统信息、文件操作、用户权限、进程服务、网络、磁盘、包管理、日志、性能、安全、文本处理等众多领域，命令数量庞大（数百个），参数复杂，运维工程师不可能全部记住。一个系统化、分类清晰、可快速查阅的命令手册，能大大提高运维工作效率，减少查文档的时间，避免记错参数导致操作失误。它是运维工程师的「随身工具箱」和「速查字典」。
>
> **底层原理**：①Linux 的设计哲学是「一切皆文件」——系统信息在 /proc 和 /sys 伪文件系统中（cpuinfo/meminfo/loadavg/interrupts），设备在 /dev，配置在 /etc，日志在 /var/log，所以很多「查看命令」本质上是读取这些文件（cat /proc/cpuinfo）。②systemd 是现代 Linux 的 init 系统和服务管理器——它统一管理系统服务（systemctl）、日志（journalctl）、设备（udev）、网络（systemd-networkd）、定时（systemd timer），是理解现代 Linux 运维的核心。③权限模型基于「用户-组-其他」的三位八进制（rwx=4+2+1），加上 SUID/SGID/Sticky Bit 特殊权限和 ACL 扩展权限，控制文件和进程的访问权限。④网络栈基于 TCP/IP，通过 iproute2（ip/ss）或 net-tools（ifconfig/netstat）管理，抓包用 libpcap（tcpdump），防火墙用 netfilter（iptables/nftables）。⑤性能分析基于「负载-资源-瓶颈」模型——CPU（top/mpstat/vmstat）、内存（free/vmstat/smem）、磁盘IO（iostat/iotop）、网络（sar/ss/tcpdump），通过 sar 等工具收集历史数据，定位性能瓶颈。
>
> **用法要点**：① 系统信息：uname/hostnamectl/os-release（系统）、lscpu/free/lsblk/df/du（硬件资源）、uptime/w/top/htop（负载和进程） ② 文件：ls/cd/pwd/mkdir/touch/cp/mv/rm/ln（基本）、cat/more/less/head/tail/wc（查看）、find/locate/which/whereis（查找） ③ 用户权限：useradd/passwd/usermod/userdel/id/who/last（用户）、chmod/chown/chgrp/getfacl/setfacl（权限，r=4 w=2 x=1） ④ 进程服务：ps/top/htop/pstree/pgrep/kill/killall/pkill/nice/renice（进程）、systemctl start/stop/restart/status/enable/disable/daemon-reload（服务）、journalctl -u/-f/--since/-n（日志） ⑤ 网络：ip addr/link/route/neigh（配置）、ping/traceroute/mtr（连通性）、telnet/nc/ss/netstat（端口）、curl/wget（HTTP）、dig/nslookup/host（DNS）、tcpdump/iftop/nethogs（抓包/流量） ⑥ 磁盘：lsblk/fdisk/df/du（查看）、fdisk/parted/mkfs/mount/umount/fstab（分区/格式化/挂载）、fsck/smartctl（检查）、LVM（pvcreate/vgcreate/lvcreate/lvextend/resize2fs）、SWAP（mkswap/swapon/free） ⑦ 包管理：apt（Debian/Ubuntu）、yum/dnf（CentOS/RHEL）、apk（Alpine）、pacman（Arch）、rpm/dpkg（底层包管理） ⑧ 日志：journalctl（systemd）、/var/log/（传统日志文件 messages/syslog/auth/secure/kern/cron）、dmesg（内核）、tail -f/multitail（实时）、grep/awk/sed（分析）、logrotate（切割） ⑨ 性能：CPU（top/mpstat/vmstat/sar）、内存（free/vmstat/smem/pmap）、磁盘IO（iostat/iotop/pidstat/sar/dd/fio）、网络（sar/ss/tcpdump/sysctl调优） ⑩ 安全：firewalld/iptables/ufw（防火墙）、sshd_config/ssh-keygen/ssh-copy-id（SSH安全）、passwd/pam_faillock/sudo（用户安全）、last/lastb/who/loginctl（登录审计）、chkrootkit/rkhunter/clamscan（后门/病毒）、find / -perm -4000（SUID检查） ⑪ 文本三剑客：grep（查找，-i/-v/-n/-c/-r/-A/-B/-C/-E）、sed（编辑，s替换/d删除/i插入/a追加）、awk（处理，$字段/NF/NR/BEGIN/END/数组） ⑫ 压缩：tar（cvf/xvf/czvf/xzvf/cjvf/cJvf）、gzip/bzip2/xz/zip/7z ⑬ Cron：crontab -l/-e/-r、格式 分 时 日 月 周、@reboot/@daily/@hourly ⑭ 排查流程：系统变慢（uptime→top→vmstat→iostat→free→df→ss）、服务不可访问（status→ss→防火墙→curl本地→curl远程→DNS→路由→日志）、磁盘满（df→du→找大文件→清理日志/Docker→lsof deleted）、OOM（free→top→dmesg OOM→smem→增加swap/内存）、网络不通（ip link→ip addr→ping网关→ping 8.8.8.8→ping域名→ip route→nc端口→防火墙→tcpdump）。

> 💡 **深度讲解**：Linux 运维最核心的智慧是「一切皆文件」的设计哲学——在 Linux 中，几乎所有东西都被抽象为文件：进程信息在 /proc，硬件信息在 /sys，设备在 /dev，配置在 /etc，日志在 /var/log，套接字在 /proc/net，甚至网络接口也可以通过 /sys/class/net 访问。这种「一切皆文件」的设计让 Linux 的管理接口高度统一——你不需要为每种资源学习不同的 API，只需要学会读写文件就能管理几乎所有系统资源。cat /proc/cpuinfo 查看 CPU，cat /proc/meminfo 查看内存，cat /proc/loadavg 查看负载，echo 1 > /proc/sys/vm/drop_caches 清理缓存——这些命令本质上都是文件操作。这种统一的抽象是 Linux 强大而优雅的根源。「systemd 是现代 Linux 运维的核心」——传统的 SysVinit 时代，服务管理用 service/chkconfig，日志在 /var/log 各个文件，设备用 udev，网络用 init 脚本，定时用 cron，每个子系统独立管理，配置分散，学习成本高。systemd 统一了这一切：服务管理用 systemctl，日志用 journalctl（统一的结构化日志，支持按服务/时间/级别/启动批次过滤），设备用 systemd-udevd，网络用 systemd-networkd，定时用 systemd timer（比 cron 更强大，支持依赖关系和日志），甚至登录管理用 loginctl。这种统一大大降低了运维复杂度——你只需要学习 systemctl 和 journalctl 两个命令，就能管理大部分系统服务和日志。这也是为什么现代 Linux 发行版（CentOS 7+/Ubuntu 16.04+）都转向了 systemd。「排查问题的方法论比记住命令更重要」——很多运维新手遇到问题时会慌乱地敲各种命令，希望碰巧找到原因；而资深运维工程师有一套系统化的排查流程：先看整体（uptime/top/df/free），再定位范围（是 CPU 问题还是内存问题还是磁盘 IO 问题还是网络问题），然后深入具体（高 CPU 是哪个进程？高内存是哪个进程？磁盘满是哪个目录？网络不通是哪一层？），最后修复验证。这种「从整体到局部、从现象到原因」的排查方法论，比记住一百个命令更有价值。命令会忘，但方法论一旦掌握就不会忘。这也是为什么本手册专门整理了「常见故障排查流程」——它教你的不是命令，而是「如何思考和排查问题」。

> 📝 **精简总结**：Linux运维命令分类：系统信息(uname/hostnamectl/lscpu/free/df/uptime/top)、文件(ls/cd/cp/mv/rm/cat/less/head/tail/find)、用户权限(useradd/passwd/chmod/chown/id/who/last)、进程服务(ps/top/kill/systemctl/journalctl)、网络(ip/ping/traceroute/nc/ss/curl/dig/tcpdump)、磁盘(lsblk/fdisk/mkfs/mount/fstab/LVM/swap)、包管理(apt/yum/dnf/apk/rpm/dpkg)、日志(journalctl//var/log/tail -f/grep/awk/logrotate)、性能(top/vmstat/iostat/sar/iotop/smem)、安全(firewalld/iptables/ufw/ssh/chkrootkit)、文本三剑客(grep/sed/awk)、压缩(tar/gzip/zip)、定时(crontab)。排查流程：系统变慢(uptime→top→vmstat→iostat→free→df)、服务不可访问(status→ss→防火墙→curl→DNS→日志)、磁盘满(df→du→清理)、OOM(free→top→dmesg)、网络不通(ip→ping→nc→防火墙→tcpdump)。发行版差异：CentOS(yum/firewalld/messages)、Ubuntu(apt/ufw/syslog)、Alpine(apk/openrc)。

> **学习路径建议**：先学习 [[Linux系统管理与常用命令]] 掌握基础命令 → 学习本文档掌握运维常用命令和排查方法 → 实践：在虚拟机/云服务器上练习各种命令 → 学习 [[Bash脚本编程]] 掌握脚本编写 → 学习 [[Docker容器化]] 和 [[K8s-核心概念与架构]] 理解容器化运维 → 学习 [[Ansible-配置管理]] 和 [[Terraform-基础设施编排]] 掌握自动化运维 → 学习 [[Prometheus-指标采集]] 和 [[ELK日志栈]] 掌握监控和日志 → 备考 RHCE/LPIC 认证系统学习 → 在实际工作中积累运维经验和排障案例。

---

> **Linux 运维命令手册的本质是「将数百个命令和操作系统化、结构化，变成可快速查阅和执行的知识体系」——Linux 是一个「由命令驱动的操作系统」，几乎所有操作都通过命令完成，从查看系统信息到配置网络，从管理用户到排查故障，从安装软件到性能调优，都有对应的命令。但命令数量庞大（数百个），参数复杂（每个命令可能有几十个参数），运维工程师不可能全部记住，也不需要全部记住——关键是建立一个「系统化的知识框架」，知道「什么问题该用什么类别的命令」，具体参数可以查手册或用 --help。这就是命令手册的价值：它不是让你「背命令」，而是让你「建立命令的分类体系和排查方法论」，在遇到问题时能快速定位到正确的命令类别，然后查具体用法。当你掌握了这个体系，Linux 运维就不再是「记命令的苦差事」，而是「系统化的工程实践」——你知道系统的各个层面（硬件/内核/进程/文件/网络/服务），知道每个层面有哪些工具，知道如何从现象到原因层层排查，知道如何自动化重复性工作。这就是资深运维工程师和新手的区别：不是记住了多少命令，而是建立了多深的系统理解和多清晰的排查方法论。**



## 补充：概述

Linux 运维命令是后端开发和运维工程师的必备技能，服务器的状态查看、性能分析、故障排查、日常维护都离不开命令行操作。与开发人员常用的基础命令不同，运维命令更关注系统监控、性能分析、网络诊断、进程管理、日志分析、服务管理等运维场景。

| 命令类别 | 代表命令 | 核心用途 |
|---------|---------|---------|
| 系统信息 | uname/hostnamectl/lscpu/lsmem | 查看系统版本、CPU、内存信息 |
| 性能监控 | top/htop/vmstat/mpstat/iostat/sar | 实时监控 CPU、内存、IO、网络性能 |
| 进程管理 | ps/pstree/kill/pkill/nice/renice/pgrep | 查看和管理进程、调整优先级 |
| 内存管理 | free/vmstat/pmap/smem/slabtop | 查看内存使用、缓存、Swap |
| 磁盘 IO | iostat/iotop/df/du/lsblk/blkid/fdisk | 磁盘空间、IO 性能、分区管理 |
| 网络诊断 | ss/netstat/ip/ping/traceroute/tcpdump/dig/curl | 网络连接、路由、抓包、DNS、HTTP 测试 |
| 日志分析 | tail/head/less/grep/awk/sed/cut/sort/uniq/wc/journalctl | 查看、过滤、分析日志文件 |
| 服务管理 | systemctl/service/journalctl/systemd-analyze | 管理系统服务、查看服务日志 |
| 用户权限 | useradd/usermod/passwd/chmod/chown/su/sudo/id | 用户和权限管理 |
| 软件包 | apt/yum/dnf/rpm/dpkg/pip/npm | 软件安装和管理 |
| 定时任务 | crontab/at/systemd timer | 定时任务管理 |
| 文件系统 | mount/umount/fsck/tune2fs/lsof/fuser | 挂载、文件系统检查、文件占用 |
| 安全审计 | last/lastb/who/w/history/auditctl/ausearch | 登录历史、安全审计 |

运维核心方法论：自上而下排查（整体→局部→细节）、USE 方法（每个资源检查 Utilization/Saturation/Errors）、RED 方法（每个服务检查 Rate/Errors/Duration）、黄金四指标（延迟/流量/错误/饱和度）、保留现场（排查问题时先保存状态再操作恢复）。

---

## 补充：进阶与最佳实践

### 1. 常用性能分析命令组合

```bash
# 快速查看系统整体状态（运维三板斧）
uptime                    # 系统负载（1/5/15分钟）
free -h                   # 内存使用（含缓存和 Swap）
df -h                     # 磁盘空间
top -bn1 | head -20       # CPU 和进程概览（非交互模式）

# CPU 性能分析
mpstat -P ALL 1 3         # 每个 CPU 核心使用率（每秒1次，共3次）
pidstat 1 5               # 每个进程的 CPU 使用率
vmstat 1 5                # 系统整体状态（r=运行队列，us/sy/id=用户/系统/空闲）
perf top                  # 实时查看 CPU 热点函数

# 内存性能分析
free -h                   # 内存概览（available 是关键指标）
vmstat 1 5                # si/so=Swap换入换出（非0说明内存紧张）
pmap -x <pid>             # 进程内存映射
smem -tk                  # 按 PSS 统计进程内存（更准确）
slabtop                   # 内核 Slab 缓存使用

# 磁盘 IO 分析
iostat -xz 1 3            # 磁盘 IO 详情（%util=IO利用率，await=平均等待时间）
iotop -oP                  # 实时查看 IO 最高的进程
df -hT                     # 磁盘空间和文件系统类型
du -sh /* 2>/dev/null | sort -rh | head -10  # 找出占用空间最大的目录
lsof +L1                   # 查看已删除但被进程占用的文件（空间未释放）

# 网络分析
ss -tlnp                   # 查看监听的 TCP 端口和进程
ss -s                       # 网络连接统计
ss -tanp | grep :80 | wc -l  # 统计 80 端口连接数
ip addr show                # 网络接口和 IP 地址
ip route show               # 路由表
ping -c 4 -W 2 8.8.8.8     # 测试连通性
traceroute -n 8.8.8.8       # 路由追踪
dig example.com              # DNS 查询（详细）
curl -v -o /dev/null -s -w "DNS:%{time_namelookup}s Connect:%{time_connect}s Total:%{time_total}s\n" https://example.com  # HTTP 请求各阶段耗时
tcpdump -i any -nn port 80 -c 100  # 抓包（80端口，100个包）

# 进程分析
ps aux --sort=-%cpu | head -10   # CPU 使用率最高的 10 个进程
ps aux --sort=-%mem | head -10   # 内存使用率最高的 10 个进程
pstree -ap                  # 进程树（含参数）
pgrep -af java              # 查找 Java 进程（含命令行）
kill -3 <pid>               # 发送 SIGQUIT，Java 进程会打印线程堆栈
jstack <pid> > thread.txt   # Java 线程堆栈
jmap -heap <pid>            # Java 堆信息
jstat -gcutil <pid> 1000 5  # Java GC 统计

# 日志分析
tail -f /var/log/syslog     # 实时跟踪系统日志
grep -c "ERROR" /var/log/app.log  # 统计错误日志数量
grep "ERROR" /var/log/app.log | tail -20  # 最近 20 条错误
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10  # 访问量最高的 10 个 IP
journalctl -u nginx --since "1 hour ago" --no-pager  # systemd 服务最近1小时日志
journalctl -p err -b --no-pager  # 本次启动以来的错误日志
less +F /var/log/app.log    # 实时查看大日志（类似 tail -f，但可搜索）

# 系统服务管理
systemctl status nginx      # 查看服务状态
systemctl start/stop/restart nginx  # 启动/停止/重启
systemctl enable/disable nginx      # 开机自启/禁用
systemctl list-units --type=service --state=running  # 列出运行中的服务
systemd-analyze blame       # 查看开机启动耗时排名
journalctl -u nginx -f      # 实时查看服务日志
```

### 2. 故障排查速查表

| 现象 | 排查命令 | 可能原因 |
|------|---------|---------|
| 系统负载高 | uptime/top/vmstat/mpstat | CPU 密集进程、IO 等待、进程数过多 |
| CPU 100% | top/pidstat/perf top/jstack | 死循环、频繁 GC、计算密集任务 |
| 内存不足/OOM | free/vmstat/dmesg/pmap | 内存泄漏、缓存过大、进程内存溢出 |
| 磁盘满 | df/du/lsof +L1 | 日志未轮转、大文件、已删除文件被占用 |
| IO 高 | iostat/iotop/pidstat -d | 慢查询、大量读写、磁盘性能不足 |
| 网络不通 | ping/traceroute/telnet/nc/ss | 防火墙、路由、DNS、服务未监听 |
| 连接数过多 | ss -s/ss -tanp | TIME_WAIT 堆积、连接泄漏、攻击 |
| 服务无响应 | systemctl status/journalctl/curl/strace | 进程死锁、端口被占、配置错误 |
| 登录慢 | last/dmesg/systemd-analyze | DNS 反向解析、PAM 配置、资源不足 |
| 时间不同步 | date/timedatectl/chronyc tracking | NTP 服务未运行、时区错误 |

### 3. 运维效率提升

| 技巧 | 说明 |
|------|------|
| 别名和函数 | 在 ~/.bashrc 中定义常用命令别名 |
| 历史命令搜索 | Ctrl+R 反向搜索历史命令，!$ 引用上条命令最后一个参数 |
| Tmux/Screen | 终端复用，断开 SSH 后任务继续运行，支持分屏 |
| Ansible | 批量管理多台服务器，自动化运维操作 |
| 监控告警 | Prometheus + Grafana + AlertManager，提前发现问题 |
| 日志聚合 | ELK/Loki，集中管理和搜索多台服务器日志 |
| 配置管理 | 环境变量/配置中心（Nacos/Apollo），避免硬编码 |
| 文档记录 | 每次故障后写复盘文档，积累知识库 |
