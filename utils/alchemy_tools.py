import os
import requests
from typing import Union, List


def alchemy_asset_transfers(
        from_address: str,
        to_address: str,
        from_block: Union[int, str],
        to_block: Union[int, str] = 'latest',
        page_key: str = None
):
    if not to_block == 'latest':
        to_block = hex(to_block)

    parameters = {
        "fromBlock": hex(from_block),
        "toBlock": to_block,
        "fromAddress": from_address,
        "toAddress": to_address
    }

    if not from_address:
        parameters.pop('fromAddress')
    if not to_address:
        parameters.pop('toAddress')

    if page_key:
        parameters['pageKey'] = page_key

    response_post = requests.post(
        "https://eth-mainnet.alchemyapi.io/v2/"
        + os.environ["ALCHEMY_API_KEY"],
        json={
            "jsonrpc": "2.0",
            "id": 0,
            "method": "alchemy_getAssetTransfers",
            "params": [parameters]
        },
        )

    response_json = response_post.json()
    return response_json


def get_asset_transfers(
        from_address: str,
        to_address: str,
        from_block: Union[int, str],
        to_block: Union[int, str]
) -> List:

    page_key = None
    all_txes = []
    while True:
        response = alchemy_asset_transfers(
            from_address=from_address,
            to_address=to_address,
            from_block=from_block,
            to_block=to_block,
            page_key=page_key
        )
        transactions = response["result"]["transfers"]
        all_txes.extend(transactions)
        if not 'pageKey' in response['result'].keys():
            break
        page_key = response['result']['pageKey']

    return all_txes