import { ethers, network, run } from "hardhat";
import * as fs from "fs";
import * as path from "path";
import * as dotenv from "dotenv";

async function main() {
    const [deployer] = await ethers.getSigners();
    console.log(`\n🚀 Starting Deployment on ${network.name.toUpperCase()}`);
    console.log(`👤 Deployer: ${deployer.address}`);
    
    const balance = await ethers.provider.getBalance(deployer.address);
    console.log(`💰 Balance: ${ethers.formatEther(balance)} XTZ\n`);

    // Configuration
    const ETHERLINK_WXTZ = "0xc9B53AB2679f573e480d01e0f49e2b5cfb7a3eab".toLowerCase();
    const VAULT_NAME = "Etherlink Arbitrage Vault";
    const VAULT_SYMBOL = "EAV";

    // 1. Deploy ArbitrageVault
    console.log(`🏗️  Deploying ArbitrageVault...`);
    const ArbitrageVault = await ethers.getContractFactory("ArbitrageVault");
    const vault = await ArbitrageVault.deploy(ETHERLINK_WXTZ, VAULT_NAME, VAULT_SYMBOL);
    
    await vault.waitForDeployment();
    const vaultAddress = await vault.getAddress();
    console.log(`✅ ArbitrageVault deployed to: ${vaultAddress}`);

    // 2. Grant Roles
    const STRATEGIST_ROLE = await vault.STRATEGIST_ROLE();
    await vault.grantRole(STRATEGIST_ROLE, deployer.address);
    console.log(`👤 STRATEGIST_ROLE granted to: ${deployer.address}`);

    // 3. Synchronization of ABIs
    const artifactPath = path.join(__dirname, "../artifacts/contracts/ArbitrageVault.sol/ArbitrageVault.json");
    const artifact = JSON.parse(fs.readFileSync(artifactPath, "utf8"));
    const abi = JSON.stringify(artifact.abi, null, 2);

    // Indexer ABI
    const indexerAbiDir = path.join(__dirname, "../../indexer/src/arbitrage_vault/abi/ArbitrageVault");
    if (!fs.existsSync(indexerAbiDir)) fs.mkdirSync(indexerAbiDir, { recursive: true });
    fs.writeFileSync(path.join(indexerAbiDir, "abi.json"), abi);
    console.log(`📄 Indexer ABI updated: ${path.relative(process.cwd(), indexerAbiDir)}`);

    // Frontend ABI
    const frontendAbiDir = path.join(__dirname, "../../frontend/src/abis");
    if (!fs.existsSync(frontendAbiDir)) fs.mkdirSync(frontendAbiDir, { recursive: true });
    fs.writeFileSync(path.join(frontendAbiDir, "ArbitrageVault.json"), abi);
    console.log(`📄 Frontend ABI updated: ${path.relative(process.cwd(), frontendAbiDir)}`);

    // 4. Update Environment Files (Sync Address)
    updateEnvFile(path.join(__dirname, "../.env"), "VAULT_ADDRESS", vaultAddress);
    updateEnvFile(path.join(__dirname, "../../indexer/.env"), "VAULT_ADDRESS", vaultAddress);

    // 5. Verification
    if (network.name === "etherlink") {
        console.log("\n📦 Starting contract verification...");
        console.log("⏱️  Waiting for 10 seconds for explorer to index...");
        await new Promise((resolve) => setTimeout(resolve, 10000));

        try {
            await run("verify:verify", {
                address: vaultAddress,
                constructorArguments: [ETHERLINK_WXTZ, VAULT_NAME, VAULT_SYMBOL],
                contract: "contracts/ArbitrageVault.sol:ArbitrageVault"
            });
            console.log("✅ Verification successful!");
        } catch (error) {
            console.error("❌ Verification failed:", error);
        }
    }

    console.log("\n✨ Deployment and project synchronization complete!");
}

function updateEnvFile(filePath: string, key: string, value: string) {
    if (!fs.existsSync(filePath)) {
        console.warn(`⚠️  Warning: ${filePath} not found. Skipping.`);
        return;
    }
    let content = fs.readFileSync(filePath, "utf8");
    const regex = new RegExp(`^${key}=.*`, "m");
    
    if (regex.test(content)) {
        content = content.replace(regex, `${key}=${value}`);
    } else {
        content += `\n${key}=${value}`;
    }
    
    fs.writeFileSync(filePath, content);
    console.log(`📝 Updated ${key} in: ${path.relative(process.cwd(), filePath)}`);
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
