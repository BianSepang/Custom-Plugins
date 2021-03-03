#!/usr/bin/env python3
# https://github.com/Sorrow446/ZS-DL
# plugin by @aryanvikash

import re

import requests

from userge import userge, Message, pool
from userge.plugins.misc.download import url_download


@userge.on_cmd("zippy", about={
    'header': "Download from Zippyshare website",
    'usage': "{tr}zippy : [Zippyshare Link ]",
    'examples': "{tr}zippy https://www10.zippyshare.com/v/dyh988sh/file.html"}, del_pre=True)
async def zippyshare(message: Message):
    """ zippy to direct and automatically download """
    url = message.input_str
    try:
        direct_url = await _generate_zippylink(url)
        dl_loc, dl_time = await url_download(message, direct_url)
        await message.edit(f"Downloaded to `{dl_loc}` in {dl_time} seconds.")
    except Exception as z_e:  # pylint: disable=broad-except
        await message.edit(f"`{z_e}`")


_REGEX_LINK = r'https://www(\d{1,3}).zippyshare.com/v/(\w{8})/file.html'
_REGEX_RESULT = (
    r'document.getElementById\(\'dlbutton\'\).href = "/d/[a-zA-Z\d]{8}/" '
    r'\+ \((\d+) % (\d+) \+ (\d+) % (\d+)\) \+ "\/(.+)";'
)
_HEADERS = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome"
                          "/75.0.3770.100 Safari/537.36"}


@pool.run_in_thread
def _generate_zippylink(url):
    session = requests.Session()
    session.headers.update(_HEADERS)
    with session as ses:
        match = re.match(_REGEX_LINK, url)
        if not match:
            raise ValueError("Invalid URL: " + str(url))
        server, id_ = match.group(1), match.group(2)
        res = ses.get(url)
        res.raise_for_status()
        match = re.search(_REGEX_RESULT, res.text)
        if not match:
            raise ValueError("Invalid Response!")
        val_1 = int(match.group(1))
        val_2 = int(match.group(2))
        val_3 = int(match.group(3))
        val_4 = int(match.group(4))
        val = val_1 % val_2 + val_3 % val_4
        name = match.group(5)
        d_l = "https://www{}.zippyshare.com/d/{}/{}/{}".format(server, id_, val, name)
    return d_l
