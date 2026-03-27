import ChainlinkPriceOracleABI from './abis/ChainlinkPriceOracle.json'

// Contract addresses - placeholders for AgentLink
const ADDRESSES = {
  development: {
    VaultManager: '0x0000000000000000000000000000000000000000',
    ChainlinkPriceOracle: '0xC56684d7B3414880c8A035aeFcE0ca1fC7d2296A'
  },
  testnet: {
    VaultManager: '0x0000000000000000000000000000000000000000',
    ChainlinkPriceOracle: '0xC56684d7B3414880c8A035aeFcE0ca1fC7d2296A'
  },
  mainnet: {
    VaultManager: '',
    ChainlinkPriceOracle: ''
  }
}

const NETWORK_ENV = import.meta.env.VITE_NETWORK_ENV || 'development'

export const ABIs = {
  ChainlinkPriceOracle: ChainlinkPriceOracleABI
}

export const CONTRACT_ADDRESSES = ADDRESSES[NETWORK_ENV]