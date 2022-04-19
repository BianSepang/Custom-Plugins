import re

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from pyrogram.errors.exceptions.bad_request_400 import MediaCaptionTooLong
from userge import Message, userge


@userge.on_cmd(
    "kuso", about = {
        "header": "Anime Scraper for Kusonime",
        "description": "Get anime download links from Kusonime",
        "flags": {"-s": "for searching from kusonime"},
        "examples": "{tr}kuso https://kusonime.com/enen-shouboutai-batch-sub-indo \n"
                    "{tr}kuso -s Fire Force"})
async def kuso_scraper(message: Message):
    input_str = message.filtered_input_str
    content = ""
    msg_obj = await message.edit("`Getting information...`")

    search_mode = False
    if "-s" in message.flags:
        search_mode=True

    if not input_str:
        return await msg_obj.err("`Please enter a query to search/scrape!`")

    async with ClientSession() as ses:
        if search_mode:
            try:
                async with ses.get(
                    "https://kusonime.com", params={"s": input_str}
                ) as resp:
                    soup = BeautifulSoup(await resp.text(), "html.parser")
            except BaseException as err:
                return await msg_obj.err(err)

            n_result = 0
            for search_content in soup.find_all("div", class_="content"):
                genres = [
                    genre.text
                    for genre in search_content.find_all("a")
                    if genre.has_attr("rel")
                ]
                anime_title = f"[{search_content.h2.text}]({search_content.h2.a.get('href')})"
                content += f"• {anime_title}\n**Genre :** __{', '.join(genres)}__\n\n"
                n_result += 1

            if not n_result:
                content = "__No result found.__"

            msg = (
                f"**Kusonime Search** | **Query :** `{input_str}`\n"
                f"__Found {n_result} result :__\n\n"
                f"{content}"
            )
            await msg_obj.edit(msg, disable_web_page_preview=True)
        else:
            if not re.search(r"https?://(?:www\.)?kusonime\.com/(?:.+)/?", input_str):
                return await message.err("`Please enter valid kusonime link!`")

            try:
                async with ses.get(input_str) as resp:
                    soup = BeautifulSoup(await resp.text(), "html.parser")
            except BaseException as err:
                return await msg_obj.err(str(err))

            # Get anime title and info
            anime_title = soup.find("h1", class_="jdlz").text
            anime_banner = soup.find("img", class_="wp-post-image").get("src")
            content = f"[{anime_title}]({input_str})\n"
            content += "\n"

            # Get anime link
            for smokeddl in soup.find_all("div", class_="smokeddl"):
                for smokettl in smokeddl.find_all("div", class_="smokettl"):
                    dl_head = smokettl.text
                    content += f"**{dl_head}**\n"
                for smokeurl in smokeddl.find_all("div", class_="smokeurl"):
                    reso = smokeurl.find("strong").text
                    content += f"__{reso}__\n"
                    links = [
                        f"[{link.text}]({link.get('href')})"
                        for link in smokeurl.find_all("a")
                    ]
                    content += " | ".join(links)
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


@userge.on_cmd(
    "wibudesu", about = {
        "header": "Anime Scraper for Wibudesu",
        "description": "Get anime download links from Wibudesu",
        "flags": {"-s": "for searching from wibudesu"},
        "examples": "{tr}wibudesu https://wibudesu.com/vinland-saga-bd-subtitle-indonesia \n"
                    "{tr}wibudesu -s Vinland Saga"})
async def wibudesu_scraper(message: Message):
    input_str = message.filtered_input_str
    content = ""
    msg_obj = await message.edit("`Getting information...`")

    search_mode = False
    if "-s" in message.flags:
        search_mode = True

    if not input_str:
        return await msg_obj.err("`Please enter a query to search/scrape!`")

    async with ClientSession() as ses:
        if search_mode:
            try:
                async with ses.get(
                    "https://wibudesu.com/", params={"s": input_str, "post_type": "post"}
                ) as resp:
                    soup = BeautifulSoup(await resp.text(), "html.parser")
            except BaseException as err:
                return await msg_obj.err(str(err))

            n_result = 0
            for post_section in soup.find_all("div", attrs={"class": "detpost"}):
                anime_title = post_section.find("a").get("title")
                anime_url = post_section.find("a").get("href")
                genre = [
                    genre.text
                    for genre in post_section.find_all("a", attrs={"rel": "category tag"})
                    if all(x not in genre.text for x in ["Version", "Uncategorized"])
                ]
                content += (
                    f"• [{anime_title}]({anime_url})\n"
                    f"**Genre :** __{', '.join(genre)}__\n\n"
                )
                n_result += 1

            if not n_result:
                content = "__No result found.__"

            msg = (
                f"**Wibudesu Search** | **Query :** `{input_str}`\n"
                f"__Found {n_result} result :__\n\n"
                f"{content}"
            )
            await msg_obj.edit(msg, disable_web_page_preview=True)
        else:
            if not re.search(r"https?://(?:www\.)?wibudesu\.com/(?:.+)/?", input_str):
                return await message.err("`Please enter valid wibudesu link!`")
            try:
                async with ses.get(input_str) as resp:
                    soup = BeautifulSoup(await resp.text(), "html.parser")
            except BaseException as err:
                return await msg_obj.err(str(err))

            anime_section = soup.find("div", class_="lexot")

            # Anime Info
            anime_banner = anime_section.find("img").get("data-lazy-src")
            anime_title = soup.find("div", class_="jdlr")
            content += f"[{anime_title.h1.text}]({input_str})\n\n"

            # Anime Download Links
            header_dl = [
                p for p in anime_section.find_all("p", attrs={"style": "text-align: center;"})
                if p.strong
            ][0]
            content += f"**{header_dl.strong.text}**\n"
            for p_tag in anime_section.find_all("p")[1:]:
                if p_tag.has_attr("style") and p_tag.strong and "LINK" not in p_tag.strong.text:
                    content += f"\n**{p_tag.strong.text}**\n"
                if (
                    not p_tag.has_attr("style")
                    and p_tag.find("a")
                    and "Sinopsis" not in p_tag.strong.text
                ):
                    reso = p_tag.strong.text.replace("[", "(").replace("]", ")")
                    content += f"__{reso}__\n"
                    links = [
                        f"[{link.text.strip()}]({link.get('href')})"
                        for link in p_tag.find_all("a")
                    ]
                    content += f" | ".join(links)
                    content += "\n"

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
            finally:
                await msg_obj.delete()
