# these utility scripts are used to prepare, simulate and broadcast votes within Curve's DAO
# modify the constants below according the the comments, and then use `simulate` in
# a forked mainnet to verify the result of the vote prior to broadcasting on mainnet
#
# NOMENCLATURE:
#
# target: the intended target of the vote, should be one of the above constant dicts
# sender: address to create the vote from - you will need to modify this prior to mainnet use
# action: a list of calls to perform in the vote, formatted as a lsit of tuples
#         in the format (target, function name, *input args).
#         for example, to call:
#         GaugeController("0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB").add_gauge("0xFA712...", 0, 0)
#
#         use the following:
#         [("0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB", "add_gauge", "0xFA712...", 0, 0),]
#
#         commonly used addresses:
#         GaugeController - 0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB
#         GaugeProxy - 0x519AFB566c05E00cfB9af73496D00217A630e4D5
#         PoolProxy - 0xeCb456EA5365865EbAb8a2661B0c503410e9B347
# description: description of the vote, will be pinned to IPFS

import json
import warnings

import requests

from typing import Dict, List, Tuple

from brownie import chain, network
from brownie.convert import to_address

from utils import init_contract

warnings.filterwarnings("ignore")


# ------- CONSTANTS --------- #
# addresses related to the DAO - these should not need modification

CURVE_DAO_OWNERSHIP = {
    "agent": "0x40907540d8a6c65c637785e8f8b742ae6b0b9968",
    "voting": "0xe478de485ad2fe566d49342cbd03e49ed7db3356",
    "token": "0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2",
    "quorum": 30,
}

CURVE_DAO_PARAM = {
    "agent": "0x4eeb3ba4f221ca16ed4a0cc7254e2e32df948c5f",
    "voting": "0xbcff8b0b9419b9a88c44546519b1e909cf330399",
    "token": "0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2",
    "quorum": 15,
}

EMERGENCY_DAO = {
    "forwarder": "0xf409Ce40B5bb1e4Ef8e97b1979629859c6d5481f",
    "agent": "0x00669DF67E4827FCc0E48A1838a8d5AB79281909",
    "voting": "0x1115c9b3168563354137cdc60efb66552dd50678",
    "token": "0x4c0947B16FB1f755A2D32EC21A0c4181f711C500",
    "quorum": 51,
}


# ------- DAO VOTE SIM SCRIPTS --------- #


def prepare_evm_script(target: Dict, actions: Dict) -> str:
    """Generates EVM script to be executed by AragonDAO contracts.

    Args:
        target (dict): one of either CURVE_DAO_OWNERSHIP, CURVE_DAO_PARAMS or EMERGENCY_DAO
        actions (list(tuple)): ("target addr", "fn_name", *args)

    Returns:
        str: Generated EVM script.
    """
    agent = init_contract(target["agent"])
    evm_script = "0x00000001"

    for address, fn_name, *args in actions:
        contract = init_contract(address)
        fn = getattr(contract, fn_name)
        calldata = fn.encode_input(*args)
        agent_calldata = agent.execute.encode_input(address, 0, calldata)[2:]
        length = hex(len(agent_calldata) // 2)[2:].zfill(8)
        evm_script = f"{evm_script}{agent.address[2:]}{length}{agent_calldata}"

    return evm_script


def make_vote(sender: str, target: Dict, actions: List[Tuple], description: str) -> str:
    """Prepares EVM script and creates an on-chain AragonDAO vote.

    Note: this script can be used to deploy on-chain governance proposals as well.

    Args:
        sender (str): msg.sender address
        target (dict): one of either CURVE_DAO_OWNERSHIP, CURVE_DAO_PARAMS or EMERGENCY_DAO
        actions (list(tuple)): ("target addr", "fn_name", *args)
        description (str): Description of the on-chain governance proposal

    Returns:
        str: vote ID of the created vote.
    """
    if network.show_active() == "mainnet":
        kw = {"from": sender, "priority_fee": "2 gwei"}
    else:
        kw = {"from": sender}
    text = json.dumps({"text": description})
    response = requests.post(
        "https://ipfs.infura.io:5001/api/v0/add", files={"file": text}
    )
    ipfs_hash = response.json()["Hash"]
    print(f"ipfs hash: {ipfs_hash}")

    aragon = init_contract(target["voting"])
    evm_script = prepare_evm_script(target, actions)
    if target.get("forwarder"):
        # the emergency DAO only allows new votes via a forwarder contract
        # so we have to wrap the call in another layer of evm script
        vote_calldata = aragon.newVote.encode_input(
            evm_script, description, False, False
        )[2:]
        length = hex(len(vote_calldata) // 2)[2:].zfill(8)
        evm_script = f"0x00000001{aragon.address[2:]}{length}{vote_calldata}"
        print(f"Target: {target['forwarder']}\nEVM script: {evm_script}")
        tx = init_contract(target["forwarder"]).forward(evm_script, kw)
    else:
        print(f"Target: {aragon.address}\nEVM script: {evm_script}")
        tx = aragon.newVote(evm_script, f"ipfs:{ipfs_hash}", False, False, kw)

    vote_id = tx.events["StartVote"]["voteId"]

    print(f"\nSuccess! Vote ID: {vote_id}")
    return vote_id


def simulate(target: Dict, actions: List[Tuple], description: str):
    """Create AragonDAO vote and simulate passing vote on mainnet-fork.

    Args:
        target (dict): one of either CURVE_DAO_OWNERSHIP, CURVE_DAO_PARAMS or EMERGENCY_DAO
        actions (list(tuple)): ("target addr", "fn_name", *args)
        description (str): Description of the on-chain governance proposal
    """
    # fetch the top holders so we can pass the vote
    data = requests.get(
        f"https://api.ethplorer.io/getTopTokenHolders/{target['token']}",
        params={"apiKey": "freekey", "limit": 50},
    ).json()["holders"][::-1]

    # create a list of top holders that will be sufficient to make quorum
    holders = []
    weight = 0
    while weight < target["quorum"] + 5:
        row = data.pop()
        holders.append(to_address(row["address"]))
        weight += row["share"]

    # make the new vote
    top_holder = holders[0]
    vote_id = make_vote(top_holder, target, actions, description)

    # vote
    aragon = init_contract(target["voting"])
    for acct in holders:
        aragon.vote(vote_id, True, False, {"from": acct})

    # sleep for a week so it has time to pass
    chain.sleep(86400 * 7)

    # moment of truth - execute the vote!
    aragon.executeVote(vote_id, {"from": top_holder})
