# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory located in app.py."""
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_wtf.csrf import CSRFProtect
from flask_pymongo import PyMongo
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from flask_compress import Compress

compress = Compress()
csrf_protect = CSRFProtect()
cache = Cache()
debug_toolbar = DebugToolbarExtension()
mongo = PyMongo()
scheduler = APScheduler(BackgroundScheduler())
