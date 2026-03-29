import { ethers } from "hardhat";
import * as dotenv from "dotenv";

dotenv.config();

/**
 * 🚀 HELLO MULTI-HOP ARBITRAGE
 * This script performs a real-world WXTZ -> USDC -> WXTZ swap on Etherlink
 * using the Universal Router (Oku Trade) to verify the new "executeMultiHop" logic.
 */
async function main() {
    const vaultAddress = process.env.VAULT_ADDRESS;
    const wxtzAddress = process.env.WXTZ_ADDRESS;
    const usdcAddress = process.env.USDC_ADDRESS;
    const okurouter = process.env.OKU_ROUTER;

    if (!vaultAddress || !wxtzAddress || !usdcAddress || !okurouter) {
        throw new Error("Missing env variables in .env");
    }

    const vault = await ethers.getContractAt("ArbitrageVault", vaultAddress);
    const [signer] = await ethers.getSigners();

    console.log(`\n🤖 Strategist Account: ${signer.address}`);
    console.log(`🏦 Vault Instance: ${vaultAddress}`);

    // 1. Check Initial Balance
    const initialBalance = await vault.totalAssets();
    console.log(`💰 Vault Initial Assets: ${ethers.formatUnits(initialBalance, 18)} WXTZ`);

    if (initialBalance < ethers.parseUnits("0.1", 18)) {
        console.log("⚠️ Vault needs at least 0.1 WXTZ for this test. Please deposit first.");
        return;
    }

    // 2. Enable Test Mode (Allows unprofitable swaps for verification)
    console.log("\n🛠️ Enabling testMode...");
    await (await vault.setTestMode(true)).wait();

    // 3. Prepare Payloads
    const swapAmount = ethers.parseUnits("0.1", 18);
    
    // Leg 1 Path: WXTZ -> USDC (500 fee)
    const path1 = ethers.solidityPacked(["address", "uint24", "address"], [wxtzAddress, 500, usdcAddress]);
    
    // Leg 2 Path: USDC -> WXTZ (500 fee)
    const path2 = ethers.solidityPacked(["address", "uint24", "address"], [usdcAddress, 500, wxtzAddress]);

    // Leg 1 UR Data (Fixed Amount)
    const commandsLeg1 = Uint8Array.from([0x00]); // V3_SWAP_EXACT_IN
    const input1 = ethers.AbiCoder.defaultAbiCoder().encode(
        ["address", "uint256", "uint256", "bytes", "bool"],
        [vaultAddress, swapAmount, 0, path1, false]
    );
    const urDataLeg1 = ethers.AbiCoder.defaultAbiCoder().encode(["bytes", "bytes[]"], [commandsLeg1, [input1]]);

    // Leg 2 UR Data (Zero Placeholder - Vault will inject the actual amount)
    const commandsLeg2 = Uint8Array.from([0x00]);
    const input2 = ethers.AbiCoder.defaultAbiCoder().encode(
        ["address", "uint256", "uint256", "bytes", "bool"],
        [vaultAddress, 0, 0, path2, false]
    );
    const urDataLeg2 = ethers.AbiCoder.defaultAbiCoder().encode(["bytes", "bytes[]"], [commandsLeg2, [input2]]);

    // 4. Execute Arbitrage using Generalized Multi-Hop
    console.log("🔥 Executing Hardened Multi-Hop legs...");
    
    const steps = [
        {
            dex: okurouter,
            dexType: 3, // DexType.UNIVERSAL_ROUTER
            tokenIn: wxtzAddress,
            tokenOut: usdcAddress,
            data: urDataLeg1
        },
        {
            dex: okurouter,
            dexType: 3, // DexType.UNIVERSAL_ROUTER
            tokenIn: usdcAddress,
            tokenOut: wxtzAddress,
            data: urDataLeg2
        }
    ];

    const tx = await vault.executeMultiHop(
        steps,
        swapAmount,
        0, // minExpectedProfit
        { gasLimit: 1500000 }
    );

    console.log(`⏳ Pending: ${tx.hash}`);
    await tx.wait();

    // 5. Cleanup and Results
    console.log("\n🔒 Disabling testMode...");
    await (await vault.setTestMode(false)).wait();

    const finalBalance = await vault.totalAssets();
    const diff = finalBalance - initialBalance;
    
    console.log(`✅ Success! Final Assets: ${ethers.formatUnits(finalBalance, 18)} WXTZ`);
    console.log(`📊 Net Cost (Fees/Slippage): ${ethers.formatUnits(diff, 18)} WXTZ`);
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
