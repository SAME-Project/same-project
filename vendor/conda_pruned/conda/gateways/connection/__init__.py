# -*- coding: utf-8 -*-
# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import absolute_import, division, print_function, unicode_literals
from functools import partial


def should_bypass_proxies_patched(should_bypass_proxies_func, url, no_proxy=None):
    # Monkey patch requests, per https://github.com/requests/requests/pull/4723
    if url.startswith("file://"):
        return True
    try:
        return should_bypass_proxies_func(url, no_proxy)
    except TypeError:
        # For versions of requests we shouldn't have to deal with.
        # https://github.com/conda/conda/issues/7503
        # https://github.com/conda/conda/issues/7506
        return should_bypass_proxies_func(url)


from requests import ConnectionError, HTTPError, Session
from requests.adapters import BaseAdapter, HTTPAdapter
from requests.auth import AuthBase, _basic_auth_str
from requests.cookies import extract_cookies_to_jar
from requests.exceptions import InvalidSchema, SSLError, ProxyError as RequestsProxyError
from requests.hooks import dispatch_hook
from requests.models import Response
from urllib3.exceptions import InsecureRequestWarning
from requests.structures import CaseInsensitiveDict
from requests.utils import get_auth_from_url, get_netrc_auth
from urllib3.util.retry import Retry

# monkeypatch requests
from requests.utils import should_bypass_proxies
import requests.utils  # lgtm [py/import-and-import-from]

requests.utils.should_bypass_proxies = partial(should_bypass_proxies_patched, should_bypass_proxies)


dispatch_hook = dispatch_hook
BaseAdapter = BaseAdapter
Response = Response
CaseInsensitiveDict = CaseInsensitiveDict
Session = Session
HTTPAdapter = HTTPAdapter
AuthBase = AuthBase
_basic_auth_str = _basic_auth_str
extract_cookies_to_jar = extract_cookies_to_jar
get_auth_from_url = get_auth_from_url
get_netrc_auth = get_netrc_auth
ConnectionError = ConnectionError
HTTPError = HTTPError
InvalidSchema = InvalidSchema
SSLError = SSLError
InsecureRequestWarning = InsecureRequestWarning
RequestsProxyError = RequestsProxyError
Retry = Retry
