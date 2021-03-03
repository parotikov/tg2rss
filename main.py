from typing import Optional
from fastapi import FastAPI, Response, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from telethon import TelegramClient, events, sync, functions, types, utils
from feedgen.feed import FeedGenerator
import markdown2
import asyncio
import os
import logging
from dotenv import load_dotenv
load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
master_account = os.getenv("MASTER_ACCOUNT")

logger = logging.getLogger("tg2rss")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("tg2rss.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

client = TelegramClient('tg2rss_session', api_id, api_hash)

loop = asyncio.get_event_loop()

async def start() -> None:
    await client.start()
    await client.send_message(master_account, 'tg2rss is running!')

async def stop() -> None:
    await client.disconnect()

try:
    loop.run_until_complete(start())
except Exception:
    logger.fatal("Failed to initialize", exc_info=True)
    # sys.exit(2)

try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.run_until_complete(stop())
except Exception:
    logger.fatal("Fatal error in event loop", exc_info=True)
    # sys.exit(3)


templates = Jinja2Templates(directory="templates")
app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/channel/{channel_alias}")
async def read_item(channel_alias: str, request: Request):
    
    try:
        channel = await client.get_entity(channel_alias)
    except Exception as e:
        logger.error('channel ERROR: {}'.format(e))
        channel = None
        return channel
    else:
        logger.info('Запросили канал {}'.format(channel.username))

    fg = FeedGenerator()
    fg.title('Recent posts from @' + channel_alias)
    fg.author( {'name':'Nik Parotikov','email':'nik.parotikov@gmail.com'} )
    fg.link( href=str(request.url), rel='alternate' )
    fg.subtitle(channel.title + ' ' + 'https://t.me/' + channel.username + ' (id ' + str(channel.id) + ')')
    fg.generator('http://tg2rss.prosto-tak.ru/ - Convert any Telegram channel to RSS feed')
    fg.link( href=str(request.url), rel='self' )
    fg.language('ru')

    # return channel


    # messages = await client.get_messages(channel, 20)
    # logger.info('сообщения из канала {}'.format(messages))

    async for message in client.iter_messages(channel, 20):
        # if hasattr(message.photo, 'file_reference'): 
        #     logger.info('Сообщение {}'.format(message.photo.sizes[-1].location))

        fe = fg.add_entry()
        fe.guid(guid='https://t.me/' + channel_alias + '/' + str(message.id), permalink=True)
        # fe.link(href='https://t.me/' + channel_alias + '/' + str(message.id))
        # fe.title(message.text)
        # fe.description(message.text)
        fe.content(markdown2.markdown(message.text))
        # fe.enclosure()
        fe.published(message.date)

    # rssfeed  = fg.rss_str(pretty=True)
    rssfeed  = fg.rss_str()

    # return rssfeed.decode()
    return Response(content=rssfeed, media_type="application/xml")
