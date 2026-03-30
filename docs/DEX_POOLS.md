AgentLink currently monitors and executes arbitrage opportunities across leading decentralized exchanges on the Etherlink Mainnet. This page provides a technical overview of the liquidity pools integrated into our strategist's analytical loop.

## Monitored Pools

The following pools are prioritized for arbitrage due to their high liquidity and consistent volatility spreads.

| Pair | DEX Platform | Contract Address 
| :--- | :--- | :--- |
| **mBASIS / USDC** | Curve  | [0x071402...4c24](https://explorer.etherlink.com/) 
| **mRe7YIELD / USDC** | Curve  | [0x5d37f9...c88f](https://explorer.etherlink.com/) 
| **stXTZ / WXTZ** | Curve  | [0x74d80e...25d4](https://explorer.etherlink.com/) 
| **mTBILL / USDC** | Curve  | [0x942644...91ab](https://explorer.etherlink.com/) 
| **USDSM / USDC** | Curve  | [0x95af75...d080](https://explorer.etherlink.com/) 
| **mMEV / USDC** | Curve  | [0x269b47...fcfe](https://explorer.etherlink.com/) 
| **USDC / WXTZ (0.05%)** | Oku Trade  | [0x659fe2...2a74](https://explorer.etherlink.com/) 
| **USDC / USDT** | Curve  | [0x2d84d7...d457](https://explorer.etherlink.com/) 
| **WETH / WXTZ (0.05%)** | Oku Trade  | [0xd03b92...fc28](https://explorer.etherlink.com/) 
| **SOGNI / WXTZ (0.3%)** | Oku Trade  | [0x23a5c9...d8c4](https://explorer.etherlink.com/) 

## Integration Standards

### Curve
We utilize the Curve v2 stableswap and tri-crypto invariants. Our agent interfaces directly with the `Registry` and `Router` contracts to ensure atomic swaps with minimal slippage.

### Oku Trade (Uniswap v3)
For Uniswap v3 concentrated liquidity pools (via Oku), the agent calculates optimal tick-range swaps and utilizes `Universal Router` encoding for gas-efficient multi-step paths.

> [!TIP]
> Use the [Explorer] to view real-time yield and trade history for these specific pools.
