'''
Get text from LibreOffice Impress
'''

import asyncio
import logging
import uno
from slidetextbridge.core import config
from slidetextbridge.core.logging import HideSameLogFilter
from . import base


class ImpressCapture(base.PluginBase):
    '''
    Get text from LibreOffice Impress
    '''
    @staticmethod
    def type_name():
        return 'impress'

    @staticmethod
    def config(data):
        'Return the config object'
        cfg = config.ConfigBase()
        base.set_config_arguments(cfg, has_src=False)
        cfg.add_argment('host', type=str, default='localhost')
        cfg.add_argment('port', type=int, default=2002)
        cfg.add_argment('pipe_name', type=str)
        cfg.add_argment('poll_wait_time', type=float, default=0.1)
        cfg.parse(data)
        return cfg

    def __init__(self, ctx, cfg=None):
        super().__init__(ctx=ctx, cfg=cfg)
        self.logger = logging.getLogger(f'impress({self.cfg.location})')
        self.logger.addFilter(HideSameLogFilter(4))
        self._last_slide = self
        self._desktop = None

    async def initialize(self):
        asyncio.create_task(self._loop())

    async def _loop(self):
        while True:
            if not await self._loop_once():
                await asyncio.sleep(1)

    async def _loop_once(self):
        if not self._desktop:
            try:
                self._connect()
                self.logger.info('Connected to impress.')
            except Exception as e:
                self._desktop = None
                self.logger.warning('Failed to connect impress. %s', e)
                return False

        try:
            slide = self._get_slide()
        except Exception as e:
            self.logger.warning('Failed to get slide. %s', e)
            self._desktop = None
            return False

        if slide != self._last_slide:
            self._last_slide = slide
            await self.emit(base.SlideBase(data=_dict_from_slide(slide), parent=self))

        await asyncio.sleep(self.cfg.poll_wait_time)
        return True

    def _connect(self):
        context = uno.getComponentContext()
        resolver = context.ServiceManager.createInstanceWithContext(
                'com.sun.star.bridge.UnoUrlResolver', context)
        if self.cfg.pipe_name:
            uno_conn = f'uno:pipe,name={self.cfg.pipe_name}'
        else:
            uno_conn = f'uno:socket,host={self.cfg.host},port={self.cfg.port}'
        uno_inst = resolver.resolve(f'{uno_conn};urp;StarOffice.ComponentContext')
        self._desktop = uno_inst.ServiceManager.createInstanceWithContext(
                'com.sun.star.frame.Desktop', uno_inst)

    def _get_slide(self):
        if not self._desktop:
            self.logger.warning('No desktop is available')
            return None

        c = self._desktop.getCurrentComponent()
        if not c:
            self.logger.info('Found no component. Probably, all windows have been closed.')
            return None
        presentation = c.getPresentation()
        controller = presentation.getController()
        if not controller:
            self.logger.info('Found no active presentation controller.')
            return None
        return controller.getCurrentSlide()


def _dict_from_slide(slide):
    shapes = []
    if slide:
        for shape in slide:
            s = base.SlideBase.convert_object(shape, params=(
                ('Text', lambda v: v.getString()),
                'CharColor',
                'CharHeight',
                'CharFontName',
            ))
            s['text'] = shape.Text.getString()
            shapes.append(s)
    return {'shapes': shapes}
