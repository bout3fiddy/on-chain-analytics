from brownie import Contract


def init_contract(contract_addr: str):
    try:
        return Contract(contract_addr)
    except:
        return Contract.from_explorer(contract_addr)


def main():
    import brownie

    brownie.network.connect("mainnet")

    pool_contract_addr = "0x5a6A4D54456819380173272A5E8E9B9904BdF41B"  # mim-3crv pool
    pool_contract = init_contract(pool_contract_addr)
    print(pool_contract.info(), pool_contract.name())

    brownie.network.disconnect()


if __name__ == "__main__":
    main()
