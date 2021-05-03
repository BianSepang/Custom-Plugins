# Userge Plugin for Torrent Search from torrent-paradise.ml
# Author: Nageen (https://github.com/archie9211) (@archie9211)
# All rights reserved

import re

from aiohttp import ClientSession

from userge import userge, Message
from userge.utils import humanbytes


@userge.on_cmd("tstp", about={
    'header': "Torrent Search On torrent-paradise.ml ",
    'description': "Search torrent from different websites"
                   "offered by torrent-paradise",
    'flags': {'-l': "limit the number of torrent results. (Default is 10)"},
    'usage': "{tr}tstp [flag] [query]",
    'examples': "{tr}tstp -5 The Avengers"})
async def torr_search(message: Message):
    query = message.filtered_input_str
    if message.reply_to_message:
        query = message.reply_to_message.text
    if not query:
        return await message.err(
            text="Put some query to search with or reply to message"
        )
    await message.edit("`Searching for available Torrents!`")
    max_limit = int(message.flags.get("-l", 10))
    try:
        async with ClientSession() as ses:
            resp = await ses.get("https://torrent-paradise.ml/api/search?q=" + query)
            torrents = await resp.text()
        reply_ = ""
        torrents = sorted(torrents, key=lambda i: i['s'], reverse=True)
        for torrent in torrents[:min(max_limit, len(torrents))]:
            if len(reply_) < 4096 and torrent["s"] > 0:
                try:
                    reply_ = (reply_ + f"\n\n<b>{torrent['text']}</b>\n"
                              f"<b>Size:</b> {humanbytes(torrent['len'])}\n"
                              f"<b>Seeders:</b> {torrent['s']}\n"
                              f"<b>Leechers:</b> {torrent['l']}\n"
                              f"<code>magnet:?xt=urn:btih:{torrent['id']}</code>")
                except Exception:
                    pass
        if reply_ == "":
            await message.edit(f"No torrents found for {query}!")
        else:
            await message.edit(text=reply_, parse_mode="html")
    except Exception:
        await message.edit("Torrent Search API is Down!\nTry again later")
