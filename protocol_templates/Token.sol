// Token.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyToken is ERC20, Ownable {
    // TEMPLATE-PLACEHOLDERS:
    // - TOKEN_NAME: The name of the token (e.g., "My Coin").
    // - TOKEN_SYMBOL: The symbol of the token (e.g., "MYC").
    // - INITIAL_SUPPLY: The number of tokens to mint initially.

    constructor(string memory name, string memory symbol, uint256 initialSupply) ERC20(name, symbol) Ownable(msg.sender) {
        _mint(msg.sender, initialSupply * 10**decimals());
    }

    function mint(address to, uint256 amount) public onlyOwner {
        _mint(to, amount);
    }
}