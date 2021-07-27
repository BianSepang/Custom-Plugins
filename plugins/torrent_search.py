from urllib.parse import quote

from aiohttp import ClientSession

from userge import userge, Message
from userge.utils import humanbytes


@userge.on_cmd("ts", about={
    "header": "Search torrent using torrent-paradise.ml ",
    "description": "Search torrent from different website "
                   "offered by torrent-paradise.ml. Default limit is 10.",
    "usage": "{tr}ts [flags] [query]",
    "examples": "{tr}ts -l5 The Avengers"})
async def torrent_search(message: Message):
    input_str = message.filtered_input_str
    await message.edit(f"**Searching for** `{input_str}`")
    limit = int(message.flags.get("-l", 10))

    try:
        async with ClientSession() as ses, ses.get(
            "https://torrent-paradise.ml/api/search", params={"q": input_str}
        ) as resp:
            if resp.status != 200:
                return await message.edit("`Failed to reach torrent-paradise`")
            data = await resp.json(content_type="text/plain")
            if not data:
                return await message.edit(f"`No torrents found for {input_str}`")
            data = sorted(data, key=lambda i: i["s"], reverse=True)
            reply = ""
            for torrent in data[:min(limit, len(data))]:
                if len(reply) < 4096 and int(torrent["s"]) > 0:
                    magnet = (
                        f"magnet:?xt=urn:btih:{torrent['id']}"
                        f"&dn={quote(torrent['text'])}"
                        f"&tr={quote('udp://tracker.coppersurfer.tk:6969/announce')}"
                        f"&tr={quote('udp://tracker.opentrackr.org:1337/announce')}"
                        f"&tr={quote('udp://tracker.leechers-paradise.org:6969/announce')}"
                    )
                    try:
                        reply = (
                            f"{reply}\n\n<b>{torrent['text']}</b>\n"
                            f"<b>Size :</b> <code>{humanbytes(torrent['len'])}</code>\n"
                            f"<b>Seeders :</b> <code>{torrent['s']}</code>\n"
                            f"<b>Leechers :</b> <code>{torrent['l']}</code>\n"
                            f"<code>{magnet}</code>"
                        )
                    except BaseException:
                        pass
            if reply == "":
                return await message.edit(f"`No torrents found for {input_str}`")
            await message.edit(reply, parse_mode="html")
    except BaseException as err:
        return await message.err(str(err))
