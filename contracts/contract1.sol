// SPDX-License-Identifier: MIT

pragma solidity 0.8.7;

/**
 * THIS IS AN EXAMPLE CONTRACT THAT USES UN-AUDITED CODE.
 * DO NOT USE THIS CODE IN PRODUCTION.
 */

contract HelloWorldTrain {
    string public conductorName;
    uint128 public trainCount;

    struct Train {
        string conductor;
        uint16 passengers; // uint16, can store up to 65,535 passengers
    }

    mapping(uint128 => Train) public trains;

    constructor(string memory _itsTippi) {
        conductorName = _itsTippi;
        trains[0] = Train(conductorName, 55); // tippi rolls with mad homies
        trainCount = 1;
    }

    function addTrain(string memory _newConductor, uint16 _initialPassengers) public {
    string memory conductor;
    if (bytes(_newConductor).length > 0) {
        conductor = _newConductor;
    } else {
        conductor = conductorName;
    }
    trains[trainCount] = Train(conductor, _initialPassengers);
    trainCount++;
}

    function addPassenger(uint128 _trainId) public {
        require(_trainId < trainCount, "Train does not exist");
        require(trains[_trainId].passengers < type(uint16).max, "Train is full");
        trains[_trainId].passengers++;
    }
}

// quiz: can you find any vulnerablilites in this contract?
// hint: there are a lot of them