<!-- src/components/WalletConnectButton.vue -->
<template>
  <div class="wallet-connect">
    <button 
      @click="connect" 
      class="connect-btn"
      :disabled="isConnecting"
    >
      <span v-if="isConnecting" class="connect-btn-text">Connecting...</span>
      <span v-else class="connect-btn-text">Connect Wallet</span>
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useAccountStore } from '@/store/account';
import { activeChainConfig } from '@config';

const accountStore = useAccountStore();

// Computed properties
const isConnected = computed(() => accountStore.isConnected);
const isConnecting = computed(() => accountStore.isConnecting);
const balance = computed(() => 
  Number(accountStore.balance).toFixed(4)
);
const networkName = computed(() => accountStore.networkName);
const isCorrectNetwork = computed(() => accountStore.chainId === 912559); // Flame devnet

const shortAddress = computed(() => {
  if (!accountStore.pkh) return '';
  return `${accountStore.pkh.substring(0, 6)}...${accountStore.pkh.substring(38)}`;
});

// Methods
const connect = () => {
  accountStore.connectWallet();
};

const disconnect = () => {
  accountStore.logout();
};
</script>

<style scoped>
.wallet-connect {
  display: flex;
  align-items: center;
  gap: 12px;
}

.wallet-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.wallet-address {
  font-weight: 600;
  font-size: 14px;
}

.wallet-balance {
  font-size: 12px;
  color: #6c757d;
}

.wallet-network {
  font-size: 12px;
  background-color: #28a745;
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
}

.wallet-network.wrong-network {
  background-color: #dc3545;
}

.connect-btn, .disconnect-btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-weight: 600;
}

.connect-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-radius: 7px;
  cursor: pointer;
  outline: 1px solid transparent;
  color: var(--text-primary);
  font-weight: 600;
  white-space: nowrap;
  transition: all .2s ease;
  background: var(--btn-primary-bg);
  fill: var(--text-primary);
  height: 32px;
  padding: 0 10px;
  font-size: 13px;
  gap: 8px;
  border-radius: 6px;
}

.disconnect-btn {
  background-color: #f8f9fa;
  color: #212529;
  border: 1px solid #dee2e6;
}

.connect-btn:hover {
  background-color: #0b5ed7;
}

.disconnect-btn:hover {
  background-color: #e9ecef;
}

.connect-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}
</style>