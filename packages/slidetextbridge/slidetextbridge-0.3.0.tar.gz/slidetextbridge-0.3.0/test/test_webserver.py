import unittest
import logging
from unittest.mock import MagicMock, patch, AsyncMock
from aiohttp.test_utils import AioHTTPTestCase

from slidetextbridge.plugins import webserver, base

# https://docs.aiohttp.org/en/stable/testing.html#unittest

class TestWebServerEmitter(AioHTTPTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls._orig_log_level = {}
        for name in ('aiohttp', 'asyncio'):
            logger = logging.getLogger(name)
            cls._orig_log_level[name] = logger.level
            logger.setLevel(logging.WARNING)

    @classmethod
    def tearDownClass(cls):
        for name, level in cls._orig_log_level.items():
            logging.getLogger(name).setLevel(level)

        super().tearDownClass()

    def test_type_name(self):
        self.assertEqual(webserver.WebServerEmitter.type_name(), 'webserver')

    def test_config(self):
        cfg_data = {'host': '192.0.2.3', 'port': 8081}
        cfg = webserver.WebServerEmitter.config(cfg_data)
        self.assertEqual(cfg.host, '192.0.2.3')
        self.assertEqual(cfg.port, 8081)

    async def get_application(self):
        self.obj = await self._create_mocked_obj(cfg_data={
            'host': '192.0.2.3',
            'port': 8081,
        })
        return self.obj.app

    @staticmethod
    async def _create_mocked_obj(cfg_data):
        ctx = MagicMock()

        cfg = webserver.WebServerEmitter.config(cfg_data)

        mockAppRunner = MagicMock()
        mockAppRunner.return_value = MagicMock()
        mockAppRunner.return_value.setup = AsyncMock()
        mockTCPSite = MagicMock()
        mockTCPSite.return_value = MagicMock()
        mockTCPSite.return_value.start = AsyncMock()

        with patch.multiple(
                'aiohttp.web',
                AppRunner=mockAppRunner,
                TCPSite=mockTCPSite,
        ):
            obj = webserver.WebServerEmitter(ctx=ctx, cfg=cfg)
            obj.logger = MagicMock()
            await obj.initialize()
            obj.logger.info.assert_called_once_with('Listening on %s:%d', cfg_data['host'], cfg_data['port'])

        mockAppRunner.assert_called_once_with(obj.app)
        mockAppRunner.return_value.setup.assert_called_once_with()
        mockTCPSite.assert_called_once_with(
                mockAppRunner.return_value,
                obj.cfg.host, obj.cfg.port)
        mockTCPSite.return_value.start.assert_called_once_with()

        return obj

    async def test_get(self):
        async with self.client.request('GET', '/') as resp:
            self.assertEqual(resp.status, 200)
            text = await resp.text()
            self.assertIn('<html>', text)

    async def test_ws_text(self):

        # no text are pending
        async with self.client.ws_connect('/ws/text') as ws:
            await self.obj.update('first text', None)
            self.assertEqual(await ws.receive_str(), 'first text')

        # pending text will be sent soon
        await self.obj.update('pending text', None)
        async with self.client.ws_connect('/ws/text') as ws:
            await ws.send_str('ignored text')
            await self.obj.update('updated text', None)
            self.assertEqual(await ws.receive_str(), 'pending text')
            self.assertEqual(await ws.receive_str(), 'updated text')

    async def test_ws_shape_and_clear(self):
        async with self.client.ws_connect('/ws/text') as ws:
            # The SlideBase instance will be converted to a string.
            await self.obj.update(base.SlideBase({'shapes': {'text': 'shape text'}}), None)
            self.assertEqual(await ws.receive_str(), 'shape text')

            # Also tests to clear the text.
            await self.obj.update(None, None)
            self.assertEqual(await ws.receive_str(), '')

class TestWebServerEmitter_CustomContents(TestWebServerEmitter):

    async def get_application(self):
        self.obj = await self._create_mocked_obj(cfg_data={
            'host': '192.0.2.3',
            'port': 8081,
            'index_html': '<!-- index html -->',
            'script_js': '/* script data */',
            'style_css': '/* style data */',
        })
        return self.obj.app

    async def test_get(self):
        async with self.client.request('GET', '/') as resp:
            self.assertEqual(resp.status, 200)
            text = await resp.text()
            self.assertEqual(text, '<!-- index html -->')

        async with self.client.request('GET', '/script.js') as resp:
            self.assertEqual(resp.status, 200)
            text = await resp.text()
            self.assertEqual(text, '/* script data */')

        async with self.client.request('GET', '/style.css') as resp:
            self.assertEqual(resp.status, 200)
            text = await resp.text()
            self.assertEqual(text, '/* style data */')



if __name__ == '__main__':
    unittest.main()
