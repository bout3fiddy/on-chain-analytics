import os
import asyncio
from aiohttp import ClientSession

from web3.providers.base import JSONBaseProvider

from typing import List

ALCHEMY_API_KEY = os.environ['ALCHEMY_API_KEY']
ALCHEMY_RPC = f"https://eth-mainnet.alchemyapi.io/v2/{ALCHEMY_API_KEY}"


def get_ethtx_receipt(transactions: List):

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(
        async_getTransactionReceipt(ALCHEMY_RPC, transactions)
    )
    result = loop.run_until_complete(future)

    return result


async def async_make_request(session, url, method, params):
    """Asynchronous JSON RPC API request"""
    base_provider = JSONBaseProvider()
    request_data = base_provider.encode_rpc_request(method, params)
    async with session.post(
        url, data=request_data, headers={"Content-Type": "application/json"}
    ) as response:
        content = await response.read()
    response = base_provider.decode_rpc_response(content)
    return response


async def async_getTransactionReceipt(node_address, transactions):
    """Fetch all responses within one Client session, keep connection alive for all requests."""
    tasks = []
    async with ClientSession() as session:
        for tran in transactions:
            task = asyncio.ensure_future(
                async_make_request(
                    session, node_address, "eth_getTransactionReceipt", [tran]
                )
            )
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
    return responses
