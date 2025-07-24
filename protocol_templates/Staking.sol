// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title StakingContract
 * @dev A simple contract for staking a specific ERC20 token to earn rewards.
 * TEMPLATE-PLACEHOLDERS:
 * - STAKING_TOKEN_ADDRESS: The address of the ERC20 token to be staked (e.g., BDAG).
 * - REWARD_TOKEN_ADDRESS: The address of the token given as a reward.
 * - REWARD_RATE_PER_SECOND: The amount of reward tokens distributed per second to all stakers, proportional to their stake.
 */
contract StakingContract is Ownable {
    IERC20 public stakingToken;
    IERC20 public rewardToken;

    // Placeholder: This will be replaced by the AI.
    uint256 public constant REWARD_RATE_PER_SECOND = 10000000000000; // Example: 0.00001 tokens/sec

    mapping(address => uint256) public stakedBalance;
    mapping(address => uint256) public rewards;
    mapping(address => uint256) public lastUpdateTime;
    
    uint256 public totalStaked;

    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount);
    event RewardPaid(address indexed user, uint256 reward);

    constructor(address _stakingTokenAddress, address _rewardTokenAddress) Ownable(msg.sender) {
        // Placeholder: The AI should modify this constructor if needed,
        // or replace these addresses directly in the code.
        stakingToken = IERC20(_stakingTokenAddress);
        rewardToken = IERC20(_rewardTokenAddress);
    }

    function calculateReward(address _user) public view returns (uint256) {
        uint256 timeElapsed = block.timestamp - lastUpdateTime[_user];
        if (totalStaked == 0) return 0;
        return (stakedBalance[_user] * timeElapsed * REWARD_RATE_PER_SECOND) / totalStaked;
    }

    function stake(uint256 _amount) external {
        require(_amount > 0, "Cannot stake 0");
        updateRewards(msg.sender);
        
        stakingToken.transferFrom(msg.sender, address(this), _amount);
        stakedBalance[msg.sender] += _amount;
        totalStaked += _amount;
        
        emit Staked(msg.sender, _amount);
    }

    function unstake(uint256 _amount) external {
        require(stakedBalance[msg.sender] >= _amount, "Insufficient staked balance");
        updateRewards(msg.sender);
        
        stakedBalance[msg.sender] -= _amount;
        totalStaked -= _amount;
        stakingToken.transfer(msg.sender, _amount);
        
        emit Unstaked(msg.sender, _amount);
    }

    function claimReward() external {
        updateRewards(msg.sender);
        uint256 reward = rewards[msg.sender];
        if (reward > 0) {
            rewards[msg.sender] = 0;
            rewardToken.transfer(msg.sender, reward);
            emit RewardPaid(msg.sender, reward);
        }
    }

    function updateRewards(address _user) internal {
        rewards[_user] += calculateReward(_user);
        lastUpdateTime[_user] = block.timestamp;
    }

    // Function for the owner to fund the contract with reward tokens.
    function fundRewardTokens(uint256 _amount) external onlyOwner {
        require(_amount > 0, "Cannot fund with 0 tokens");
        rewardToken.transferFrom(msg.sender, address(this), _amount);
    }
}