import os
import re

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from fake_headers import Headers
from pyrogram.errors.exceptions.bad_request_400 import MediaCaptionTooLong

from userge import Message, pool, userge


HEADERS = Headers().generate()


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

    async with ClientSession(headers=HEADERS) as ses:
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

    async with ClientSession(headers=HEADERS) as ses:
        if search_mode:
            try:
                async with ses.get(
                    "https://wibudesu.co/", params={"s": input_str}
                ) as resp:
                    soup = BeautifulSoup(await resp.text(), "html.parser")
            except BaseException as err:
                return await msg_obj.err(str(err))

            search_content = soup.find_all("a", attrs={"class": "tip", "itemprop": "url"})
            n_result = len(search_content)

            for result in search_content:
                anime_title = result.get("title")
                anime_link = result.get("href")
                anime_score = result.find("div", class_="numscore").text
                anime_type = result.select_one("div[class*='typez ']").text
                content += (
                    f"• [{anime_title}]({anime_link})"
                    f"\n**Score :** __{anime_score}__ | **{anime_type}**\n\n"
                )

            if not n_result:
                content = "__No result found.__"

            msg = (
                f"**Wibudesu Search** | **Query :** `{input_str}`\n"
                f"__Found {n_result} result :__\n\n"
                f"{content}"
            )
            await msg_obj.edit(msg, disable_web_page_preview=True)
        else:
            if not re.search(r"https?://(?:www\.)?wibudesu\.co/(?:.+)/?", input_str):
                return await message.err("`Please enter valid wibudesu link!`")
            try:
                async with ses.get(input_str) as resp:
                    soup = BeautifulSoup(await resp.text(), "html.parser")
            except BaseException as err:
                return await msg_obj.err(str(err))

            # Anime title
            anime_title = soup.find("h1", class_="entry-title").text
            content = f"**{anime_title}**\n\n"

            # Anime download links
            for soraddl in soup.find_all("div", class_="soraddl dltwo"):
                header = soraddl.find("div", class_="sorattl").h3.text
                content += f"{header}\n" if header else ""
                for soraurl in soraddl.find_all("div", class_="soraurl"):
                    reso = soraurl.find("div", class_="res").text
                    links = [f"[{a.text}]({a.get('href')})" for a in soraurl.find_all("a")]
                    content += f"{reso} - {' | '.join(links)}\n"
                content += "\n"
            content = content.strip("\n")

            # Download anime banner
            anime_banner = soup.find(
                "img",
                class_="ts-post-image wp-post-image attachment-medium size-medium"
            ).get("data-lazy-src")
            banner_name = anime_banner.split("/")[-1]
            async with ses.get(anime_banner) as resp_img:
                with open(banner_name, "wb") as file:
                    file.write(await resp_img.read())

            try:
                await message.reply_photo(
                    photo=banner_name,
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
                os.remove(banner_name)
                await msg_obj.delete()


@userge.on_cmd(
    "otakudesu", about = {
        "header": "Anime Scraper for Otakudesu",
        "description": "Get anime download links from Otakudesu",
        "flags": {"-s": "for searching from otakudesu"},
        "examples": "{tr}wibudesu https://wibudesu.com/vinland-saga-bd-subtitle-indonesia \n"
                    "{tr}wibudesu -s Vinland Saga"})
async def otakudesu_scraper(message: Message):
    input_str = message.filtered_input_str
    content = ""

    async with ClientSession() as ses:
        async with ses.get(input_str) as req:
            soup = BeautifulSoup(await req.text(), "html.parser")

    dl_section = soup.find("div", class_="download")
    content += f"{dl_section.find('h4').text}\n"
    for link in dl_section.find_all("li"):
        reso = link.find("strong").text
        size = link.find("i").text
        links = [
            f"[{x.text}]({x['href']})"
            for x in link.find_all("a")
            if x.has_attr("href")
        ]
        content += f"**{reso}** - {' | '.join(links)} __({size})__\n"

    await message.reply_or_send_as_file(
        text=content,
        quote=True,
        disable_web_page_preview=True,
    )
