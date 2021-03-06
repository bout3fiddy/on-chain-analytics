import requests


ETH_BLOCKS_SUBGRAPH = "https://api.thegraph.com/subgraphs/name/blocklytics/ethereum-blocks"


def get_current_block():

    r = requests.get("https://api.blockcypher.com/v1/eth/main")
    payload = dict(r.json())
    return int(payload['height'])


def get_block_for_timestamp(timestamp: int):

    query = (
        f'''{{
          blocks(
          first: 1,
          orderBy: timestamp,
          orderDirection: asc,
          where: {{timestamp_gt: "{int(timestamp)}"}}) {{
            id
            number
            timestamp
          }}
        }}
        '''
    )

    r = requests.post(ETH_BLOCKS_SUBGRAPH, json={'query': query})
    payload = dict(r.json())

    try:
        return int(payload['data']['blocks'][0]['number'])
    except KeyError:
        return None
    except IndexError:
        return None


def get_timestamp_for_block(block: int):

    query = (
        f'''{{
          blocks(
          first: 1,
          orderBy: number,
          orderDirection: asc,
          where: {{number_gt: "{int(block)}"}}) {{
            id
            number
            timestamp
          }}
        }}
        '''
    )

    r = requests.post(ETH_BLOCKS_SUBGRAPH, json={'query': query})
    payload = dict(r.json())

    try:
        return int(payload['data']['blocks'][0]['timestamp'])
    except KeyError:
        return None
    except IndexError:
        return None


if __name__ == "__main__":
    block_for_timestamp = get_block_for_timestamp(timestamp=1577836800)
    print(block_for_timestamp)
    print(get_timestamp_for_block(block_for_timestamp))
