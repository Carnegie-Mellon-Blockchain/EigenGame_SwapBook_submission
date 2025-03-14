import defaultConfig from './config.default.json';

export const config = {
  ...defaultConfig,
  tokens: {
    WETH: {
      address: import.meta.env.VITE_WETH_ADDRESS || defaultConfig.tokens.WETH.address,
      symbol: "WETH",
      decimals: 18
    },
    USDC: {
      address: import.meta.env.VITE_USDC_ADDRESS || defaultConfig.tokens.USDC.address,
      symbol: "USDC",
      decimals: 6
    }
  },
  contracts: {
    P2P_ORDERBOOK_ADDRESS: import.meta.env.VITE_P2P_ORDERBOOK_ADDRESS || defaultConfig.contracts.P2P_ORDERBOOK_ADDRESS
  },
  api: {
    baseUrl: {
      development: import.meta.env.EXECUTION_SERVICE_ADDRESS || defaultConfig.api.baseUrl.development,
      production: import.meta.env.EXECUTION_SERVICE_ADDRESS || defaultConfig.api.baseUrl.production
    },
    endpoints: {
      limitOrder: "/api/limitOrder",
      cancelOrder: "/api/cancelOrder",
      orderBook: "/api/orderbook",
      initiateWithdrawal: "/api/initiateWithdrawal"
    }
  }
};

export default config;