from nonebot import on_command, get_driver
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
import requests
import json

# 获取配置文件中的信息
# config = get_driver().config
mp_url = ""
username = ""
password = ""

# 获取MoviePilot-Token
async def get_access_token(url, username, password):
    url = f"{url}/api/v1/login/access-token"
    payload = {
        "username": username,
        "password": password
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        json_data = response.json()
        access_token = json_data.get("access_token")
        return access_token
    except requests.exceptions.RequestException as e:
        print(f"Error fetching access token: {e}")
        return None

# 处理返回的影片
async def search_media_info(url, media_name, mp_token):
    search_url = f"{url}/api/v1/media/search?title={media_name}"
    headers = {'Authorization': mp_token}
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        movies = response.json()
        return movies
    except requests.exceptions.RequestException as e:
        print(f"Error searching movies: {e}")
        return None
# 列出所有季
async def list_all_seasons(url, tmdbid, mp_token):
    season_url = f'{url}/api/v1/tmdb/seasons/{tmdbid}'
    headers = {
        'Authorization': f'{mp_token}',
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(season_url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        # 解析响应的JSON数据
        seasons = response.json()
        return seasons
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
# 订阅电影
async def subscribe_movie(url, movie, mp_token):
    subscribe_url = f"{url}/api/v1/subscribe/"
    headers = {
        'Authorization': mp_token,
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    body = {
        "name": movie['title'],
        "tmdbid": movie['tmdb_id']
    }
    try:
        response = requests.post(subscribe_url, json=body, headers=headers)
        response.raise_for_status()
        json_data = response.json()
        return json_data.get("success")
    except requests.exceptions.RequestException as e:
        print(f"Error subscribing to movie: {e}")
        return False

# 订阅剧集
async def subscribe_series(url, movie, season, mp_token):
    subscribe_url = f"{url}/api/v1/subscribe/"
    headers = {
        'Authorization': mp_token,
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    season = int(season)
    body = {
        "name": movie['title'],
        "tmdbid": movie['tmdb_id'],
        "season": season
    }
    try:
        response = requests.post(subscribe_url, json=body, headers=headers)
        response.raise_for_status()
        json_data = response.json()
        return json_data.get("success")
    except requests.exceptions.RequestException as e:
        print(f"Error subscribing to movie: {e}")
        return False

# 创建查询电影的命令处理器
search_movie = on_command("sub")

@search_movie.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()
    if args:
        movie_name = args.replace("/sub ", "", 1)  # 使用str.replace()移除"/sub "，第三个参数1表示只替换第一次出现的"/sub "
        state["movie_name"] = movie_name

@search_movie.got("movie_name", prompt="你要查询哪部影片？")
async def handle_movie_name(bot: Bot, event: Event, state: T_State):
    movie_name = state["movie_name"]
    print(movie_name)
    access_token = await get_access_token(mp_url, username, password)
    if access_token:
        mp_token = "Bearer " + access_token
        movies = await search_media_info(mp_url, movie_name, mp_token)
        if movies:
            movie_list = "\n".join([f"{i+1}. {movie['title']} ({movie['year']})\n"
                                    f"{movie['detail_link']}\n" for i, movie in enumerate(movies)])
            await bot.send(
                event=event,
                message=f"查询到的影片如下，请回复序号进行订阅：\n{movie_list}"
            )
            state["movies"] = movies
        else:
            await search_movie.finish("没有查询到影片，请检查名字。")
    else:
        await search_movie.finish("获取访问令牌失败。")

@search_movie.got("movie_index", prompt="请输入电影序号进行订阅，或输入0退出：")
async def handle_movie_index(bot: Bot, event: Event, state: T_State):
    movie_index = str(event.get_message()).strip()  # 将 Message 对象转换为字符串并去除空格

    # 如果用户输入0，则结束对话
    if movie_index == "0":
        await search_movie.finish("操作已取消。")
        return

    try:
        selected_index = int(movie_index) - 1
        movies = state["movies"]
        if 0 <= selected_index < len(movies):
            selected_movie = movies[selected_index]
            access_token = await get_access_token(mp_url, username, password)
            if access_token:
                mp_token = "Bearer " + access_token
                if selected_movie['type'] == "电视剧":
                    # 如果是电视剧，获取所有季数
                    seasons = await list_all_seasons(mp_url, selected_movie['tmdb_id'], mp_token)
                    if seasons:
                        season_list = "\n".join([f"第 {season['season_number']} 季 {season['name']}" for season in seasons])
                        await bot.send(
                            event=event,
                            message=f"请选择季数：\n{season_list}"
                        )
                        state["selected_movie"] = selected_movie
                        state["seasons"] = seasons
                        return
                    else:
                        await search_movie.finish("没有找到可用的季数。")
                else:
                    # 如果是电影，直接订阅
                    success = await subscribe_movie(mp_url, selected_movie, mp_token)
                    if success:
                        await search_movie.finish("订阅成功！")
                    else:
                        await search_movie.finish("订阅失败。")
            else:
                await search_movie.finish("获取访问令牌失败。")
        else:
            await search_movie.reject("序号无效，请重新输入：")
    except ValueError:
        await search_movie.reject("请输入有效的数字序号：")

@search_movie.got("season_number", prompt="请输入季数进行订阅，或输入0退出：")
async def handle_season_number(bot: Bot, event: Event, state: T_State):
    season_number = str(event.get_message()).strip()  # 将 Message 对象转换为字符串并去除空格

    # 如果用户输入0，则结束对话
    if season_number == "0":
        await search_movie.finish("操作已取消。")
        return

    try:
        selected_season_number = int(season_number)
        selected_movie = state["selected_movie"]
        access_token = await get_access_token(mp_url, username, password)
        if access_token:
            mp_token = "Bearer " + access_token
            # 订阅指定季数的电视剧
            success = await subscribe_series(mp_url, selected_movie, selected_season_number, mp_token)
            if success:
                await search_movie.finish("订阅成功！")
            else:
                await search_movie.finish("订阅失败。")
        else:
            await search_movie.finish("获取访问令牌失败。")
    except ValueError:
        await search_movie.reject("请输入有效的数字序号：")




