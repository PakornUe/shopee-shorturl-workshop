import logging
import traceback

from flask import Flask

from accessors.urls_tab import MysqlUrlsTabAccessor
from common.exceptions import ShortUrlException
from conf import Conf
from managers.cached_shortener import CachedShortUrlManager
from managers.default import DefaultShortUrlManager
from managers.generators.auto_inc import AutoIncShortKeyGenerator
from routes import add_short_url_routes
from views.shorten import ShortUrlsView


def init_configs(_app):
    _app.config.update(Conf['flask'])


def create_urls_view():
    urls_tab_accessor = MysqlUrlsTabAccessor()
    generator = AutoIncShortKeyGenerator()
    short_url_manager = CachedShortUrlManager(urls_tab_accessor, generator)
    short_urls_view = ShortUrlsView(short_url_manager)
    return short_urls_view


def add_routes(_app):
    add_short_url_routes(_app, view=create_urls_view())


def create_app():
    _app = Flask(__name__)
    init_configs(_app)
    add_routes(_app)
    return _app


app = create_app()


@app.errorhandler(Exception)
def exception_handler(error):
    """
    Handle all uncaught exceptions.
    """
    if isinstance(error, (ShortUrlException,)):
        return {'error': error.message}, 500

    logging.error(''.join(traceback.format_exception(type(error), error, error.__traceback__)))
    return {'error': 'system busy'}, 500
