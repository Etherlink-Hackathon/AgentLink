import { http, createConfig } from '@wagmi/vue'
import { injected, metaMask, safe, walletConnect } from '@wagmi/vue/connectors'

// Get network type from environment variable
export const NETWORK_TYPE = import.meta.env.VITE_NETWORK_TYPE || 'mainnet';
// const projectId = '<WALLETCONNECT_PROJECT_ID>'

export const chainConfig = {
  mainnet: {
    id: 42793,
    name: 'Etherlink Mainnet',
    network: 'mainnet',
    nativeCurrency: {
      name: 'XTZ',
      symbol: 'XTZ',
      decimals: 18
    },
    rpcUrls: {
      default: {
        http: ['https://node.mainnet.etherlink.com'],
        webSocket: [],
      },
      public: {
        http: ['https://node.mainnet.etherlink.com'],
        webSocket: [],
      },
    },
    blockExplorers: {
      default: { name: 'Etherlink Explorer', url: 'https://explorer.etherlink.com' },
    },
  },
  testnet: {
    id: 128123,
    name: 'Etherlink Shadownet',
    network: 'testnet',
    nativeCurrency: {
      name: 'XTZ',
      symbol: 'XTZ',
      decimals: 18
    },
    rpcUrls: {
      default: {
        http: ['https://node.shadownet.etherlink.com'],
        webSocket: [],
      },
      public: {
        http: ['https://node.shadownet.etherlink.com'],
        webSocket: [],
      },
    },
    blockExplorers: {
      default: { name: 'Etherlink Shadownet Explorer', url: 'https://shadownet.explorer.etherlink.com' },
    },
  },
};

// Get the active chain config based on environment
export const activeChainConfig = chainConfig[NETWORK_TYPE] || chainConfig.mainnet;

export const rpcNodes = {
  mainnet: {
    url: chainConfig.mainnet.rpcUrls.default,
    chainId: chainConfig.mainnet.id,
    name: chainConfig.mainnet.name,
    code: "mainnet"
  },
  testnet: {
    url: chainConfig.testnet.rpcUrls.default,
    chainId: chainConfig.testnet.id,
    name: chainConfig.testnet.name,
    code: "testnet"
  },
};

// Get active RPC node based on environment
export const activeRpcNode = rpcNodes[NETWORK_TYPE] || rpcNodes.mainnet;

// Create wagmi config with active chain
export const config = createConfig({
  chains: [activeChainConfig],
  connectors: [
    metaMask(),
    injected(),
    // walletConnect({ projectId }),
    safe(),
  ],
  transports: {
    [activeChainConfig.id]: http(activeChainConfig.rpcUrls.default.http[0])
  },
});

const GRAPHQL_URL = import.meta.env.VITE_GRAPHQL_URL || "http://localhost:8181/v1/graphql";
const GRAPHQL_WS = GRAPHQL_URL.replace(/^http/, 'ws');

export const dipdup = {
  mainnet: {
    graphql: GRAPHQL_URL,
    ws: GRAPHQL_WS,
  },
  testnet: {
    graphql: GRAPHQL_URL,
    ws: GRAPHQL_WS,
  },
}

// Sanity configuration
export const sanity = {
  id: "agentlink-vaults",
}

export const contracts = {
  mainnet: {
    vault: "0x895Ea1c1A1EF1EceF0Fb822e33BE0bB9d493559d",
  },
  testnet: {
    vault: "0x0000000000000000000000000000000000000000",
  },
}
