import { ethers, network } from "hardhat";

async function main() {
    const [deployer] = await ethers.getSigners();
    console.log(`🚀 Deploying contracts with the account: ${deployer.address}`);

    let assetAddress = process.env.BASE_ASSET_ADDRESS;
    let name = "Arbitrage Vault";
    let symbol = "vXTZ";

    // Etherlink Mainnet WXTZ address
    const ETHERLINK_WXTZ = "0xc9B53AB2679f573e480d01e0f49e2b5cfb7a3eab";

    if (network.name === "etherlink") {
        assetAddress = ETHERLINK_WXTZ;
        console.log(`🔗 Using Etherlink Mainnet WXTZ: ${assetAddress}`);
    } else if (!assetAddress) {
        // Local or testnet: deploy a Mock WXTZ
        console.log("🛠️  No BASE_ASSET_ADDRESS found, deploying MockERC20 (WXTZ)...");
        const MockERC20 = await ethers.getContractFactory("MockERC20");
        const mockWXTZ = await MockERC20.deploy("Wrapped XTZ", "WXTZ");
        await mockWXTZ.waitForDeployment();
        assetAddress = await mockWXTZ.getAddress();
        console.log(`✅ Mock WXTZ deployed to: ${assetAddress}`);

        // Mint some to deployer for testing
        await mockWXTZ.mint(deployer.address, ethers.parseUnits("10000", 18));
    }

    // Deploy ArbitrageVault
    console.log(`🏗️  Deploying ArbitrageVault (${symbol})...`);
    const ArbitrageVault = await ethers.getContractFactory("ArbitrageVault");
    const vault = await ArbitrageVault.deploy(
        assetAddress!,
        name,
        symbol
    );
    await vault.waitForDeployment();
    const vaultAddress = await vault.getAddress();
    console.log(`✅ ArbitrageVault deployed to: ${vaultAddress}`);

    // Grant Strategist Role to deployer (for initial testing)
    const STRATEGIST_ROLE = await vault.STRATEGIST_ROLE();
    await vault.grantRole(STRATEGIST_ROLE, deployer.address);
    console.log(`👤 STRATEGIST_ROLE granted to: ${deployer.address}`);

    console.log("\n✨ Deployment Summary:");
    console.log(`- Network: ${network.name}`);
    console.log(`- Base Asset: ${assetAddress}`);
    console.log(`- Vault: ${vaultAddress}`);
    console.log(`- Admin/Strategist: ${deployer.address}`);
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
