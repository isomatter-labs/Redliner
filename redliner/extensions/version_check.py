import requests

from redliner.common.constants import REMOTE_CHANGELOG


def fetch_remote_version(cbk:callable):
    try:
        resp = requests.get(REMOTE_CHANGELOG)
        resp.raise_for_status()
        txt = resp.text.strip()
        cbk(txt)
    except Exception as e:
        cbk(e)
