// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/extensions/ERC4626.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

interface IDexRouter {
    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts);
}

/**
 * @title ArbitrageVault
 * @dev ERC-4626 yield-bearing vault where deposits are autonomously managed by
 * an OpenClaw AI Strategist. The Strategist can execute arbitrage swaps across
 * whitelisted Etherlink DEXs but can NEVER withdraw the principal capital.
 */
contract ArbitrageVault is ERC4626, AccessControl, ReentrancyGuard {
    using SafeERC20 for IERC20;

    bytes32 public constant STRATEGIST_ROLE = keccak256("STRATEGIST_ROLE");
    
    // Mapping of whitelisted DEX routers the agent is allowed to interact with
    mapping(address => bool) public whitelistedDexes;

    event ArbitrageExecuted(
        address indexed strategist,
        address indexed dexBuy,
        address indexed dexSell,
        address tokenTrade,
        uint256 profit
    );

    event DexWhitelisted(address indexed dex, bool status);

    constructor(
        IERC20 asset,
        string memory name,
        string memory symbol
    ) ERC4626(asset) ERC20(name, symbol) {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    /**
     * @dev Admin function to whitelist or blacklist an Etherlink DEX router.
     */
    function setWhitelistedDex(address dex, bool status) external onlyRole(DEFAULT_ADMIN_ROLE) {
        whitelistedDexes[dex] = status;
        emit DexWhitelisted(dex, status);
    }

    /**
     * @dev Core function called by the OpenClaw Agent.
     * Enforces that the trade strictly increases the Vault's totalAssets().
     *
     * @param dexBuy     Address of the router to buy the intermediate token
     * @param dexSell    Address of the router to sell the intermediate token
     * @param tokenTrade Address of the intermediate token (e.g. WXTZ)
     * @param amountBase Amount of the Vault's underlying asset (e.g. USDC) to use in the trade
     */
    function executeArbitrage(
        address dexBuy,
        address dexSell,
        address tokenTrade,
        uint256 amountBase
    ) external onlyRole(STRATEGIST_ROLE) nonReentrant {
        require(whitelistedDexes[dexBuy], "DEX Buy not whitelisted");
        require(whitelistedDexes[dexSell], "DEX Sell not whitelisted");
        require(amountBase > 0, "Zero amount");

        address assetAddress = asset();
        uint256 initialAssets = totalAssets();
        require(initialAssets >= amountBase, "Insufficient vault liquidity");

        // 1. Approve Buy DEX
        IERC20(assetAddress).safeIncreaseAllowance(dexBuy, amountBase);

        // Define Path for Swap 1: Asset -> TokenTrade
        address[] memory pathBuy = new address[](2);
        pathBuy[0] = assetAddress;
        pathBuy[1] = tokenTrade;

        // Execute Swap 1
        uint256[] memory amountsBuy = IDexRouter(dexBuy).swapExactTokensForTokens(
            amountBase,
            0, // Min out calculated by AI off-chain, but enforced by total check at the end
            pathBuy,
            address(this),
            block.timestamp
        );
        uint256 tokensReceived = amountsBuy[1];

        // 2. Approve Sell DEX
        IERC20(tokenTrade).safeIncreaseAllowance(dexSell, tokensReceived);

        // Define Path for Swap 2: TokenTrade -> Asset
        address[] memory pathSell = new address[](2);
        pathSell[0] = tokenTrade;
        pathSell[1] = assetAddress;

        // Execute Swap 2
        IDexRouter(dexSell).swapExactTokensForTokens(
            tokensReceived,
            0,
            pathSell,
            address(this),
            block.timestamp
        );

        // 3. Mathematical Safety Enforcement
        // The transaction MUST strictly increase the vault's net balance of the base asset.
        uint256 finalAssets = totalAssets();
        require(finalAssets > initialAssets, "Arbitrage unprofitable, reverting");

        uint256 profit = finalAssets - initialAssets;

        emit ArbitrageExecuted(msg.sender, dexBuy, dexSell, tokenTrade, profit);
    }

    /**
     * @dev Standard ERC-4626 deposit function.
     * Users can deposit the base asset and receive vault shares.
     */
    function deposit(uint256 assets, address receiver) public virtual override returns (uint256) {
        return super.deposit(assets, receiver);
    }

    /**
     * @dev Standard ERC-4626 withdraw function.
     * Users can withdraw their principal and profits by burning shares.
     */
    function withdraw(uint256 assets, address receiver, address owner) public virtual override returns (uint256) {
        return super.withdraw(assets, receiver, owner);
    }

    /**
     * @dev Prevents Strategist from withdrawing directly.
     * Handled implicitly by extending ERC4626, where the standard withdraw/redeem
     * functions strictly burn shares belonging to the owner.
     */
}
