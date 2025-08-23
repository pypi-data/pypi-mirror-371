'''
Send text to OBS Studio
'''

import asyncio
import logging
import simpleobsws
from slidetextbridge.core import config
from . import base

class ObsWsEmitter(base.PluginBase):
    '''
    Emit text to OBS Studio
    '''
    @staticmethod
    def type_name():
        return 'obsws'

    @staticmethod
    def config(data):
        'Return the config object'
        cfg = config.ConfigBase()
        base.set_config_arguments(cfg)
        cfg.add_argment('url', type=str, default='ws://localhost:4455/')
        cfg.add_argment('password', type=str, default=None)
        cfg.add_argment('source_name', type=str, default=None)
        cfg.parse(data)
        return cfg

    def __init__(self, ctx, cfg=None):
        super().__init__(ctx=ctx, cfg=cfg)
        self.logger = logging.getLogger(f'obsws({self.cfg.location})')
        self._pending_text = None
        self._sending_task = None
        self.ws = None
        self.connect_to(cfg.src)

    async def _ws_connect(self):
        self.ws = simpleobsws.WebSocketClient(url=self.cfg.url, password=self.cfg.password)
        await self.ws.connect()
        if not await self.ws.wait_until_identified():
            self.ws.disconnect()
            self.ws = None
            raise ConnectionError('Identification error')

    async def update(self, slide, args):
        if not slide:
            text = ''
        elif isinstance(slide, str):
            text = slide
        else:
            text = str(slide)

        self._send_text(text)

    def _send_text(self, text):
        self._pending_text = text
        if not self._sending_task:
            self._sending_task = asyncio.create_task(self._send_text_routine())

    async def _send_text_routine(self):
        self.logger.debug('Starting text sending routine...')
        sent_text = object()
        while self._pending_text != sent_text:
            text = self._pending_text

            try:
                self.logger.debug('Attempting to send "%s"...', text)
                await self._send_request(simpleobsws.Request('SetInputSettings', {
                    'inputName': self.cfg.source_name,
                    'inputSettings': {'text': text}
                }))
                sent_text = text
            except Exception as e:
                self.logger.warning('Could not send text. %s', e)
                break

        self._sending_task = None
        self.logger.debug('Ending text sending routine. The text was "%s"', text)

    async def _send_request(self, req, retry=2):
        while retry > 0:
            retry -= 1

            if not self.ws:
                try:
                    await self._ws_connect()
                except Exception as e:
                    self.logger.warning('Could not connect to %s. %s', self.cfg.url, e)
                    self.ws = None
            if not self.ws:
                if retry > 0:
                    self.logger.info('Retrying to connect...')
                continue

            try:
                res = await self.ws.call(req)
                if res.ok():
                    return res.responseData
                self.logger.warning('%s: %d: %s', res.requestType,
                                    res.requestStatus.code, res.requestStatus.comment)

            except Exception as e:
                self.logger.warning('Failed to send text. %s', e)

                try:
                    await self.ws.disconnect()
                except Exception as e1:
                    self.logger.warning('Disconnect failed. %s', e1)
                self.ws = None

                if retry == 0:
                    raise e
                self.logger.info('Retrying...')
