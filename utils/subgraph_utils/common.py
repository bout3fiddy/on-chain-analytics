import pandas as pd
import requests

from utils.subgraph_utils.constants import CRV_EMISSIONS, SUBGRAPH_API


def get_curve_fees(pool_token_addr: str) -> pd.DataFrame:
    # needs pool token addr and not pool addr:
    query = f'''
    {{
      poolSnapshots (
        where:{{
          pool: "{pool_token_addr.lower()}"
        }}
      )
      {{
        fees
        block
      }}
    }}
    '''

    r = requests.post(CRV_EMISSIONS, json={'query': query})
    dict_response = dict(r.json())

    try:
        data = pd.DataFrame(dict_response['data']['poolSnapshots'])
        data['block'] = data.block.astype(int)
        data['fees'] = data.fees.astype(float)
    except KeyError:
        raise f"No data in subgraph for: {pool_token_addr}"

    return data

