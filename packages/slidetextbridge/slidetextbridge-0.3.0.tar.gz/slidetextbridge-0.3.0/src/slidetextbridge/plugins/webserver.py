'''
Send text through HTTP
'''

import logging
import os
from aiohttp import web
from slidetextbridge.core import config
from . import base


def _get_data_path(file):
    module_dir = os.path.dirname(os.path.abspath(__file__))
    return module_dir + '/data/webserver/' + file


class _GetHandler:
    def __init__(self, content=None, path=None, content_type=None, logger=None):
        if content:
            self.content = content
        elif path:
            self.content = None
            self.load(path)
        elif logger: # pragma: no cover
            logger.error('_GetHandler: Need path or content')

        self.content_type = content_type or 'text/html'

    def load(self, path):
        'Load the content from the given path'
        with open(path, encoding='utf-8') as fr:
            self.content = fr.read()

    async def handler(self, request):
        'The handler compatible with aiohttp'
        # pylint: disable=unused-argument
        return web.Response(text=self.content, content_type=self.content_type)


class WebServerEmitter(base.PluginBase):
    '''
    HTTP server to send text through HTTP
    '''
    @staticmethod
    def type_name():
        return 'webserver'

    @staticmethod
    def config(data):
        'Return the config object'
        cfg = config.ConfigBase()
        base.set_config_arguments(cfg)
        cfg.add_argment('host', type=str, default='localhost')
        cfg.add_argment('port', type=int, default=8080)
        cfg.add_argment('uri_index', type=str, default='/index.html')
        cfg.add_argment('uri_script', type=str, default='/script.js')
        cfg.add_argment('uri_style', type=str, default='/style.css')
        cfg.add_argment('index_html', type=str, default='')
        cfg.add_argment('script_js', type=str, default='')
        cfg.add_argment('style_css', type=str, default='')
        cfg.add_argment('theme', type=str, default='default')
        cfg.parse(data)
        return cfg

    def __init__(self, ctx, cfg=None):
        super().__init__(ctx=ctx, cfg=cfg)
        self.logger = logging.getLogger(f'webserver({self.cfg.location})')
        self.app = None
        self.clients = set()
        self._last_text = None
        self.connect_to(cfg.src)

    def _fmt(self, text):
        if not text:
            return None
        return text \
                .replace('{uri_script}', self.cfg.uri_script) \
                .replace('{uri_style}', self.cfg.uri_style)

    async def _handle_ws(self, request):
        # pylint: disable=unused-argument
        self.logger.info('Starting %s remote=%s', request.rel_url, request.remote)
        try:
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            self.clients.add(ws)

            if self._last_text:
                await self._send_text(ws, self._last_text)

            async for _ in ws:
                pass
        except Exception as e:
            self.logger.error('%s: Failed to process ws message. %s', request.remote, e)
        finally:
            self.clients.discard(ws)

        self.logger.info('Closing %s remote=%s', request.rel_url, request.remote)
        return ws

    async def initialize(self):
        self.app = web.Application()
        theme_dir = _get_data_path(self.cfg.theme) if self.cfg.theme else '.'
        index_handler = _GetHandler(
                content=self._fmt(self.cfg.index_html),
                path=theme_dir + '/index.html',
                logger=self.logger
        )
        script_handler = _GetHandler(
                content=self._fmt(self.cfg.script_js),
                path=theme_dir + '/script.js',
                content_type='text/javascript',
                logger=self.logger
        )
        style_handler = _GetHandler(
                content=self._fmt(self.cfg.style_css),
                path=theme_dir + '/style.css',
                content_type='text/css',
                logger=self.logger
        )
        self.app.add_routes([
            web.get('/', index_handler.handler),
            web.get(self.cfg.uri_index, index_handler.handler),
            web.get(self.cfg.uri_script, script_handler.handler),
            web.get(self.cfg.uri_style, style_handler.handler),
            web.get('/ws/text', self._handle_ws),
        ])
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.cfg.host, self.cfg.port)
        await site.start()
        self.logger.info('Listening on %s:%d', self.cfg.host, self.cfg.port)

    async def update(self, slide, args):
        if not slide:
            text = ''
        elif isinstance(slide, str):
            text = slide
        else:
            text = str(slide)

        self._last_text = text
        for ws in self.clients:
            await self._send_text(ws, text)

    async def _send_text(self, ws, text):
        try:
            await ws.send_str(text)
        except Exception as e:
            self.logger.warning('Failed to send text to ws. %s', e)
