'''
Filter with JMESPath
'''

import jmespath
from slidetextbridge.core import config
from . import base

def _convert_text_paths(orig_obj):
    if 'text_paths' not in orig_obj:
        return ['shapes', 'text']

    def _traverse_dict(d):
        if isinstance(d, dict):
            for key, value in d.items():
                yield key
                if value:
                    yield from _traverse_dict(value)
        if isinstance(d, (list, tuple)):
            yield from d

    return list(_traverse_dict(orig_obj['text_paths']))


class JMESPathFilter(base.PluginBase):
    '''
    Filter shapes with JMESPath
    '''
    @staticmethod
    def type_name():
        return 'jmespath'

    @staticmethod
    def config(data):
        'Return the config object'
        cfg = config.ConfigBase()
        base.set_config_arguments(cfg)
        cfg.add_argment('filter', type=str)
        cfg.parse(data)
        return cfg

    def __init__(self, ctx, cfg=None):
        super().__init__(ctx=ctx, cfg=cfg)
        self.connect_to(cfg.src)
        self.jmespath_filter = jmespath.compile(cfg.filter)

    async def update(self, slide, args):
        orig_obj = slide.to_dict()
        new_obj = self.jmespath_filter.search(orig_obj)

        if not isinstance(new_obj, dict):
            new_obj = {'shapes': new_obj}

        new_obj['text_paths'] = _convert_text_paths(orig_obj)

        for key, value in orig_obj.items():
            if key in new_obj:
                continue
            new_obj[key] = value

        slide = base.SlideBase(data=new_obj)
        await self.emit(slide)
