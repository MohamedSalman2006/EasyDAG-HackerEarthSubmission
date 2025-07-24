const bdagAddress = "0x91792f96D2eF065486E31a3AB06726AB03f8194F"; // BDAG token
const WETH_ADDRESS = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"; // WETH Mainnet
const uniswapRouterAddress = "0xE592427A0AEce92De3Edee1F18E0157C05861564"; // Uniswap V3 Router

const web3 = new Web3(window.ethereum);

async function buyBDAG() {
  const ethAmount = document.getElementById("buyAmount").value;
  const accounts = await web3.eth.getAccounts();

  if (!ethAmount || isNaN(ethAmount)) {
    alert("Invalid amount");
    return;
  }

  const deadline = Math.floor(Date.now() / 1000) + 60 * 10; 

  const router = new web3.eth.Contract([
    {
      name: "exactInputSingle",
      type: "function",
      stateMutability: "payable",
      inputs: [
        {
          components: [
            { name: "tokenIn", type: "address" },
            { name: "tokenOut", type: "address" },
            { name: "fee", type: "uint24" },
            { name: "recipient", type: "address" },
            { name: "deadline", type: "uint256" },
            { name: "amountIn", type: "uint256" },
            { name: "amountOutMinimum", type: "uint256" },
            { name: "sqrtPriceLimitX96", type: "uint160" }
          ],
          name: "params",
          type: "tuple"
        }
      ],
      outputs: [{ name: "amountOut", type: "uint256" }]
    }
  ], uniswapRouterAddress);

  const params = {
    tokenIn: WETH_ADDRESS,
    tokenOut: bdagAddress,
    fee: 3000,
    recipient: accounts[0],
    deadline: deadline,
    amountIn: web3.utils.toWei(ethAmount, "ether"),
    amountOutMinimum: 0,
    sqrtPriceLimitX96: 0
  };

  try {
    await router.methods.exactInputSingle(params).send({
      from: accounts[0],
      value: web3.utils.toWei(ethAmount, "ether"), 
      gas: 300000
    });

    alert("Purchase complete!");
  } catch (err) {
    console.error(err);
    alert("Transaction failed: " + err.message);
  }
}

window.addEventListener("load", async () => {
  if (window.ethereum) {
    try {
      await window.ethereum.request({ method: "eth_requestAccounts" });
    } catch (err) {
      alert("MetaMask connection rejected.");
    }
  } else {
    alert("MetaMask not found");
  }
});

