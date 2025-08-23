'''
Main routine
'''

import argparse
import asyncio
import logging
import sys

from slidetextbridge.core.context import Context
from slidetextbridge.core import configtop

def _get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', action='store', default='config.yaml')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('-q', '--quiet', action='count', default=0)
    parser.add_argument('--strict', action='store_true')
    return parser.parse_args()

def _setup_logging(args):
    verbose = args.verbose - args.quiet
    if verbose >= 1:
        log_level = logging.DEBUG
    elif verbose >= 0:
        log_level = logging.INFO
    elif verbose >= -1:
        log_level = logging.WARNING
    elif verbose >= -2:
        log_level = logging.ERROR
    else:
        log_level = logging.CRITICAL
    logging.basicConfig(level=log_level)

def _setup_ctx(cfgs):
    ctx = Context()
    from slidetextbridge.plugins import accumulate # pylint: disable=C0415
    for step in cfgs.steps:
        cls = accumulate.plugins[step.type]
        inst = cls(ctx=ctx, cfg=step)
        ctx.add_instance(inst)
    return ctx

async def _loop(ctx):
    await ctx.initialize_all()
    while True:
        tt = list(asyncio.all_tasks())
        t = asyncio.current_task()
        if t:
            tt.remove(t)
        if not tt:
            break
        rr = await asyncio.gather(*tt, return_exceptions=True)
        for t, r in zip(tt, rr):
            if isinstance(r, Exception):
                logging.getLogger(__name__).error('%s: Unknown exception %s', t, r)
    logging.getLogger(__name__).info('All tasks are done.')

def main():
    'The entry point'
    try:
        args = _get_args()
        _setup_logging(args)
        cfgs = configtop.load(args.config)
        ctx = _setup_ctx(cfgs)
    except Exception as e:
        logging.getLogger(__name__).error('Failed to start. %s', e)
        return 1

    try:
        asyncio.run(_loop(ctx))
    except KeyboardInterrupt:
        logging.getLogger(__name__).info('Interrupted')

    return 0

if __name__ == '__main__':
    sys.exit(main())
