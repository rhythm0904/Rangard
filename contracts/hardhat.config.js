/**
 * hardhat.config.js
 * ──────────────────
 * Hardhat configuration for compiling and deploying the FileRegistry contract.
 *
 * SETUP (run from the /contracts directory):
 *   npm install
 *   npx hardhat compile
 *
 * DEPLOY TO SEPOLIA TESTNET:
 *   1. Get free test ETH: https://sepoliafaucet.com
 *   2. Set WALLET_PRIVATE_KEY in your .env
 *   3. npx hardhat run scripts/deploy.js --network sepolia
 *   4. Copy the printed contract address to your .env CONTRACT_ADDRESS
 */

require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config({ path: "../.env" });

module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: { enabled: true, runs: 200 },
    },
  },
  networks: {
    // Local Hardhat node (for testing without real ETH)
    localhost: {
      url: "http://127.0.0.1:8545",
    },
    // Sepolia testnet (free, use test ETH from a faucet)
    sepolia: {
      url: `https://sepolia.infura.io/v3/${process.env.INFURA_PROJECT_ID}`,
      accounts: process.env.WALLET_PRIVATE_KEY
        ? [process.env.WALLET_PRIVATE_KEY]
        : [],
      gasMultiplier: 1.2,
    },
  },
  etherscan: {
    // Verify contract on Etherscan (optional but useful)
    apiKey: process.env.ETHERSCAN_API_KEY || "",
  },
};
