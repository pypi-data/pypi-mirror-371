# SPDX-FileCopyrightText: © 2025 Roger Wilson
#
# SPDX-License-Identifier: MIT
import contextlib as cl
import contextvars as cv
import typing as ty

from ..util import gather, reform_tag
from ..util import scatter

# This contextvar must be created on main thread.
_STASH_GRAB_CONTEXT = cv.ContextVar('STASH_GRAB_CONTEXT', default={})


def stash(stashed: ty.Union[ty.Dict, None], f: ty.Callable, *args, **kwargs) -> ty.Any:
    with stasher(stashed):
        return f(*args, **kwargs)


@cl.contextmanager
@reform_tag(None) # Default stashed value is None.
def stasher(stashed: ty.Union[ty.Dict, None]) -> ty.Generator[None, None, None]:
    try:
        scatter(stashed, _STASH_GRAB_CONTEXT)
        yield None
    finally:
        if stashed is not None:
            for tag in stashed.keys():
                gather(tag, _STASH_GRAB_CONTEXT)


def grab(tag: ty.Hashable = None) -> ty.Any:
    return _STASH_GRAB_CONTEXT.get()[tag][-1]
