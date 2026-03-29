// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../interfaces/ISwapRouterV3.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract MockUniswapV3Router is ISwapRouterV3 {
    uint256 public multiplier = 110; 

    function setMultiplier(uint256 _multiplier) external {
        multiplier = _multiplier;
    }

    // Simple mock: swap with multiplier
    function exactInputSingle(ExactInputSingleParams calldata params) external override returns (uint256 amountOut) {
        IERC20(params.tokenIn).transferFrom(msg.sender, address(this), params.amountIn);
        
        amountOut = (params.amountIn * multiplier) / 100;
        
        IERC20(params.tokenOut).transfer(params.recipient, amountOut);
    }
}
