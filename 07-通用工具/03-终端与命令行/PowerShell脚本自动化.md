---
title: PowerShell脚本自动化
tags: [自动化运维, PowerShell, 脚本自动化, 命令行, Windows, 跨平台, PowerShell Core, 管道]
category: 通用工具
created: 2026-08-12
updated: 2026-09-01
difficulty: ⭐⭐⭐
status: ✅ 内容已完善
priority: 重要
pre: []
aliases: [PowerShell脚本自动化]
---

# ⚡ PowerShell 脚本自动化

> **文档说明**：系统讲解 PowerShell 脚本自动化的完整知识体系，涵盖 PowerShell 的发展历程与版本（Windows PowerShell 5.1 vs PowerShell 7+ 跨平台）、核心设计理念（面向对象的管道、Verb-Noun 命令规范）、语法基础（变量/类型/运算符/控制流/函数）、管道与对象操作（Where-Object/Select-Object/ForEach-Object/Sort-Object/Group-Object/Measure-Object）、常用命令速查（文件操作/进程管理/服务管理/网络/注册表/系统信息）、脚本编写规范（参数/注释/错误处理/日志）、模块开发与管理、远程管理（WinRM/SSH）、与 Bash/CMD 的对比、典型自动化场景（批量文件处理/系统巡检/部署脚本/备份恢复）、调试与性能优化、常见问题与最佳实践。
>
> **适用人群**：Windows 用户、运维工程师、开发者、需要自动化重复性工作的技术人员
>
> **前置知识**：[[Linux系统管理与常用命令]] · [[Git基础与核心命令]]

---

## 一、概述

### 1.1 什么是 PowerShell

PowerShell 是微软开发的跨平台任务自动化和配置管理框架，由命令行 shell 和脚本语言组成。

**核心特点**：
| 特点 | 说明 |
|------|------|
| **面向对象** | 管道传递的是 .NET 对象，而非纯文本，可以直接操作属性和方法 |
| **Verb-Noun 命名** | 命令遵循 `动词-名词` 规范（如 `Get-ChildItem`、`Stop-Service`），易于猜测和记忆 |
| **跨平台** | PowerShell 7+ 支持 Windows/Linux/macOS（基于 .NET Core） |
| **强大管道** | 支持对象管道，可链式调用，一行命令完成复杂操作 |
| **丰富模块** | 内置大量模块，支持 Azure/AWS/VMware/Exchange 等第三方模块 |
| **远程管理** | 支持 WinRM（Windows）和 SSH（跨平台）远程执行命令 |
| **集成 .NET** | 可直接调用 .NET 类库，能力几乎无上限 |

**PowerShell vs CMD vs Bash**：

| 维度 | PowerShell | CMD（Command Prompt） | Bash（Linux/macOS） |
|------|-----------|---------------------|-------------------|
| **管道数据** | .NET 对象 | 纯文本 | 纯文本 |
| **命令命名** | Verb-Noun（Get-ChildItem） | 短命令（dir/cd） | 短命令（ls/cd） |
| **脚本能力** | 强大（函数/模块/类） | 弱（批处理 .bat） | 强大（函数/awk/sed） |
| **跨平台** | ✅ PowerShell 7+ | ❌ 仅 Windows | ✅ 类 Unix |
| **远程管理** | ✅ WinRM/SSH | ❌ 弱 | ✅ SSH |
| **对象操作** | ✅ 原生 | ❌ 纯文本 | ⚠️ 需 awk/jq |
| **学习曲线** | 较陡（概念多） | 简单 | 中等 |

### 1.2 版本选择

| 版本 | 说明 | 推荐场景 |
|------|------|---------|
| **Windows PowerShell 5.1** | 内置在 Windows 10/11/Server，基于 .NET Framework | 仅 Windows 环境，兼容旧脚本 |
| **PowerShell 7.x（Core）** | 跨平台，基于 .NET Core/.NET 5+，性能更好 | ✅ 推荐，新脚本用这个 |
| **PowerShell 7.4+** | 最新稳定版，持续更新 | 追求新特性 |

**安装 PowerShell 7**：
```powershell
# Windows（winget）
winget install Microsoft.PowerShell

# Windows（MSI 下载）
# https://github.com/PowerShell/PowerShell/releases

# Linux（Ubuntu）
sudo apt-get install -y powershell

# macOS
brew install powershell
```

**启动 PowerShell 7**：
```bash
pwsh  # PowerShell 7+ 的启动命令
powershell  # Windows PowerShell 5.1
```

### 1.3 核心设计理念

**1. Verb-Noun 命令规范**：
所有命令（Cmdlet）遵循 `动词-名词` 格式，动词来自标准动词集（Get/Set/Start/Stop/Remove/New/Add/Invoke 等），名词是单数形式。

```text
Get-ChildItem    # 获取子项（文件列表）
Stop-Service     # 停止服务
New-Item         # 新建项（文件/目录）
Remove-Item      # 删除项
Invoke-Command   # 调用命令
```

**2. 对象管道**：
PowerShell 管道传递的是对象，而非文本。可以直接访问对象的属性和方法：

```powershell
# 获取所有进程，按 CPU 排序，取前 5，只显示名称和 CPU
Get-Process | Sort-Object CPU -Descending | Select-Object -First 5 Name, CPU

# 获取大于 100MB 的文件
Get-ChildItem -Path C:\ -Recurse -File | Where-Object { $_.Length -gt 100MB }
```

**3. 一致性与可发现性**：
- 所有命令参数名一致（`-Path`、`-Name`、`-Recurse`）
- `Get-Command` 查找命令
- `Get-Help` 查看帮助
- `Get-Member` 查看对象的属性和方法

---

## 二、语法基础

### 2.1 变量与类型

```powershell
# 变量定义（$ 前缀）
$name = "PowerShell"
$age = 30
$pi = 3.14159
$isActive = $true
$items = @(1, 2, 3)           # 数组
$person = @{ Name = "张三"; Age = 30 }  # 哈希表

# 类型强转
[int]$number = "42"           # 字符串转整数
[datetime]$date = "2024-01-01"  # 字符串转日期

# 常用类型
[string]    # 字符串
[int]       # 整数
[double]    # 浮点数
[bool]      # 布尔
[array]     # 数组
[hashtable] # 哈希表
[datetime]  # 日期时间
[pscustomobject]  # 自定义对象
```

**变量操作**：
```powershell
# 环境变量
$env:PATH
$env:COMPUTERNAME

# 自动变量
$_  # 当前管道对象
$PSVersionTable  # PowerShell 版本信息
$PWD  # 当前目录
$HOME  # 用户主目录
$Error  # 错误记录数组
$LASTEXITCODE  # 最后一个原生程序的退出码
```

### 2.2 运算符

```powershell
# 算术运算符
+ - * / %     # 加减乘除取模
++ --         # 自增自减

# 比较运算符（不区分大小写，加 c 区分大小写）
-eq  -ne      # 等于/不等于
-gt  -lt      # 大于/小于
-ge  -le      # 大于等于/小于等于
-like -notlike  # 通配符匹配（* ?）
-match -notmatch  # 正则匹配
-contains -notcontains  # 数组包含
-in -notin    # 元素在数组中

# 逻辑运算符
-and -or -not -xor

# 字符串运算符
-f  # 格式化字符串："Hello {0}" -f "World"
-replace  # 替换："hello" -replace "l", "L"
-split -join  # 分割/连接

# 示例
"Hello {0}, you are {1} years old" -f "张三", 30
"hello world" -replace "world", "powershell"
"a,b,c" -split ","
```

### 2.3 控制流

```powershell
# if/elseif/else
if ($age -lt 18) {
    "未成年"
} elseif ($age -lt 60) {
    "成年"
} else {
    "老年"
}

# switch（强大，支持通配符/正则/条件）
switch ($day) {
    "Mon" { "星期一" }
    "Tue" { "星期二" }
    { $_ -in "Sat","Sun" } { "周末" }
    default { "其他" }
}

# for 循环
for ($i = 0; $i -lt 10; $i++) {
    "Number: $i"
}

# foreach（遍历集合）
foreach ($item in $items) {
    "Item: $item"
}

# while/do-while
while ($count -lt 10) { $count++ }
do { $count++ } while ($count -lt 10)

# try/catch/finally（错误处理）
try {
    Get-Content "nonexistent.txt" -ErrorAction Stop
} catch {
    "错误: $_"
} finally {
    "清理工作"
}
```

### 2.4 函数

```powershell
# 基本函数
function Get-Greeting {
    param(
        [string]$Name = "World",
        [int]$Age = 0
    )
    "Hello, $Name! You are $Age years old."
}

# 调用
Get-Greeting -Name "张三" -Age 30

# 高级函数（支持管道输入、-WhatIf、-Confirm）
function Stop-ProcessByName {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory, ValueFromPipeline)]
        [string]$Name
    )
    process {
        if ($PSCmdlet.ShouldProcess($Name, "Stop process")) {
            Get-Process -Name $Name -ErrorAction SilentlyContinue | Stop-Process
        }
    }
}

# 支持管道输入
"notepad", "calc" | Stop-ProcessByName -WhatIf
```

**函数参数属性**：
| 属性 | 说明 |
|------|------|
| `[Parameter(Mandatory)]` | 必填参数 |
| `[Parameter(ValueFromPipeline)]` | 接受管道输入 |
| `[ValidateSet("A","B")]` | 限定取值范围 |
| `[ValidateRange(1,100)]` | 限定数值范围 |
| `[ValidatePattern("regex")]` | 正则校验 |
| `[ValidateScript({...})]` | 自定义校验脚本 |

---

## 三、管道与对象操作

### 3.1 管道基础

PowerShell 管道（`|`）将前一个命令的输出对象传递给下一个命令：

```powershell
# 基本管道
Get-ChildItem | Where-Object { $_.Length -gt 1MB } | Sort-Object Length -Descending

# 等价于（显式写法）
$files = Get-ChildItem
$bigFiles = $files | Where-Object { $_.Length -gt 1MB }
$sorted = $bigFiles | Sort-Object Length -Descending
```

**`$_` 或 `$PSItem`**：表示当前管道中的对象。

### 3.2 常用管道命令

| 命令 | 别名 | 说明 | 示例 |
|------|------|------|------|
| `Where-Object` | `?` / `where` | 过滤对象 | `Get-Process \| Where-Object CPU -gt 10` |
| `Select-Object` | `select` | 选择属性/数量 | `Get-Process \| Select-Object Name, CPU -First 5` |
| `ForEach-Object` | `%` / `foreach` | 对每个对象执行操作 | `1..10 \| ForEach-Object { $_ * 2 }` |
| `Sort-Object` | `sort` | 排序 | `Get-ChildItem \| Sort-Object Length -Descending` |
| `Group-Object` | `group` | 分组 | `Get-ChildItem \| Group-Object Extension` |
| `Measure-Object` | `measure` | 统计（数量/求和/平均/最大/最小） | `Get-ChildItem \| Measure-Object Length -Sum` |
| `Compare-Object` | `compare` / `diff` | 比较两个集合 | `Compare-Object $a $b` |
| `Format-Table` | `ft` | 表格格式输出 | `Get-Process \| ft Name, CPU` |
| `Format-List` | `fl` | 列表格式输出 | `Get-Process \| fl *` |
| `ConvertTo-Json` | - | 转 JSON | `$obj \| ConvertTo-Json` |
| `ConvertFrom-Json` | - | JSON 转对象 | `$json \| ConvertFrom-Json` |
| `Export-Csv` | - | 导出 CSV | `Get-Process \| Export-Csv proc.csv` |
| `Import-Csv` | - | 导入 CSV | `Import-Csv data.csv` |

### 3.3 管道操作示例

```powershell
# 1. 找出占用 CPU 最高的 5 个进程
Get-Process | Sort-Object CPU -Descending | Select-Object -First 5 Name, Id, CPU

# 2. 找出当前目录下大于 100MB 的文件并按大小排序
Get-ChildItem -File | Where-Object Length -gt 100MB | Sort-Object Length -Descending | Select-Object Name, @{N="SizeMB";E={[math]::Round($_.Length/1MB,2)}}

# 3. 统计各类型文件的数量和总大小
Get-ChildItem -Recurse -File | Group-Object Extension | Sort-Object Count -Descending | Select-Object Name, Count, @{N="TotalMB";E={[math]::Round(($_.Group | Measure-Object Length -Sum).Sum/1MB,2)}}

# 4. 停止所有名称包含 "chrome" 的进程
Get-Process | Where-Object Name -like "*chrome*" | Stop-Process -WhatIf

# 5. 批量重命名文件（.txt 改为 .md）
Get-ChildItem -Filter "*.txt" | Rename-Item -NewName { $_.Name -replace '\.txt$', '.md' }

# 6. 获取系统信息并导出 JSON
Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, BuildNumber, @{N="TotalGB";E={[math]::Round($_.TotalVisibleMemorySize/1MB,2)}} | ConvertTo-Json

# 7. 测试端口连通性
"google.com", "github.com" | ForEach-Object { [PSCustomObject]@{ Host=$_; Port443=(Test-NetConnection -ComputerName $_ -Port 443).TcpTestSucceeded } }

# 8. 查找最近 7 天修改过的文件
Get-ChildItem -Path C:\Projects -Recurse -File | Where-Object LastWriteTime -gt (Get-Date).AddDays(-7) | Sort-Object LastWriteTime -Descending
```

---

## 四、常用命令速查

### 4.1 文件与目录操作

| 操作 | 命令 | 示例 |
|------|------|------|
| 列出文件 | `Get-ChildItem` (`ls`/`dir`) | `Get-ChildItem -Recurse -File` |
| 创建目录 | `New-Item -ItemType Directory` | `New-Item -ItemType dir -Name newdir` |
| 创建文件 | `New-Item -ItemType File` | `New-Item file.txt` |
| 复制 | `Copy-Item` (`cp`) | `Copy-Item a.txt b.txt` |
| 移动/重命名 | `Move-Item` / `Rename-Item` (`mv`) | `Move-Item a.txt dir/` |
| 删除 | `Remove-Item` (`rm`/`del`) | `Remove-Item *.tmp -Recurse` |
| 读取内容 | `Get-Content` (`cat`/`type`) | `Get-Content file.txt -Tail 10` |
| 写入内容 | `Set-Content` / `Out-File` | `Set-Content file.txt "hello"` |
| 追加内容 | `Add-Content` | `Add-Content file.txt "new line"` |
| 查找内容 | `Select-String` (`grep`) | `Select-String -Path *.log -Pattern "error"` |
| 当前目录 | `Get-Location` (`pwd`) | `Get-Location` |
| 切换目录 | `Set-Location` (`cd`) | `Set-Location C:\Projects` |

### 4.2 进程与服务管理

| 操作 | 命令 | 示例 |
|------|------|------|
| 列出进程 | `Get-Process` (`ps`) | `Get-Process | Sort-Object CPU -Descending` |
| 停止进程 | `Stop-Process` (`kill`) | `Stop-Process -Name notepad` |
| 启动进程 | `Start-Process` | `Start-Process notepad.exe` |
| 列出服务 | `Get-Service` | `Get-Service | Where-Object Status -eq "Running"` |
| 启动服务 | `Start-Service` | `Start-Service wuauserv` |
| 停止服务 | `Stop-Service` | `Stop-Service wuauserv` |
| 设置服务启动类型 | `Set-Service` | `Set-Service wuauserv -StartupType Automatic` |

### 4.3 网络操作

| 操作 | 命令 | 示例 |
|------|------|------|
| 测试网络连接 | `Test-NetConnection` | `Test-NetConnection google.com -Port 443` |
| Ping | `Test-Connection` | `Test-Connection google.com -Count 4` |
| 获取 IP 配置 | `Get-NetIPAddress` | `Get-NetIPAddress -AddressFamily IPv4` |
| DNS 解析 | `Resolve-DnsName` | `Resolve-DnsName google.com` |
| 下载文件 | `Invoke-WebRequest` (`iwr`/`curl`) | `Invoke-WebRequest -Uri $url -OutFile file.zip` |
| HTTP 请求 | `Invoke-RestMethod` (`irm`) | `Invoke-RestMethod -Uri https://api.example.com/data` |
| 监听端口 | `Test-NetConnection -Port` | `Test-NetConnection -ComputerName localhost -Port 8080` |

### 4.4 系统信息

| 操作 | 命令 | 示例 |
|------|------|------|
| 操作系统信息 | `Get-CimInstance Win32_OperatingSystem` | 版本、构建号、内存 |
| 计算机信息 | `Get-CimInstance Win32_ComputerSystem` | 制造商、型号、域 |
| CPU 信息 | `Get-CimInstance Win32_Processor` | 型号、核心数、频率 |
| 磁盘信息 | `Get-PSDrive` / `Get-CimInstance Win32_LogicalDisk` | 盘符、容量、可用空间 |
| 热修复/补丁 | `Get-HotFix` | 已安装的 Windows 更新 |
| 事件日志 | `Get-WinEvent` | 系统/应用/安全日志 |
| 当前用户 | `$env:USERNAME` / `whoami` | 当前登录用户 |

---

## 五、脚本编写规范

### 5.1 脚本结构

```powershell
<#
.SYNOPSIS
    脚本功能简要说明

.DESCRIPTION
    脚本的详细说明

.PARAMETER Path
    参数说明

.EXAMPLE
    .\Script.ps1 -Path C:\Data

.NOTES
    作者: 张三
    版本: 1.0
    日期: 2024-01-01
#>

# 严格模式（捕获更多错误）
Set-StrictMode -Version Latest

# 错误处理策略
$ErrorActionPreference = "Stop"

# 参数定义
param(
    [Parameter(Mandatory)]
    [string]$Path,
    
    [int]$MaxCount = 100,
    
    [switch]$VerboseOutput
)

# 主逻辑
try {
    if ($VerboseOutput) { $VerbosePreference = "Continue" }
    
    Write-Verbose "开始处理路径: $Path"
    
    # ... 脚本逻辑 ...
    
    Write-Output "处理完成"
}
catch {
    Write-Error "脚本执行失败: $_"
    exit 1
}
```

### 5.2 错误处理

```powershell
# 错误处理策略
$ErrorActionPreference = "Stop"   # 遇到错误立即停止
# "Continue"（默认，继续执行）
# "SilentlyContinue"（静默忽略）
# "Inquire"（询问用户）

# try/catch
try {
    Get-Content "nonexistent.txt" -ErrorAction Stop
}
catch [System.IO.FileNotFoundException] {
    "文件不存在: $_"
}
catch {
    "其他错误: $_"
}
finally {
    "总是执行的清理代码"
}

# 检查命令是否成功
if (Test-Path $file) {
    "文件存在"
} else {
    "文件不存在"
}

# 原生程序退出码
ping google.com
if ($LASTEXITCODE -eq 0) {
    "Ping 成功"
}
```

### 5.3 日志与输出

```powershell
# 输出流
Write-Output "正常输出"        # 成功流（1）
Write-Error "错误信息"          # 错误流（2）
Write-Warning "警告信息"        # 警告流（3）
Write-Verbose "详细信息"        # 详细流（4），需 -Verbose 才显示
Write-Debug "调试信息"          # 调试流（5），需 -Debug 才显示
Write-Information "信息"        # 信息流（6）

# 写日志文件
"$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - 操作完成" | Add-Content -Path script.log

# 带时间戳的日志函数
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Add-Content -Path "script.log" -Value $logMessage
    if ($Level -eq "ERROR") { Write-Error $Message }
    else { Write-Output $logMessage }
}
```

### 5.4 注释规范

```powershell
<# 多行注释，常用于脚本/函数帮助文档 #>

# 单行注释

# 函数帮助注释（基于注释的帮助）
function Get-Example {
    <#
    .SYNOPSIS
        简要说明
    .DESCRIPTION
        详细说明
    .PARAMETER Name
        参数说明
    .EXAMPLE
        Get-Example -Name "test"
    #>
    param([string]$Name)
    # ...
}
```

---

## 六、模块与远程管理

### 6.1 模块管理

```powershell
# 查看已安装模块
Get-Module -ListAvailable

# 查看已导入模块
Get-Module

# 导入模块
Import-Module AzureRM

# 查找模块（PowerShell Gallery）
Find-Module -Name *azure*

# 安装模块
Install-Module -Name Az -Scope CurrentUser

# 更新模块
Update-Module -Name Az

# 卸载模块
Uninstall-Module -Name Az

# 常用模块
# Az          - Azure 管理
# AWS.Tools   - AWS 管理
# VMware.PowerCLI - VMware 管理
# Pester      - 测试框架
# posh-git    - Git 集成
# PSReadLine  - 命令行编辑增强
```

### 6.2 远程管理

**WinRM 远程（Windows）**：
```powershell
# 启用 WinRM（目标机器）
Enable-PSRemoting -Force

# 信任主机（客户端，测试环境）
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "*.example.com"

# 远程执行命令
Invoke-Command -ComputerName server01 -ScriptBlock {
    Get-Service | Where-Object Status -eq "Running"
} -Credential (Get-Credential)

# 远程会话（交互式）
Enter-PSSession -ComputerName server01 -Credential $cred

# 持久会话
$session = New-PSSession -ComputerName server01
Invoke-Command -Session $session -ScriptBlock { ... }
Remove-PSSession $session
```

**SSH 远程（跨平台，PowerShell 7+）**：
```powershell
# 通过 SSH 远程执行
Enter-PSSession -HostName user@linux-server -KeyFilePath ~/.ssh/id_rsa

# SSH 远程命令
Invoke-Command -HostName user@linux-server -ScriptBlock {
    uname -a
}
```

---

## 七、典型自动化场景

### 7.1 批量文件处理

```powershell
# 批量重命名（日期前缀）
Get-ChildItem -Path .\photos -Filter "*.jpg" | ForEach-Object {
    $newName = "$($_.LastWriteTime.ToString('yyyyMMdd'))_$($_.Name)"
    Rename-Item -Path $_.FullName -NewName $newName
}

# 批量转换编码（GBK → UTF-8）
Get-ChildItem -Path . -Filter "*.txt" -Recurse | ForEach-Object {
    $content = Get-Content $_.FullName -Encoding Default
    Set-Content -Path $_.FullName -Value $content -Encoding UTF8
}

# 批量压缩备份
$backupName = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"
Compress-Archive -Path .\data\* -DestinationPath .\backup\$backupName
```

### 7.2 系统巡检脚本

```powershell
<#
.SYNOPSIS
    Windows 系统健康巡检脚本
#>

$report = @()

# 1. 磁盘空间
$disks = Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3"
foreach ($disk in $disks) {
    $freePct = [math]::Round(($disk.FreeSpace / $disk.Size) * 100, 1)
    $report += [PSCustomObject]@{
        检查项 = "磁盘 $($disk.DeviceID)"
        状态 = if ($freePct -lt 10) { "警告" } else { "正常" }
        详情 = "可用空间 ${freePct}%"
    }
}

# 2. 内存使用
$os = Get-CimInstance Win32_OperatingSystem
$memUsedPct = [math]::Round((($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / $os.TotalVisibleMemorySize) * 100, 1)
$report += [PSCustomObject]@{
    检查项 = "内存使用"
    状态 = if ($memUsedPct -gt 90) { "警告" } else { "正常" }
    详情 = "使用率 ${memUsedPct}%"
}

# 3. CPU 负载
$cpu = (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
$report += [PSCustomObject]@{
    检查项 = "CPU 负载"
    状态 = if ($cpu -gt 90) { "警告" } else { "正常" }
    详情 = "使用率 ${cpu}%"
}

# 4. 关键服务
$services = @("wuauserv", "WinDefend", "Spooler")
foreach ($svc in $services) {
    $service = Get-Service -Name $svc -ErrorAction SilentlyContinue
    if ($service) {
        $report += [PSCustomObject]@{
            检查项 = "服务 $svc"
            状态 = if ($service.Status -eq "Running") { "正常" } else { "异常" }
            详情 = $service.Status
        }
    }
}

# 输出报告
$report | Format-Table -AutoSize
$report | Export-Csv -Path "health_report_$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation -Encoding UTF8
```

### 7.3 部署脚本

```powershell
<#
.SYNOPSIS
    Web 应用部署脚本
#>
param(
    [Parameter(Mandatory)]
    [string]$AppPath,
    
    [string]$BackupPath = "D:\backup",
    
    [switch]$NoBackup
)

$ErrorActionPreference = "Stop"

try {
    Write-Host "=== 开始部署 ===" -ForegroundColor Green
    
    # 1. 备份
    if (-not $NoBackup) {
        $backupFile = Join-Path $BackupPath "app_$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"
        Write-Host "备份到: $backupFile"
        Compress-Archive -Path "$AppPath\*" -DestinationPath $backupFile -Force
    }
    
    # 2. 停止应用池（IIS）
    Write-Host "停止应用池..."
    Stop-WebAppPool -Name "MyAppPool"
    
    # 3. 等待进程退出
    Start-Sleep -Seconds 5
    
    # 4. 复制新文件
    Write-Host "部署新文件..."
    Copy-Item -Path ".\publish\*" -Destination $AppPath -Recurse -Force
    
    # 5. 启动应用池
    Write-Host "启动应用池..."
    Start-WebAppPool -Name "MyAppPool"
    
    # 6. 健康检查
    Write-Host "健康检查..."
    $response = Invoke-WebRequest -Uri "http://localhost/health" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "=== 部署成功 ===" -ForegroundColor Green
    } else {
        throw "健康检查失败: $($response.StatusCode)"
    }
}
catch {
    Write-Host "部署失败: $_" -ForegroundColor Red
    # 回滚
    if (-not $NoBackup) {
        Write-Host "正在回滚..."
        $latestBackup = Get-ChildItem $BackupPath -Filter "app_*.zip" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        Expand-Archive -Path $latestBackup.FullName -DestinationPath $AppPath -Force
        Start-WebAppPool -Name "MyAppPool"
        Write-Host "回滚完成" -ForegroundColor Yellow
    }
    exit 1
}
```

---

## 八、调试与性能优化

### 8.1 调试技巧

```powershell
# 1. 严格模式（捕获未定义变量等）
Set-StrictMode -Version Latest

# 2. 详细输出
$VerbosePreference = "Continue"
Write-Verbose "调试信息"

# 3. 调试输出
$DebugPreference = "Continue"
Write-Debug "调试信息"

# 4. 断点调试（PowerShell ISE / VS Code）
# 在脚本中设置断点，单步执行
# 快捷键：F9 设断点，F10 单步，F11 步入，F5 继续

# 5. 查看变量
Get-Variable | Where-Object Name -like "*temp*"

# 6. 查看错误详情
$Error[0] | Format-List *  # 最近一个错误的详细信息
$Error[0].Exception.StackTrace  # 错误堆栈

# 7. 命令追踪
Set-PSDebug -Trace 1  # 跟踪执行的每一行
Set-PSDebug -Off      # 关闭跟踪
```

### 8.2 性能优化

```powershell
# 1. 避免在循环中追加数组（数组是不可变的，每次追加都复制）
# ❌ 慢
$results = @()
foreach ($item in $items) {
    $results += $item  # 每次都创建新数组
}

# ✅ 快（用 List[T]）
$results = [System.Collections.Generic.List[object]]::new()
foreach ($item in $items) {
    $results.Add($item)
}

# 2. 用 Filter 代替 Where-Object（对于简单过滤）
# 对于大集合，Filter 更快
Get-ChildItem | Where-Object { $_.Length -gt 1MB }

# 3. 用 -Filter 参数（提供者端过滤，比 Where-Object 快）
Get-ChildItem -Path C:\ -Recurse -Filter "*.log" -File  # 比 Where-Object 快

# 4. 避免 Write-Host（不输出到管道，且性能差）
# ✅ 用 Write-Output 或直接输出
"结果: $x"

# 5. 用 [PSCustomObject] 代替 New-Object（更快）
# ✅
[PSCustomObject]@{ Name = "test"; Value = 42 }

# 6. 测量执行时间
Measure-Command { Get-ChildItem -Recurse }

# 7. 并行执行（PowerShell 7+ 的 ForEach-Object -Parallel）
$items | ForEach-Object -Parallel {
    Invoke-RestMethod -Uri "https://api.example.com/item/$_"
} -ThrottleLimit 10
```

---

## 九、PowerShell vs Bash 速查

| 操作 | PowerShell | Bash |
|------|-----------|------|
| 列出文件 | `Get-ChildItem` / `ls` / `dir` | `ls` |
| 切换目录 | `Set-Location` / `cd` | `cd` |
| 查看当前目录 | `Get-Location` / `pwd` | `pwd` |
| 查看文件内容 | `Get-Content` / `cat` | `cat` |
| 搜索文件内容 | `Select-String` / `grep` | `grep` |
| 复制文件 | `Copy-Item` / `cp` | `cp` |
| 移动/重命名 | `Move-Item` / `mv` | `mv` |
| 删除文件 | `Remove-Item` / `rm` | `rm` |
| 创建目录 | `New-Item -ItemType dir` / `mkdir` | `mkdir` |
| 查看进程 | `Get-Process` / `ps` | `ps` |
| 杀死进程 | `Stop-Process` / `kill` | `kill` |
| 环境变量 | `$env:VAR` | `$VAR` |
| 管道对象 | 对象（可访问属性） | 文本 |
| 脚本后缀 | `.ps1` | `.sh` |
| 注释 | `#` | `#` |
| 变量前缀 | `$var` | `$var` |
| 字符串插值 | `"Hello $name"` | `"Hello $name"` |
| 条件判断 | `if ($a -eq $b)` | `if [ $a -eq $b ]` |
| 循环 | `foreach ($i in $items)` | `for i in items; do` |
| 函数 | `function Name { ... }` | `name() { ... }` |

---

## 十、常见问题与最佳实践

### 10.1 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| **脚本无法运行（执行策略）** | PowerShell 默认禁止运行脚本 | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| **中文乱码** | 编码不一致 | 脚本保存为 UTF-8 with BOM，`[Console]::OutputEncoding = [Text.Encoding]::UTF8` |
| **命令找不到** | 模块未导入或未安装 | `Import-Module` 或 `Install-Module` |
| **管道输出被截断** | 默认显示宽度限制 | `Format-Table -AutoSize` 或 `Out-String -Width 200` |
| **递归删除提示** | 目录非空时确认 | `Remove-Item -Recurse -Force` |
| **复制文件权限不足** | 需要管理员权限 | 以管理员身份运行 PowerShell |
| **远程连接失败** | WinRM 未启用或防火墙 | 目标机器 `Enable-PSRemoting -Force`，开放 5985/5986 端口 |
| **脚本执行慢** | 数组追加/Where-Object 过滤大集合 | 用 List[T]、-Filter 参数、ForEach-Object -Parallel |
| **$LASTEXITCODE 不对** | 原生程序退出码未正确捕获 | 检查 `$LASTEXITCODE`，注意 PowerShell 命令不设置它 |
| **路径中有空格** | 路径未加引号 | 用引号包裹路径：`"C:\Program Files\app"` |

### 10.2 最佳实践

1. **使用 PowerShell 7+**：
   - 跨平台、性能更好、新特性更多
   - 新脚本默认用 `pwsh` 运行

2. **遵循 Verb-Noun 命名**：
   - 函数和脚本用标准动词（`Get-Verb` 查看）
   - 名词用单数形式
   - 自定义函数加前缀避免冲突（如 `MyApp-GetData`）

3. **使用参数而非硬编码**：
   - 脚本接受参数，不硬编码路径/名称
   - 必填参数用 `[Parameter(Mandatory)]`
   - 提供默认值和验证

4. **错误处理**：
   - 用 `try/catch` 处理预期错误
   - 设置 `$ErrorActionPreference = "Stop"` 让错误可捕获
   - 用 `-ErrorAction Stop` 对特定命令强制报错
   - 提供有意义的错误信息

5. **输出规范**：
   - 用 `Write-Output` 输出数据（可管道传递）
   - 用 `Write-Error`/`Write-Warning`/`Write-Verbose` 区分信息类型
   - 避免 `Write-Host`（不输出到管道）
   - 返回对象而非格式化文本

6. **脚本结构**：
   - 开头有基于注释的帮助文档（`.SYNOPSIS`/`.DESCRIPTION`/`.EXAMPLE`）
   - `param()` 块在最前面
   - `Set-StrictMode -Version Latest` 捕获更多错误
   - 主逻辑用 `try/catch/finally` 包裹

7. **安全实践**：
   - 不在脚本中硬编码密码/密钥
   - 用 `Get-Credential` 或 SecretManagement 模块
   - 敏感操作加 `-WhatIf` 支持（`[CmdletBinding(SupportsShouldProcess)]`）
   - 执行策略用 `RemoteSigned` 而非 `Unrestricted`

8. **性能优化**：
   - 用 `[List[T]]` 代替数组追加
   - 用 `-Filter` 代替 `Where-Object`（提供者端过滤）
   - 大集合用 `ForEach-Object -Parallel`（PowerShell 7+）
   - 用 `Measure-Command` 测量性能瓶颈

9. **代码风格**：
   - 缩进用 4 空格
   - 大括号换行（K&R 风格或 Allman 风格，保持一致）
   - 变量名用 PascalCase 或 camelCase
   - 复杂逻辑加注释

10. **测试**：
    - 用 Pester 框架写单元测试
    - 关键函数都有测试用例
    - CI 中运行测试

---

## 十一、关联笔记

### 终端与命令行
- [[Linux系统管理与常用命令]] · [[Bash脚本编程]] · [[Windows常用命令]]

### 自动化与运维
- [[CI-CD流水线]] · [[Ansible-配置管理]] · [[Terraform-基础设施编排]]
- [[Docker容器化]] · [[K8s-核心概念与架构]]

### 开发工具
- [[Git基础与核心命令]] · [[VSCode高效开发]] · [[Vim-Neovim入门与配置]]

### 导航
- [[MOC-通用工具]] · [[MOC-云原生与运维]] · [[MOC-综合导航]] · [[Home]]

> 🔍 **知识点深度解析**
>
> **作用**：PowerShell 脚本自动化解决的是「Windows 环境和跨平台环境下重复性工作的自动化问题」——传统的 CMD 批处理能力弱（纯文本、语法简陋、难以处理复杂逻辑），Bash 在 Windows 上原生不支持（需要 WSL/Git Bash），而 Windows 系统管理（AD/Exchange/IIS/注册表/WMI）又需要强大的脚本能力。PowerShell 作为微软官方的命令行 shell 和脚本语言，面向对象的管道、Verb-Noun 命令规范、.NET 集成、远程管理能力，让 Windows 自动化从「批处理的噩梦」变成「对象化的优雅」，PowerShell 7+ 的跨平台特性更让它成为统一 Windows/Linux/macOS 自动化的选择。
>
> **底层原理**：①PowerShell 的核心是「面向对象的管道」——传统 shell（Bash/CMD）的管道传递的是纯文本，需要用 awk/sed/cut 等工具解析文本；PowerShell 的管道传递的是 .NET 对象，可以直接访问属性（`$_.Name`）和调用方法（`$_.ToString()`），不需要文本解析。这是 PowerShell 与传统 shell 最本质的区别。②Verb-Noun 命名规范让命令可预测——所有命令遵循 `动词-名词` 格式，动词来自标准集（Get/Set/Start/Stop/Remove/New/Add/Invoke 等），看到命令名就能猜到功能，也能通过 `Get-Command -Verb Get` 查找所有查询类命令。③PowerShell 是构建在 .NET 之上的——PowerShell 的一切（变量、对象、类型）都是 .NET 对象，可以直接调用 .NET 类库（`[System.IO.File]::ReadAllText()`），能力几乎无上限。④PowerShell 7+ 基于 .NET Core/.NET 5+，实现了真正的跨平台——同一个脚本可以在 Windows/Linux/macOS 上运行，远程管理同时支持 WinRM（Windows）和 SSH（跨平台）。⑤Cmdlet（命令）是编译的 .NET 类，不是可执行程序——每个 Cmdlet 都有统一的参数绑定、管道输入、错误处理、-WhatIf/-Confirm 支持，这是 PowerShell 一致性的基础。
>
> **用法要点**：① 基础：变量 `$name`、数组 `@(1,2,3)`、哈希表 `@{k=v}`、比较运算符 `-eq/-ne/-gt/-lt/-like/-match`、控制流 if/switch/for/foreach/while、try/catch/finally ② 管道：`|` 传递对象，`$_` 当前对象，常用命令 Where-Object(过滤)/Select-Object(选择)/ForEach-Object(遍历)/Sort-Object(排序)/Group-Object(分组)/Measure-Object(统计)/Format-Table(表格) ③ 文件操作：Get-ChildItem(列文件)/New-Item(新建)/Copy-Item(复制)/Move-Item(移动)/Remove-Item(删除)/Get-Content(读)/Set-Content(写)/Add-Content(追加)/Select-String(搜索) ④ 系统管理：Get-Process/Stop-Process(进程)、Get-Service/Start-Service/Stop-Service(服务)、Get-CimInstance(WMI/CIM)、Test-NetConnection(网络)、Invoke-WebRequest/Invoke-RestMethod(HTTP) ⑤ 脚本规范：param()参数、[CmdletBinding()]高级函数、基于注释的帮助(.SYNOPSIS/.DESCRIPTION/.EXAMPLE)、Set-StrictMode、$ErrorActionPreference、Write-Output/Error/Warning/Verbose ⑥ 模块：Get-Module/Import-Module/Find-Module/Install-Module ⑦ 远程：Invoke-Command/Enter-PSSession(WinRM)、SSH 远程(PowerShell 7+) ⑧ 性能：用 List[T] 代替数组追加、用 -Filter 代替 Where-Object、ForEach-Object -Parallel(并行)、Measure-Command 测性能 ⑨ 常见坑：执行策略(Set-ExecutionPolicy)、中文乱码(UTF-8 BOM)、Remove-Item 需要 -Recurse -Force、路径空格加引号、$LASTEXITCODE 只对原生程序有效 ⑩ 最佳实践：用 PowerShell 7+、Verb-Noun 命名、参数化不硬编码、try/catch 错误处理、返回对象而非文本、-WhatIf 支持、Pester 测试。

> 💡 **深度讲解**：PowerShell 最核心的智慧是「面向对象的管道」——这是它与 Bash/CMD 最本质的区别，也是它强大的根源。在 Bash 中，一切都是文本：`ls` 输出文本，`grep` 过滤文本，`awk` 解析文本，`cut` 切分文本——处理数据的过程就是「文本→解析→处理→输出文本」的循环，充满了文本解析的繁琐和脆弱性（空格、换行、特殊字符都会导致解析错误）。在 PowerShell 中，一切都是对象：`Get-ChildItem` 输出 FileInfo 对象，`Where-Object { $_.Length -gt 1MB }` 直接访问对象的 Length 属性，`Sort-Object Length` 直接按属性排序——不需要文本解析，直接操作对象的属性和方法。这种「对象管道」让复杂的数据处理变得优雅而健壮：你不需要关心输出格式，不需要写正则解析，直接 `$_.属性名` 就能拿到数据。这就像「从电报时代进入互联网时代」——电报只能传文本，需要编码解码；互联网直接传结构化数据，开箱即用。「Verb-Noun 命名规范」是另一个智慧——它让 PowerShell 的命令具有「可预测性」和「可发现性」。在 Bash 中，命令名是历史遗留的缩写（`ls`、`grep`、`awk`、`sed`），没有规律，只能死记硬背；在 PowerShell 中，所有命令都是 `动词-名词`，动词来自标准集，看到 `Get-` 就知道是查询，`Stop-` 就知道是停止，`New-` 就知道是创建——你甚至可以「猜」出命令名（想找进程？`Get-Process`；想停服务？`Stop-Service`）。这种一致性大大降低了学习成本，也让 `Get-Command -Verb Get -Noun *service*` 这样的命令搜索成为可能。命名规范的本质是「用规则降低认知负担」——当所有命令遵循同一规则时，大脑不需要为每个命令单独记忆，只需要记住规则就能推导。

> 📝 **精简总结**：PowerShell = 面向对象的命令行 shell + 脚本语言，Verb-Noun 命名，管道传 .NET 对象，跨平台（PowerShell 7+）。核心：变量$var、数组@()、哈希表@{k=v}、比较运算符-eq/-like/-match、管道|和$_、常用命令Where/Select/ForEach/Sort/Group/Measure。文件：Get-ChildItem/New-Item/Copy/Move/Remove/Get-Content/Set-Content/Select-String。系统：Get-Process/Get-Service/Get-CimInstance/Test-NetConnection/Invoke-RestMethod。脚本：param()、[CmdletBinding()]、注释帮助、Set-StrictMode、try/catch、Write-Output/Error/Verbose。模块：Get/Import/Find/Install-Module。远程：Invoke-Command/Enter-PSSession(WinRM)、SSH(7+)。性能：List[T]、-Filter、ForEach-Object -Parallel。坑：执行策略、中文乱码(UTF-8 BOM)、Remove-Item -Recurse -Force、路径空格。vs Bash：对象管道vs文本管道，Verb-Noun vs缩写命令。

> **学习路径建议**：先学习 [[Linux系统管理与常用命令]] 理解命令行基础 → 学习本文档掌握 PowerShell 基础 → 实践：用 PowerShell 写批量文件处理脚本 → 学习 [[Bash脚本编程]] 对比理解 → 学习 [[Ansible-配置管理]] 理解配置管理自动化 → 学习 [[Terraform-基础设施编排]] 理解基础设施自动化 → 深入：模块开发、远程管理、Pester 测试、DCS 配置管理 → 在实际工作中用 PowerShell 自动化重复性工作。

---

> **PowerShell 的本质是「用对象的思维重新发明命令行」——在传统的命令行世界里，一切都是文本，数据处理就是文本解析的艺术（awk/sed/grep 的组合拳），强大但繁琐，优雅但脆弱。PowerShell 把 .NET 的对象模型引入命令行，让管道传递的不再是文本，而是有属性、有方法、有类型的对象——你不再需要 `ls -l | awk '{print $5}'` 来获取文件大小，直接 `(Get-ChildItem).Length` 就能拿到；不再需要 `ps | grep java | awk '{print $2}' | xargs kill` 来杀进程，直接 `Get-Process java | Stop-Process` 就能完成。这种「对象化」不仅仅是语法糖，更是思维方式的升级——从「文本流的处理」变成「对象集合的操作」，从「解析+拼接」变成「过滤+选择+排序+分组」的声明式操作。当你掌握了 PowerShell 的对象管道，你会发现很多原本需要几十行 Bash 脚本的任务，在 PowerShell 中一行管道就能完成；很多原本脆弱的文本解析，变成了健壮的对象属性访问。这就是 PowerShell 的力量——它不是「又一个 shell」，而是「面向对象的自动化平台」，让 Windows 系统管理和跨平台自动化从「手工艺术」变成「工业产品」。**

---

## 🔗 关联笔记

- [[MOC-通用工具]] — 返回本分类知识地图，查看更多相关文档

## 📖 前置知识

- 无特殊前置知识要求，具备基础编程概念即可

## 🏷️ 相关标签

`#自动化运维` `#PowerShell` `#脚本自动化` `#命令行` `#Windows` `#跨平台`

[[Home|🏠 返回首页]] · [[MOC-通用工具|📚 返回分类]]
