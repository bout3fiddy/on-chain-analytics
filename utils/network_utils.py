from brownie._config import CONFIG


def configure_network(node_provider_https: str, network_name: str = "mainnet") -> None:
    # change network provider to user specified
    CONFIG.networks[network_name]["host"] = node_provider_https
    CONFIG.networks[network_name]["name"] = "Ethereum mainnet"
