import os

import brownie
from brownie._config import CONFIG

ALCHEMY_API_KEY = os.environ['ALCHEMY_API_KEY']


def configure_network(node_provider_https: str, network_name: str = "mainnet") -> None:
    # change network provider to user specified
    CONFIG.networks[network_name]["host"] = node_provider_https
    CONFIG.networks[network_name]["name"] = "Ethereum mainnet"


def configure_network_and_connect(
    node_provider_https: str, network_name: str = "mainnet"
) -> None:
    # change network provider to user specified
    CONFIG.networks[network_name]["host"] = node_provider_https
    CONFIG.networks[network_name]["name"] = "Ethereum mainnet"

    brownie.network.connect(network_name)


def connect_eth_alchemy():
    if not brownie.network.is_connected():
        configure_network_and_connect(
            node_provider_https=f"https://eth-mainnet.alchemyapi.io/v2/{ALCHEMY_API_KEY}",
            network_name='mainnet'
        )
