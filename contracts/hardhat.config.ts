import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";

const config: HardhatUserConfig = {
  solidity: "0.8.20",
  networks: {
    etherlink: {
      url: "https://node.mainnet.etherlink.com",
      chainId: 42793
    }
  }
};

export default config;
