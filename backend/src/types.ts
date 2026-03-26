/**
 * Shared TypeScript interfaces for the Etherlink Omni-DEX Arbitrage Agent.
 */

/** Token metadata */
export interface Token {
  address: string;
  symbol: string;
  name: string;
  decimals: number;
}

/** Liquidity pool from a DEX */
export interface Pool {
  address: string;
  dexName: string;
  token0: Token;
  token1: Token;
  reserve0: bigint;
  reserve1: bigint;
  feeBps: number; // fee in basis points (e.g. 30 = 0.3%)
  /** Price of token0 in terms of token1 */
  price0: number;
  /** Price of token1 in terms of token0 */
  price1: number;
  /** Total value locked in USD */
  tvlUsd: number;
}

/** A normalized token pair with price from a specific pool */
export interface TokenPairPrice {
  baseToken: Token;
  quoteToken: Token;
  /** Price of base in terms of quote */
  price: number;
  pool: Pool;
}

/** Detected arbitrage opportunity */
export interface ArbitrageOpportunity {
  /** Pair identifier, e.g. "USDC/WETH" */
  pairId: string;
  baseToken: Token;
  quoteToken: Token;
  /** Pool to buy from (lower price) */
  buyPool: Pool;
  buyPrice: number;
  /** Pool to sell into (higher price) */
  sellPool: Pool;
  sellPrice: number;
  /** Price spread as a ratio (e.g. 0.02 = 2%) */
  spreadPct: number;
  /** Estimated gross profit in quote token units */
  estimatedGrossProfit: number;
}

/** Profitability evaluation result */
export interface ProfitEvaluation {
  opportunity: ArbitrageOpportunity;
  /** Estimated gas cost in native token (XTZ) */
  gasCostXtz: number;
  /** Estimated gas cost in USD */
  gasCostUsd: number;
  /** Net profit after gas + margin, in USD */
  netProfitUsd: number;
  /** EXECUTE or SKIP */
  decision: "EXECUTE" | "SKIP";
  /** Reason for decision */
  reason: string;
}

/** Unsigned transaction payload for user signing */
export interface TradePayload {
  to: string;
  data: string;
  value: string;
  chainId: number;
  gasLimit: string;
  /** Human-readable description */
  description: string;
}

/** Agent report output */
export interface AgentReport {
  timestamp: string;
  poolsDiscovered: number;
  pairsAnalyzed: number;
  opportunitiesFound: number;
  evaluations: ProfitEvaluation[];
  trades: TradePayload[];
}

/** Supported token symbols */
export const SUPPORTED_TOKENS = ["USDC", "USDT", "WETH", "WXTZ"] as const;
export type SupportedToken = (typeof SUPPORTED_TOKENS)[number];

/** GeckoTerminal API response types */
export interface GeckoPoolAttributes {
  address: string;
  name: string;
  base_token_price_usd: string;
  quote_token_price_usd: string;
  base_token_price_native_currency: string;
  quote_token_price_native_currency: string;
  reserve_in_usd: string;
  pool_created_at: string;
}

export interface GeckoTokenRelationship {
  id: string;
  type: string;
}

export interface GeckoPoolData {
  id: string;
  type: string;
  attributes: GeckoPoolAttributes;
  relationships: {
    base_token: { data: GeckoTokenRelationship };
    quote_token: { data: GeckoTokenRelationship };
    dex: { data: GeckoTokenRelationship };
  };
}

export interface GeckoIncludedToken {
  id: string;
  type: string;
  attributes: {
    address: string;
    name: string;
    symbol: string;
    decimals: number;
  };
}

export interface GeckoPoolsResponse {
  data: GeckoPoolData[];
  included?: GeckoIncludedToken[];
}
