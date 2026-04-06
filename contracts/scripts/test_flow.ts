import { ethers, network } from "hardhat";
import * as fs from "fs";
import * as path from "path";

/**
 * Modular Flow Testing Script for ArbitrageVault.
 * Use flags to execute specific parts of the flow:
 * --whitelist, --deposit, --arbitrage, --withdraw
 */
async function main() {
    const [deployer] = await ethers.getSigners();
    const args = process.argv;

    const whitelistFlag = process.env.npm_config_whitelist === "true" || args.includes("--whitelist") || process.env.WHITELIST === "true";
    const depositFlag = process.env.npm_config_deposit === "true" || args.includes("--deposit") || process.env.DEPOSIT === "true";
    const arbitrageFlag = process.env.npm_config_arbitrage === "true" || args.includes("--arbitrage") || process.env.ARBITRAGE === "true";
    const withdrawFlag = process.env.npm_config_withdraw === "true" || args.includes("--withdraw") || process.env.WITHDRAW === "true";

    if (!whitelistFlag && !depositFlag && !arbitrageFlag && !withdrawFlag) {
        console.log("ℹ️  Usage via npm: npm run test-flow:etherlink --whitelist --deposit --arbitrage --withdraw");
        console.log("ℹ️  Usage via env: WHITELIST=true npx hardhat run scripts/test_flow.ts --network <network>");
        return;
    }

    console.log(`🚀 Executing flow with account: ${deployer.address}`);

    // Load setup data
    const poolsPath = path.join(__dirname, "../../indexer/src/arbitrage_vault/etherlink_pools.json");
    const pools = JSON.parse(fs.readFileSync(poolsPath, "utf8"));

    const ETHERLINK_WXTZ = process.env.WXTZ_ADDRESS?.toLowerCase();
    const ETHERLINK_USDC = process.env.USDC_ADDRESS?.toLowerCase();
    const OKU_ROUTER = process.env.OKU_ROUTER?.toLowerCase();

    if (!ETHERLINK_WXTZ || !ETHERLINK_USDC || !OKU_ROUTER) {
        throw new Error("❌ Missing WXTZ_ADDRESS, USDC_ADDRESS, or OKU_ROUTER in .env");
    }

    const vaultAddress = process.env.VAULT_ADDRESS?.toLowerCase();
    if (!vaultAddress) {
        throw new Error("❌ Missing VAULT_ADDRESS in .env");
    }

    const DexType = { UNISWAP_V2: 0, UNISWAP_V3: 1, CURVE: 2 };
    const vault = await ethers.getContractAt("ArbitrageVault", vaultAddress);
    const wxtz = await ethers.getContractAt("IERC20", ETHERLINK_WXTZ);

    // --- STEP: WHITELIST ---
    if (whitelistFlag) {
        console.log("\n🛡️  Whitelisting real DEX addresses...");

        // Whitelist all pools from the JSON file
        for (const pool of pools) {
            await (await vault.setWhitelistedDex(pool.address, true)).wait();
            console.log(`✅ Whitelisted ${pool.dex_name} pool (${pool.token0.symbol}/${pool.token1.symbol}): ${pool.address}`);
        }

        // Whitelist Key Routers
        const routers = [
            OKU_ROUTER,
        ];
        for (const router of routers) {
            if (router) {
                await (await vault.setWhitelistedDex(router, true)).wait();
                console.log(`✅ Whitelisted Router: ${router}`);
            }
        }

        console.log("✅ Whitelisting completed.");
    }

    // --- STEP: DEPOSIT ---
    if (depositFlag) {
        const depositAmount = ethers.parseUnits("1", 18);
        console.log(`\n🏦 Depositing ${ethers.formatUnits(depositAmount, 18)} WXTZ...`);

        const balance = await wxtz.balanceOf(deployer.address);
        if (balance < depositAmount) {
            throw new Error(`Insufficient WXTZ balance. Need ${ethers.formatUnits(depositAmount, 18)} but have ${ethers.formatUnits(balance, 18)}`);
        }

        await (await wxtz.approve(vaultAddress, depositAmount)).wait();
        await (await vault.deposit(depositAmount, deployer.address)).wait();
        console.log(`✅ Deposited. Vault assets: ${ethers.formatUnits(await vault.totalAssets(), 18)} WXTZ`);
    }

    // --- STEP: ARBITRAGE ---
    if (arbitrageFlag) {
        console.log("\n🔄 Executing Real Pool Swap (Oku Trade V3)...");
        const depositAmount = await vault.totalAssets();
        if (depositAmount === 0n) {
            throw new Error("❌ Vault is empty. Deposit some funds first using --deposit");
        }

        const swapAmount = depositAmount / 2n;
        // Universal Router (V3_SWAP_EXACT_IN)
        // Command 0x00 = V3_SWAP_EXACT_IN
        const commands = new Uint8Array([0x00]);

        // Path encoding: [tokenIn(20 bytes), fee(3 bytes), tokenOut(20 bytes)]
        const pathBaseToIntermediate = ethers.solidityPacked(
            ["address", "uint24", "address"],
            [ETHERLINK_WXTZ, 500, ETHERLINK_USDC]
        );

        const pathIntermediateToBase = ethers.solidityPacked(
            ["address", "uint24", "address"],
            [ETHERLINK_USDC, 500, ETHERLINK_WXTZ]
        );

        // Input encoding: [address recipient, uint256 amountIn, uint256 amountOutMinimum, bytes path, bool payerIsUser]
        const inputBaseToIntermediate = ethers.AbiCoder.defaultAbiCoder().encode(
            ["address", "uint256", "uint256", "bytes", "bool"],
            [vaultAddress, swapAmount, 0, pathBaseToIntermediate, false]
        );

        const inputIntermediateToBase = ethers.AbiCoder.defaultAbiCoder().encode(
            ["address", "uint256", "uint256", "bytes", "bool"],
            [vaultAddress, 0, 0, pathIntermediateToBase, false]
        );

        // Final payload structure for ArbitrageVault DexType.UNIVERSAL_ROUTER
        const urDataLeg1 = ethers.AbiCoder.defaultAbiCoder().encode(
            ["bytes", "bytes[]"],
            [commands, [inputBaseToIntermediate]]
        );

        const urDataLeg2 = ethers.AbiCoder.defaultAbiCoder().encode(
            ["bytes", "bytes[]"],
            [commands, [inputIntermediateToBase]]
        );

        console.log(`🚀 Swapping ${ethers.formatUnits(swapAmount, 18)} WXTZ via Oku...`);
        console.log("🛠️  Enabling testMode to bypass unprofitable trade reverts...");
        await (await vault.setTestMode(true)).wait();

        const steps = [
            {
                dex: OKU_ROUTER,
                dexType: 3, // DexType.UNIVERSAL_ROUTER
                tokenIn: ETHERLINK_WXTZ,
                tokenOut: ETHERLINK_USDC,
                data: urDataLeg1
            },
            {
                dex: OKU_ROUTER,
                dexType: 3, // DexType.UNIVERSAL_ROUTER
                tokenIn: ETHERLINK_USDC,
                tokenOut: ETHERLINK_WXTZ,
                data: urDataLeg2
            }
        ];

        await (await vault.executeMultiHop(
            steps,
            swapAmount,
            0 // minExpectedProfit
        )).wait();

        await (await vault.setTestMode(false)).wait();
        console.log("🔒 Disabling testMode. Trade complete!");

        console.log(`✅ Arbitrage executed. New total assets: ${ethers.formatUnits(await vault.totalAssets(), 18)}`);
    }

    // --- STEP: WITHDRAW ---
    if (withdrawFlag) {
        console.log("\n💸 Withdrawing assets...");
        const userShares = await vault.balanceOf(deployer.address);
        if (userShares === 0n) {
            console.log("ℹ️  Nothing to withdraw.");
        } else {
            await (await vault.redeem(userShares, deployer.address, deployer.address)).wait();
            console.log("✅ Withdrawal completed.");
        }
    }

    console.log("\n✨ Selective Flow Completed!");
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
