const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("ArbitrageVault Flow Tests", function () {
  let vault, asset, dexBuy, dexSell, strategist, owner, user;
  const initialDeposit = ethers.parseEther("1000");

  beforeEach(async function () {
    [owner, strategist, user] = await ethers.getSigners();

    // Deploy Mock Asset (e.g., USDC)
    const MockERC20 = await ethers.getContractFactory("MockERC20");
    asset = await MockERC20.deploy("USD Coin", "USDC");
    await asset.waitForDeployment();

    // Deploy Mock DEX Routers
    const MockDexRouter = await ethers.getContractFactory("MockDexRouter");
    dexBuy = await MockDexRouter.deploy();
    await dexBuy.waitForDeployment();
    dexSell = await MockDexRouter.deploy();
    await dexSell.waitForDeployment();

    // Deploy Vault
    const ArbitrageVault = await ethers.getContractFactory("ArbitrageVault");
    vault = await ArbitrageVault.deploy(await asset.getAddress(), "Arbitrage Vault USDC", "vUSDC");
    await vault.waitForDeployment();

    // Setup Roles and Whitelist
    const STRATEGIST_ROLE = await vault.STRATEGIST_ROLE();
    await vault.grantRole(STRATEGIST_ROLE, strategist.address);
    await vault.setWhitelistedDex(await dexBuy.getAddress(), true);
    await vault.setWhitelistedDex(await dexSell.getAddress(), true);

    // Initial funding
    await asset.mint(user.address, initialDeposit * 2n);
    await asset.connect(user).approve(await vault.getAddress(), initialDeposit * 2n);
  });

  it("Should allow a user to deposit and receive shares", async function () {
    await vault.connect(user).deposit(initialDeposit, user.address);
    expect(await vault.balanceOf(user.address)).to.equal(initialDeposit);
    expect(await vault.totalAssets()).to.equal(initialDeposit);
  });

  it("Should allow a user to withdraw their assets", async function () {
    await vault.connect(user).deposit(initialDeposit, user.address);
    const initialBalance = await asset.balanceOf(user.address);
    
    await vault.connect(user).withdraw(initialDeposit, user.address, user.address);
    
    expect(await asset.balanceOf(user.address)).to.equal(initialBalance + initialDeposit);
    expect(await vault.balanceOf(user.address)).to.equal(0n);
  });

  it("Should correctly reflect profits after a successful arbitrage", async function () {
    await vault.connect(user).deposit(initialDeposit, user.address);
    
    // Create intermediate token (e.g. WXTZ)
    const MockERC20 = await ethers.getContractFactory("MockERC20");
    const tokenTrade = await MockERC20.deploy("Wrapped Tezos", "WXTZ");
    await tokenTrade.waitForDeployment();
    
    // Fund the DEXs with the intermediate token and base asset
    await tokenTrade.mint(await dexBuy.getAddress(), initialDeposit * 10n);
    await tokenTrade.mint(await dexSell.getAddress(), initialDeposit * 10n);
    await asset.mint(await dexBuy.getAddress(), initialDeposit * 10n);
    await asset.mint(await dexSell.getAddress(), initialDeposit * 10n);

    const amountToTrade = initialDeposit / 2n;
    
    // Execute Arbitrage
    await vault.connect(strategist).executeArbitrage(
      await dexBuy.getAddress(),
      await dexSell.getAddress(),
      await tokenTrade.getAddress(),
      amountToTrade
    );

    const finalAssets = await vault.totalAssets();
    expect(finalAssets).to.be.greaterThan(initialDeposit);
    
    // Check share value increase
    // Initially 1:1, now 1 share worth more than 1 asset
    const assetsForShares = await vault.previewRedeem(initialDeposit);
    expect(assetsForShares).to.be.greaterThan(initialDeposit);
  });
});
