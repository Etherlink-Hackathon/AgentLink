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

describe("ArbitrageVault Universal DEX Support", function () {
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

  beforeEach(async function () {
    [owner, strategist, user] = await ethers.getSigners();

    // 1. Deploy Tokens
    const MockERC20Factory = await ethers.getContractFactory("MockERC20");
    usdc = await MockERC20Factory.deploy("USD Coin", "USDC") as MockERC20;
    wxtz = await MockERC20Factory.deploy("Wrapped XTZ", "WXTZ") as MockERC20;

    // 2. Deploy Vault
    const ArbitrageVaultFactory = await ethers.getContractFactory("ArbitrageVault");
    vault = await ArbitrageVaultFactory.deploy(
      await usdc.getAddress(), 
      "Arbitrage Vault USDC", 
      "vUSDC"
    ) as ArbitrageVault;

    // 3. Deploy DEX Mocks
    const MockDexRouterFactory = await ethers.getContractFactory("MockDexRouter");
    v2Router = await MockDexRouterFactory.deploy() as MockDexRouter;

    const MockUniswapV3RouterFactory = await ethers.getContractFactory("MockUniswapV3Router");
    v3Router = await MockUniswapV3RouterFactory.deploy() as MockUniswapV3Router;

    const MockCurvePoolFactory = await ethers.getContractFactory("MockCurvePool");
    curvePool = await MockCurvePoolFactory.deploy(
      await usdc.getAddress(), 
      await wxtz.getAddress()
    ) as MockCurvePool;

    // 4. Setup Whitelisting & Roles
    await vault.setWhitelistedDex(await v2Router.getAddress(), true);
    await vault.setWhitelistedDex(await v3Router.getAddress(), true);
    await vault.setWhitelistedDex(await curvePool.getAddress(), true);

    const STRATEGIST_ROLE = await vault.STRATEGIST_ROLE();
    await vault.grantRole(STRATEGIST_ROLE, strategist.address);

    // 5. Initial Funding
    const depositAmount = ethers.parseUnits("1000", 18);
    await usdc.mint(owner.address, depositAmount);
    await usdc.approve(await vault.getAddress(), depositAmount);
    await vault.deposit(depositAmount, owner.address);

    // Fund DEXs with liquidity
    const liquidityAmount = ethers.parseUnits("10000", 18);
    await usdc.mint(await v2Router.getAddress(), liquidityAmount);
    await wxtz.mint(await v2Router.getAddress(), liquidityAmount);
    await usdc.mint(await v3Router.getAddress(), liquidityAmount);
    await wxtz.mint(await v3Router.getAddress(), liquidityAmount);
    await usdc.mint(await curvePool.getAddress(), liquidityAmount);
    await wxtz.mint(await curvePool.getAddress(), liquidityAmount);
  });

  it("Should execute arbitrage between two Uniswap V2 pools", async function () {
    const amountBase = ethers.parseUnits("100", 18);
    const data = "0x"; // Not used for V2 in our impl but passed in signature

    // Buy Leg: V2 Router
    // Sell Leg: V2 Router
    // Note: In our mock, V2 router gives 1.1x profit by default
    
    const initialBalance = await vault.totalAssets();
    
    const steps = [
      {
        dex: await v2Router.getAddress(),
        dexType: DexType.UNISWAP_V2,
        tokenIn: await usdc.getAddress(),
        tokenOut: await wxtz.getAddress(),
        data: data
      },
      {
        dex: await v2Router.getAddress(),
        dexType: DexType.UNISWAP_V2,
        tokenIn: await wxtz.getAddress(),
        tokenOut: await usdc.getAddress(),
        data: data
      }
    ];

    await vault.connect(strategist).executeMultiHop(
      steps,
      amountBase,
      0 // minExpectedProfit
    );

    const finalBalance = await vault.totalAssets();
    expect(finalBalance).to.be.greaterThan(initialBalance);
  });

  it("Should execute arbitrage between Uniswap V3 (Oku) and Curve", async function () {
    const amountBase = ethers.parseUnits("100", 18);
    
    // V3 specific data: fee (3000 = 0.3%) and sqrtPriceLimitX96 (0)
    const v3Data = ethers.AbiCoder.defaultAbiCoder().encode(
      ["uint24", "uint160"], 
      [3000, 0]
    );

    // Curve specific data: i=0 (USDC), j=1 (WXTZ) for buy, i=1, j=0 for sell
    const curveDataBuy = ethers.AbiCoder.defaultAbiCoder().encode(
      ["int128", "int128"], 
      [0, 1]
    );
    const curveDataSell = ethers.AbiCoder.defaultAbiCoder().encode(
      ["int128", "int128"], 
      [1, 0]
    );

    const initialBalance = await vault.totalAssets();

    // Buy on V3, Sell on Curve
    const steps = [
      {
        dex: await v3Router.getAddress(),
        dexType: DexType.UNISWAP_V3,
        tokenIn: await usdc.getAddress(),
        tokenOut: await wxtz.getAddress(),
        data: v3Data
      },
      {
        dex: await curvePool.getAddress(),
        dexType: DexType.CURVE,
        tokenIn: await wxtz.getAddress(),
        tokenOut: await usdc.getAddress(),
        data: curveDataSell
      }
    ];

    await vault.connect(strategist).executeMultiHop(
      steps,
      amountBase,
      0 // minExpectedProfit
    );

    const finalBalance = await vault.totalAssets();
    expect(finalBalance).to.be.greaterThan(initialBalance);
  });

  it("Should revert if arbitrage is unprofitable", async function () {
    const amountBase = ethers.parseUnits("100", 18);
    const data = "0x";

    // Set V2 multiplier to 0.9 (90/100) to simulate loss
    await v2Router.setMultiplier(90);

    const steps = [
      {
        dex: await v2Router.getAddress(),
        dexType: DexType.UNISWAP_V2,
        tokenIn: await usdc.getAddress(),
        tokenOut: await wxtz.getAddress(),
        data: data
      },
      {
        dex: await v2Router.getAddress(),
        dexType: DexType.UNISWAP_V2,
        tokenIn: await wxtz.getAddress(),
        tokenOut: await usdc.getAddress(),
        data: data
      }
    ];

    await expect(
      vault.connect(strategist).executeMultiHop(
        steps,
        amountBase,
        0 // minExpectedProfit
      )
    ).to.be.revertedWith("Arbitrage Unprofitable");
  });

  it("Should revert if DEX is not whitelisted", async function () {
    const amountBase = ethers.parseUnits("100", 18);
    const randomAddress = user.address;

    const steps = [
      {
        dex: randomAddress,
        dexType: DexType.UNISWAP_V2,
        tokenIn: await usdc.getAddress(),
        tokenOut: await wxtz.getAddress(),
        data: "0x"
      },
      {
        dex: await v2Router.getAddress(),
        dexType: DexType.UNISWAP_V2,
        tokenIn: await wxtz.getAddress(),
        tokenOut: await usdc.getAddress(),
        data: "0x"
      }
    ];

    await expect(
      vault.connect(strategist).executeMultiHop(
        steps,
        amountBase,
        0 // minExpectedProfit
      )
    ).to.be.revertedWith("DEX not whitelisted");
  });
});
