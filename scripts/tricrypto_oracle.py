POOL: str = "0xD51a44d3FaE010294C616388b506AcdA1bfAAE46"
GAMMA0: int = 28000000000000  # 2.8e-5
A0: int = 2 * 3**3 * 10000
DISCOUNT0: int = 1087460000000000  # 0.00108..


def cubic_root(x: int) -> int:
    # x is taken at base 1e36
    # result is at base 1e18
    # Will have convergence problems when ETH*BTC is cheaper than 0.01 squared dollar
    # (for example, when BTC < $0.1 and ETH < $0.1)
    D: int = x / 10**18
    for i in range(255):
        diff: int = 0
        D_prev: int = D
        D = D * (2 * 10**18 + x / D * 10**18 / D * 10**18 / D) / (3 * 10**18)
        if D > D_prev:
            diff = D - D_prev
        else:
            diff = D_prev - D
        if diff <= 1 or diff * 10**18 < D:
            return D
        print(f"diff: {diff}")
    raise "Did not converge"


def lp_price(
        vp: int,
        p1: int,
        p2: int,
        gamma: int,
        A: int
) -> int:

    max_price: int = 3 * vp * cubic_root(p1 * p2) / 10**18

    # ((A/A0) * (gamma/gamma0)**2) ** (1/3)
    g: int = gamma * 10**18 / GAMMA0
    a: int = A * 10**18 / A0
    discount: int = max(g**2 / 10**18 * a, 10**34)  # handle qbrt nonconvergence
    # if discount is small, we take an upper bound
    discount = cubic_root(discount) * DISCOUNT0 / 10**18

    max_price -= max_price * discount / 10**18

    return max_price


def main():
    import brownie
    from utils.contract_utils import init_contract
    from utils.network_utils import connect_eth_alchemy

    connect_eth_alchemy()
    oracle = init_contract("0xE8b2989276E2Ca8FDEA2268E3551b2b4B2418950")
    pool = init_contract("0xD51a44d3FaE010294C616388b506AcdA1bfAAE46")

    vp = pool.get_virtual_price()
    A = pool.A()
    gamma = pool.gamma()
    p1 = pool.price_oracle(0)
    p2 = pool.price_oracle(1)

    lp_price_from_oracle = oracle.lp_price()
    lp_price_from_script = lp_price(vp, p1, p2, gamma, A)

    print(f"oracle price: {lp_price_from_oracle}")
    print(f"computed price: {lp_price_from_script}")

    if brownie.network.is_connected():
        brownie.network.disconnect()


if __name__ == "__main__":
    main()
