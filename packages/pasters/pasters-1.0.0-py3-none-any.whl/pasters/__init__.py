#  pasters - Minimal Python client for paste.rs
#  Copyright (C) 2025-present RimMirK
#
#  This file is part of pastes.
#
#  pasters is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, version 3 of the License.
#
#  pasters is an independent, unofficial client library.
#  It provides a very simple interface for uploading, getting and deleting code to paste.rs
#
#  You should have received a copy of the GNU General Public License
#  along with pasters.  If not, see the LICENSE file.
#
#  Repository: https://github.com/RimMirK/pasters
#  Telegram: @RimMirK

from .main import paste, get_paste, delete_paste, apaste, aget_paste, adelete_paste

__version__ = version = '0.0.1'

__all__ = [
    'paste',
    'get_paste',
    'delete_paste',
    'aget_paste',
    'apaste',
    'adelete_paste',
    'version'
]
