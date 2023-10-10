# **一些说明**
 - 本仓库仅作为对moviepilot的一些使用上的内容补充
 - 提问题前一定记着先去看看日志，一般日志会写出问题所在，在提问时记得附上日志截图
 - 待补充

---

# **站点问题**

- ### 为什么我的站点添加不了？
  MoviePilot使用的是`域名白名单`机制，如果添加不了可以去站点公告或者论坛查看站点的其他可用域名，并尝试添加。

例如问的最多的馒头，可以尝试将域名的`.cc`更改为`.io`进行添加



- ### 为什么我的站点添加了搜索不到内容？
  可通过**查看日志**按以下顺序排查
  1. `站点`或`tmdb`是否能正常连接上
  2. 检查是否返回了搜索结果
  3. 搜索结果是否被`搜索优先级`过滤
  4. 有时种子名与tmdb进行匹配时，由于命名问题可能会同时存在多个同名影视，导致匹配到其他影视剧，也会造成搜索失败，此时建议直接去站点或是使用ptpp进行检索下载。

---

# **转移问题**

- ### 转移媒体文件时提示“-1”错误
一般出现这种提示是出现了跨盘的问题，在建立docker容器时，路径的映射容易出现以下情况
```yaml
        volumes:
            - '/volume1/video/media:/media'
            - '/volume1/video/link:/link'
```
此时在容器内部，视频文件和硬链接目录为无隶属关系的两个文件夹，此时使用硬链接时便会报错。正确的路径映射应为下面这种
```yaml
        volumes:
            - '/volume1/video:/volume1/video'
        #此时环境变量中的路径设置
        environment:
            # 下载保存目录
            - 'DOWNLOAD_PATH=/volume1/video/download'
            - 'DOWNLOAD_MOVIE_PATH=/volume1/video/download/movies'
            - 'DOWNLOAD_TV_PATH=/volume1/video/download/tv'
            - 'DOWNLOAD_ANIME_PATH=/volume1/video/download/anime'
            # 媒体库目录
            - 'LIBRARY_PATH=/volume1/video/link'
            - 'LIBRARY_MOVIE_NAME=movies'
            - 'LIBRARY_TV_NAME=tv'
            - 'LIBRARY_ANIME_NAME=anime'

```
保持目录与宿主机一致，此时在配置文件中可以在后续维护中减少出问题的概率。关于其他容器关于路径的配置问题可以参见下面这张图
 <div align=center> <img src="img/路径解析.png" width="600"> </div>

# **刮削问题**

- ### 刮削完成后演员不显示头像/英文名字

1.使用`演职人员刮削`插件，需要将emby的演员元数据文件夹映射进MoviePilot的容器内。

 - docker版本的emby，其元数据文件夹的路径为config文件内的`/emby/metadata/people`
 - 群晖套件版本的emby，其元数据文件夹的路径为`/volume1/@appdata/EmbyServer/metadata/people`,其中`/volume1`为你安装套件所在的硬盘

2.使用[MediaServerTools](https://github.com/sleikang/MediaServerTools)来刷新emby的元数据，config文件可在[这里](https://github.com/sleikang/MediaServerTools/blob/main/config/config.yaml)下载。

```yaml
version: '3.3'
services:
    MediaServerTools:
        container_name: MediaServerTools
        volumes:
            - './config:/config'
        environment:
            - TZ=Asia/Shanghai
            - PUID=1000
            - PGID=1000
            - UMASK=022
            - MediaServerTools_AUTO_UPDATE=true # 自动更新
            - MediaServerTools_CN_UPDATE=true # 使用国内源更新
        network_mode: host
        logging:
          driver: json-file
          options:
            max-size: 5m
        image: 'ddsderek/mediaservertools:latest'

```

- ### 刮削很慢或者是刮削不出图片

1.检查日志

2.检查Tmdb、FanArt等网站的的连接性，推荐将这些站点手动添加到代理的规则列表或配置文件中。以下以clash为例：
```yaml
  - DOMAIN-SUFFIX,fanart.tv,🚀 节点选择 #🚀 节点选择更改为clash文件中的代理服务器组的名称即可
  - DOMAIN-KEYWORD,tmdb,🚀 节点选择
  - DOMAIN-KEYWORD,themoviedb,🚀 节点选择  
```

- ### 资源不识别导致无法刮削

1.检查日志，查看是否能正常连接tmdb

2.资源名称命名与tmdb不同导致无法识别，下面是一个例子

 <div align=center> <img src="./img/图片1.png" width="600"> </div>

 通过检查tmdb的剧集的别名可以看到，该剧集目前是没有`Otona_Precure_23`的译名的，因此也会导致MoviePilot无法识别
 
 <div align=center> <img src="./img/图片2.png" width="600"> </div>

解决方法也很简单，在`设定-词表-自定义识别词`中填写

> **Otona_Precure_23 => Kibou no Chikara: Otona Precure `23**
> 
> 推荐优先将替换为**英文译名或原名**，中文译名有时候会歧义导致被经常修改

之后就可以正常识别了，有时候改完以后还无法识别，可以先**清除缓存**后再进行尝试。

 <div align=center> <img src="./img/图片3.png" width="600"> </div>


# **订阅问题**

