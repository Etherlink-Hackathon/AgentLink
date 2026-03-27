const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("ArbitrageVault Security Tests", function () {
  let vault, asset, dexBuy, dexSell, strategist, owner, user, tokenTrade;
  const initialDeposit = ethers.parseEther("1000");

  beforeEach(async function () {
    [owner, strategist, user] = await ethers.getSigners();

    const MockERC20 = await ethers.getContractFactory("MockERC20");
    asset = await MockERC20.deploy("USD Coin", "USDC");
    await asset.waitForDeployment();

    const MockDexRouter = await ethers.getContractFactory("MockDexRouter");
    dexBuy = await MockDexRouter.deploy();
    await dexBuy.waitForDeployment();
    dexSell = await MockDexRouter.deploy();
    await dexSell.waitForDeployment();

    const ArbitrageVault = await ethers.getContractFactory("ArbitrageVault");
    vault = await ArbitrageVault.deploy(await asset.getAddress(), "Arbitrage Vault USDC", "vUSDC");
    await vault.waitForDeployment();

    const STRATEGIST_ROLE = await vault.STRATEGIST_ROLE();
    await vault.grantRole(STRATEGIST_ROLE, strategist.address);
    await vault.setWhitelistedDex(await dexBuy.getAddress(), true);
    await vault.setWhitelistedDex(await dexSell.getAddress(), true);

    tokenTrade = await MockERC20.deploy("Wrapped Tezos", "WXTZ");
    await tokenTrade.waitForDeployment();

    await asset.mint(user.address, initialDeposit);
    await asset.connect(user).approve(await vault.getAddress(), initialDeposit);
    await vault.connect(user).deposit(initialDeposit, user.address);

    // Fund DEXs
    await tokenTrade.mint(await dexBuy.getAddress(), initialDeposit * 10n);
    await tokenTrade.mint(await dexSell.getAddress(), initialDeposit * 10n);
    await asset.mint(await dexBuy.getAddress(), initialDeposit * 10n);
    await asset.mint(await dexSell.getAddress(), initialDeposit * 10n);
  });

  it("Should prevent non-strategists from executing arbitrage", async function () {
    await expect(
      vault.connect(user).executeArbitrage(
        await dexBuy.getAddress(),
        await dexSell.getAddress(),
        await tokenTrade.getAddress(),
        initialDeposit / 2n
      )
    ).to.be.reverted; // General revert check for role failure
  });

  it("Should revert if arbitrage is unprofitable", async function () {
    // Set DEX to be unprofitable (90% return)
    await dexBuy.setMultiplier(90);
    await dexSell.setMultiplier(100);

    await expect(
      vault.connect(strategist).executeArbitrage(
        await dexBuy.getAddress(),
        await dexSell.getAddress(),
        await tokenTrade.getAddress(),
        initialDeposit / 2n
      )
    ).to.be.revertedWith("Arbitrage unprofitable, reverting");
  });

  it("Should revert if DEX is not whitelisted", async function () {
    const MockDexRouter = await ethers.getContractFactory("MockDexRouter");
    const rogueDex = await MockDexRouter.deploy();
    await rogueDex.waitForDeployment();

    await expect(
      vault.connect(strategist).executeArbitrage(
        await rogueDex.getAddress(),
        await dexSell.getAddress(),
        await tokenTrade.getAddress(),
        initialDeposit / 2n
      )
    ).to.be.revertedWith("DEX Buy not whitelisted");
  });

  it("Should prevent strategist from withdrawing directly", async function () {
    // Strategist has role but no shares
    await expect(
      vault.connect(strategist).withdraw(initialDeposit, strategist.address, strategist.address)
    ).to.be.reverted; // Standard ERC4626/ERC20 failure as they have 0 shares
  });
});
