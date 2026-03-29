import { run } from "hardhat";
import * as dotenv from "dotenv";
dotenv.config();
/**
 * Script for verifying the ArbitrageVault contract on Etherlink Explorer.
 * Usage: npx hardhat run scripts/verify.ts --network etherlink
 */
async function main() {
  const vaultAddress = process.env.VAULT_ADDRESS?.toLowerCase();
  const assetAddress = process.env.WXTZ_ADDRESS?.toLowerCase();

  if (!vaultAddress || !assetAddress) {
    throw new Error("❌ Missing VAULT_ADDRESS or WXTZ_ADDRESS in .env");
  }

  const name = "Arbitrage Vault";
  const symbol = "vXTZ";

  console.log(`🔍 Verifying contract at ${vaultAddress}...`);

  try {
    await run("verify:verify", {
      address: vaultAddress,
      constructorArguments: [assetAddress, name, symbol],
    });
    console.log("✅ Contract verified successfully!");
  } catch (error: any) {
    if (error.message.toLowerCase().includes("already verified")) {
      console.log("ℹ️  Contract is already verified.");
    } else {
      console.error("❌ Verification failed:", error);
    }
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
