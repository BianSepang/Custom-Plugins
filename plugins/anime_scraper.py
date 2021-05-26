from aiohttp import ClientSession
from bs4 import BeautifulSoup
from pyrogram.errors.exceptions.bad_request_400 import MediaCaptionTooLong

from userge import userge, Message


@userge.on_cmd(
    "kuso", about = {
        "header": "Anime Scraper for Kusonime",
        "description": "Get anime info and "
                       "download links from Kusonime",
        "flags": {"-search": "for searching from kusonime"},
        "examples": "{tr}kuso https://kusonime.com/enen-shouboutai-batch-sub-indo \n"
                    "{tr}kuso -search Fire Force"})
async def kuso_scraper(message: Message):
    input_str = message.filtered_input_str
    content = ""
    search_mode = False
    if "-search" in message.flags:
        search_mode=True

    async with ClientSession() as ses:
        if search_mode:
            if not input_str:
                await message.err("`Please enter a query to search!`")
                return
            await message.edit("`Searching...`")
            params = {"s": input_str}
            try:
                async with ses.get("https://kusonime.com", params=params) as resp:
                    page_content = await resp.text()
            except BaseException as err:
                await message.err(err)
                return
            soup = BeautifulSoup(page_content, "html.parser")
            page_content = soup.find_all("div", class_="content")
            if not page_content:
                content = "__No result found.__"
            for search_content in page_content:
                genres = ""
                for a_tag in search_content.find_all("a"):
                    if a_tag.has_attr("title"):
                        anime_title = f"[{a_tag.text}]({a_tag.get('href')})"
                        content += f"• {anime_title}\n"
                    if a_tag.has_attr("rel"):
                        genres += f"__{a_tag.text}__, "
                genres = genres.removesuffix(", ")
                content += f"Genres : {genres}\n\n"
                del genres
            msg = (
                f"**Kusonime Search** | **Query :** `{input_str}`\n"
                f"__Found {len(page_content)} result :__\n\n"
                f"{content}"
            )
            await message.edit(msg, disable_web_page_preview=True)
        else:
            if not input_str or "kusonime" not in input_str:
                await message.err("`Please enter kusonime link to scrape!`")
                return
            msg_obj = await message.edit("`Getting Information`")
            try:
                async with ses.get(input_str) as resp:
                    page_content = await resp.text()
            except BaseException as err:
                await msg_obj.err(err)
                return
            soup = BeautifulSoup(page_content, "html.parser")
            # Get anime title and info
            anime_title = soup.find("h1", class_="jdlz").text
            anime_banner = soup.find(
                "img",
                class_="attachment-thumb-large size-thumb-large wp-post-image"
            )
            anime_banner = anime_banner.get("src")
            anime_info = soup.find("div", class_="info")
            content = f"[{anime_title}]({input_str})\n"
            for info in anime_info.find_all("p"):
                content += info.text + "\n"
            content += "\n"
            # Get anime link
            for smokeddl in soup.find_all("div", class_="smokeddl"):
                    for smokettl in smokeddl.find_all("div", class_="smokettl"):
                        dl_head = smokettl.text
                        content += f"**{dl_head}**\n"
                    for smokeurl in smokeddl.find_all("div", class_="smokeurl"):
                        reso = smokeurl.find("strong").text
                        content += f"__{reso}__\n"
                        for links in smokeurl.find_all("a"):
                            dl_link = f"[{links.text}]({links.get('href')})"
                            content += dl_link + " | "
                        content = content.removesuffix("| ")
                        content += "\n"
                    content += "\n"
            await msg_obj.delete()
            try:
                await message.reply_photo(
                    photo=anime_banner,
                    caption=content,
                    quote=True,
                )
            except MediaCaptionTooLong:
                await message.reply_or_send_as_file(
                    text=content,
                    quote=True,
                    disable_web_page_preview=True,
                )