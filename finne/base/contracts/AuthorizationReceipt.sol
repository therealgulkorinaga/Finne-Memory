// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

/// @title AuthorizationReceipt
/// @notice Records a Finné Memory authorization decision as verifiable
/// onchain evidence. Moves no funds and holds no balance: authorizedAmount
/// is a policy value (e.g. 6-decimal USDC units), never a transfer, and
/// every call is non-payable — msg.value must be zero, per
/// PREREQ-003 section 11 ("every demonstration transaction carries zero
/// value").
contract AuthorizationReceipt {
    struct Receipt {
        uint256 authorizedAmount;
        bytes32 factsHash;
        address submittedBy;
        uint256 recordedAt;
    }

    /// @dev The only address ever permitted to record an authorization —
    /// the deployer, i.e. Finné Memory's own demo wallet (the same key
    /// finne/base/adapter.py signs with). Without this, independent
    /// review found any third party could permanently record any
    /// predictable decisionId (decisionId = keccak256(decision_version_id),
    /// and decision_version_id values like "DV-001-V1" are fixed,
    /// public strings in this repository's own source) with arbitrary
    /// data — preempting a real authorization before this project's own
    /// session1.py/session2.py ever runs, or creating misleading
    /// "evidence" a reader might mistake for genuine.
    address public immutable authorizedSigner;

    /// @dev decisionId => whether it has already been recorded.
    /// Consulted before every write for onchain duplicate-execution
    /// protection (NEG-08), independent of and in addition to the
    /// application-level idempotency check in finne/base/adapter.py.
    mapping(bytes32 => bool) public recorded;

    mapping(bytes32 => Receipt) private _receipts;

    event AuthorizationRecorded(
        bytes32 indexed decisionId,
        uint256 authorizedAmount,
        bytes32 factsHash,
        address indexed submittedBy,
        uint256 recordedAt
    );

    constructor() {
        authorizedSigner = msg.sender;
    }

    /// @notice Records a single authorization. decisionId is expected to
    /// be keccak256(decision_version_id); factsHash binds the receipt to
    /// the exact material facts and cited precedents relied upon, so the
    /// stored record is verifiable evidence rather than a bare log line.
    /// Reverts if decisionId has already been recorded, or if the caller
    /// is not this contract's authorizedSigner.
    function recordAuthorization(
        bytes32 decisionId,
        uint256 authorizedAmount,
        bytes32 factsHash
    ) external {
        require(msg.sender == authorizedSigner, "AuthorizationReceipt: not the authorized signer");
        require(!recorded[decisionId], "AuthorizationReceipt: already recorded");
        recorded[decisionId] = true;
        _receipts[decisionId] = Receipt({
            authorizedAmount: authorizedAmount,
            factsHash: factsHash,
            submittedBy: msg.sender,
            recordedAt: block.timestamp
        });
        emit AuthorizationRecorded(decisionId, authorizedAmount, factsHash, msg.sender, block.timestamp);
    }

    /// @notice Reads back the stored receipt for a decisionId directly
    /// from contract storage (no event-log scanning required). Returns
    /// all-zero fields if nothing has been recorded yet — callers must
    /// check `recorded[decisionId]` (or `submittedBy != address(0)`)
    /// before trusting the result as a real receipt.
    function getReceipt(bytes32 decisionId)
        external
        view
        returns (uint256 authorizedAmount, bytes32 factsHash, address submittedBy, uint256 recordedAt)
    {
        Receipt storage r = _receipts[decisionId];
        return (r.authorizedAmount, r.factsHash, r.submittedBy, r.recordedAt);
    }
}
