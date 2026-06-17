# Rain SDK

TypeScript SDK for the Rain prediction-markets protocol on Arbitrum One.

Build, sign, and send prediction market transactions — from creating markets and trading options to claiming winnings and streaming live events.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                      Your Application                     │
├────────────────────────┬─────────────────────────────────┤
│         Rain           │            RainAA               │
│   (WHAT to do)         │       (HOW to execute)          │
│                        │                                 │
│  • Market queries      │  • Smart account creation       │
│  • Tx builders         │  • Gas-sponsored execution      │
│  • Position reads      │  • Tx submission                │
│  • WebSocket streams   │  • Session management           │
│  • Analytics           │                                 │
├────────────────────────┴─────────────────────────────────┤
│                     RawTransaction                        │
│              { to, data, value? }                         │
├──────────────────────────────────────────────────────────┤
│               Arbitrum One (on-chain)                     │
│         Diamond Proxy Pools + AMM per option              │
└──────────────────────────────────────────────────────────┘
```

The SDK is split into two independent classes:

- **`Rain`** — Stateless. Fetches data, builds unsigned transactions, subscribes to events. Does not require a wallet.
- **`RainAA`** — Stateful. Manages Alchemy smart accounts, signs and sends transactions via account abstraction.

All transaction builders return a `RawTransaction` — the caller decides how to execute it (via `RainAA`, wagmi, ethers, or any provider).

## Installation

```bash
npm install @buidlrrr/rain-sdk
```

**Peer dependency**: `viem ^2.0.0`

## Quick Start

```ts
import { Rain, RainAA } from '@buidlrrr/rain-sdk';

// 1. Initialize (stateless — no wallet needed)
const rain = new Rain({ environment: 'development' });

// 2. Fetch markets
const markets = await rain.getPublicMarkets({ limit: 10 });

// 3. Build a buy transaction
const rawTx = rain.buildBuyOptionRawTx({
  marketContractAddress: '0x...',
  selectedOption: 1n,
  buyAmountInWei: 10_000_000n,  // 10 USDT (6 decimals)
});

// 4. Execute via your provider, OR via RainAA:
await yourProvider.sendTransaction(rawTx);
```

## Configuration

```ts
const rain = new Rain({
  environment: 'development',         // 'development' | 'stage' | 'production'
  rpcUrl: 'https://...',              // Optional — defaults to public Arbitrum RPCs
  wsRpcUrl: 'wss://...',             // Required for subscribeToMarketEvents / subscribePriceUpdates
  subgraphUrl: 'https://...',        // Required for transaction history / price history / analytics
  subgraphApiKey: '...',             // Optional — TheGraph API key
  wsReconnect: { attempts: 5, delay: 1000 },  // Optional — WebSocket auto-reconnect
});
```

### Environments

| Environment   | API                    | Factory Address                              |
| ------------- | ---------------------- | -------------------------------------------- |
| `development` | `dev-api.rain.one`     | `0x05b1fd504583B81bd14c368d59E8c3e354b6C1dc` |
| `stage`       | `stg-api.rain.one`     | `0xD4900CA167228365806FBA4cB21f7EAe8b6d96BE` |
| `production`  | `prod-api.rain.one`    | `0xA8640B62D755e42C9ed6A86d0fc65CE09e31F264` |

---

## API Reference

### Market Queries

#### `getPublicMarkets(params)` — Browse markets

```ts
const markets = await rain.getPublicMarkets({
  limit: 12,
  offset: 0,
  sortBy: 'Liquidity',          // 'Liquidity' | 'Volumn' | 'latest'
  status: 'Live',               // 'Live' | 'Trading' | 'Closed' | ...
  creator: '0x...',             // Optional — filter by creator
});
// Returns: Market[]
// { id, title, totalVolume, status, contractAddress, poolOwnerWalletAddress }
```

#### `getMarketDetails(marketId)` — Full market data

Combines Rain API data with on-chain reads from the diamond proxy.

```ts
const details = await rain.getMarketDetails('698c8f116e985bbfacc7fc01');
// Returns: MarketDetails
// {
//   id, title, status, contractAddress,
//   options: [{ choiceIndex, optionName, currentPrice, totalFunds, totalVotes }],
//   poolState, numberOfOptions, startTime, endTime, oracleEndTime,
//   allFunds, allVotes, totalLiquidity, winner, poolFinalized,
//   isPublic, baseToken, baseTokenDecimals, poolOwner, resolver,
//   resolverIsAI, isDisputed, isAppealed
// }
```

#### `getMarketPrices(marketId)` — Current option prices

```ts
const prices = await rain.getMarketPrices('698c8f116e985bbfacc7fc01');
// Returns: OptionPrice[]
// [{ choiceIndex: 0, optionName: 'Yes', currentPrice: 650000000000000000n }]
// currentPrice is in 1e18 — divide by 1e18 for decimal (0.65 = 65%)
```

#### `getMarketVolume(marketId)` — Volume breakdown

```ts
const volume = await rain.getMarketVolume('698c8f116e985bbfacc7fc01');
// Returns: MarketVolume
// { marketId, contractAddress, totalVolume, optionVolumes: [{ choiceIndex, optionName, volume }] }
```

#### `getMarketLiquidity(marketId)` — Liquidity & order book

```ts
const liq = await rain.getMarketLiquidity('698c8f116e985bbfacc7fc01');
// Returns: MarketLiquidity
// { marketId, contractAddress, totalLiquidity, allFunds,
//   optionLiquidity: [{ choiceIndex, optionName, totalFunds, firstBuyOrderPrice, firstSellOrderPrice }] }
```

#### `getMarketAddress(marketId)` / `getMarketId(marketAddress)` — ID/Address lookup

```ts
const address = await rain.getMarketAddress('698c8f116e985bbfacc7fc01');
const id = await rain.getMarketId('0xd262abd3d58038e15736Ec32c4F7b020C2B21dB5');
```

#### `getProtocolStats()` — Protocol-wide metrics

```ts
const stats = await rain.getProtocolStats();
// Returns: ProtocolStats
// { tvl, totalVolume, activeMarkets, totalMarkets, uniqueTraders }
```

---

### Transaction Builders

All builders return `RawTransaction` — `{ to, data, value? }`. They do **not** send transactions.

#### `buildApprovalTx(params)` — ERC20 approve

```ts
const tx = rain.buildApprovalTx({
  tokenAddress: '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',  // USDT
  spender: '0x...',    // market contract address
  amount: 100_000_000n, // Optional — defaults to max uint256
});
```

#### `buildCreateMarketTx(params)` — Create a market

Returns an array: `[approveTx, createTx]` if approval is needed, or `[createTx]` if already approved.

```ts
const txs = await rain.buildCreateMarketTx({
  marketQuestion: 'Will BTC hit 100k?',
  marketOptions: ['Yes', 'No'],
  marketTags: ['crypto', 'bitcoin'],
  marketDescription: 'Prediction market for BTC price',
  isPublic: true,
  isPublicPoolResolverAi: false,
  creator: '0x996ea23940f4a01610181D04bdB6F862719b63f0',
  startTime: 1770836400n,
  endTime: 1770922800n,
  no_of_options: 2n,
  inputAmountWei: 100_000_000n,   // 100 USDT (min 10 tokens)
  barValues: [50, 50],             // Initial probability distribution (%)
  baseToken: '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
  tokenDecimals: 6,
});

// Execute sequentially
for (const tx of txs) {
  await provider.sendTransaction(tx);
}
```

#### `buildBuyOptionRawTx(params)` — Market buy

```ts
const tx = rain.buildBuyOptionRawTx({
  marketContractAddress: '0x...',
  selectedOption: 1n,              // Option index (bigint)
  buyAmountInWei: 10_000_000n,    // 10 USDT
});
```

#### `buildLimitBuyOptionTx(params)` — Limit buy order

```ts
const tx = rain.buildLimitBuyOptionTx({
  marketContractAddress: '0x...',
  selectedOption: 1,
  pricePerShare: 500000000000000000n,  // 0.50 in 1e18
  buyAmountInWei: 10_000_000n,
  tokenDecimals: 6,
});
```

#### `buildSellOptionTx(params)` — Place sell order

```ts
const tx = rain.buildSellOptionTx({
  marketContractAddress: '0x...',
  selectedOption: 1,
  pricePerShare: 0.75,     // Target price (0-1)
  shares: 5_000_000n,     // Shares to sell
  tokenDecimals: 6,
});
```

#### `buildCancelBuyOrdersTx(params)` / `buildCancelSellOrdersTx(params)` — Cancel orders

```ts
const tx = rain.buildCancelBuyOrdersTx({
  marketContractAddress: '0x...',
  orders: [
    { option: 1, price: 0.5, orderID: 1n },
    { option: 1, price: 0.6, orderID: 2n },
  ],
});
```

#### `buildAddLiquidityTx(params)` — Provide liquidity

```ts
const tx = rain.buildAddLiquidityTx({
  marketContractAddress: '0x...',
  liquidityAmountInWei: 100_000_000n,  // 100 USDT
});
```

> Note: Liquidity is locked until market resolution. There is no `removeLiquidity` — LPs recover their share via `buildClaimTx` after resolution.

#### `buildClaimTx(params)` — Claim winnings

```ts
const tx = await rain.buildClaimTx({
  marketId: '698c8f116e985bbfacc7fc01',
  walletAddress: '0x996ea23940f4a01610181D04bdB6F862719b63f0',
});
```

#### `buildResolveMarketTx(params)` — Resolve a market (admin)

Combines close + choose winner into a multi-step transaction array.

```ts
const txs = await rain.buildResolveMarketTx({
  marketId: '698c8f116e985bbfacc7fc01',
  winningOption: 1,  // 1-indexed
});

for (const tx of txs) {
  await provider.sendTransaction(tx);
}
```

Individual steps are also available: `buildCloseMarketTx(params)` and `buildChooseWinnerTx(params)`.

#### `buildDepositToSmartAccountTx(params)` / `buildWithdrawFromSmartAccountTx(params)`

```ts
// Deposit: EOA → Smart Account
const depositTx = rain.buildDepositToSmartAccountTx({
  tokenAddress: '0x...USDT',
  smartAccountAddress: '0x...smartAccount',
  amount: 50_000_000n,
});

// Withdraw: Smart Account → EOA
const withdrawTx = rain.buildWithdrawFromSmartAccountTx({
  tokenAddress: '0x...USDT',
  eoaAddress: '0x...eoa',
  amount: 50_000_000n,
});
```

---

### Positions & Portfolio

#### `getPositions(address)` — All positions across markets

```ts
const positions = await rain.getPositions('0x...');
// Returns: PositionsResult
// { address, markets: [{ marketId, title, status, contractAddress,
//     options: [{ choiceIndex, optionName, shares, sharesInEscrow, amountInEscrow, currentPrice }],
//     userLiquidity, claimed, dynamicPayout }] }
```

#### `getPositionByMarket(address, marketId)` — Single market position

```ts
const pos = await rain.getPositionByMarket('0x...', '698c8f116e985bbfacc7fc01');
// Returns: PositionByMarket (same shape as a single MarketPosition)
```

#### `getLPPosition(address, marketId)` — LP position details

```ts
const lp = await rain.getLPPosition('0x...', '698c8f116e985bbfacc7fc01');
// Returns: LPPosition
// { marketId, title, status, contractAddress,
//   userLiquidity, totalLiquidity, poolShareBps, liquidityShareBps }
```

#### `getPortfolioValue(params)` — Aggregate portfolio

```ts
const portfolio = await rain.getPortfolioValue({
  address: '0x...',
  tokenAddresses: ['0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9'],  // USDT
});
// Returns: PortfolioValue
// { address, tokenBalances, positions: [{ marketId, title, dynamicPayout, totalPositionValue }],
//   totalPositionValue }
```

`dynamicPayout` is per-option: `[0, 804164316, 0, 0]` means ~804 USDT payout if option 1 wins.

---

### Account Management

#### `getSmartAccountBalance(params)` — Token balances

```ts
const balance = await rain.getSmartAccountBalance({
  address: '0x...',
  tokenAddresses: ['0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9'],
});
// Returns: AccountBalanceResult { address, balances: [{ token, balance, decimals }] }
```

#### `getEOAFromSmartAccount(smartAccountAddress)` — Reverse lookup

```ts
const eoa = await rain.getEOAFromSmartAccount('0x...smartAccount');
// Returns: '0x...eoa'
```

---

### Transaction History

Requires `subgraphUrl` in the constructor config (or per-method override).

#### `getTransactions(params)` — Wallet transaction history

```ts
const txs = await rain.getTransactions({
  address: '0x...',
  first: 20,
  skip: 0,
  orderBy: 'timestamp',
  orderDirection: 'desc',
});
```

#### `getTransactionDetails(params)` — Decode a single transaction

```ts
const details = await rain.getTransactionDetails({ txHash: '0x...' });
```

#### `getMarketTransactions(params)` — All trades on a market

```ts
const trades = await rain.getMarketTransactions({
  marketAddress: '0x...',
  first: 50,
});
```

#### `getTradeHistory(params)` — User trades on a specific market

```ts
const history = await rain.getTradeHistory({
  address: '0x...',
  marketAddress: '0x...',
});
```

---

### Analytics

#### `getPriceHistory(params)` — OHLC candle data

```ts
const candles = await rain.getPriceHistory({
  marketAddress: '0x...',
  interval: '1h',       // '5m' | '15m' | '1h' | '4h' | '1d'
  option: 0,
});
// Returns: PriceHistoryResult { candles: [{ open, high, low, close, timestamp }] }
```

#### `getPnL(params)` — Realized & unrealized P&L

```ts
const pnl = await rain.getPnL({
  address: '0x...',
  marketId: '...',  // Optional — omit for aggregate
});
```

#### `getLeaderboard(params)` — Top traders

```ts
const leaders = await rain.getLeaderboard({
  timeframe: '7d',       // '24h' | '7d' | '30d' | 'all'
  sortBy: 'pnl',        // 'pnl' | 'volume' | 'winRate'
  first: 10,
});
```

---

### WebSocket Subscriptions

Requires `wsRpcUrl` in the constructor config.

#### `subscribeToMarketEvents(params)` — Live on-chain events

```ts
const rain = new Rain({
  environment: 'development',
  wsRpcUrl: 'wss://arbitrum-one-rpc.publicnode.com',
});

const unsubscribe = rain.subscribeToMarketEvents({
  marketAddress: '0x...',
  eventNames: ['EnterOption', 'Sync'],  // Optional filter — omit for all events
  onEvent: (event) => {
    console.log(event.eventName, event.args);
  },
  onError: (err) => console.error(err),
});

// Stop listening
unsubscribe();
```

**Available events:**

| Category   | Events                                                                                        |
| ---------- | --------------------------------------------------------------------------------------------- |
| Trades     | `EnterOption`, `PlaceBuyOrder`, `PlaceSellOrder`, `ExecuteBuyOrder`, `ExecuteSellOrder`, `CancelBuyOrder`, `CancelSellOrder` |
| Price sync | `Sync` — AMM reserve rebalance (emitted once per option pair per trade)                       |
| Lifecycle  | `Claim`, `ChooseWinner`, `ClosePool`                                                          |

#### `subscribePriceUpdates(params)` — Real-time price feed

```ts
const unsubscribe = rain.subscribePriceUpdates({
  marketAddress: '0x...',
  onPriceUpdate: (update) => {
    // update.prices: OptionPrice[] — fresh prices after each trade
    // update.triggeredBy: MarketTradeEvent — the event that caused the update
    console.log(update.prices);
  },
  onError: (err) => console.error(err),
});
```

#### `destroyWebSocket()` — Cleanup

```ts
await rain.destroyWebSocket();
```

---

## RainAA — Account Abstraction

`RainAA` manages Alchemy smart accounts with gas sponsorship.

```ts
import { RainAA } from '@buidlrrr/rain-sdk';
import { arbitrum } from 'viem/chains';

const rainAA = new RainAA({
  walletClient: yourWalletClient,       // viem WalletClient
  alchemyApiKey: 'your-alchemy-key',
  paymasterPolicyId: 'your-policy-id',
  chain: arbitrum,
  rpcUrl: 'https://...',               // Optional
});

// Connect — derives smart account from EOA
const smartAccountAddress = await rainAA.connect();
console.log('Smart account:', smartAccountAddress);

// Send transactions built by Rain
const rain = new Rain({ environment: 'production' });
const rawTx = rain.buildBuyOptionRawTx({ ... });
const txHash = await rainAA.sendTransaction(rawTx);

// Accessors
rainAA.address;   // Smart account address (throws if not connected)
rainAA.client;    // Underlying AA client (throws if not connected)

// Disconnect
rainAA.disconnect();
```

### Flow: Rain + RainAA Together

```ts
// 1. Rain builds the transaction (WHAT)
const rawTx = rain.buildBuyOptionRawTx({
  marketContractAddress: '0x...',
  selectedOption: 1n,
  buyAmountInWei: 10_000_000n,
});

// 2. RainAA sends it via smart account (HOW)
const txHash = await rainAA.sendTransaction(rawTx);
```

---

## Data Sources

The SDK reads from three sources depending on the method:

| Source       | Used by                                                        | Config                       |
| ------------ | -------------------------------------------------------------- | ---------------------------- |
| **Rain API** | `getPublicMarkets`, `getMarketDetails` (partial), `buildClaimTx`, `buildCreateMarketTx` | `environment` (auto)         |
| **On-chain** | `getMarketPrices`, `getMarketVolume`, `getPositions`, all tx builders | `rpcUrl` (auto-selected)     |
| **Subgraph** | `getTransactions`, `getPriceHistory`, `getPnL`, `getLeaderboard` | `subgraphUrl` + `subgraphApiKey` |

Methods that require the subgraph will throw if `subgraphUrl` is not configured.

---

## Key Types

```ts
// Core transaction type — returned by all builders
interface RawTransaction {
  to: `0x${string}`;
  data: `0x${string}`;
  value?: bigint;
}

// Market from listing endpoint
interface Market {
  id: string;
  title: string;
  totalVolume: string;
  status: MarketStatus;
  contractAddress?: string;
}

// Full market details (API + on-chain)
interface MarketDetails {
  id: string;
  title: string;
  status: MarketStatus;
  contractAddress: `0x${string}`;
  options: MarketOption[];
  poolState: number;
  numberOfOptions: bigint;
  startTime: bigint;
  endTime: bigint;
  totalLiquidity: bigint;
  // ... and more
}

// Position data per market
interface MarketPosition {
  marketId: string;
  title: string;
  options: OptionPosition[];
  userLiquidity: bigint;
  claimed: boolean;
  dynamicPayout: bigint[];
}

// WebSocket event payload
interface MarketTradeEvent {
  eventName: MarketEventName;
  marketAddress: `0x${string}`;
  blockNumber: bigint;
  transactionHash: `0x${string}`;
  logIndex: number;
  args: Record<string, unknown>;
}

type MarketStatus = 'Live' | 'New' | 'WaitingForResult' | 'UnderDispute' |
  'UnderAppeal' | 'ClosingSoon' | 'InReview' | 'InEvaluation' | 'Closed' | 'Trading';
```

---

## Full Method Reference

### Rain Class

| Category             | Method                              | Returns                  | Async |
| -------------------- | ----------------------------------- | ------------------------ | ----- |
| **Markets**          | `getPublicMarkets(params)`          | `Market[]`               | Yes   |
|                      | `getMarketDetails(marketId)`        | `MarketDetails`          | Yes   |
|                      | `getMarketPrices(marketId)`         | `OptionPrice[]`          | Yes   |
|                      | `getMarketVolume(marketId)`         | `MarketVolume`           | Yes   |
|                      | `getMarketLiquidity(marketId)`      | `MarketLiquidity`        | Yes   |
|                      | `getMarketAddress(marketId)`        | `0x${string}`            | Yes   |
|                      | `getMarketId(marketAddress)`        | `string`                 | Yes   |
|                      | `getProtocolStats()`                | `ProtocolStats`          | Yes   |
| **Tx Builders**      | `buildApprovalTx(params)`           | `RawTransaction`         | No    |
|                      | `buildCreateMarketTx(params)`       | `RawTransaction[]`       | Yes   |
|                      | `buildBuyOptionRawTx(params)`       | `RawTransaction`         | No    |
|                      | `buildLimitBuyOptionTx(params)`     | `RawTransaction`         | No    |
|                      | `buildSellOptionTx(params)`         | `RawTransaction`         | No    |
|                      | `buildCancelBuyOrdersTx(params)`    | `RawTransaction`         | No    |
|                      | `buildCancelSellOrdersTx(params)`   | `RawTransaction`         | No    |
|                      | `buildAddLiquidityTx(params)`       | `RawTransaction`         | No    |
|                      | `buildClaimTx(params)`              | `RawTransaction`         | Yes   |
|                      | `buildCloseMarketTx(params)`        | `RawTransaction`         | Yes   |
|                      | `buildChooseWinnerTx(params)`       | `RawTransaction`         | Yes   |
|                      | `buildResolveMarketTx(params)`      | `RawTransaction[]`       | Yes   |
|                      | `buildDepositToSmartAccountTx(p)`   | `RawTransaction`         | No    |
|                      | `buildWithdrawFromSmartAccountTx(p)`| `RawTransaction`         | No    |
| **Positions**        | `getPositions(address)`             | `PositionsResult`        | Yes   |
|                      | `getPositionByMarket(addr, id)`     | `PositionByMarket`       | Yes   |
|                      | `getLPPosition(addr, id)`           | `LPPosition`             | Yes   |
|                      | `getPortfolioValue(params)`         | `PortfolioValue`         | Yes   |
| **Accounts**         | `getSmartAccountBalance(params)`    | `AccountBalanceResult`   | Yes   |
|                      | `getEOAFromSmartAccount(addr)`      | `0x${string}`            | Yes   |
| **Tx History**       | `getTransactions(params)`           | `TransactionsResult`     | Yes   |
|                      | `getTransactionDetails(params)`     | `TransactionDetails`     | Yes   |
|                      | `getMarketTransactions(params)`     | `MarketTransactionsResult` | Yes |
|                      | `getTradeHistory(params)`           | `TradeHistoryResult`     | Yes   |
| **Analytics**        | `getPriceHistory(params)`           | `PriceHistoryResult`     | Yes   |
|                      | `getPnL(params)`                    | `PnLResult`              | Yes   |
|                      | `getLeaderboard(params)`            | `LeaderboardResult`      | Yes   |
| **WebSocket**        | `subscribeToMarketEvents(params)`   | `Unsubscribe`            | No    |
|                      | `subscribePriceUpdates(params)`     | `Unsubscribe`            | No    |
|                      | `destroyWebSocket()`                | `void`                   | Yes   |

### RainAA Class

| Method               | Returns              | Async |
| -------------------- | -------------------- | ----- |
| `connect()`          | `0x${string}`        | Yes   |
| `sendTransaction(tx)`| `0x${string}` (hash) | Yes   |
| `disconnect()`       | `void`               | No    |
| `.address`           | `0x${string}`        | —     |
| `.client`            | Smart wallet client  | —     |

---

## Development

```bash
# Build
cd rain-sdk && npm run build

# Watch mode
npm run dev

# Run tests
npm test

# Integration tests
npm run test:integration
```
