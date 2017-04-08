# -*- coding: utf-8 -*-
"""Application configuration."""
import os

SECONDS = 60
HOURS = 60 * SECONDS
DAYS = 24 * HOURS

class Config(object):
    """Base configuration."""

    SECRET_KEY = os.environ.get('LIAR_SECRET', 'secret-key')  # TODO: Change me
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    ASSETS_DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    SCHEDULER_API_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JOBS = [
        {
            'id': 'scrape-db',
            'func': 'liar.commands:scrape',
            'trigger': 'interval',
            'seconds': 6 * HOURS
        }
    ]


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'
    DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True
    DB_NAME = 'dev.db'
    # Put the db file in project root
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    DEBUG_TB_ENABLED = True
    ASSETS_DEBUG = True  # Don't bundle/minify static assets
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    DEBUG = True
    SCHEDULER_API_ENABLED = False
    WTF_CSRF_ENABLED = False  # Allows form testing
