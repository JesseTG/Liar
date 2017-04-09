# -*- coding: utf-8 -*-
"""Application configuration."""
import os

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore


SECONDS = 1
MINUTES = 60 * SECONDS
HOURS = 60 * MINUTES
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
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SCHEDULER_JOBSTORES = {
        'default': MemoryJobStore()
    }
    SCHEDULER_EXECUTORS = {
    }
    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 1
    }
    JOBS = [
        {
            'id': 'scrape-db',
            'func': 'liar.commands:scrape_noclick',
            'trigger': 'interval',
            'args': (),
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

    SCHEDULER_API_ENABLED = True
    DEBUG_TB_ENABLED = True
    ASSETS_DEBUG = True  # Don't bundle/minify static assets
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    DEBUG = True
    SCHEDULER_API_ENABLED = False
    WTF_CSRF_ENABLED = False  # Allows form testing
