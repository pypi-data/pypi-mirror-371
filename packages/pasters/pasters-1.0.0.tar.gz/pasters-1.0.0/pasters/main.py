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

def strip_ext(url: str) -> str:
    """
    Remove extension from paste.rs URL if present.
    Examples:
        paste.rs/abcd.md  -> paste.rs/abcd
        paste.rs/abcd     -> paste.rs/abcd
        paste.rs/abcd.txt -> paste.rs/abcd
    """
    head, sep, tail = url.rpartition('/')
    if not sep:
        return url
    paste_id = tail.rsplit('.', 1)[0]
    return f"{head}/{paste_id}"


# sync
import requests 

def paste(text: str, ext: str = '', allow_206: bool = False) -> str:
    """
    Upload some text or code to the [paste.rs](https://paste.rs/)
    
    Args:
        text (str): a text or a code to upload.
        ext (str): a file extension. If pass `md`, `mdown`, or `markdown`, the paste is rendered as
          markdown into HTML. If ext is a known code file extension, the paste
          is syntax highlighted and returned as HTML. If ext is a known format
          extension, the paste is returned with the format's corresponding
          Content-Type. Otherwise, the paste is returned as unmodified text.
        allow_206 (bool): Should the response code 206 be allowed?
          If the response code is 201 (CREATED), then the entire paste was
          uploaded. If the response is 206 (PARTIAL), then the paste exceeded
          the server's maximum upload size, and only part of the paste was
          uploaded. If the response code is anything else, an error has
          occurred. Pasting is heavily rate limited.
    
    Returns:
        str: a link to the paste.
    
    Exceptions:
        requests.exceptions.HTTPError: 
    """
    
    r = requests.post('https://paste.rs/', data=text)
        
    allowed_statuses = [201]
    if allow_206:
        allowed_statuses.append(206)
    if r.status_code not in allowed_statuses:
        raise requests.exceptions.HTTPError(f"Unexpected status {r.status_code}: {r.text}")
    
    if ext:
        ext = ext[1:] if ext.startswith('.') else ext
        return r.text + '.' + ext
    return r.text


def get_paste(url) -> str:
    """Download a paste from paste.rs"""
    r = requests.get(strip_ext(url))
    if r.status_code != 200:
        raise requests.exceptions.HTTPError(f"Unexpected status {r.status_code}: {r.text}")
    return r.text


def delete_paste(url) -> None:
    """Delete a paste from paste.rs"""
    r = requests.delete(strip_ext(url))
    if r.status_code != 200:
        raise requests.exceptions.HTTPError(f"Unexpected status {r.status_code}: {r.text}")




# async
import httpx

async def apaste(text: str, ext: str = '', allow_206: bool = False) -> str:
    """
    Async upload some text or code to the [paste.rs](https://paste.rs/)
    
    Args:
        text (str): a text or a code to upload.
        ext (str): a file extension. If pass `md`, `mdown`, or `markdown`, the paste is rendered as
          markdown into HTML. If ext is a known code file extension, the paste
          is syntax highlighted and returned as HTML. If ext is a known format
          extension, the paste is returned with the format's corresponding
          Content-Type. Otherwise, the paste is returned as unmodified text.
        allow_206 (bool): Should the response code 206 be allowed?
    
    Returns:
        str: a link to the paste.
    
    Exceptions:
        httpx.HTTPStatusError
    """
    async with httpx.AsyncClient() as client:
        r = await client.post("https://paste.rs/", data=text)

    allowed_statuses = [201]
    if allow_206:
        allowed_statuses.append(206)
    if r.status_code not in allowed_statuses:
        raise httpx.HTTPStatusError(
            f"Unexpected status {r.status_code}: {r.text}",
            request=r.request,
            response=r,
        )

    if ext:
        ext = ext[1:] if ext.startswith('.') else ext
        return r.text + '.' + ext
    return r.text

async def aget_paste(url) -> str:
    """Async download a paste from paste.rs"""
    async with httpx.AsyncClient() as client:
        r = await client.get(strip_ext(url))
    if r.status_code != 200:
        raise httpx.HTTPStatusError(
            f"Unexpected status {r.status_code}: {r.text}",
            request=r.request,
            response=r,
        )
    return r.text


async def adelete_paste(url) -> None:
    """Async delete a paste from paste.rs"""
    async with httpx.AsyncClient() as client:
        r = await client.delete(strip_ext(url))
    if r.status_code != 200:
        raise httpx.HTTPStatusError(
            f"Unexpected status {r.status_code}: {r.text}",
            request=r.request,
            response=r,
        )

  
