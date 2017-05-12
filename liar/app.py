# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""

import math
import logging

from slugify import slugify
from flask import Flask, render_template

from liar import commands, public
from liar.assets import assets
from liar.extensions import cache, csrf_protect, debug_toolbar, mongo, scheduler
from liar.settings import ProdConfig


def create_app(config_object=ProdConfig):
    """An application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)

    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    register_shellcontext(app)
    register_commands(app)
    register_jinja(app)

    scheduler.start()
    return app


def register_extensions(app):
    """Register Flask extensions."""
    assets.init_app(app)
    cache.init_app(app)
    csrf_protect.init_app(app)
    debug_toolbar.init_app(app)
    mongo.init_app(app)
    scheduler.init_app(app)
    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(public.views.blueprint)
    return None


def register_errorhandlers(app):
    """Register error handlers."""
    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        return render_template('{0}.html'.format(error_code)), error_code
    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_shellcontext(app):
    """Register shell context objects."""
    def shell_context():
        """Shell context objects."""
        return {
            'db': mongo}

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)
    app.cli.add_command(commands.clean)
    app.cli.add_command(commands.urls)
    app.cli.add_command(commands.scrape)


def register_jinja(app):
    with app.app_context():
        app.jinja_env.globals['db'] = mongo.db
        app.jinja_env.globals['statements'] = mongo.db.statements
        app.jinja_env.globals['pi'] = math.pi

        app.jinja_env.filters['sqrt'] = math.sqrt
        app.jinja_env.filters['log10'] = math.log10
        app.jinja_env.filters['log'] = math.log
        app.jinja_env.filters['log1p'] = math.log1p
        app.jinja_env.filters['log2'] = math.log2
        app.jinja_env.filters['slugify'] = slugify
