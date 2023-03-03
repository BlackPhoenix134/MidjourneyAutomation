import json
import time
from attr import dataclass
import discord
from libs.data import MjChannelState, MjChannel, Storage, SETTINGS
from libs.botrequests import SimulatePrompt, SimulateUpscale
from discord.ext import tasks
from queue import Queue
import uuid
import os

@dataclass
class PromptCommand():
    str

channel_id_protocol = 1077698060085383188
channel_id_upscaled = 1077582970547871784

channel_bot_1 = 1077519680136294472
channel_bot_2 = 1077568863316746272
channel_bot_3 = 1077580957915287582

channel_state_storage = Storage[int, MjChannel]()
channel_state_storage.set(channel_bot_1, MjChannel(None, MjChannelState.DONE))
channel_state_storage.set(channel_bot_2, MjChannel(None, MjChannelState.DONE))
channel_state_storage.set(channel_bot_3, MjChannel(None, MjChannelState.DONE))

bot = discord.Bot(intents=discord.Intents.all())
command_queue = Queue()
imagine_queue = Queue()

out_folder = os.path.abspath("./out")
os.makedirs(out_folder, exist_ok=True)

def gen_image_file():
    file_name = str(uuid.uuid4()) + ".png"
    return os.path.join(out_folder, file_name)

@tasks.loop(seconds = 4)
async def command_queue_loop():
    while not command_queue.empty():
        data = command_queue.get()
        imagine_queue.put(data)
        print(f"Enqueued '{data}' at pos '{imagine_queue.qsize()}'")

@tasks.loop(seconds = 10) #rate limit prevention
async def imagine_queue_loop():
    free_channels = get_free_storage_units()
    for free_channel in free_channels:
        if not imagine_queue.empty():
            prompt = imagine_queue.get()    
            print(f"starting '{prompt}' from queue, sleeping 5 seconds")
            time.sleep(5) #rate limit prevention
            await do_imagine(free_channel, prompt)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    command_queue_loop.start()
    imagine_queue_loop.start()

def get_free_storage_unit() -> int:
    for channel_id, obj in channel_state_storage.local_storage.items():
        if obj.state is MjChannelState.DONE:
            return channel_id
    return -1


def get_free_storage_units() -> list[int]:
    free_channels = []
    for channel_id, obj in channel_state_storage.local_storage.items():
        if obj.state is MjChannelState.DONE:
            free_channels.append(channel_id)
    return free_channels

async def get_channel(channel_id: int):
    return (bot.get_channel(channel_id) or await bot.fetch_channel(channel_id))

async def on_message_attachment(message: discord.Message):
    channel_id = message.channel.id
    channel_state: MjChannel = channel_state_storage.get(channel_id) # todo handle shit attachments someone send just for fun
    if channel_state.state is MjChannelState.AWAITING_GEN:
        channel_state.state = MjChannelState.AWAITING_TARGET_SET
        await message.reply("upscale")
    elif channel_state.state is MjChannelState.AWAITING_UPSCALE:
        channel_state.state = MjChannelState.DONE
        url = message.attachments[0].url
        file = gen_image_file()
        await message.attachments[0].save(file)
        channel = await get_channel(channel_id_upscaled)
        await channel.send(url)

async def handle_req_upscale(message: discord.Message):
    await message.delete()
    print(f"upscale")
    target_channel_id = message.channel.id
    channel_state: MjChannel = channel_state_storage.get(target_channel_id)
    channel_state.state = MjChannelState.AWAITING_UPSCALE
    message_id = (message.reference.message_id)
    target_hash = (message.reference.resolved.attachments[0].url.split("_")[-1]).split(".")[0]
    try:
        response = SimulateUpscale(1, message_id, target_hash, target_channel_id, SETTINGS)
        if response.status_code >= 400:
            print("upscale returned 400")
            raise Exception("upscale returned 400")
    except Exception as e:
        print(e)
        channel_state.state = MjChannelState.DONE
        raise


async def do_imagine(channel_id, prompt):
    request_id = str(uuid.uuid4())
    channel_state = channel_state_storage.set(channel_id, MjChannel(request_id, MjChannelState.AWAITING_GEN))
    response = SimulatePrompt(prompt, channel_id, SETTINGS)
    print(response.content)
    if response.status_code >= 400:
        channel_state.state = MjChannelState.DONE
        raise Exception(f"Request image prompt failed, releasing lock")
    return request_id
    
def get_queue_content():
    return list(imagine_queue.queue)

def build_channel_status():
    send_dict = {}
    for k, v in channel_state_storage.local_storage.items():
        send_dict[k] = v.state
    return send_dict

async def request_imagine(prompt: str) -> str:
    print(f"imagine {prompt}")
    channel_id = get_free_storage_unit()
    if channel_id == -1:
        return None
    
    request_id = await do_imagine(channel_id, prompt)
    return request_id


@bot.event
async def on_message(message: discord.Message):
    if message.attachments:
       await on_message_attachment(message)
    if "upscale" in message.content:
        await handle_req_upscale(message)

@bot.command()
async def mj_protocol_status(ctx: discord.ApplicationContext):
    channel_id = ctx.channel.id
    if channel_id != channel_id_protocol:
        await ctx.respond("only usable in protocol channel")
        return
    response = build_channel_status()
    return ctx.respond(json.dumps(response))

@bot.command()
async def mj_protocol_imagine(ctx: discord.ApplicationContext, prompt: discord.Option(str)):
    channel_id = ctx.channel.id
    if channel_id != channel_id_protocol:
        await ctx.respond("only usable in protocol channel")
        return
    try:
        imagine_queue.put(prompt)
        print(f"Enqueued '{prompt}' at '{imagine_queue.qsize()}'")
        await ctx.respond(f"Enqueued '{prompt}' at '{imagine_queue.qsize()}'")
    except Exception as e:
        print(e)
        await ctx.respond(e)


def start():
    bot.run(SETTINGS.bot_token)
