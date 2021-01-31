import hoshino, datetime, calendar, time, json, requests, os
from hoshino import Service, logger, priv
from bs4 import BeautifulSoup
from ..D2_API import *

sv = Service('d2-xur')
sv_bc = Service('d2-xur-bc', enable_on_default=False)

from .xur import *