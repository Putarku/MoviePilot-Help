# QQ通知

## 安装QQ机器人

使用包含LiteLoaderQQNT 插件[LLOneBot](https://github.com/LLOneBot/LLOneBot?tab=readme-ov-file)是最方便的部署方式。

### Windows 一键安装方案（推荐，开一个windows的虚拟机即可）

<https://github.com/super1207/install_llob/releases> 下载 exe，双击运行即可，之后打开 QQ 的设置，看到了 `LLOneBot` 就代表安装成功了。

### Linux 安装

Linux 安装方法与 Windows 类似，只是需要手动安装 LiteLoaderQQNT

如果要使用 Docker 安装 LLOneBot，可参考 <https://github.com/LLOneBot/llonebot-docker>

如果你的 Linux 上的 QQ 出现各种问题了，推荐使用无头 NTQQ 框架 [NapCatQQ](https://github.com/NapNeko/NapCatQQ)

<br>

## 配置QQ机器人

首先需要去[QQ官网](https://www.qq.com)注册一个小号，手机可以直接用自己的，同一个手机号可以注册多个QQ号。之后在电脑上登录。

 <div align=center> <img src="https://github.com/Putarku/MoviePilot-Help/raw/main/img/QQ_1726579343068.png" width="600"> </div>

Windows版本中，进入设置，开启`启用HTTP服务`，并记住监听端口，之后MP插件的配置中需要填写`http:{ip}:{端口}`。


## 配置nonebot机器人

将本项目中的`nonebot`文件夹的内容下载到本地（或者直接下载解压这个压缩包[nonebot.zip](https://github.com/Putarku/MoviePilot-Help/blob/main/nonebot/nonebot.zip)），修改`plugins/sub.py`中的MP配置信息，之后在`nonebot`文件夹中打开命令行，运行`docker-compose up -d`，即可启动机器人。

在`LLOneBot`的`反向 WebSocket 监听地址`中填写`ws://ip:端口/onebot/v11/ws/`。

此时私聊或是群聊中发送`/sub 片名`即可触发查询并添加订阅。

 <div align=center> <img src="https://github.com/Putarku/MoviePilot-Help/raw/main/img/QQ20240922-163922.png" width="600"> </div>


<br>

## 配置MP插件
 <div align=center> <img src="https://github.com/Putarku/MoviePilot-Help/raw/main/img/QQ_1726668218021.png" width="600"> </div>
填写上面机器人的http地址和端口，以及想要通知的QQ号和QQ群号，同时点击`配置消息模板`，将下面的模板复制进去，保存即可。

```python
${render_image(image)}
${title}
${render_text(text)}
<%!
def render_image(image):
    if image:
        return f"[CQ:image,file={image}]"
    return ""

def render_text(text):
    if text is not None:
        return text
    return ""
%>
```

<br>

# 微信通知

### 如何配置企业微信通知
  
  1.参见[此教程](https://pt-helper.notion.site/50a7b44e255d40109bd7ad474abfeba5)
  
  <br>

### 建立企业微信的代理服务器
  

首先需要先准备一个具有固定公网地址的服务器，例如VPS，之后在该服务器上搭建代理服务。搭建方式可以有以下两种，两种任选其一即可

 > #### 1、使用[`caddy`](https://github.com/caddyserver/caddy)搭建

  1. 从 https://github.com/caddyserver/caddy/releases
下载自己对应系统的版本，例如 AMD64 下载`caddy_2.7.5_linux_amd64.tar.gz`
  1. 解压得到 `caddy` 文件 上传到`/usr/local/bin` 目录下，注意设置权限 `0755`
  2. 在任意目录新建 `Caddyfile` 文件(例如`/usr/local/caddy`) ，注意设置权限 `0755`，文
件内容如下
```yaml
:3000
reverse_proxy https://qyapi.weixin.qq.com {
header_up Host {upstream_hostport}
}
```
  1. SSH 控制台 cd 到 `Caddyfile` 文件的目录(例如`/usr/local/caddy`)
  2. 输入 caddr start 启动完成，在防火墙中放行3000端口
  3.  NasTools / MoviePilot 设置微信的代理 IP 地址为 `http://你的服务器ip/域名:3000`

<br>

 > #### 2、使用[ddsderek/wxchat](https://hub.docker.com/r/ddsderek/wxchat)docker镜像搭建

```yaml
version: '3.3'
services:
    wxchat:
        container_name: wxchat
        restart: always
        ports:
            - '3000:80'
        image: 'ddsderek/wxchat:latest'
```
```yaml
docker run -d \
    --name wxchat \
    --restart=always \
    -p 3000:80 \
    ddsderek/wxchat:latest
```
搭建完成后，在防火墙中放行3000端口，并在NasTools / MoviePilot 设置微信的代理 IP 地址为 `http://你的服务器ip/域名:3000`

<br>

### 配置企业微信时提示“回调失败”
  

 1.在企业微信的填写的地址可以有两种方式

 ①`http://ip:端口/api/v1/message/?token=moviepilot`

 ②`http://ip:端口/api/v1/message/`

 如果自行配置了`API_TOKEN`的值，那么就需要在地址后面补上`?token=moviepilot`。如果`API_TOKEN`为默认值，那么两种填写方式均可。

 2.确认在手机打开流量时，直接打开`http://ip:端口`，可以直接访问MoviePilot的网页。

 3.微信不支持ipv6,因此如果域名是使用ipv6解析的时候，也会导致不通过。如果没有ipv4的公网ip，建议使用内网穿透。

 <br>

 ### 企业微信部署后不显示菜单

如果是沿用nastool的代理服务器配置，需要在`nginx`的配置文件中额外加入下列代码，才能自动生成菜单。

```
location  /cgi-bin/menu/create {
    proxy_pass https://qyapi.weixin.qq.com;
}
```

 <br>



