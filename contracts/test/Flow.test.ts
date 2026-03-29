import { expect } from "chai";
import { ethers } from "hardhat";
import { 
  ArbitrageVault, 
  MockERC20, 
  MockDexRouter, 
  MockUniswapV3Router, 
  MockCurvePool 
} from "../typechain-types";
import { HardhatEthersSigner } from "@nomicfoundation/hardhat-ethers/signers";

describe("ArbitrageVault Flow Tests", function () {
  let vault: ArbitrageVault;
  let usdc: MockERC20;
  let wxtz: MockERC20;
  let v2Router: MockDexRouter;
  let v3Router: MockUniswapV3Router;
  let curvePool: MockCurvePool;
  
  let owner: HardhatEthersSigner;
  let strategist: HardhatEthersSigner;
  let user: HardhatEthersSigner;

  const DexType = {
    UNISWAP_V2: 0,
    UNISWAP_V3: 1,
    CURVE: 2,
    UNIVERSAL_ROUTER: 3,
    CURVE_V2: 4
  };

  const initialDeposit = ethers.parseUnits("1000", 18);

  beforeEach(async function () {
    [owner, strategist, user] = await ethers.getSigners();

    const MockERC20Factory = await ethers.getContractFactory("MockERC20");
    usdc = await MockERC20Factory.deploy("USD Coin", "USDC") as MockERC20;
    wxtz = await MockERC20Factory.deploy("Wrapped XTZ", "WXTZ") as MockERC20;

    const ArbitrageVaultFactory = await ethers.getContractFactory("ArbitrageVault");
    vault = await ArbitrageVaultFactory.deploy(
      await usdc.getAddress(), 
      "Arbitrage Vault USDC", 
      "vUSDC"
    ) as ArbitrageVault;

    const MockDexRouterFactory = await ethers.getContractFactory("MockDexRouter");
    v2Router = await MockDexRouterFactory.deploy() as MockDexRouter;
    const MockUniswapV3RouterFactory = await ethers.getContractFactory("MockUniswapV3Router");
    v3Router = await MockUniswapV3RouterFactory.deploy() as MockUniswapV3Router;
    const MockCurvePoolFactory = await ethers.getContractFactory("MockCurvePool");
    curvePool = await MockCurvePoolFactory.deploy(
      await usdc.getAddress(), 
      await wxtz.getAddress()
    ) as MockCurvePool;

    await vault.setWhitelistedDex(await v2Router.getAddress(), true);
    await vault.setWhitelistedDex(await v3Router.getAddress(), true);
    await vault.setWhitelistedDex(await curvePool.getAddress(), true);

    const STRATEGIST_ROLE = await vault.STRATEGIST_ROLE();
    await vault.grantRole(STRATEGIST_ROLE, strategist.address);

    // Initial Funding
    await usdc.mint(user.address, initialDeposit * 5n);
    await usdc.connect(user).approve(await vault.getAddress(), initialDeposit * 5n);

    // Fund DEXs with liquidity
    const liquidityAmount = ethers.parseUnits("10000", 18);
    await usdc.mint(await v2Router.getAddress(), liquidityAmount);
    await wxtz.mint(await v2Router.getAddress(), liquidityAmount);
    await usdc.mint(await v3Router.getAddress(), liquidityAmount);
    await wxtz.mint(await v3Router.getAddress(), liquidityAmount);
    await usdc.mint(await curvePool.getAddress(), liquidityAmount);
    await wxtz.mint(await curvePool.getAddress(), liquidityAmount);
  });

  it("Full Journey: Deposit -> Arbitrage -> Withdraw", async function () {
    // 1. User Deposits
    await vault.connect(user).deposit(initialDeposit, user.address);
    expect(await vault.balanceOf(user.address)).to.equal(initialDeposit);
    expect(await vault.totalAssets()).to.equal(initialDeposit);

    // 2. Strategist Executes Arbitrage (V2 -> V3)
    const amountToTrade = initialDeposit / 2n;
    const v3Data = ethers.AbiCoder.defaultAbiCoder().encode(["uint24", "uint160"], [3000, 0]);
    
    const steps = [
      {
        dex: await v2Router.getAddress(),
        dexType: DexType.UNISWAP_V2,
        tokenIn: await usdc.getAddress(),
        tokenOut: await wxtz.getAddress(),
        data: "0x"
      },
      {
        dex: await v3Router.getAddress(),
        dexType: DexType.UNISWAP_V3,
        tokenIn: await wxtz.getAddress(),
        tokenOut: await usdc.getAddress(),
        data: v3Data
      }
    ];

    await vault.connect(strategist).executeMultiHop(
      steps,
      amountToTrade,
      0 // minExpectedProfit
    );

    const midAssets = await vault.totalAssets();
    expect(midAssets).to.be.greaterThan(initialDeposit);

    // 3. User Withdraws (with profits)
    const initialUserBalance = await usdc.balanceOf(user.address);
    const userShares = await vault.balanceOf(user.address);
    
    // Preview withdrawal value
    const expectedAssets = await vault.previewRedeem(userShares);
    expect(expectedAssets).to.be.greaterThan(initialDeposit);

    await vault.connect(user).redeem(userShares, user.address, user.address);
    
    const finalUserBalance = await usdc.balanceOf(user.address);
    expect(finalUserBalance - initialUserBalance).to.equal(expectedAssets);
    expect(await vault.balanceOf(user.address)).to.equal(0n);
  });

  it("Multiple Arbitrages: Cumulative Profit Tracking", async function () {
    await vault.connect(user).deposit(initialDeposit, user.address);
    const amountToTrade = initialDeposit / 4n;
    
    // Arb 1: V2 -> Curve
    const curveDataSell = ethers.AbiCoder.defaultAbiCoder().encode(["int128", "int128"], [1, 0]);
    await vault.connect(strategist).executeMultiHop(
      [
        {
          dex: await v2Router.getAddress(),
          dexType: DexType.UNISWAP_V2,
          tokenIn: await usdc.getAddress(),
          tokenOut: await wxtz.getAddress(),
          data: "0x"
        },
        {
          dex: await curvePool.getAddress(),
          dexType: DexType.CURVE,
          tokenIn: await wxtz.getAddress(),
          tokenOut: await usdc.getAddress(),
          data: curveDataSell
        }
      ],
      amountToTrade,
      0 // minExpectedProfit
    );

    const asset1 = await vault.totalAssets();
    expect(asset1).to.be.greaterThan(initialDeposit);

    // Arb 2: Curve -> V3
    const curveDataBuy = ethers.AbiCoder.defaultAbiCoder().encode(["int128", "int128"], [0, 1]);
    const v3Data = ethers.AbiCoder.defaultAbiCoder().encode(["uint24", "uint160"], [3000, 0]);
    await vault.connect(strategist).executeMultiHop(
      [
        {
          dex: await curvePool.getAddress(),
          dexType: DexType.CURVE,
          tokenIn: await usdc.getAddress(),
          tokenOut: await wxtz.getAddress(),
          data: curveDataBuy
        },
        {
          dex: await v3Router.getAddress(),
          dexType: DexType.UNISWAP_V3,
          tokenIn: await wxtz.getAddress(),
          tokenOut: await usdc.getAddress(),
          data: v3Data
        }
      ],
      amountToTrade,
      0 // minExpectedProfit
    );

    const asset2 = await vault.totalAssets();
    expect(asset2).to.be.greaterThan(asset1);
  });
});
