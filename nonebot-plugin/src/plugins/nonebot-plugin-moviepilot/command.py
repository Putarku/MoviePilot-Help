from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.typing import T_State

from .api import MoviepilotApi


search_movie = on_command("sub")
api = MoviepilotApi()


@search_movie.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()
    if args:
        movie_name = args.replace("/sub ", "", 1)  # 使用str.replace()移除"/sub "，第三个参数1表示只替换第一次出现的"/sub "
        state["movie_name"] = movie_name


@search_movie.got("movie_name", prompt="你要查询哪部影片？")
async def handle_movie_name(bot: Bot, event: Event, state: T_State):
    movie_name = state["movie_name"]
    logger.debug(movie_name)

    movies = await api.search_media_info(movie_name)
    if movies:
        movie_list = "\n".join([f"{i + 1}. {movie['title']} ({movie['year']})\n"
                                f"{movie['detail_link']}\n" for i, movie in enumerate(movies)])
        await bot.send(
            event=event,
            message=f"查询到的影片如下，请回复序号进行订阅：\n{movie_list}"
        )
        state["movies"] = movies
    else:
        await search_movie.finish("没有查询到影片，请检查名字。")


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
            if selected_movie['type'] == "电视剧":
                # 如果是电视剧，获取所有季数
                seasons = await api.list_all_seasons(selected_movie['tmdb_id'])
                if seasons:
                    season_list = "\n".join(
                        [f"第 {season['season_number']} 季 {season['name']}" for season in seasons])
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
                success = await api.subscribe_movie(selected_movie)
                if success:
                    await search_movie.finish("订阅成功！")
                else:
                    await search_movie.finish("订阅失败。")
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
        success = await api.subscribe_series(selected_movie, selected_season_number)
        if success:
            await search_movie.finish("订阅成功！")
        else:
            await search_movie.finish("订阅失败。")
    except ValueError:
        await search_movie.reject("请输入有效的数字序号：")
