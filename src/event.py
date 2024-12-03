import interactions
from loguru import logger
from itypes import *
from components import *
from commands import start_play, send_panel, setIndex, PLAYLIST, INDEX

ORIGIN_VOLUME = 0

@interactions.listen("on_ready")
async def on_ready():
    logger.info("server is ready")

@interactions.listen("on_message_create")
async def on_message_create(event: interactions.api.events.MessageCreate):
    msg: interactions.Message = event.message
    logger.info(f"{msg.author.username} message: {msg.content}")
    
@interactions.listen(Component)
async def componentHandle(event: Component):
    global ORIGIN_VOLUME, PLAYLIST, INDEX
    ctx = event.ctx
    await ctx.defer(edit_origin=True)
    match ctx.custom_id:
        case "play":
            ctx.voice_state.resume()
            await ctx.message.edit(components=[stopButton, previousButton, nextButton, VDButton, VUButton])
            logger.info(f"{ctx.author.username} 播放音乐")
        case "pause":
            ctx.voice_state.pause()
            await ctx.message.edit(components=[continueButton, previousButton, nextButton, VDButton, VUButton])
            logger.info(f"{ctx.author.username} 暂停音乐")
            
        case "volume_down":
            if ctx.voice_state.volume - 0.2 <= 0:
                ctx.voice_state.volume = 0
                VDButton.disabled = True
            else:
                ctx.voice_state.volume = round(ctx.voice_state.volume - 0.2, 1)
            
            VUButton.disabled = False
            stateButton = stopButton if ctx.voice_state.playing else continueButton
            await ctx.message.edit(components=[stateButton, previousButton, nextButton, VDButton, VUButton])
            logger.info(f"{ctx.author.username} 音量减小, 音量：{ctx.voice_state.volume}")
            
        case "volume_up":
            if ctx.voice_state.volume + 0.2 >= 2:
                ctx.voice_state.volume = 2
                VUButton.disabled = True
            else:
                ctx.voice_state.volume = round(ctx.voice_state.volume + 0.2, 1)
            
            VDButton.disabled = False
            stateButton = stopButton if ctx.voice_state.playing else continueButton
            await ctx.message.edit(components=[stateButton, previousButton, nextButton, VDButton, VUButton])
            logger.info(f"{ctx.author.username} 音量增大, 音量：{ctx.voice_state.volume}")

        case "select_audio":
            PLAYLIST.append(ctx.values[0])
            await send_panel(ctx)
            await start_play(ctx, ctx.message)
        
        case "next":
            await ctx.voice_state.stop()  # 停止当前音频        
            logger.info("已停止当前音频，准备播放下一首")
            await send_panel(ctx, next=True)
            await start_play(ctx, ctx.message)
        
        case "previous": 
            await ctx.voice_state.stop()
            setIndex(-2)
            logger.info("已停止当前音频，准备播放上一首")
            await send_panel(ctx)
            await start_play(ctx, ctx.message)