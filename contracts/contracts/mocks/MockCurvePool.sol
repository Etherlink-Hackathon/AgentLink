// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../interfaces/ICurvePool.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract MockCurvePool is ICurvePool {
    address[] public coins;
    uint256 public multiplier = 110; 

    constructor(address _coin0, address _coin1) {
        coins.push(_coin0);
        coins.push(_coin1);
    }

    function setMultiplier(uint256 _multiplier) external {
        multiplier = _multiplier;
    }

    // Simple mock: swap with multiplier
    function exchange(int128 i, int128 j, uint256 dx, uint256 min_dy) external override returns (uint256 dy) {
        address tokenIn = coins[uint256(int256(i))];
        address tokenOut = coins[uint256(int256(j))];
        
        IERC20(tokenIn).transferFrom(msg.sender, address(this), dx);
        
        dy = (dx * multiplier) / 100;
        
        IERC20(tokenOut).transfer(msg.sender, dy);
    }

    // Curve V2 mock
    function exchange(uint256 i, uint256 j, uint256 dx, uint256 min_dy) external override returns (uint256 dy) {
        address tokenIn = coins[i];
        address tokenOut = coins[j];
        
        IERC20(tokenIn).transferFrom(msg.sender, address(this), dx);
        
        dy = (dx * multiplier) / 100;
        
        IERC20(tokenOut).transfer(msg.sender, dy);
    }
}
