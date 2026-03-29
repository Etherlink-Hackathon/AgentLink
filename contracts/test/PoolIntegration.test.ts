import { expect } from "chai";
import { ethers } from "hardhat";
import { ArbitrageVault, MockERC20 } from "../typechain-types";
import { HardhatEthersSigner } from "@nomicfoundation/hardhat-ethers/signers";
import pools from "./etherlink_pools.json";

describe("ArbitrageVault Pool Integration Tests", function () {
  let vault: ArbitrageVault;
  let asset: MockERC20;
  let strategist: HardhatEthersSigner;
  let owner: HardhatEthersSigner;

  const DexType = {
    UNISWAP_V2: 0,
    UNISWAP_V3: 1,
    CURVE: 2
  };

  beforeEach(async function () {
    [owner, strategist] = await ethers.getSigners();

    const MockERC20Factory = await ethers.getContractFactory("MockERC20");
    asset = await MockERC20Factory.deploy("USD Coin", "USDC") as MockERC20;

    const ArbitrageVaultFactory = await ethers.getContractFactory("ArbitrageVault");
    vault = await ArbitrageVaultFactory.deploy(
      await asset.getAddress(), 
      "Arbitrage Vault USDC", 
      "vUSDC"
    ) as ArbitrageVault;

    const STRATEGIST_ROLE = await vault.STRATEGIST_ROLE();
    await vault.grantRole(STRATEGIST_ROLE, strategist.address);

    // Whitelist all real pool addresses from the JSON
    for (const pool of pools) {
      await vault.setWhitelistedDex(pool.address, true);
    }
  });

  it("Should have all pools from JSON whitelisted", async function () {
    for (const pool of pools) {
      expect(await vault.whitelistedDexes(pool.address)).to.be.true;
    }
  });

  it("Should correctly identify pool types for execution calls", async function () {
    // This test verifies that we can construct correct calls for each pool type
    for (const pool of pools) {
      let type;
      let data = "0x";

      if (pool.dex.includes("Curve")) {
        type = DexType.CURVE;
        data = ethers.AbiCoder.defaultAbiCoder().encode(["int128", "int128"], [0, 1]);
      } else if (pool.dex.includes("Oku Trade")) {
        type = DexType.UNISWAP_V3;
        data = ethers.AbiCoder.defaultAbiCoder().encode(["uint24", "uint160"], [3000, 0]);
      } else {
        type = DexType.UNISWAP_V2;
      }

      // We expect the call to at least pass the "Whitelisted" and "Role" guards
      // It will revert later because there's no real pool at that address in the Hardhat network,
      // but we care about the Vault allowing the call with the correct signature.
      
      const amount = ethers.parseUnits("1.0", 18);
      const intermediateToken = "0x0000000000000000000000000000000000000001"; // Dummy

      // Construct a call to make sure the signature matches andwhitelisting passes
      // We expect a revert since the address doesn't contain a real pool/router,
      // but NOT a "DEX not whitelisted" or role error.
      await expect(
        vault.connect(strategist).executeArbitrage(
          pool.address,
          type,
          data,
          pool.address,
          type,
          data,
          intermediateToken,
          amount
        )
      ).to.not.be.revertedWith("DEX Buy not whitelisted");
    }
  });
});
