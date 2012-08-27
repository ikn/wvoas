from collections import defaultdict

import pygame as pg


# abstract


def dd (default, items = {}, **kwargs):
    """Create a collections.defaultdict with a static default.

dd(default[, items], **kwargs) -> default_dict

default: the default value.
items: dict or dict-like to initialise with.
kwargs: extra items to initialise with.

default_dict: the created defaultdict.

"""
    items.update(kwargs)
    return defaultdict(lambda: default, items)


def ir (x):
    """Returns the argument rounded to the nearest integer."""
    # this is about twice as fast as int(round(x))
    y = int(x)
    return (y + (x - y >= .5)) if x > 0 else (y - (y - x >= .5))


def split (size, intervals):
    """Split a region into integer-sized intervals.

split(size, intervals) -> size_list

size: the size of the region to split.
intervals: the number of intervals to use.

size_list: a list of sizes for each interval in turn.

"""
    intervals = max(intervals, 0)
    if intervals == 0:
        return []
    if intervals == 1:
        return [size]
    avg = float(size) / intervals
    base = int(avg)
    diff = avg - base
    sizes = []
    current_diff = 0
    for i in xrange(intervals):
        # add up excess bits
        current_diff += diff
        # when we have 1, add it on
        if current_diff >= 1:
            sizes.append(base + 1)
            current_diff -= 1
        else:
            sizes.append(base)
    # adjust first interval (probably only by 1, if any)
    sizes[0] += size - sum(sizes)
    return sizes


# graphics


def position_sfc (sfc, dest, pos = 0, offset = (0, 0), rect = None,
                  dest_rect = None):
    """Blit a surface onto another in a relative manner.

blit_centred(sfc, dest, pos = 0, offset = (0, 0))

sfc, dest: blit sfc onto dest.
pos: where to position sfc relative to dest.  This is (x, y) for each axis,
     where for each, a number < 0 is top-/left-aligned, 0 is centred, and > 0
     is bottom-/right-aligned.  If not centred, the given edges of the surfaces
     are made to align.  This argument can also be just a number, to position
     in the same manner on both axes.
offset: an (x, y) amount to offset the blit position by.
rect: the rect within sfc to copy, defaulting to the whole surface.  If given,
      the edges of this rect are used for alignment, as opposed to the edges of
      the whole surface.  This can be larger than sfc.
dest_rect: the rect within dest to align to, instead of the whole surface.
           This only affects alignment, not whether anything is blitted outside
           this rect.  This can be larger than dest.

"""
    if rect is None:
        rect = sfc.get_rect()
    if isinstance(pos, (int, float)):
        pos = (pos, pos)
    if dest_rect is None:
        dest_rect = dest.get_rect()
    # get blit position
    p = []
    for sfc_w, dest_w, x, o in zip(rect[2:4], dest_rect[2:4], pos, offset):
        if x < 0:
            # top/left
            p.append(o)
        elif x == 0:
            # centre
            p.append((dest_w - sfc_w) / 2 + o)
        else:
            # bottom/right
            p.append(dest_w - sfc_w + o)
    # blit
    dest.blit(sfc, p, rect)


def convert_sfc (sfc):
    """Convert a surface for blitting."""
    if sfc.get_alpha() is None and sfc.get_colorkey() is None:
        sfc = sfc.convert()
    else:
        sfc = sfc.convert_alpha()
    return sfc
