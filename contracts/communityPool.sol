// mission: fundraise a community prize pool for all eligible Jammer teams to claim their automatic prize
// stretch 1: nft for all contributors to the community prize pool of over 500$ in eth using chainlink
// stretch 2: allow tippi to mint nfts to specific addresses by sending in only 250$ in eth because he wrote the contract
// stretch 3: allow tippi to input final community votes from offchain voting, and all contributors to distribute 5 votes to their favorite teams

// SPDX-License-Identifier: MIT
pragma solidity 0.8.26;

import "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title CommunityPrizePool
 * @dev A contract for fundraising a community prize pool for Jammer teams
 */
contract CommunityPrizePool is ERC721, Ownable {
    AggregatorV3Interface private ethUsdPriceFeed;
    uint256 public constant MINIMUM_CONTRIBUTION = 500 * 10**18; // 500 USD in wei
    uint256 public constant TIPPI_CONTRIBUTION = 250 * 10**18; // 250 USD in wei
    uint256 public prizePool;
    mapping(address => bool) public eligibleTeams;
    mapping(address => bool) public hasClaimedPrize;
    uint256 private _nextTokenId;

    event ContributionMade(address contributor, uint256 amount);
    event PrizeClaimed(address team, uint256 amount);
    event TeamAdded(address team);

    constructor(address _priceFeedAddress, address initialOwner) ERC721("CommunityPoolContributor", "CPC") Ownable(initialOwner) {
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
    }

    function contribute() external payable {
        require(msg.value > 0, "Contribution must be greater than 0");
        uint256 contributionInUsd = getConversionRate(msg.value);
        require(contributionInUsd >= MINIMUM_CONTRIBUTION, "Contribution must be at least 500 USD");

        prizePool += msg.value;
        _mintNFT(msg.sender);

        emit ContributionMade(msg.sender, msg.value);
    }

    function contributeAsTippi() external payable onlyOwner {
        require(msg.value > 0, "Contribution must be greater than 0");
        uint256 contributionInUsd = getConversionRate(msg.value);
        require(contributionInUsd >= TIPPI_CONTRIBUTION, "Tippi's contribution must be at least 250 USD");

        prizePool += msg.value;
        _mintNFT(msg.sender);

        emit ContributionMade(msg.sender, msg.value);
    }

    function addEligibleTeam(address _team) external onlyOwner {
        require(!eligibleTeams[_team], "Team already eligible");
        eligibleTeams[_team] = true;
        emit TeamAdded(_team);
    }

    function claimPrize() external {
        require(eligibleTeams[msg.sender], "Team is not eligible");
        require(!hasClaimedPrize[msg.sender], "Prize already claimed");

        uint256 prizeAmount = prizePool / getEligibleTeamCount();
        hasClaimedPrize[msg.sender] = true;

        (bool success, ) = msg.sender.call{value: prizeAmount}("");
        require(success, "Transfer failed");

        emit PrizeClaimed(msg.sender, prizeAmount);
    }

    function getConversionRate(uint256 ethAmount) public view returns (uint256) {
        (, int256 price, , , ) = ethUsdPriceFeed.latestRoundData();
        uint256 ethPrice = uint256(price) * 10**10; // Adjust for decimals
        return (ethAmount * ethPrice) / 10**18;
    }

    function getEligibleTeamCount() public view returns (uint256) {
        uint256 count = 0;
        for (uint256 i = 0; i < getTeamAddresses().length; i++) {
            if (eligibleTeams[getTeamAddresses()[i]] && !hasClaimedPrize[getTeamAddresses()[i]]) {
                count++;
            }
        }
        return count;
    }

    function getTeamAddresses() public view returns (address[] memory) {
        // This function should be implemented to return all team addresses
        // For simplicity, we're returning an empty array here
        return new address[](0);
    }

    function _mintNFT(address recipient) private {
        uint256 newTokenId = _nextTokenId++;
        _safeMint(recipient, newTokenId);
    }

    function withdrawRemainingFunds() external onlyOwner {
        require(getEligibleTeamCount() == 0, "Not all teams have claimed their prizes");
        uint256 remainingBalance = address(this).balance;
        (bool success, ) = owner().call{value: remainingBalance}("");
        require(success, "Transfer failed");
    }
}
