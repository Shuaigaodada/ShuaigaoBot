import asyncio
from qqmusic_api import song

async def get_music_link(keyword):
    # 使用关键词搜索音乐，返回结果中取第一首
    search_result = await song.search_by_type(keyword=keyword, num=1)
    
    if not search_result['data']['list']:
        print("未找到相关歌曲")
        return None

    # 获取歌曲 MID
    song_mid = search_result['data']['list'][0]['mid']

    # 根据歌曲 MID 获取歌曲的详情
    song_details = await song.get_song_by_id(song_mid)
    
    # 获取歌曲的播放链接
    song_url = song_details.get('url')
    
    if song_url:
        print(f"歌曲《{song_details['name']}》的播放链接为：{song_url}")
        return song_url
    else:
        print("无法获取歌曲播放链接，可能受版权或会员限制")
        return None

# 异步运行获取音乐链接函数
asyncio.run(get_music_link("周杰伦"))
