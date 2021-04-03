from typing import Optional

from dotmap import DotMap
from peewee import DoesNotExist

from avdc.utility.image import getRawImageFormat, getRawImageSize
from avdc.utility.metadata import Actress as _A
from avdc.utility.metadata import Metadata as _M
from server.database import Metadata, Actresses, Backdrops


def GetMetadataByVID(vid: str) -> Optional[_M]:
    vid = vid.upper()
    try:
        result: Metadata = Metadata.get((Metadata.vid == vid) |
                                        (Metadata.vid == vid.replace('-', '_')) |
                                        (Metadata.vid == vid.replace('_', '-')))
    except DoesNotExist:
        return
    return _M(**result.__data__)


def StoreMetadata(metadata: _M, update: bool = False):
    (Metadata
     .insert(**dict(metadata))
     .on_conflict('REPLACE' if update else 'IGNORE')
     .execute())


def GetActressByName(name: str) -> Optional[_A]:
    try:
        result: Actresses = Actresses.get((Actresses.name == name))
    except DoesNotExist:
        return
    return _A(**result.__data__)


def StoreActress(actress: _A, update: bool = False):
    (Actresses
     .insert(**dict(actress))
     .on_conflict('REPLACE' if update else 'IGNORE')
     .execute())


def GetCoverByVID(vid: str) -> Optional[DotMap]:
    vid = vid.upper()
    try:
        result: Backdrops = Backdrops.get((Backdrops.vid == vid) |
                                          (Backdrops.vid == vid.replace('-', '_')) |
                                          (Backdrops.vid == vid.replace('_', '-')))
    except DoesNotExist:
        return

    return DotMap(**result.__data__)


def StoreCover(vid: str,
               data: bytes,
               width: Optional[int] = None,
               height: Optional[int] = None,
               fmt: Optional[str] = None,
               pos: float = -1,
               update: bool = False):
    if not width or not height:
        height, width = getRawImageSize(data)

    (Backdrops
     .insert(vid=vid,
             pos=pos,
             data=data,
             width=width,
             height=height,
             fmt=fmt or getRawImageFormat(data), )
     .on_conflict('REPLACE' if update else 'IGNORE')
     .execute())
