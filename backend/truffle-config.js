/**
 * Truffle Configuration for Smart Contract Deployment
 * Use this configuration to deploy PolicyEnforcement contract
 */

module.exports = {
  networks: {
    // Development network (Ganache)
    development: {
      host: "127.0.0.1",
      port: 8545,
      network_id: "*", // Match any network id
      gas: 6721975,
      gasPrice: 20000000000
    },
    
    // Local Ganache GUI
    ganache: {
      host: "127.0.0.1",
      port: 7545,
      network_id: "5777",
      gas: 6721975,
      gasPrice: 20000000000
    },
    
    // Test network configuration (for future use)
    testnet: {
      host: "127.0.0.1",
      port: 8545,
      network_id: "1337",
      gas: 6721975,
      gasPrice: 20000000000
    }
  },
  
  // Configure your compilers
  compilers: {
    solc: {
      version: "0.8.19",
      settings: {
        optimizer: {
          enabled: true,
          runs: 200
        },
        evmVersion: "istanbul"
      }
    }
  },
  
  // Contract directory
  contracts_directory: './contracts',
  contracts_build_directory: './build/contracts',
  
  // Migrations directory
  migrations_directory: './migrations',
  
  // Mocha testing framework options
  mocha: {
    timeout: 100000
  },
  
  // Plugins
  plugins: []
};
