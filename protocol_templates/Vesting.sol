// Vesting.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/math/Math.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract TokenVesting is Ownable {
    IERC20 public immutable token;
    address public immutable beneficiary;
    uint64 public immutable duration;
    uint64 public immutable startTimestamp;
    uint256 public totalVestedAmount;
    uint256 public releasedAmount;

    event TokensReleased(address indexed beneficiary, uint256 amount);

    constructor(
        address tokenAddress,
        address beneficiaryAddress,
        uint64 vestingDurationSeconds,
        uint256 totalAmount
    ) Ownable(msg.sender) {
        require(totalAmount > 0, "Vesting amount must be greater than 0");
        token = IERC20(tokenAddress);
        beneficiary = beneficiaryAddress;
        duration = vestingDurationSeconds;
        startTimestamp = uint64(block.timestamp);
        totalVestedAmount = totalAmount;
    }

    function vestedAmount() public view returns (uint256) {
        uint256 currentTime = uint256(block.timestamp);
        if (currentTime < startTimestamp) {
            return 0;
        }
        uint256 elapsedTime = currentTime - startTimestamp;
        if (elapsedTime >= duration) {
            return totalVestedAmount;
        }
        return Math.mulDiv(totalVestedAmount, elapsedTime, duration);
    }

    function release() public {
        uint256 releasable = vestedAmount() - releasedAmount;
        require(releasable > 0, "No tokens to release");
        
        releasedAmount += releasable;
        token.transfer(beneficiary, releasable);
        
        emit TokensReleased(beneficiary, releasable);
    }
}