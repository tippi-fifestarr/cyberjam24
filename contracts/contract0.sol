// SPDX-License-Identifier: MIT
pragma solidity 0.8.7;
/**
 * THIS IS AN EXAMPLE CONTRACT THAT USES UN-AUDITED CODE.
 * DO NOT USE THIS CODE IN PRODUCTION.
 */
contract HelloConductor {
    string public conductorName;

    constructor(string memory _initialConductor) {
        conductorName = _initialConductor;
    }

    function setConductor(string memory _newConductor) public {
        conductorName = _newConductor;
    }
}