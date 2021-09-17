from brownie import Contract


def init_contract(contract_addr: str):
    try:
        return Contract(contract_addr)
    except:
        return Contract.from_explorer(contract_addr)
