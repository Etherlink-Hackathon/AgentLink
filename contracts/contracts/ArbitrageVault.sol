// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/extensions/ERC4626.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

import "./interfaces/IDexRouter.sol";
import "./interfaces/ISwapRouterV3.sol";
import "./interfaces/ICurvePool.sol";

/**
 * @title ArbitrageVault
 * @dev ERC-4626 yield-bearing vault where deposits are autonomously managed by
 * an OpenClaw AI Strategist. Now supports multiple DEX types on Etherlink.
 */
contract ArbitrageVault is ERC4626, AccessControl, ReentrancyGuard {
    using SafeERC20 for IERC20;

    enum DexType { UNISWAP_V2, UNISWAP_V3, CURVE }

    bytes32 public constant STRATEGIST_ROLE = keccak256("STRATEGIST_ROLE");
    
    // Mapping of whitelisted DEX routers/pools
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
     * @dev Admin function to whitelist or blacklist a DEX.
     */
    function setWhitelistedDex(address dex, bool status) external onlyRole(DEFAULT_ADMIN_ROLE) {
        whitelistedDexes[dex] = status;
        emit DexWhitelisted(dex, status);
    }

    /**
     * @dev Core function called by the OpenClaw Agent.
     * Enforces that the trade strictly increases the Vault's totalAssets().
     *
     * @param dexBuy           Address of the router/pool to buy the intermediate token
     * @param typeBuy          Type of DEX for the buy leg
     * @param dataBuy          DEX-specific encoded data (e.g. fee for V3, indices for Curve)
     * @param dexSell          Address of the router/pool to sell the intermediate token
     * @param typeSell         Type of DEX for the sell leg
     * @param dataSell         DEX-specific encoded data
     * @param intermediateToken Address of the token to trade against the base asset
     * @param amountBase       Amount of the Vault's underlying asset to use
     */
    function executeArbitrage(
        address dexBuy,
        DexType typeBuy,
        bytes calldata dataBuy,
        address dexSell,
        DexType typeSell,
        bytes calldata dataSell,
        address intermediateToken,
        uint256 amountBase
    ) external onlyRole(STRATEGIST_ROLE) nonReentrant {
        require(whitelistedDexes[dexBuy], "DEX Buy not whitelisted");
        require(whitelistedDexes[dexSell], "DEX Sell not whitelisted");
        require(amountBase > 0, "Zero amount");

        address baseAsset = asset();
        uint256 initialAssets = totalAssets();
        require(initialAssets >= amountBase, "Insufficient vault liquidity");

        // 1. Swap Leg 1: Base Asset -> Intermediate Token
        IERC20(baseAsset).safeIncreaseAllowance(dexBuy, amountBase);
        uint256 tokensReceived = _performSwap(
            dexBuy,
            typeBuy,
            baseAsset,
            intermediateToken,
            amountBase,
            dataBuy
        );
        require(tokensReceived > 0, "First swap failed");

        // 2. Swap Leg 2: Intermediate Token -> Base Asset
        IERC20(intermediateToken).safeIncreaseAllowance(dexSell, tokensReceived);
        _performSwap(
            dexSell,
            typeSell,
            intermediateToken,
            baseAsset,
            tokensReceived,
            dataSell
        );

        // 3. Mathematical Safety Enforcement
        uint256 finalAssets = totalAssets();
        require(finalAssets > initialAssets, "Arbitrage unprofitable, reverting");

        uint256 profit = finalAssets - initialAssets;
        emit ArbitrageExecuted(msg.sender, dexBuy, dexSell, intermediateToken, profit);
    }

    /**
     * @dev Internal helper to route swaps to different DEX types.
     */
    function _performSwap(
        address dex,
        DexType dexType,
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        bytes calldata dexData
    ) internal returns (uint256) {
        uint256 balanceBefore = IERC20(tokenOut).balanceOf(address(this));

        if (dexType == DexType.UNISWAP_V2) {
            address[] memory path = new address[](2);
            path[0] = tokenIn;
            path[1] = tokenOut;
            // Existing V2 interface
            IDexRouter(dex).swapExactTokensForTokens(
                amountIn,
                0, // Min out enforced by final totalAssets() check
                path,
                address(this),
                block.timestamp
            );
        } else if (dexType == DexType.UNISWAP_V3) {
            (uint24 fee, uint160 sqrtPriceLimitX96) = abi.decode(dexData, (uint24, uint160));
            ISwapRouterV3(dex).exactInputSingle(ExactInputSingleParams({
                tokenIn: tokenIn,
                tokenOut: tokenOut,
                fee: fee,
                recipient: address(this),
                deadline: block.timestamp,
                amountIn: amountIn,
                amountOutMinimum: 0,
                sqrtPriceLimitX96: sqrtPriceLimitX96
            }));
        } else if (dexType == DexType.CURVE) {
            (int128 i, int128 j) = abi.decode(dexData, (int128, int128));
            ICurvePool(dex).exchange(i, j, amountIn, 0);
        }

        return IERC20(tokenOut).balanceOf(address(this)) - balanceBefore;
    }

    /**
     * @dev Standard ERC-4626 deposit function.
     */
    function deposit(uint256 assets, address receiver) public virtual override returns (uint256) {
        return super.deposit(assets, receiver);
    }

    /**
     * @dev Standard ERC-4626 withdraw function.
     */
    function withdraw(uint256 assets, address receiver, address owner) public virtual override returns (uint256) {
        return super.withdraw(assets, receiver, owner);
    }
}
