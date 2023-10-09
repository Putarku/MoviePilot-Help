# **一些说明**
 - 本仓库仅作为对moviepilot的一些使用上的内容补充
 - 提问题前一定记着先去看看日志，一般日志会写出问题所在，在提问时记得附上日志截图
 - 待补充

---

# **站点问题**

### 为什么我的站点添加不了？
  MoviePilot使用的是`域名白名单`机制，如果添加不了可以去站点公告或者论坛查看站点的其他可用域名，并尝试添加。出于保护站点的原因，这里不再列出常用站点的可用域名。

### 为什么我的站点添加了搜索不到内容？
  可通过**查看日志**按以下顺序排查
  1. `站点`或`tmdb`是否能正常连接上
  2. 检查是否返回了搜索结果
  3. 搜索结果是否被`搜索优先级`过滤

---

# **转移问题**

### 转移媒体文件时提示“-1”错误
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
![路径解析](img/路径解析.png)