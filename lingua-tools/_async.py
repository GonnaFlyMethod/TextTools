import asyncio
import json
from aiohttp import ClientSession 

async def get_json_response(session, url):
    data = None
    response = await session.request(method='GET', url=url)
    get_string = await response.text()
    data = json.loads(get_string)
    return data

async def run_program(session, url):
    """Wrapper for running program in an asynchronous manner"""
    res = None
    try:
        res = await get_json_response(session, url)
    except Exception as err:
        print(f"Exception occured: {err}")
        pass
    return res

async def async_HTTP_request(urls):
    loop = asyncio.get_event_loop()
    res = None
    async with ClientSession() as session:
        res = await asyncio.gather(*[run_program(session, url) for url in urls])
    return res
