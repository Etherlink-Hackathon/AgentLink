// src/store/wallet.js
import { defineStore } from 'pinia';
import { ethers } from 'ethers';
import { flameWager, initWithSigner } from "@sdk";
import {
  getBalance,
  disconnect,
  connect,
  reconnect,
  switchChain
} from '@wagmi/core';
import { injected, metaMask } from '@wagmi/vue/connectors'
import { config, activeRpcNode, activeChainConfig } from "@config";

export const useAccountStore = defineStore({
  id: 'account',

  state: () => ({
    provider: null,
    signer: null,
    pkh: "", // Using pkh instead of address for consistency
    chainId: null,
    balance: "0",
    isConnecting: false,

    pendingTransaction: {
      awaiting: false,
      when: null,
      hash: null
    },
  }),

  getters: {
    isConnected: (state) => !!state.pkh,
    isLoggined: (state) => !!state.pkh,

    networkName: (state) => {
      if (!state.chainId) return 'Not Connected';

      switch (state.chainId) {
        case 42793:
          return "Etherlink Mainnet";
        case 128123:
          return "Etherlink Shadownet";
        default:
          return 'Unknown Network';
      }
    },

    isCorrectNetwork: (state) => state.chainId === activeChainConfig.id,
  },

  actions: {
    async connectWallet() {
      try {
        this.isConnecting = true;

        // Connect using wagmi with metamask connector prioritized
        const result = await connect(config, {
          chainId: activeChainConfig.id,
          connector: metaMask(),
        });

        if (!result.accounts.length) {
          throw new Error('Failed to connect wallet');
        }

        // Set address
        this.pkh = result.accounts[0];

        // Create ethers provider & signer from the injected provider
        const provider = new ethers.BrowserProvider(window.ethereum)
        const signer = await provider.getSigner()

        // Initialize FlameWager SDK with the signer
        await initWithSigner(signer, result.accounts[0])

        // Get and set network info
        this.chainId = activeChainConfig.id;

        // Get balance
        await this.refreshBalance();

        // Save connection state
        localStorage.setItem('wallet-autoconnect', 'true');

        return true;
      } catch (error) {
        console.error('Connection error:', error);
        throw error;
      } finally {
        this.isConnecting = false;
      }
    },

    async logout() {
      try {
        // Disconnect using wagmi
        await disconnect();

        // Reset state
        this.handleDisconnect();
      } catch (error) {
        console.error('Logout error:', error);
      }
    },

    handleDisconnect() {
      // Reset all state
      this.provider = null;
      this.signer = null;
      this.pkh = "";
      this.chainId = null;
      this.balance = "0";
      this.pendingTransaction = {
        awaiting: false,
        when: null,
        hash: null
      };

      // Clear local storage
      localStorage.removeItem('wallet-autoconnect');
    },

    updateBalance() {
      this.refreshBalance();
    },

    async refreshBalance() {
      if (!this.pkh) return;

      try {
        const balanceData = await getBalance(config, {
          address: this.pkh,
          chainId: activeChainConfig.id,
        });

        this.balance = ethers.formatEther(balanceData.value);
      } catch (error) {
        console.error('Error fetching balance:', error);
        this.balance = "0";
      }
    },

    setPendingTransaction(hash) {
      this.pendingTransaction = {
        awaiting: true,
        when: Date.now(),
        hash
      };
    },

    clearPendingTransaction() {
      this.pendingTransaction = {
        awaiting: false,
        when: null,
        hash: null
      };
    },

    async init() {
      // Attempt to auto-connect using wagmi's reconnect
      try {
        const result = await reconnect(config);

        if (result && result.length > 0) {
          // Success, update state
          this.pkh = result[0].accounts[0];
          this.chainId = activeChainConfig.id;

          // Initialize FlameWager SDK with signer on auto-connect
          if (window.ethereum) {
            const provider = new ethers.BrowserProvider(window.ethereum)
            const signer = await provider.getSigner()
            await initWithSigner(signer, this.pkh)
          }

          await this.refreshBalance();
          localStorage.setItem('wallet-autoconnect', 'true');
        } else {
          // If reconnect fails/returns empty, check manual flag as fallback
          const shouldAutoConnect = localStorage.getItem('wallet-autoconnect') === 'true';
          if (shouldAutoConnect) {
            await this.connectWallet();
          }
        }
      } catch (error) {
        console.error('Auto-connect failed:', error);
        // Fallback to manual connect if reconnect throws (but check flag first)
        const shouldAutoConnect = localStorage.getItem('wallet-autoconnect') === 'true';
        if (shouldAutoConnect) {
          try {
            await this.connectWallet();
          } catch (e) {
            console.error("Manual connect fallback failed", e);
            localStorage.removeItem('wallet-autoconnect');
          }
        }
      }
    }
  }
});