import os
import json
import time
import typing
import asyncio
import components
from itypes import *
from loguru import logger

PLAYLIST = []
CACHE = {}
INDEX = 0
PLAYING = False
CURRENT_URL = None

def load_config(name: str):
    """加载config文件
    
    Args:
        name: 配置文件名
    """
    def decorator(func: typing.Callable):
        path = os.path.join("configs", name + ".json")
        
        if not os.path.exists(path):
            logger.error("Config file not found")
            return func
        
        # 加载配置文件
        with open(path, "r", encoding="utf-8") as f:
            config = f.read()
            
        if not config:
            logger.error("Config file is empty")
            return func
        
        # 解析配置文件
        try:
            config = json.loads(config)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse config file: {e}")
            return func
        # 为函数添加参数(反向遍历以保证参数顺序)
        for argument in config[::-1]:
            argument["opt_type"] = getattr(OptionType, argument["opt_type"])
            func = slash_option(**argument)(func)
        return func
    return decorator

# 辅助函数
async def get_audio_url(song: str) -> str:
    """异步获取音频 URL
    
    Args:
        song: 音频 URL
    
    Returns:
        音频 URL
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'extract_flat': True,
    }
    loop = asyncio.get_event_loop()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = await loop.run_in_executor(None, lambda: ydl.extract_info(song, download=False))
            return info_dict['url'] if 'url' in info_dict else None
    except yt_dlp.utils.DownloadError:
        return None


async def search_audio(keyword: str, max_count: int) -> dict:
    """搜索音频
    
    Args:
        keyword: 搜索关键字
        max_count: 最大搜索结果数量
    
    Returns:
        搜索结果
    """
    # 异步搜索音频
    loop = asyncio.get_event_loop()
    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            return await loop.run_in_executor(None, lambda: ydl.extract_info(f"ytsearch{max_count}:{keyword}", download=False))
    except yt_dlp.utils.DownloadError:
        return None


async def start_play(ctx: SlashContext, message: Message):
    """开始播放音频
    
    Args:
        ctx: 上下文
        message: 消息
    """
    global PLAYING, CURRENT_URL, INDEX, CACHE
    components.previousButton.disabled = (INDEX == 0)
    components.nextButton.disabled = (INDEX + 1 == len(PLAYLIST))
    
    logger.info(f"当前索引: {INDEX} 当前播放列表长度: {len(PLAYLIST)}")
    
    logger.info("当前播放列表: " + str(PLAYLIST))
    logger.info("将components.nextButton.disabled设置为: " + str((INDEX + 1 == len(PLAYLIST))))
    logger.info("将components.previousButton.disabled设置为: " + str((INDEX == 0)))
    if PLAYING:
        logger.info("调用播放函数时，音频正在播放") 
        return
    
    # 如果机器人还没有加入语音频道，加入作者所在的语音频道
    if not ctx.voice_state or ctx.voice_state.channel != ctx.author.voice.channel:
        await ctx.author.voice.channel.connect()
    PLAYING = True
    while PLAYING:
        url = PLAYLIST[INDEX]
        await message.edit(content="正在加载音频...")

        logger.info(f"正在播放: {url}")
        CURRENT_URL = url

        if url in CACHE.keys():
            audio_url = CACHE[url]
        else:
            # 异步获取音频 URL
            audio_url = await get_audio_url(url)
        if audio_url is None:
            await message.edit(content="无法获取音频，请检查输入内容。")
            return

        # 使用 AudioVolume 播放音频
        audio = AudioVolume(audio_url)
        CACHE[url] = audio_url
        await send_panel(ctx, continueButton=True)
        
        await ctx.voice_state.play(audio)
        INDEX += 1
        logger.info("播放完成")

    PLAYING = False


def setIndex(i: int):
    """设置INDEX
    
    Args:
        i: 索引增量
    """
    global INDEX
    INDEX += i

async def send_panel(ctx: SlashContext, content: str = None, continueButton = False) -> Message:
    """发送播放面板
    
    Args:
        ctx: 上下文
        content: 内容
        continueButton: 是否设置stateButton为continueButton
        
    Returns:
        信息
    """
    if not PLAYING or not ctx.voice_state:
        logger.info("音频未播放或机器人未加入语音频道")
        await ctx.send("音频未播放或机器人未加入语音频道")
        return
    stateButton = components.stopButton if ctx.voice_state.playing or continueButton else components.continueButton
    components.previousButton.disabled = (INDEX == 0)
    components.nextButton.disabled = (INDEX + 1 == len(PLAYLIST))
    components.VDButton.disabled = (ctx.voice_state.volume == 0)
    components.VUButton.disabled = (ctx.voice_state.volume == 2)
    logger.info(f"在新pannel中components.previousButton.disabled: {components.previousButton.disabled}")
    logger.info(f"在新pannel中components.nextButton.disabled: {components.nextButton.disabled}")
    logger.info(f"在新pannel中components.VDButton.disabled: {components.VDButton.disabled}")
    logger.info(f"在新pannel中components.VUButton.disabled: {components.VUButton.disabled}")
    content = content if content else f"正在播放: {CURRENT_URL}"
    return await ctx.send(
        content=content, 
        components=[
            stateButton, components.previousButton, 
            components.nextButton, components.VDButton,
            components.VUButton
            ])

@slash_command(name="ping", description="测试延迟")
@load_config("ping")
async def ping(ctx: SlashContext, count: int = 5) -> None:
    """测试服务器与机器人的延迟
    
    Args:
        count: 测试次数
    Returns:
        None
    """
    
    pings = []
    
    before = time.perf_counter()
    message: Message = await ctx.send("正在计算延迟...")
    after = time.perf_counter()
    
    pings.append(after - before)
    for i in range(count - 1):
        before = time.perf_counter()
        await message.edit(content="正在计算延迟... {}次".format(i + 1))
        after = time.perf_counter()
        pings.append(after - before)
    
    await message.edit(content=f"延迟: {sum(pings) / count * 1000:.2f}ms")


@slash_command(name="play", description="播放音乐")
@load_config("play")
async def play(ctx: SlashContext, url: str) -> None:
    """播放音频，如果音频正在播放，则添加到播放列表
    
    Args:
        ctx: 上下文
        url: 音频 URL
    Returns:
        None
    """
    
    PLAYLIST.append(url)
    logger.info(f"{ctx.author.username} 添加音频: {url}")
    if PLAYING: 
        msg = await send_panel(ctx, "已添加到播放列表, 请等待当前音频播放完毕: " + CURRENT_URL)
        if msg is None:
            return
    else: msg = await ctx.send("正在加载音频...")
        
    await start_play(ctx, msg)

    
@slash_command(name="search", description="搜索音乐")
@load_config("search")
async def search(ctx: SlashContext, keyword: str, max_count: int = 5):
    """搜索音频并显示选择菜单
    
    Args:
        ctx: 上下文
        keyword: 搜索关键字
        max_count: 最大搜索结果数量
    
    Returns:
        None
    
    TODO: 优化搜索结果显示(显示添加到播放列表) 优化搜索速度
    """
    
    # 延迟响应以避免交互超时
    await ctx.defer()
    message = await ctx.send("正在搜索中...")

    
    info_dict = await search_audio(keyword, max_count)
    if info_dict is None:
        await ctx.send("无法获取音频，请检查输入内容。")
        return
    
    # 构建选择菜单
    options = []
    for i, entry in enumerate(info_dict["entries"]):
        options.append(StringSelectOption(label=entry["title"], value=entry["webpage_url"]))

    await message.edit(content="请选择要播放的音频", components=[StringSelectMenu(*options, custom_id="select_audio")])


@slash_command(name="panel", description="显示播放面板")
async def panel(ctx: SlashContext):
    """通过`send_panel`发送播放面板"""
    await send_panel(ctx)

@slash_command(name="showlist", description="显示播放列表")
async def showlist(ctx: SlashContext):
    """显示播放列表
    
    TODO: 优化显示效果
    """
    plylst = PLAYLIST[INDEX:]
    plylst.insert(0, CURRENT_URL)
    await ctx.send("当前列表: \n" + "\n".join(plylst))

@slash_command(name='connect', description="连接到语音频道")
async def connect(ctx: SlashContext):
    """连接到语音频道"""
    
    global PLAYING
    if not ctx.author.voice:
        await ctx.send("您未连接到语音频道")
        return

    channel = ctx.author.voice.channel
    await channel.connect()
    if INDEX != len(PLAYLIST):
        message = await ctx.send(f"已连接到语音频道: {channel.name}, 继续播放音频: {CURRENT_URL}")
        await start_play(ctx, message)
    else:
        await ctx.send(f"已连接到语音频道: {channel.name}")
        

@slash_command(name="disconnect", description="断开连接")
async def disconnect(ctx: SlashContext):
    """断开连接"""
    
    global PLAYING, INDEX
    if ctx.voice_state:
        PLAYING = False
        await ctx.voice_state.stop()
        INDEX -= 1
        await ctx.voice_state.disconnect()
        await ctx.send("已断开连接")
    else:
        await ctx.send("机器人未加入语音频道")

@slash_command(name="clear_list", description="清空播放列表")
async def clearList(ctx: SlashContext):
    """清空播放列表"""
    
    global PLAYLIST, INDEX
    PLAYLIST = []
    INDEX = 0
    await ctx.send("播放列表已清空")
