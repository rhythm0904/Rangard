/**
 * contracts/scripts/deploy.js
 * ────────────────────────────
 * Deploys FileRegistry.sol to Ethereum.
 *
 * Run: npx hardhat run scripts/deploy.js --network sepolia
 *
 * After deployment, copy the printed address to your .env:
 *   CONTRACT_ADDRESS=0x...
 */

const { ethers } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();

  console.log("Deploying FileRegistry...");
  console.log("Deployer address:", deployer.address);

  const balance = await deployer.provider.getBalance(deployer.address);
  console.log("Deployer balance:", ethers.formatEther(balance), "ETH");

  const FileRegistry = await ethers.getContractFactory("FileRegistry");
  const contract = await FileRegistry.deploy();

  await contract.waitForDeployment();
  const address = await contract.getAddress();

  console.log("\n✅ FileRegistry deployed!");
  console.log("Contract address:", address);
  console.log("\nAdd this to your .env:");
  console.log(`CONTRACT_ADDRESS=${address}`);
  console.log("\nView on Etherscan:");
  console.log(`https://sepolia.etherscan.io/address/${address}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
