/**
 * Migration script for deploying PolicyEnforcement smart contract
 */

const PolicyEnforcement = artifacts.require("PolicyEnforcement");

module.exports = function(deployer) {
  // Deploy the PolicyEnforcement contract
  deployer.deploy(PolicyEnforcement);
};
