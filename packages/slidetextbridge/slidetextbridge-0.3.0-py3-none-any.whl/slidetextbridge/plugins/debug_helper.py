'''
Helper classes for debugging
'''

import json
import logging
import sys
import asyncio
from slidetextbridge.core import config
from . import base

class StdinCapture(base.PluginBase):
    '''
    Just read from stdin
    '''
    @staticmethod
    def type_name():
        return 'stdin'

    @staticmethod
    def config(data):
        'Return the config object'
        cfg = config.ConfigBase()
        base.set_config_arguments(cfg, has_src=False)
        cfg.parse(data)
        return cfg

    def __init__(self, ctx, cfg=None):
        super().__init__(ctx=ctx, cfg=cfg)
        self.logger = logging.getLogger(f'stdin({self.cfg.location})')
        self._eof = False

    async def initialize(self):
        asyncio.create_task(self._loop())

    async def _loop(self):
        while not self._eof:
            try:
                await self._loop_once()
            except EOFError:
                break

    async def _loop_once(self):
        lines = await asyncio.to_thread(self._read_chunk_lines)
        slide = base.SlideBase(data={'shapes': [{'text': '\n'.join(lines)}]}, parent=self)
        await self.emit(slide)

    def _read_chunk_lines(self) -> list[str]:
        ret: list[str] = []
        while True:
            line = sys.stdin.readline()
            if not line:
                self._eof = True
                if not ret:
                    raise EOFError()
                break
            if line=='\n':
                break
            ret.append(line.rstrip('\n'))
        return ret


class StdoutEmitter(base.PluginBase):
    '''
    Just print to stdout
    '''
    @staticmethod
    def type_name():
        return 'stdout'

    @staticmethod
    def config(data):
        'Return the config object'
        cfg = config.ConfigBase()
        base.set_config_arguments(cfg)
        cfg.add_argment('page_delimiter', type=str, default='\n\n')
        cfg.add_argment('json', type=bool, default=False)
        cfg.parse(data)
        return cfg

    def __init__(self, ctx, cfg=None):
        super().__init__(ctx=ctx, cfg=cfg)
        self.logger = logging.getLogger(f'stdout({self.cfg.location})')
        self.connect_to(cfg.src)

    async def update(self, slide, args):
        try:
            if self.cfg.json:
                text = json.dumps(slide.to_dict(), ensure_ascii=False, indent=2)
            elif not slide:
                text = ''
            else:
                text = str(slide)

            sys.stdout.write(f'{text}{self.cfg.page_delimiter}')
        except Exception as e:
            self.logger.error('%s', e)

        await self.emit(slide)
