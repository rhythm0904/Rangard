"""
app/blockchain/service.py
─────────────────────────
Ethereum blockchain integration for immutable file versioning.

WHAT THIS DOES (plain English):
────────────────────────────────
When a file is scanned and stored, we "anchor" its SHA-256 hash to the
Ethereum blockchain.  This means:
  1. We call a smart contract function that stores (fileHash → timestamp)
  2. The transaction is recorded permanently in Ethereum's history
  3. Later, anyone can verify a file hasn't been tampered with by:
     a. Computing the file's current SHA-256
     b. Checking if that hash exists in the blockchain record
     c. If it matches: file is authentic.  If not: file was altered.

This is the core "blockchain-backed file versioning" feature.

DEVELOPMENT MODE:
─────────────────
If Infura credentials aren't configured, the service runs in DEMO MODE —
it generates fake but realistic-looking tx hashes.  Your code paths stay
identical whether you're in demo or production mode.
"""

import hashlib
import os
import time
from dataclasses import dataclass
from typing import Optional

from app.core.config import get_settings

settings = get_settings()

# We import web3 lazily to avoid crashing if it's not installed
try:
    from web3 import Web3
    from web3.exceptions import ContractLogicError
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False


# ── Smart contract ABI ────────────────────────────────────────────────────────
# This is the interface to our deployed Solidity contract.
# The full contract source is in contracts/FileRegistry.sol

FILE_REGISTRY_ABI = [
    {
        "inputs": [
            {"internalType": "bytes32", "name": "fileHash",  "type": "bytes32"},
            {"internalType": "string",  "name": "ipfsCid",   "type": "string"},
            {"internalType": "uint256", "name": "version",   "type": "uint256"},
        ],
        "name": "registerFile",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "fileHash", "type": "bytes32"},
        ],
        "name": "getFile",
        "outputs": [
            {"internalType": "address", "name": "owner",     "type": "address"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"internalType": "string",  "name": "ipfsCid",   "type": "string"},
            {"internalType": "uint256", "name": "version",   "type": "uint256"},
            {"internalType": "bool",    "name": "exists",    "type": "bool"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
]


# ── Result dataclass ──────────────────────────────────────────────────────────

@dataclass
class AnchorResult:
    success: bool
    tx_hash: str
    block_number: Optional[int]
    gas_used: Optional[int]
    network: str
    demo_mode: bool
    error: Optional[str] = None


# ── Service class ─────────────────────────────────────────────────────────────

class BlockchainService:

    def __init__(self):
        self.w3: Optional[object] = None
        self.contract = None
        self.demo_mode = True
        self._connect()

    def _connect(self):
        """Attempt to connect to Ethereum via Infura."""
        if not WEB3_AVAILABLE:
            print("[Blockchain] web3 not installed — running in demo mode")
            return

        if not settings.INFURA_PROJECT_ID or settings.INFURA_PROJECT_ID == "your_infura_project_id_here":
            print("[Blockchain] No Infura credentials — running in demo mode")
            return

        try:
            self.w3 = Web3(Web3.HTTPProvider(settings.infura_rpc_url))
            if not self.w3.is_connected():
                print("[Blockchain] Could not connect to Infura — running in demo mode")
                self.w3 = None
                return

            # Only load contract if we have a real address
            if (settings.CONTRACT_ADDRESS and
                    settings.CONTRACT_ADDRESS != "0x0000000000000000000000000000000000000000"):
                self.contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(settings.CONTRACT_ADDRESS),
                    abi=FILE_REGISTRY_ABI,
                )

            self.demo_mode = False
            print(f"[Blockchain] Connected to Ethereum ({settings.ETHEREUM_NETWORK})")

        except Exception as e:
            print(f"[Blockchain] Connection error: {e} — running in demo mode")
            self.w3 = None

    def _demo_anchor(self, file_hash: str) -> AnchorResult:
        """
        Return a realistic-looking but fake result for development.
        Useful for testing the full pipeline without real ETH.
        """
        # Generate a deterministic fake tx hash from the file hash + time
        fake_seed = f"{file_hash}{time.time()}".encode()
        fake_tx = "0x" + hashlib.sha256(fake_seed).hexdigest()
        fake_block = 19_000_000 + int(time.time()) % 1_000_000

        return AnchorResult(
            success=True,
            tx_hash=fake_tx,
            block_number=fake_block,
            gas_used=52_000,
            network=settings.ETHEREUM_NETWORK,
            demo_mode=True,
        )

    def anchor_file(
        self,
        file_hash: str,
        ipfs_cid: str = "",
        version: int = 1,
    ) -> AnchorResult:
        """
        Anchor a file hash to the Ethereum blockchain.

        Args:
            file_hash: SHA-256 hex string of the file
            ipfs_cid:  IPFS content identifier (optional)
            version:   File version number (increment to track history)

        Returns:
            AnchorResult with transaction details
        """
        if self.demo_mode or self.contract is None:
            return self._demo_anchor(file_hash)

        try:
            # Convert hex hash to bytes32 for Solidity
            hash_bytes32 = bytes.fromhex(file_hash)

            # Load the wallet
            account = self.w3.eth.account.from_key(settings.WALLET_PRIVATE_KEY)

            # Estimate gas to avoid running out
            gas_estimate = self.contract.functions.registerFile(
                hash_bytes32, ipfs_cid, version
            ).estimate_gas({"from": account.address})

            # Build the transaction
            tx = self.contract.functions.registerFile(
                hash_bytes32, ipfs_cid, version
            ).build_transaction({
                "from":  account.address,
                "gas":   int(gas_estimate * 1.2),  # 20% buffer
                "nonce": self.w3.eth.get_transaction_count(account.address),
                "maxFeePerGas": self.w3.eth.gas_price * 2,
                "maxPriorityFeePerGas": self.w3.to_wei("2", "gwei"),
            })

            # Sign and send
            signed = account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)

            # Wait for confirmation (up to 120s)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            return AnchorResult(
                success=receipt.status == 1,
                tx_hash=tx_hash.hex(),
                block_number=receipt.blockNumber,
                gas_used=receipt.gasUsed,
                network=settings.ETHEREUM_NETWORK,
                demo_mode=False,
            )

        except Exception as e:
            return AnchorResult(
                success=False,
                tx_hash="",
                block_number=None,
                gas_used=None,
                network=settings.ETHEREUM_NETWORK,
                demo_mode=False,
                error=str(e),
            )

    def verify_file(self, file_hash: str) -> dict:
        """
        Check if a file hash exists on-chain and return its metadata.
        Returns dict with: exists, owner, timestamp, ipfs_cid, version
        """
        if self.demo_mode or self.contract is None:
            return {
                "exists": True,
                "owner": "0xDEMO000000000000000000000000000000000000",
                "timestamp": int(time.time()) - 3600,
                "ipfs_cid": "",
                "version": 1,
                "demo_mode": True,
            }

        try:
            hash_bytes32 = bytes.fromhex(file_hash)
            result = self.contract.functions.getFile(hash_bytes32).call()
            owner, timestamp, ipfs_cid, version, exists = result
            return {
                "exists": exists,
                "owner": owner,
                "timestamp": timestamp,
                "ipfs_cid": ipfs_cid,
                "version": version,
                "demo_mode": False,
            }
        except Exception as e:
            return {"exists": False, "error": str(e), "demo_mode": False}


# ── Singleton ─────────────────────────────────────────────────────────────────

_blockchain_service: Optional[BlockchainService] = None

def get_blockchain_service() -> BlockchainService:
    global _blockchain_service
    if _blockchain_service is None:
        _blockchain_service = BlockchainService()
    return _blockchain_service
