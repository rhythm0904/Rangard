// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * FileRegistry.sol
 * ─────────────────
 * Immutable on-chain registry of file hashes.
 *
 * WHAT IT DOES:
 *   registerFile()  → stores (hash → owner, timestamp, IPFS CID, version)
 *   getFile()       → retrieves that record for verification
 *
 * DEPLOYMENT:
 *   1. Install Hardhat: npm install --save-dev hardhat
 *   2. Compile:  npx hardhat compile
 *   3. Deploy to Sepolia testnet: npx hardhat run scripts/deploy.js --network sepolia
 *   4. Copy the deployed address to your .env CONTRACT_ADDRESS
 *
 * COST: Each registerFile() call costs ~50,000 gas (~$0.05 on mainnet).
 * On Sepolia testnet it's free (use test ETH from a faucet).
 */

contract FileRegistry {

    struct FileRecord {
        address owner;
        uint256 timestamp;
        string  ipfsCid;
        uint256 version;
        bool    exists;
    }

    // fileHash (bytes32) → FileRecord
    mapping(bytes32 => FileRecord) private records;

    // Track all hashes per owner for history lookup
    mapping(address => bytes32[]) private ownerFiles;

    // ── Events ─────────────────────────────────────────────────────────
    // Events are emitted when transactions succeed.
    // Your backend can listen for these to update the DB.
    event FileRegistered(
        bytes32 indexed fileHash,
        address indexed owner,
        uint256 timestamp,
        string  ipfsCid,
        uint256 version
    );

    event FileUpdated(
        bytes32 indexed fileHash,
        address indexed owner,
        uint256 newVersion
    );

    // ── Register a new file or update an existing one ───────────────────
    function registerFile(
        bytes32 fileHash,
        string calldata ipfsCid,
        uint256 version
    ) external {
        require(fileHash != bytes32(0), "FileRegistry: empty hash");

        if (records[fileHash].exists) {
            // Update: only original owner can update their file
            require(
                records[fileHash].owner == msg.sender,
                "FileRegistry: not the file owner"
            );
            records[fileHash].ipfsCid   = ipfsCid;
            records[fileHash].version   = version;
            records[fileHash].timestamp = block.timestamp;
            emit FileUpdated(fileHash, msg.sender, version);
        } else {
            // New registration
            records[fileHash] = FileRecord({
                owner:     msg.sender,
                timestamp: block.timestamp,
                ipfsCid:   ipfsCid,
                version:   version,
                exists:    true
            });
            ownerFiles[msg.sender].push(fileHash);
            emit FileRegistered(fileHash, msg.sender, block.timestamp, ipfsCid, version);
        }
    }

    // ── Read a file record ──────────────────────────────────────────────
    function getFile(bytes32 fileHash)
        external
        view
        returns (
            address owner,
            uint256 timestamp,
            string memory ipfsCid,
            uint256 version,
            bool    exists
        )
    {
        FileRecord storage r = records[fileHash];
        return (r.owner, r.timestamp, r.ipfsCid, r.version, r.exists);
    }

    // ── Get all hashes registered by an address ─────────────────────────
    function getOwnerFiles(address owner)
        external
        view
        returns (bytes32[] memory)
    {
        return ownerFiles[owner];
    }

    // ── Verify a file hash matches the stored record ─────────────────────
    function verifyFile(bytes32 fileHash)
        external
        view
        returns (bool isRegistered, address owner, uint256 registeredAt)
    {
        FileRecord storage r = records[fileHash];
        return (r.exists, r.owner, r.timestamp);
    }
}
