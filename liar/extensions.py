# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory located in app.py."""
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_wtf.csrf import CSRFProtect
from flask_pymongo import PyMongo


bcrypt = Bcrypt()
csrf_protect = CSRFProtect()
cache = Cache()
debug_toolbar = DebugToolbarExtension()
mongo = PyMongo()