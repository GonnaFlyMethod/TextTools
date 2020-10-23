import asyncio
import json
from aiohttp import ClientSession 

async def get_json_response(session, func_name, url) -> dict:
    data = None
    response = await session.request(method='GET', url=url)
    get_string = await response.text()
    data = json.loads(get_string)
    return {func_name:data}

async def run_program(session, func_name, url) -> dict:
    """Wrapper for running program in an asynchronous manner"""
    res = None
    try:
        res = await get_json_response(session, func_name, url)
    except Exception as err:
        print(f"Exception occured: {err}")
        pass
    return res

async def async_HTTP_request(functions_name_and_urls) -> dict:
    loop = asyncio.get_event_loop()
    res = None
    async with ClientSession() as session:
        async_arr = []
        for func_name, url in functions_name_and_urls.items():
            async_arr.append(run_program(session, func_name, url))
        res = await asyncio.gather(*async_arr)
    return res
