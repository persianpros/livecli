import re

from livecli.plugin import Plugin
from livecli.plugin.api import http
from livecli.stream import HLSStream
from livecli.utils import update_scheme

__livecli_docs__ = {
    "domains": [
        "ntvspor.net",
        "eurostartv.com.tr",
    ],
    "geo_blocked": [],
    "notes": "",
    "live": True,
    "vod": False,
    "last_update": "2016-12-15",
}


class Dogus(Plugin):
    """
    Support for live streams from Dogus sites include ntv, ntvspor, and kralmuzik
    """

    url_re = re.compile(r"""https?://(?:www.)?
        (?:
            ntvspor.net/canli-yayin|
            eurostartv.com.tr/canli-izle
        )/?""", re.VERBOSE)
    mobile_url_re = re.compile(r"""(?P<q>["'])(?P<url>(https?:)?//[^'"]*?/live/hls/[^'"]*?\?token=)
                                   (?P<token>[^'"]*?)(?P=q)""", re.VERBOSE)
    token_re = re.compile(r"""token=(?P<q>["'])(?P<token>[^'"]*?)(?P=q)""")

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        res = http.get(self.url)
        mobile_url_m = self.mobile_url_re.search(res.text)

        mobile_url = mobile_url_m and update_scheme(self.url, mobile_url_m.group("url"))

        token = mobile_url_m and mobile_url_m.group("token")
        if not token:
            # if no token is in the url, try to find it else where in the page
            token_m = self.token_re.search(res.text)
            token = token_m and token_m.group("token")

        return HLSStream.parse_variant_playlist(self.session, mobile_url + token,
                                                headers={"Referer": self.url})


__plugin__ = Dogus
