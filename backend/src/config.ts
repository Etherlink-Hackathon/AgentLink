import "dotenv/config";

export interface AppConfig {
  rpcUrl: string;
  chainId: number;
  geckoNetworkId: string;
  minProfitMargin: number;
  loopIntervalMs: number;
  maxSlippage: number;
  logLevel: string;
}

function requireEnv(key: string, fallback?: string): string {
  const value = process.env[key] ?? fallback;
  if (!value) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
  return value;
}

export function loadConfig(): AppConfig {
  return {
    rpcUrl: requireEnv("RPC_URL", "https://node.mainnet.etherlink.com"),
    chainId: parseInt(requireEnv("CHAIN_ID", "42793"), 10),
    geckoNetworkId: requireEnv("GECKO_NETWORK_ID", "etherlink"),
    minProfitMargin: parseFloat(requireEnv("MIN_PROFIT_MARGIN", "0.005")),
    loopIntervalMs: parseInt(requireEnv("LOOP_INTERVAL_MS", "900000"), 10),
    maxSlippage: parseFloat(requireEnv("MAX_SLIPPAGE", "0.01")),
    logLevel: requireEnv("LOG_LEVEL", "info"),
  };
}
