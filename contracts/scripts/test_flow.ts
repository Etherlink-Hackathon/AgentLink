import { ethers, network } from "hardhat";
import * as fs from "fs";
import * as path from "path";

async function main() {
    const [deployer] = await ethers.getSigners();
    console.log(`🚀 Testing flow with the account: ${deployer.address}`);

    const poolsPath = path.join(__dirname, "../test/etherlink_pools.json");
    const pools = JSON.parse(fs.readFileSync(poolsPath, "utf8"));

    const ETHERLINK_WXTZ = "0xc9B53AB2679f573e480d01e0f49e2b5cfb7a3eab";
    const ETHERLINK_USDC = "0x796Ea11Fa2dD751eD01b53C372fFDB4AAa8f00F9";
    const OKU_ROUTER = "0x973aCbcC75E4D40f379e950882e37905188E67E7"; 

    const DexType = { UNISWAP_V2: 0, UNISWAP_V3: 1, CURVE: 2 };

    const baseAssetAddress = ETHERLINK_WXTZ;
    const envAddress = process.env.VAULT_ADDRESS;
    let vaultAddress: string;

    if (!envAddress) {
        console.log("🏗️  No VAULT_ADDRESS found, deploying new instance on fork...");
        const ArbitrageVault = await ethers.getContractFactory("ArbitrageVault");
        const vaultInstance = await ArbitrageVault.deploy(baseAssetAddress, "Arbitrage Vault XTZ", "vXTZ");
        await vaultInstance.waitForDeployment();
        vaultAddress = await vaultInstance.getAddress();
        console.log(`✅ ArbitrageVault deployed to: ${vaultAddress}`);

        // Grant Strategist Role
        const STRATEGIST_ROLE = await vaultInstance.STRATEGIST_ROLE();
        await vaultInstance.grantRole(STRATEGIST_ROLE, deployer.address);
    } else {
        vaultAddress = envAddress as string;
    }

    const vault = await ethers.getContractAt("ArbitrageVault", vaultAddress);
    const wxtz = await ethers.getContractAt("IERC20", baseAssetAddress);

    console.log("\n🛡️  Whitelisting real DEX addresses...");
    await (await vault.setWhitelistedDex(OKU_ROUTER, true)).wait();
    
    const curvePool = pools.find((p: any) => p.dex.includes("Curve"));
    if (curvePool) {
        await (await vault.setWhitelistedDex(curvePool.address, true)).wait();
        console.log(`✅ Whitelisted Curve pool: ${curvePool.address}`);
    }

    // 1. Initial Deposit (XTZ -> WXTZ -> Vault)
    const depositAmount = ethers.parseUnits("1", 18); // 1 XTZ
    console.log(`\n🏦 1. Depositing ${ethers.formatUnits(depositAmount, 18)} WXTZ...`);

    // Wrap XTZ
    const wxtzContract = new ethers.Contract(baseAssetAddress, ["function deposit() public payable"], deployer);
    await (await wxtzContract.deposit({ value: depositAmount })).wait();

    await (await wxtz.approve(vaultAddress, depositAmount)).wait();
    await (await vault.deposit(depositAmount, deployer.address)).wait();
    console.log(`✅ Deposited. Vault state: ${ethers.formatUnits(await vault.totalAssets(), 18)} WXTZ`);

    // 2. Perform Real Arbitrage/Swap Logic
    console.log("\n🔄 2. Executing Real Pool Swap (Oku Trade V3)...");
    
    // Scenario: WXTZ -> USDC on Oku (UniV3)
    const swapAmount = depositAmount / 2n;
    
    // Oku V3 Data: uint24 fee (3000 = 0.3%), uint160 sqrtPriceLimitX96 (0 = no limit)
    const okuData = ethers.AbiCoder.defaultAbiCoder().encode(["uint24", "uint160"], [3000, 0]);

    // For the purpose of this flow test, we'll use Oku for the first leg
    // and a mock or the same router for the second leg to satisfy the cycle requirement.
    // On a real fork, Leg 2 might revert if not profitable, so we'll "simulate" profit by 
    // minting tokens if on a local test environment, or just verifying the call mechanics.

    console.log(`🚀 Swapping ${ethers.formatUnits(swapAmount, 18)} WXTZ for USDC via Oku...`);
    
    await (await vault.executeArbitrage(
        OKU_ROUTER,
        DexType.UNISWAP_V3,
        okuData,
        OKU_ROUTER, // Leg 2 (reversing to USDC -> WXTZ)
        DexType.UNISWAP_V3,
        okuData,
        ETHERLINK_USDC,
        swapAmount
    )).wait();

    console.log(`✅ Arbitrage mechanics verified. Current assets: ${ethers.formatUnits(await vault.totalAssets(), 18)}`);

    // 3. Final Withdrawal
    console.log("\n💸 3. Withdrawing assets...");
    const userShares = await vault.balanceOf(deployer.address);
    await (await vault.redeem(userShares, deployer.address, deployer.address)).wait();
    console.log("✨ Integration Test Flow Complete!");
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
