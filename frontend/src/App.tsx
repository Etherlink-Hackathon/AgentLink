import { useState } from 'react';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState<'deposit' | 'withdraw'>('deposit');
  const [amount, setAmount] = useState<string>('');
  
  // Mock data for UI demonstration
  const vaultTVL = "$1,245,000.00";
  const vaultAPY = "14.2%";
  const userBalance = "0.00 USDC";
  const vaultShares = "0.00 arbUSDC";

  const handleAction = () => {
    // Scaffolded handler for web3 integration
    console.log(`${activeTab}ing ${amount}...`);
    alert(`Initiating ${activeTab} of ${amount} USDC into ArbitrageVault...`);
  };

  return (
    <div className="app-container">
      <header>
        <div className="logo">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="url(#paint0_linear)"/>
            <path d="M2 17L12 22L22 17M2 12L12 17L22 12" stroke="url(#paint1_linear)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <defs>
              <linearGradient id="paint0_linear" x1="12" y1="2" x2="12" y2="12" gradientUnits="userSpaceOnUse">
                <stop stopColor="#5E6AD2" />
                <stop offset="1" stopColor="#2563EB" />
              </linearGradient>
              <linearGradient id="paint1_linear" x1="12" y1="12" x2="12" y2="22" gradientUnits="userSpaceOnUse">
                <stop stopColor="#5E6AD2" />
                <stop offset="1" stopColor="#2563EB" />
              </linearGradient>
            </defs>
          </svg>
          <span>Etherlink Omni-DEX</span>
        </div>
        <button className="wallet-btn">Connect Wallet</button>
      </header>

      <main className="dashboard">
        
        {/* Left Column: Interactions */}
        <div className="interaction-column">
          <div className="glass-panel">
            <div className="tabs">
              <button 
                className={`tab ${activeTab === 'deposit' ? 'active' : ''}`}
                onClick={() => setActiveTab('deposit')}
              >
                Deposit
              </button>
              <button 
                className={`tab ${activeTab === 'withdraw' ? 'active' : ''}`}
                onClick={() => setActiveTab('withdraw')}
              >
                Withdraw
              </button>
            </div>

            <div className="input-group">
              <div className="input-wrapper">
                <input 
                  type="number" 
                  placeholder="0.00" 
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                />
                <span className="token-badge">
                  {activeTab === 'deposit' ? 'USDC' : 'arbUSDC'}
                </span>
              </div>
              <div className="metric-label" style={{ textAlign: 'right', marginTop: '0.5rem' }}>
                Balance: {activeTab === 'deposit' ? userBalance : vaultShares}
              </div>
            </div>

            <button className="action-btn" onClick={handleAction}>
              {activeTab === 'deposit' ? 'Deposit into Vault' : 'Withdraw from Vault'}
            </button>
          </div>
        </div>

        {/* Right Column: Analytics & Status */}
        <div className="analytics-column" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          
          <div className="glass-panel" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
            <div>
              <h3 className="section-title">Vault TVL</h3>
              <div className="metric-value">{vaultTVL}</div>
            </div>
            <div>
              <h3 className="section-title">Current APY</h3>
              <div className="metric-value success-text">{vaultAPY}</div>
              <div className="metric-label">Auto-compounded via Arbitrage</div>
            </div>
          </div>

          <div className="glass-panel">
            <h3 className="section-title">OpenClaw Strategist Status</h3>
            
            <div className="agent-status">
              <div className="status-dot"></div>
              <div>
                <div className="status-text">Agent is monitoring Etherlink Mainnet</div>
                <div className="metric-label">Last scan: 12 seconds ago</div>
              </div>
            </div>

            <div className="activity-feed" style={{ marginTop: '1.5rem' }}>
              <div className="activity-item">
                <div>
                  <div className="activity-title">Arb Executed: USDC/WXTZ</div>
                  <div className="activity-time">Curve → Oku Trade • 5 mins ago</div>
                </div>
                <div className="activity-profit success-text">+$42.10</div>
              </div>

              <div className="activity-item">
                <div>
                  <div className="activity-title">Arb Executed: USDC/WETH</div>
                  <div className="activity-time">Gecko Pool → Curve • 48 mins ago</div>
                </div>
                <div className="activity-profit success-text">+$105.80</div>
              </div>

              <div className="activity-item">
                <div>
                  <div className="activity-title">Market Scan</div>
                  <div className="activity-time">No spreads &gt; 0.5% • 15 mins ago</div>
                </div>
                <div className="activity-profit" style={{ color: 'var(--text-secondary)' }}>-</div>
              </div>
            </div>

          </div>
        </div>

      </main>
    </div>
  );
}

export default App;
