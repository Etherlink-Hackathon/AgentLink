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
import "./interfaces/IUniversalRouter.sol";

/**
 * @title ArbitrageVault
 * @dev ERC-4626 yield-bearing vault where deposits are autonomously managed by
 * an OpenClaw AI Strategist. Now supports multiple DEX types on Etherlink.
 */
contract ArbitrageVault is ERC4626, AccessControl, ReentrancyGuard {
    using SafeERC20 for IERC20;

    enum DexType { UNISWAP_V2, UNISWAP_V3, CURVE, UNIVERSAL_ROUTER, CURVE_V2 }

    struct SwapStep {
        address dex;
        DexType dexType;
        address tokenIn;
        address tokenOut;
        bytes data;
    }

    bytes32 public constant STRATEGIST_ROLE = keccak256("STRATEGIST_ROLE");
    
    // Toggle for testing Arbitrage flow on Mainnet without profitability constraints
    bool public isTestMode = false;

    // Mapping of whitelisted DEX routers/pools
    mapping(address => bool) public whitelistedDexes;


    event MultiHopArbitrageExecuted(
        address indexed strategist,
        address[] route,
        address[] pools,
        uint256 hops,
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
     * @dev Admin function to enable or disable the profitability safeguard for testing.
     */
    function setTestMode(bool _mode) external onlyRole(DEFAULT_ADMIN_ROLE) {
        isTestMode = _mode;
    }

    /**
     * @dev Core function for multi-hop triangular arbitrage.
     * @param steps             Array of swap instructions
     * @param amountIn          Input amount of the vault's asset
     * @param minExpectedProfit Minimum profit safeguard
     */
    function executeMultiHop(
        SwapStep[] calldata steps,
        uint256 amountIn,
        uint256 minExpectedProfit
    ) external onlyRole(STRATEGIST_ROLE) nonReentrant {
        _executeMultiHop(steps, amountIn, minExpectedProfit);
    }

    /**
     * @dev Internal implementation shared by multi-hop and legacy wrappers.
     */
    function _executeMultiHop(
        SwapStep[] memory steps,
        uint256 amountIn,
        uint256 minExpectedProfit
    ) internal {
        require(steps.length > 0, "No steps provided");
        require(amountIn > 0, "Zero amount");

        address baseAsset = asset();
        uint256 initialAssets = totalAssets();
        require(initialAssets >= amountIn, "Insufficient vault liquidity");

        // Safety: ensure cycle starts and ends with base asset
        require(steps[0].tokenIn == baseAsset, "Must start with base asset");
        require(steps[steps.length - 1].tokenOut == baseAsset, "Must end with base asset");

        uint256 currentAmount = amountIn;
        address[] memory route = new address[](steps.length + 1);
        address[] memory pools = new address[](steps.length);
        route[0] = steps[0].tokenIn;

        for (uint256 i = 0; i < steps.length; i++) {
            SwapStep memory step = steps[i];
            require(whitelistedDexes[step.dex], "DEX not whitelisted");

            // Handle Allowance (standard logic)
            if (IERC20(step.tokenIn).allowance(address(this), step.dex) < currentAmount) {
                IERC20(step.tokenIn).approve(step.dex, type(uint256).max);
            }

            // Perform individual leg
            currentAmount = _performSwap(
                step.dex,
                step.dexType,
                step.tokenIn,
                step.tokenOut,
                currentAmount,
                step.data
            );

            // Record route and pools
            route[i + 1] = step.tokenOut;
            pools[i] = step.dex;
        }

        uint256 finalAssets = totalAssets();
        require(finalAssets >= initialAssets + minExpectedProfit || isTestMode, "Arbitrage Unprofitable");

        uint256 profit = finalAssets > initialAssets ? finalAssets - initialAssets : 0;
        emit MultiHopArbitrageExecuted(msg.sender, route, pools, steps.length, profit);
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
        bytes memory dexData
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
                amountIn: amountIn,
                amountOutMinimum: 0,
                sqrtPriceLimitX96: sqrtPriceLimitX96
            }));
        } else if (dexType == DexType.CURVE) {
            (int128 i, int128 j) = abi.decode(dexData, (int128, int128));
            ICurvePool(dex).exchange(i, j, amountIn, 0);
        } else if (dexType == DexType.UNIVERSAL_ROUTER) {
            (bytes memory commands, bytes[] memory inputs) = abi.decode(dexData, (bytes, bytes[]));
            
            // 1. If payload says amount is "0", inject the actual amount received from leg 1
            // This protects against slippage and is the "Hardened" way to handle UR.
            if (commands.length > 0 && uint8(commands[0]) == 0x00) { // V3_SWAP_EXACT_IN
                _injectURAmount(inputs[0], amountIn);
            }

            // 2. Transfer tokens to Router (UR requires this for payerIsUser = false)
            IERC20(tokenIn).safeTransfer(dex, amountIn);
            
            // 3. Execute
            IUniversalRouter(dex).execute(commands, inputs, block.timestamp);
        } else if (dexType == DexType.CURVE_V2) {
            (uint256 i, uint256 j) = abi.decode(dexData, (uint256, uint256));
            ICurvePool(dex).exchange(i, j, amountIn, 0);
        }

        return IERC20(tokenOut).balanceOf(address(this)) - balanceBefore;
    }

    /**
     * @dev Safely injects the actual amountIn into a V3_SWAP_EXACT_IN payload.
     * This avoids complex off-chain re-encoding when slippage occurs between legs.
     */
    function _injectURAmount(bytes memory input, uint256 amount) internal pure {
        // Standard V3_SWAP_EXACT_IN (address, uint256, uint256, bytes, bool) is 160+ bytes
        require(input.length >= 160, "Input too short for V3 injection");
        assembly {
            // Memory layout of bytes memory: [32B length][32B address][32B amountIn]...
            // mstore(add(input, 64), amount) targets the second 32-byte word of the data.
            mstore(add(input, 64), amount) 
        }
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
