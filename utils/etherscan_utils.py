import os
import re
from typing import List

from etherscan.accounts import Account
from etherscan.client import Client
from etherscan.client import EmptyResponse
from web3 import Web3


class TransactionScraper(Account):
    def __init__(self, address=Client.dao_address, api_key="YourApiKey"):
        Account.__init__(self, address=address, api_key=api_key)
        self.url_dict[self.MODULE] = "account"

    def get_tx_with(
        self,
        addr: str,
        start_block: int = 0,
        end_block: int = -1,
        sort: str = "asc",
    ):

        self.url_dict[self.ACTION] = "txlist"
        self.url_dict[self.SORT] = sort
        self.url_dict[self.START_BLOCK] = str(start_block)
        self.url_dict[self.END_BLOCK] = str(end_block)
        if int(end_block) == -1:
            self.url_dict[self.END_BLOCK] = "latest"

        self.build_url()
        req = self.connect()
        relevant_txes = []
        for tx in req["result"]:
            if tx["from"] in [
                addr,
                addr.lower(),
                Web3.toChecksumAddress(addr),
            ]:
                relevant_txes.append(tx)

        return relevant_txes

    def get_tx(
            self,
            offset=10000,
            sort="asc",
            start_block: int = 0,
            end_block: int = -1
    ) -> list:

        self.url_dict[self.ACTION] = "txlist"
        self.url_dict[self.PAGE] = str(1)
        self.url_dict[self.OFFSET] = str(offset)
        self.url_dict[self.SORT] = sort
        self.url_dict[self.START_BLOCK] = str(start_block)
        self.url_dict[self.END_BLOCK] = str(end_block)
        if int(end_block) == -1:
            self.url_dict[self.END_BLOCK] = "latest"
        self.build_url()

        trans_list = []
        while True:
            self.build_url()

            try:

                req = self.connect()
                if "No transactions found" in req["message"]:
                    return trans_list

                else:

                    trans_list += req["result"]
                    # Find any character block that is a integer of any length
                    page_number = re.findall(
                        Account.PAGE_NUM_PATTERN, self.url_dict[self.PAGE]
                    )
                    self.url_dict[self.PAGE] = str(int(page_number[0]) + 1)

            except EmptyResponse:

                return trans_list


def get_all_txes(
    address: str,
) -> List:

    tx_scraper = TransactionScraper(
        address=address, api_key=os.environ["ETHERSCAN_TOKEN"]
    )
    txes = tx_scraper.get_tx()

    return txes


def get_txes_between_blocks(address: str, from_block: int, to_block: int):

    tx_scraper = TransactionScraper(
        address=address, api_key=os.environ["ETHERSCAN_TOKEN"]
    )
    txes = tx_scraper.get_tx(start_block=from_block, end_block=to_block)

    return txes


def get_txes_with_addr_between_blocks(
        address: str,
        address_with: str,
        from_block: int,
        to_block: int
):

    txes = get_txes_between_blocks(address, from_block, to_block)
    relevant_txes = []
    for tx in txes:
        if tx["from"] in [
            address_with,
            address_with.lower(),
            Web3.toChecksumAddress(address_with),
        ]:
            relevant_txes.append(tx)
        if tx["to"] in [
            address_with,
            address_with.lower(),
            Web3.toChecksumAddress(address_with),
        ]:
            relevant_txes.append(tx)

    return relevant_txes
