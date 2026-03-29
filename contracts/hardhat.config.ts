import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import * as dotenv from "dotenv";

dotenv.config();

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
      viaIR: true,
    },
  },
  networks: {
    // hardhat: {
    //   forking: {
    //     url: "https://node.mainnet.etherlink.com",
    //   }
    // },
    etherlink: {
      url: "https://node.mainnet.etherlink.com",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : []
    }
  },
  etherscan: {
    apiKey: {
      etherlink: "any" // Blockscout doesn't require a real API key
    },
    customChains: [
      {
        network: "etherlink",
        chainId: 42793,
        urls: {
          apiURL: "https://explorer.etherlink.com/api",
          browserURL: "https://explorer.etherlink.com"
        }
      }
    ]
  }
};

export default config;
