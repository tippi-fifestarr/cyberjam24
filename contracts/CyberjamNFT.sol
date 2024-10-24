// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

/**
 * @title Cyberjam 2024 Community Prize Pool and NFT Contracts.
 * @author Tippi Fifestarr
 * @notice This contract suite is designed for Cyberjam 2024, a unique hackathon that brings together 
 * artists, technologists, and innovators to create immersive "phygital" (physical + digital) experiences. 
 * Cyberjam 2024 is proudly sponsored by Chainlink, our Gold Tier sponsor, whose technology enables 
 * the smart contract's price feed functionality.  Buying the NFT is a badge of honor and gives you voting rights.
 * 
 * As part of the opening ceremony, Tippi Fifestarr will conduct a workshop demonstrating the use of 
 * this contract, showcasing how blockchain technology can be integrated into community-driven events.
 * 
 * The primary goals of this contract are:
 * 1. To create a transparent and decentralized system for managing the community prize pool
 * 2. To reward contributors with NFTs and voting rights
 * 3. To facilitate a fair distribution of prizes based on community voting
 * 4. To demonstrate the practical application of blockchain in event management and community engagement
 * 
 * This contract leverages Chainlink's price feeds to ensure accurate ETH to USD conversion rates, 
 * allowing for consistent contribution thresholds regardless of ETH price fluctuations.
 */

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title CyberjamNFT
 * @dev This contract manages the NFTs given to contributors of the Cyberjam 2024 event.
 */
contract CyberjamNFT is ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;

    address public communityPoolAddress;

    event CommunityPoolAddressUpdated(address indexed newAddress);
    event NFTMinted(address indexed recipient, uint256 indexed tokenId, string tokenURI);

    /**
     * @dev Constructor initializes the NFT with name and symbol, and sets the initial owner
     */
    constructor(address initialOwner) ERC721("CyberJamContributor", "CJC") Ownable(initialOwner) {}

    /**
     * @dev Sets the address of the Community Prize Pool contract
     * @param _communityPoolAddress The address of the Community Prize Pool contract
     */
    function setCommunityPoolAddress(address _communityPoolAddress) external onlyOwner {
        communityPoolAddress = _communityPoolAddress;
        emit CommunityPoolAddressUpdated(_communityPoolAddress);
    }

    /**
     * @dev Mints a new NFT to the recipient
     * @param recipient The address that will receive the NFT
     * @param tokenURI The URI for the NFT metadata
     * @return The ID of the newly minted NFT
     */
    function mintNFT(address recipient, string memory tokenURI) external returns (uint256) {
        require(msg.sender == communityPoolAddress, "Only Community Pool can mint");
        _tokenIds.increment();
        uint256 newTokenId = _tokenIds.current();
        _mint(recipient, newTokenId);
        _setTokenURI(newTokenId, tokenURI);
        emit NFTMinted(recipient, newTokenId, tokenURI);
        return newTokenId;
    }
}

/**
 * @title CommunityPrizePool
 * @dev This contract manages the community prize pool for Cyberjam 2024
 */
contract CommunityPrizePool is Ownable, Pausable, ReentrancyGuard {
    AggregatorV3Interface private ethUsdPriceFeed;
    CyberjamNFT public nftContract;

    uint256 public constant MINIMUM_CONTRIBUTION_USD = 500; // 500 USD
    uint256 public constant OWNER_CONTRIBUTION_USD = 250; // 250 USD
    uint256 public prizePool;

    address[] private teamAddresses;

    mapping(address => bool) public eligibleTeams;
    mapping(address => bool) public hasClaimedPrize;
    mapping(address => uint256) public contributorVotes;
    mapping(address => uint256) public teamVotes;
    mapping(address => bool) public isNFTHolder;
    mapping(address => bool) public isContributor;

    event ContributionMade(address indexed contributor, uint256 amount, bool isNFTMinted);
    event PrizeClaimed(address indexed team, uint256 amount);
    event TeamAdded(address indexed team);
    event TeamRemoved(address indexed team);
    event VoteCast(address indexed voter, address indexed team, uint256 votes);
    event OffChainVotesAdded(address[] voters, address[] teams, uint256[] votes);
    event NFTContractUpdated(address indexed newNFTContract);
    event PriceFeedUpdated(address indexed newPriceFeed);
    event PrizePoolPaused();
    event PrizePoolUnpaused();
    event FundsWithdrawn(address indexed owner, uint256 amount);

    /**
     * @dev Constructor initializes the contract with price feed and NFT contract addresses, and sets the initial owner
     * @param _priceFeedAddress The address of the Chainlink ETH/USD price feed
     * @param _nftContractAddress The address of the CyberjamNFT contract
     * @param initialOwner The address of the initial owner of the contract
     */
    constructor(
        address _priceFeedAddress,
        address _nftContractAddress,
        address initialOwner
    ) Ownable(initialOwner) {
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        nftContract = CyberjamNFT(_nftContractAddress);
    }

    /**
     * @dev Allows users to contribute to the prize pool
     * @param tokenURI The URI for the NFT metadata if the contribution is sufficient
     */
    function contribute(string memory tokenURI) external payable whenNotPaused nonReentrant {
        require(msg.value > 0, "Contribution must be greater than 0");
        uint256 contributionInUsd = getConversionRate(msg.value);
        
        prizePool += msg.value;
        if (contributionInUsd >= MINIMUM_CONTRIBUTION_USD * 1e18) {
            nftContract.mintNFT(msg.sender, tokenURI);
            isNFTHolder[msg.sender] = true;
            isContributor[msg.sender] = true;
            contributorVotes[msg.sender] += 5;
            emit ContributionMade(msg.sender, msg.value, true);
        } else {
            isContributor[msg.sender] = true;
            emit ContributionMade(msg.sender, msg.value, false);
        }
    }

    /**
     * @dev Allows the owner to contribute and mint an NFT at a discounted rate
     * @param recipient The address that will receive the NFT
     * @param tokenURI The URI for the NFT metadata
     */
    function contributeAsOwner(address recipient, string memory tokenURI) external payable onlyOwner whenNotPaused nonReentrant {
        require(msg.value > 0, "Contribution must be greater than 0");
        uint256 contributionInUsd = getConversionRate(msg.value);
        require(contributionInUsd >= OWNER_CONTRIBUTION_USD * 1e18, "Owner's contribution must be at least 250 USD");

        prizePool += msg.value;
        nftContract.mintNFT(recipient, tokenURI);
        isNFTHolder[recipient] = true;
        isContributor[recipient] = true;
        contributorVotes[recipient] += 5;

        emit ContributionMade(recipient, msg.value, true);
    }

    /**
     * @dev Adds a team to the list of eligible teams
     * @param _team The address of the team to be added
     */
    function addEligibleTeam(address _team) external onlyOwner {
        require(!eligibleTeams[_team], "Team already eligible");
        eligibleTeams[_team] = true;
        teamAddresses.push(_team);
        emit TeamAdded(_team);
    }

    /**
     * @dev Removes a team from the list of eligible teams
     * @param _team The address of the team to be removed
     */
    function removeEligibleTeam(address _team) external onlyOwner {
        require(eligibleTeams[_team], "Team is not eligible");
        eligibleTeams[_team] = false;
        for (uint i = 0; i < teamAddresses.length; i++) {
            if (teamAddresses[i] == _team) {
                teamAddresses[i] = teamAddresses[teamAddresses.length - 1];
                teamAddresses.pop();
                break;
            }
        }
        emit TeamRemoved(_team);
    }

    /**
     * @dev Allows NFT holders to cast votes for eligible teams
     * @param _team The address of the team being voted for
     * @param _votes The number of votes to cast
     */
    function castVote(address _team, uint256 _votes) external whenNotPaused {
        require(isNFTHolder[msg.sender], "Only NFT holders can vote");
        require(eligibleTeams[_team], "Invalid team");
        require(contributorVotes[msg.sender] >= _votes, "Not enough votes");

        contributorVotes[msg.sender] -= _votes;
        teamVotes[_team] += _votes;

        emit VoteCast(msg.sender, _team, _votes);
    }

    /**
     * @dev Allows the owner to input off-chain votes
     * @param _voters Array of voter addresses
     * @param _teams Array of team addresses being voted for
     * @param _votes Array of vote counts
     */
    function inputOffChainVotes(address[] memory _voters, address[] memory _teams, uint256[] memory _votes) external onlyOwner {
        require(_voters.length == _teams.length && _teams.length == _votes.length, "Input arrays must have the same length");
        for (uint i = 0; i < _voters.length; i++) {
            require(eligibleTeams[_teams[i]], "Invalid team");
            teamVotes[_teams[i]] += _votes[i];
            emit VoteCast(_voters[i], _teams[i], _votes[i]);
        }
        emit OffChainVotesAdded(_voters, _teams, _votes);
    }

    /**
     * @dev Distributes the prize pool based on votes received by each team
     */
    function distributePrizeByVotes() external onlyOwner whenNotPaused nonReentrant {
        uint256 totalVotes = getTotalVotes();
        require(totalVotes > 0, "No votes cast");
        require(teamAddresses.length > 0, "No teams registered");

        for (uint i = 0; i < teamAddresses.length; i++) {
            address team = teamAddresses[i];
            if (eligibleTeams[team] && !hasClaimedPrize[team]) {
                uint256 teamVoteCount = teamVotes[team];
                uint256 prizeAmount = (prizePool * teamVoteCount) / totalVotes;
                hasClaimedPrize[team] = true;
                require(address(this).balance >= prizeAmount, "Insufficient funds");
                (bool success, ) = team.call{value: prizeAmount}("");
                require(success, "Transfer failed");
                emit PrizeClaimed(team, prizeAmount);
            }
        }
    }

    /**
     * @dev Gets the total number of votes for a specific team
     * @param _team The address of the team
     * @return The total number of votes for the team
     */
    function getTeamVotes(address _team) public view returns (uint256) {
        return teamVotes[_team];
    }

    /**
     * @dev Gets the total number of votes across all teams
     * @return The total number of votes
     */
    function getTotalVotes() public view returns (uint256) {
        uint256 totalVotes = 0;
        for (uint i = 0; i < teamAddresses.length; i++) {
            totalVotes += teamVotes[teamAddresses[i]];
        }
        return totalVotes;
    }

    /**
     * @dev Gets the total number of registered teams
     * @return The total number of teams
     */
    function getTotalTeams() public view returns (uint256) {
        return teamAddresses.length;
    }

    /**
     * @dev Gets the number of eligible teams that haven't claimed their prize
     * @return The count of eligible teams
     */
    function getEligibleTeamCount() public view returns (uint256) {
        uint256 count = 0;
        for (uint256 i = 0; i < teamAddresses.length; i++) {
            if (eligibleTeams[teamAddresses[i]] && !hasClaimedPrize[teamAddresses[i]]) {
                count++;
            }
        }
        return count;
    }

    /**
     * @dev Converts ETH amount to USD using Chainlink price feed
     * @param ethAmount The amount of ETH to convert
     * @return The equivalent amount in USD (scaled by 1e18)
     */
    function getConversionRate(uint256 ethAmount) public view returns (uint256) {
        (, int256 price, , , ) = ethUsdPriceFeed.latestRoundData();
        uint256 ethPrice = uint256(price) * 1e10; // Adjust for decimals
        return (ethAmount * ethPrice) / 1e18;
    }

    /**
     * @dev Updates the NFT contract address
     * @param _newNFTContract The address of the new NFT contract
     */
    function updateNFTContract(address _newNFTContract) external onlyOwner {
        nftContract = CyberjamNFT(_newNFTContract);
        emit NFTContractUpdated(_newNFTContract);
    }

    /**
     * @dev Updates the price feed address
     * @param _newPriceFeed The address of the new price feed
     */
    function updatePriceFeed(address _newPriceFeed) external onlyOwner {
        ethUsdPriceFeed = AggregatorV3Interface(_newPriceFeed);
        emit PriceFeedUpdated(_newPriceFeed);
    }

    /**
     * @dev Pauses the contract
     */
    function pause() external onlyOwner {
        _pause();
        emit PrizePoolPaused();
    }

    /**
     * @dev Unpauses the contract
     */
    function unpause() external onlyOwner {
        _unpause();
        emit PrizePoolUnpaused();
    }

    /**
     * @dev Withdraws remaining funds after all prizes have been claimed
     */
    function withdrawRemainingFunds() external onlyOwner nonReentrant {
        require(getEligibleTeamCount() == 0, "Not all teams have claimed their prizes");
        uint256 remainingBalance = address(this).balance;
        require(remainingBalance > 0, "No funds to withdraw");
        (bool success, ) = owner().call{value: remainingBalance}("");
        require(success, "Transfer failed");
        emit FundsWithdrawn(owner(), remainingBalance);
    }

    /**
     * @dev Fallback function to handle accidental ETH transfers
     */
    receive() external payable {
        prizePool += msg.value;
        emit ContributionMade(msg.sender, msg.value, false);
    }

    /**
     * @dev Fallback function to handle accidental calls with ETH
     */
    fallback() external payable {
        prizePool += msg.value;
        emit ContributionMade(msg.sender, msg.value, false);
    }
}