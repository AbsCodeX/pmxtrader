# Rain SDK — Agent Reference

> Machine-readable documentation for AI agents integrating with the Rain prediction-markets protocol on Arbitrum One.
> Package: `@buidlrrr/rain-sdk` | Chain: Arbitrum One (42161) | Base token: USDT (6 decimals)

## Install

```bash
npm install @buidlrrr/rain-sdk
```

Peer dependency: `viem ^2.0.0`

---

## Quick Start

```ts
import { Rain } from '@buidlrrr/rain-sdk';

const rain = new Rain({ environment: 'production' });

// Fetch markets
const markets = await rain.getPublicMarkets({ limit: 10 });

// Build a buy transaction (returns unsigned tx — caller signs and sends)
const rawTx = rain.buildBuyOptionRawTx({
  marketContractAddress: '0x...',
  selectedOption: 1n,
  buyAmountInWei: 10_000_000n, // 10 USDT (6 decimals)
});

// Send via any provider
await provider.sendTransaction(rawTx);
```

---

## Architecture

Two independent classes:

| Class | Purpose | Stateful? | Requires wallet? |
|-------|---------|-----------|-------------------|
| `Rain` | Build transactions, query markets, subscribe to events | No | No |
| `RainAA` | Manage Alchemy smart accounts, sign & send transactions | Yes | Yes |

All transaction builders return `RawTransaction`:

```ts
interface RawTransaction {
  to: `0x${string}`;
  data: `0x${string}`;
  value?: bigint;
}
```

The caller decides how to execute (via `RainAA`, wagmi, ethers, viem, or any provider).

---

## Constructor

```ts
const rain = new Rain(config?: RainCoreConfig);
```

```ts
interface RainCoreConfig {
  environment?: 'development' | 'stage' | 'production'; // default: 'production'
  rpcUrl?: string;              // defaults to public Arbitrum RPCs
  apiUrl?: string;              // auto-set from environment
  subgraphUrl?: string;         // required for tx history, price history, analytics
  subgraphApiKey?: string;      // TheGraph API key
  wsRpcUrl?: string;            // required for WebSocket subscriptions
  wsReconnect?: boolean | { attempts?: number; delay?: number };
}
```

### Environments

| Environment   | API URL                  | Factory Address                              | Dispute Timer |
|---------------|--------------------------|----------------------------------------------|---------------|
| `development` | `https://dev-api.rain.one`  | `0x05b1fd504583B81bd14c368d59E8c3e354b6C1dc` | 60s           |
| `stage`       | `https://stg-api.rain.one`  | `0xD4900CA167228365806FBA4cB21f7EAe8b6d96BE` | 60s           |
| `production`  | `https://prod-api.rain.one` | `0xA8640B62D755e42C9ed6A86d0fc65CE09e31F264` | 7200s (2h)    |

### Default RPCs (randomly selected)

- `https://arb1.arbitrum.io/rpc`
- `https://arbitrum-one.publicnode.com`
- `https://rpc.sentio.xyz/arbitrum-one`

### Subgraph URLs (auto-set from environment)

- development: `https://gateway.thegraph.com/api/subgraphs/id/6r5tgnziCSykNHkD3yrEz1wohCz2NWqADtSH7azLmTh1`
- stage: `https://gateway.thegraph.com/api/subgraphs/id/4eW9fojV2FcAm8xvhW4SGHoy17VEPmKMqz3K3b6PEhHR`
- production: `https://gateway.thegraph.com/api/subgraphs/id/poBixDnF3hyafnLs9i1qkCpFppAAgmmWYgtsXrfYAWQ`

---

## Data Sources

| Source       | Methods                                                                      | Config                           |
|--------------|------------------------------------------------------------------------------|----------------------------------|
| **Rain API** | `getPublicMarkets`, `getMarketDetails` (partial), `buildClaimTx`, `buildCreateMarketTx` | `environment` (auto)             |
| **On-chain** | `getMarketPrices`, `getMarketVolume`, `getPositions`, all tx builders        | `rpcUrl` (auto-selected)         |
| **Subgraph** | `getTransactions`, `getPriceHistory`, `getPnL`, `getLeaderboard`             | `subgraphUrl` + `subgraphApiKey` |

Methods requiring the subgraph throw if `subgraphUrl` is not configured.

---

## Complete Method Reference

### Market Queries

#### `getPublicMarkets(params)` → `Promise<Market[]>`

Browse and filter markets.

```ts
const markets = await rain.getPublicMarkets({
  limit: 12,         // optional, number of results
  offset: 0,         // optional, pagination offset
  sortBy: 'Liquidity', // 'Liquidity' | 'Volumn' | 'latest'
  status: 'Live',    // 'Live' | 'New' | 'WaitingForResult' | 'UnderDispute' | 'UnderAppeal' | 'ClosingSoon' | 'InReview' | 'InEvaluation' | 'Closed' | 'Trading'
  creator: '0x...',  // optional, filter by creator address
});
```

Returns:
```ts
interface Market {
  id: string;                      // MongoDB-style ID (e.g., '698c8f116e985bbfacc7fc01')
  title: string;
  totalVolume: string;
  status: MarketStatus;
  poolOwnerWalletAddress?: string;
  contractAddress?: string;        // Diamond proxy address on Arbitrum
}
```

---

#### `getMarketDetails(marketId)` → `Promise<MarketDetails>`

Full market data combining API + on-chain reads.

```ts
const details = await rain.getMarketDetails('698c8f116e985bbfacc7fc01');
```

Returns:
```ts
interface MarketDetails {
  id: string;
  title: string;
  status: MarketStatus;
  contractAddress: `0x${string}`;
  options: MarketOption[];            // per-option data
  poolState: number;
  numberOfOptions: bigint;
  startTime: bigint;                  // unix timestamp (seconds)
  endTime: bigint;
  oracleEndTime: bigint;
  allFunds: bigint;                   // total funds in base token wei
  allVotes: bigint;
  totalLiquidity: bigint;
  winner: bigint;                     // 0 = no winner yet
  poolFinalized: boolean;
  isPublic: boolean;
  baseToken: `0x${string}`;
  baseTokenDecimals: bigint;
  poolOwner: `0x${string}`;
  resolver: `0x${string}`;
  resolverIsAI: boolean;
  isDisputed: boolean;
  isAppealed: boolean;
}

interface MarketOption {
  choiceIndex: number;               // 0-indexed
  optionName: string;
  currentPrice: bigint;              // 1e18 scale (divide by 1e18 for decimal, e.g., 650000000000000000 = 0.65 = 65%)
  totalFunds: bigint;                // base token wei
  totalVotes: bigint;
}
```

---

#### `getMarketPrices(marketId)` → `Promise<OptionPrice[]>`

Current option prices from on-chain AMM.

```ts
const prices = await rain.getMarketPrices('698c8f116e985bbfacc7fc01');
```

Returns:
```ts
interface OptionPrice {
  choiceIndex: number;
  optionName: string;
  currentPrice: bigint;   // 1e18 scale
}
```

**Price interpretation**: `currentPrice` is in 1e18. Divide by `1e18` for decimal. Example: `650000000000000000n` = 0.65 = 65% implied probability.

---

#### `getMarketVolume(marketId)` → `Promise<MarketVolume>`

```ts
const volume = await rain.getMarketVolume('698c8f116e985bbfacc7fc01');
```

Returns:
```ts
interface MarketVolume {
  marketId: string;
  contractAddress: `0x${string}`;
  totalVolume: bigint;
  optionVolumes: { choiceIndex: number; optionName: string; volume: bigint }[];
}
```

---

#### `getMarketLiquidity(marketId)` → `Promise<MarketLiquidity>`

```ts
const liq = await rain.getMarketLiquidity('698c8f116e985bbfacc7fc01');
```

Returns:
```ts
interface MarketLiquidity {
  marketId: string;
  contractAddress: `0x${string}`;
  totalLiquidity: bigint;
  allFunds: bigint;
  optionLiquidity: {
    choiceIndex: number;
    optionName: string;
    totalFunds: bigint;
    firstBuyOrderPrice: bigint;
    firstSellOrderPrice: bigint;
  }[];
}
```

---

#### `getMarketAddress(marketId)` → `Promise<\`0x${string}\`>`

Look up the on-chain contract address for a market ID.

```ts
const address = await rain.getMarketAddress('698c8f116e985bbfacc7fc01');
```

---

#### `getMarketId(marketAddress)` → `Promise<string>`

Reverse lookup: contract address → market ID.

```ts
const id = await rain.getMarketId('0xd262abd3d58038e15736Ec32c4F7b020C2B21dB5');
```

---

#### `getProtocolStats()` → `Promise<ProtocolStats>`

Protocol-wide metrics.

```ts
const stats = await rain.getProtocolStats();
```

Returns:
```ts
interface ProtocolStats {
  tvl: bigint;
  totalVolume: bigint;
  activeMarkets: number;
  totalMarkets: number;
  uniqueTraders: number;
}
```

---

### Transaction Builders

All builders return `RawTransaction` (`{ to, data, value? }`). They do **not** send transactions. The caller signs and sends.

#### `buildApprovalTx(params)` → `RawTransaction`

ERC20 approve. Call before any operation that spends tokens on a market contract.

```ts
const tx = rain.buildApprovalTx({
  tokenAddress: '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9' as `0x${string}`, // USDT on Arbitrum
  spender: '0x...' as `0x${string}`,    // market contract address
  amount: 100_000_000n,                 // optional — defaults to max uint256
});
```

---

#### `buildCreateMarketTx(params)` → `Promise<RawTransaction[]>`

Create a new prediction market. Returns `[approveTx, createTx]` if approval needed, or `[createTx]` if already approved.

```ts
const txs = await rain.buildCreateMarketTx({
  marketQuestion: 'Will BTC hit 100k?',
  marketOptions: ['Yes', 'No', 'Maybe'],       // 3-26 options (minimum 3)
  marketTags: ['crypto', 'bitcoin'],            // 1-3 tags
  marketDescription: 'Prediction market for BTC price',
  isPublic: true,
  isPublicPoolResolverAi: false,
  creator: '0x...' as `0x${string}`,
  startTime: 1770836400n,                       // unix timestamp (seconds, bigint)
  endTime: 1770922800n,                         // must be after startTime
  no_of_options: 3n,                            // must match marketOptions.length
  inputAmountWei: 100_000_000n,                 // initial liquidity in base token wei (min 10 tokens)
  barValues: [34, 33, 33],                      // initial probability distribution (%), should sum to ~100
  baseToken: '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9' as `0x${string}`, // USDT
  tokenDecimals: 6,                             // optional, defaults to 6
});

// Execute sequentially — order matters
for (const tx of txs) {
  await provider.sendTransaction(tx);
}
```

**Validation rules**:
- `marketOptions`: 3-26 items, no empty values
- `marketTags`: 1-3 items, no empty values
- `startTime` < `endTime`
- `inputAmountWei` ≥ 10 tokens (e.g., 10_000_000 for 6-decimal token)

---

#### `buildBuyOptionRawTx(params)` → `RawTransaction`

Market buy — instantly buy shares of an option at AMM price.

```ts
const tx = rain.buildBuyOptionRawTx({
  marketContractAddress: '0x...' as `0x${string}`,
  selectedOption: 1n,           // 0-indexed option (bigint)
  buyAmountInWei: 10_000_000n,  // 10 USDT in base token wei
});
```

**Important**: Caller must have sufficient token approval on the market contract first. Use `buildApprovalTx` if needed.

---

#### `buildLimitBuyOptionTx(params)` → `RawTransaction`

Place a limit buy order at a specific price.

```ts
const tx = rain.buildLimitBuyOptionTx({
  marketContractAddress: '0x...' as `0x${string}`,
  selectedOption: 1,                         // 0-indexed (number)
  pricePerShare: 500000000000000000n,        // 0.50 in 1e18 scale
  buyAmountInWei: 10_000_000n,               // base token wei
  tokenDecimals: 6,                          // optional, defaults to 6
});
```

---

#### `buildSellOptionTx(params)` → `RawTransaction`

Place a sell order for shares you hold.

```ts
const tx = rain.buildSellOptionTx({
  marketContractAddress: '0x...' as `0x${string}`,
  selectedOption: 1,          // 0-indexed (number)
  pricePerShare: 0.75,        // target price as decimal (0 < price < 1)
  shares: 5_000_000n,         // shares to sell (bigint)
  tokenDecimals: 6,           // optional, defaults to 6
});
```

---

#### `buildCancelBuyOrdersTx(params)` → `RawTransaction`

Cancel one or more open buy orders.

```ts
const tx = rain.buildCancelBuyOrdersTx({
  marketContractAddress: '0x...' as `0x${string}`,
  orders: [
    { option: 1, price: 0.5, orderID: 1n },
    { option: 1, price: 0.6, orderID: 2n },
  ],
});
```

---

#### `buildCancelSellOrdersTx(params)` → `RawTransaction`

Cancel one or more open sell orders. Same interface as `buildCancelBuyOrdersTx`.

```ts
const tx = rain.buildCancelSellOrdersTx({
  marketContractAddress: '0x...' as `0x${string}`,
  orders: [{ option: 1, price: 0.75, orderID: 3n }],
});
```

---

#### `buildAddLiquidityTx(params)` → `RawTransaction`

Provide liquidity to a market. Liquidity is locked until market resolution.

```ts
const tx = rain.buildAddLiquidityTx({
  marketContractAddress: '0x...' as `0x${string}`,
  liquidityAmountInWei: 100_000_000n, // 100 USDT
});
```

**Note**: There is no `removeLiquidity`. LPs recover their share via `buildClaimTx` after market resolution.

---

#### `buildClaimTx(params)` → `Promise<RawTransaction>`

Claim winnings after market resolution.

```ts
const tx = await rain.buildClaimTx({
  marketId: '698c8f116e985bbfacc7fc01',
  walletAddress: '0x...' as `0x${string}`,
});
```

---

#### `buildCloseMarketTx(params)` → `Promise<RawTransaction>`

Close a market (admin/resolver only). First step of resolution.

```ts
const tx = await rain.buildCloseMarketTx({
  marketId: '698c8f116e985bbfacc7fc01',
});
```

---

#### `buildChooseWinnerTx(params)` → `Promise<RawTransaction>`

Choose the winning option (admin/resolver only). Second step of resolution.

```ts
const tx = await rain.buildChooseWinnerTx({
  marketId: '698c8f116e985bbfacc7fc01',
  winningOption: 1, // 1-indexed (not 0-indexed)
});
```

---

#### `buildResolveMarketTx(params)` → `Promise<RawTransaction[]>`

Combined close + choose winner. Returns array of transactions to execute sequentially.

```ts
const txs = await rain.buildResolveMarketTx({
  marketId: '698c8f116e985bbfacc7fc01',
  winningOption: 1, // 1-indexed
});

for (const tx of txs) {
  await provider.sendTransaction(tx);
}
```

---

#### `buildDepositToSmartAccountTx(params)` → `RawTransaction`

Transfer tokens from EOA to smart account (ERC20 transfer).

```ts
const tx = rain.buildDepositToSmartAccountTx({
  tokenAddress: '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9' as `0x${string}`,
  smartAccountAddress: '0x...' as `0x${string}`,
  amount: 50_000_000n,
});
```

---

#### `buildWithdrawFromSmartAccountTx(params)` → `RawTransaction`

Transfer tokens from smart account back to EOA.

```ts
const tx = rain.buildWithdrawFromSmartAccountTx({
  tokenAddress: '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9' as `0x${string}`,
  eoaAddress: '0x...' as `0x${string}`,
  amount: 50_000_000n,
});
```

---

### Positions & Portfolio

#### `getPositions(address)` → `Promise<PositionsResult>`

All positions across all markets for a wallet.

```ts
const positions = await rain.getPositions('0x...' as `0x${string}`);
```

Returns:
```ts
interface PositionsResult {
  address: `0x${string}`;
  markets: MarketPosition[];
}

interface MarketPosition {
  marketId: string;
  title: string;
  status: string;
  contractAddress: `0x${string}`;
  options: OptionPosition[];
  userLiquidity: bigint;
  claimed: boolean;
  dynamicPayout: bigint[];  // per-option: payout if that option wins (base token wei)
}

interface OptionPosition {
  choiceIndex: number;
  optionName: string;
  shares: bigint;
  sharesInEscrow: bigint;   // shares locked in open sell orders
  amountInEscrow: bigint;   // base token locked in open buy orders
  currentPrice: bigint;     // 1e18 scale
}
```

**`dynamicPayout` interpretation**: Array indexed by option. Example: `[0, 804164316, 0, 0]` means ~804 USDT payout if option 1 wins.

---

#### `getPositionByMarket(address, marketId)` → `Promise<PositionByMarket>`

Single market position for a wallet.

```ts
const pos = await rain.getPositionByMarket('0x...' as `0x${string}`, '698c8f116e985bbfacc7fc01');
```

Returns same shape as a single `MarketPosition`.

---

#### `getLPPosition(address, marketId)` → `Promise<LPPosition>`

LP position details for a wallet on a specific market.

```ts
const lp = await rain.getLPPosition('0x...' as `0x${string}`, '698c8f116e985bbfacc7fc01');
```

Returns:
```ts
interface LPPosition {
  marketId: string;
  title: string;
  status: string;
  contractAddress: `0x${string}`;
  userLiquidity: bigint;
  totalLiquidity: bigint;
  poolShareBps: number;        // basis points (100 = 1%)
  liquidityShareBps: bigint;
}
```

---

#### `getPortfolioValue(params)` → `Promise<PortfolioValue>`

Aggregate portfolio: token balances + position values.

```ts
const portfolio = await rain.getPortfolioValue({
  address: '0x...' as `0x${string}`,
  tokenAddresses: ['0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9' as `0x${string}`],
});
```

Returns:
```ts
interface PortfolioValue {
  address: `0x${string}`;
  tokenBalances: TokenBalance[];
  positions: MarketPositionValue[];
  totalPositionValue: bigint;
}

interface MarketPositionValue {
  marketId: string;
  title: string;
  status: string;
  contractAddress: `0x${string}`;
  dynamicPayout: bigint[];
  totalPositionValue: bigint;
}
```

---

### Account Management

#### `getSmartAccountBalance(params)` → `Promise<AccountBalanceResult>`

Token balances for any address (works for both EOA and smart accounts).

```ts
const balance = await rain.getSmartAccountBalance({
  address: '0x...' as `0x${string}`,
  tokenAddresses: ['0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9' as `0x${string}`],
});
```

Returns:
```ts
interface AccountBalanceResult {
  address: `0x${string}`;
  nativeBalance: bigint;
  formattedNativeBalance: string;
  tokenBalances: TokenBalance[];
}

interface TokenBalance {
  tokenAddress: `0x${string}`;
  symbol: string;
  decimals: number;
  balance: bigint;
  formattedBalance: string;
}
```

---

#### `getEOAFromSmartAccount(smartAccountAddress)` → `Promise<\`0x${string}\`>`

Reverse lookup: smart account → EOA that owns it.

```ts
const eoa = await rain.getEOAFromSmartAccount('0x...' as `0x${string}`);
```

---

### Transaction History

**Requires** `subgraphUrl` in constructor config (or per-method override).

#### `getTransactions(params)` → `Promise<TransactionsResult>`

Wallet transaction history across all markets.

```ts
const txs = await rain.getTransactions({
  address: '0x...' as `0x${string}`,
  first: 20,
  skip: 0,
  orderDirection: 'desc',
  // Optional filters:
  marketAddress: '0x...' as `0x${string}`,
  types: ['buy', 'limit_buy_placed'],
  fromTimestamp: 1700000000n,
  toTimestamp: 1710000000n,
});
```

Transaction types: `'buy' | 'limit_buy_placed' | 'limit_sell_placed' | 'limit_buy_filled' | 'limit_sell_filled' | 'cancel_buy' | 'cancel_sell' | 'add_liquidity' | 'claim'`

Returns:
```ts
interface TransactionsResult {
  address: `0x${string}`;
  transactions: Transaction[];
  total: number;
}

interface Transaction {
  type: TransactionType;
  id: string;
  marketAddress: `0x${string}`;
  transactionHash: `0x${string}`;
  blockNumber: bigint;
  timestamp: bigint;
  wallet: `0x${string}`;
  option?: number;
  baseAmount?: bigint;
  optionAmount?: bigint;
  price?: bigint;
  orderId?: number;
  maker?: `0x${string}`;
  taker?: `0x${string}`;
  winnerOption?: number;
  reward?: bigint;
  liquidityReward?: bigint;
  totalReward?: bigint;
}
```

---

#### `getTransactionDetails(params)` → `Promise<TransactionDetails>`

Decode a single transaction by hash.

```ts
const details = await rain.getTransactionDetails({
  transactionHash: '0x...' as `0x${string}`,
});
```

Returns:
```ts
interface TransactionDetails {
  transactionHash: `0x${string}`;
  blockNumber: bigint;
  timestamp: bigint;
  from: `0x${string}`;
  to: `0x${string}`;
  status: 'success' | 'failed';
  gasUsed: bigint;
  effectiveGasPrice: bigint;
  events: Transaction[];
}
```

---

#### `getMarketTransactions(params)` → `Promise<MarketTransactionsResult>`

All trades on a specific market.

```ts
const trades = await rain.getMarketTransactions({
  marketAddress: '0x...' as `0x${string}`,
  first: 50,
});
```

---

#### `getTradeHistory(params)` → `Promise<TradeHistoryResult>`

A specific user's trades on a specific market.

```ts
const history = await rain.getTradeHistory({
  address: '0x...' as `0x${string}`,
  marketAddress: '0x...' as `0x${string}`,
});
```

---

### Analytics

#### `getPriceHistory(params)` → `Promise<PriceHistoryResult>`

OHLCV candle data for a market option. Requires subgraph.

```ts
const candles = await rain.getPriceHistory({
  marketId: '698c8f116e985bbfacc7fc01',
  optionIndex: 0,
  interval: '1h',  // '1m' | '5m' | '15m' | '1h' | '4h' | '1d' | '1w'
  // Optional:
  from: 1700000000n,
  to: 1710000000n,
  limit: 100,
});
```

Returns:
```ts
interface PriceHistoryResult {
  marketId: string;
  marketAddress: `0x${string}`;
  optionIndex: number;
  interval: PriceHistoryInterval;
  candles: PriceCandle[];
}

interface PriceCandle {
  timestamp: bigint;
  open: bigint;     // 1e18 scale
  high: bigint;
  low: bigint;
  close: bigint;
  volume: bigint;   // base token wei
  trades: number;
}
```

---

#### `getPnL(params)` → `Promise<PnLResult>`

Realized and unrealized P&L. Requires subgraph.

```ts
const pnl = await rain.getPnL({
  address: '0x...' as `0x${string}`,
  marketAddress: '0x...' as `0x${string}`, // optional — omit for aggregate
});
```

Returns:
```ts
interface PnLResult {
  address: `0x${string}`;
  markets: MarketPnL[];
  totalRealizedPnL: bigint;
  totalUnrealizedPnL: bigint;
  totalPnL: bigint;
  formatted: {
    totalRealizedPnL: string;
    totalUnrealizedPnL: string;
    totalPnL: string;
  };
}

interface MarketPnL {
  marketId: string;
  title: string;
  status: string;
  contractAddress: `0x${string}`;
  baseTokenDecimals: number;
  options: OptionPnL[];
  claimed: boolean;
  claimReward: bigint;
  liquidityCost: bigint;
  liquidityReward: bigint;
  totalCostBasis: bigint;
  totalCurrentValue: bigint;
  realizedPnL: bigint;
  unrealizedPnL: bigint;
  totalPnL: bigint;
  formatted: { /* same fields as string */ };
}

interface OptionPnL {
  choiceIndex: number;
  optionName: string;
  buyShares: bigint;
  buyCost: bigint;
  sellShares: bigint;
  sellProceeds: bigint;
  currentShares: bigint;
  currentValue: bigint;
  costBasis: bigint;
  realizedPnL: bigint;
  unrealizedPnL: bigint;
  formatted: { /* same fields as string */ };
}
```

---

#### `getLeaderboard(params)` → `Promise<LeaderboardResult>`

Top traders. Requires subgraph.

```ts
const leaders = await rain.getLeaderboard({
  timeframe: '7d',   // '24h' | '7d' | '30d' | 'all-time'
  sortBy: 'volume',  // currently only 'volume'
  limit: 10,
});
```

Returns:
```ts
interface LeaderboardResult {
  timeframe: LeaderboardTimeframe;
  entries: LeaderboardEntry[];
  totalTraders: number;
  generatedAt: number;
}

interface LeaderboardEntry {
  rank: number;
  address: `0x${string}`;
  totalVolume: bigint;
  tradesCount: number;
  marketsTraded: number;
  formatted: { totalVolume: string };
}
```

---

### WebSocket Subscriptions

Require `wsRpcUrl` in constructor config.

#### `subscribeToMarketEvents(params)` → `Unsubscribe`

Live on-chain events from a market.

```ts
const rain = new Rain({
  environment: 'production',
  wsRpcUrl: 'wss://arbitrum-one-rpc.publicnode.com',
});

const unsubscribe = rain.subscribeToMarketEvents({
  marketAddress: '0x...' as `0x${string}`,
  eventNames: ['EnterOption', 'Sync'],  // optional filter — omit for all events
  onEvent: (event) => {
    console.log(event.eventName, event.args);
  },
  onError: (err) => console.error(err),
});

// Stop listening
unsubscribe();
```

Event names:

| Category   | Events                                                                                        |
|------------|-----------------------------------------------------------------------------------------------|
| Trades     | `EnterOption`, `PlaceBuyOrder`, `PlaceSellOrder`, `ExecuteBuyOrder`, `ExecuteSellOrder`, `CancelBuyOrder`, `CancelSellOrder` |
| Price sync | `Sync` — AMM reserve rebalance (emitted once per option pair per trade)                       |
| Lifecycle  | `Claim`, `ChooseWinner`, `ClosePool`                                                          |

Event payload:
```ts
interface MarketTradeEvent {
  eventName: MarketEventName;
  marketAddress: `0x${string}`;
  blockNumber: bigint;
  transactionHash: `0x${string}`;
  logIndex: number;
  args: Record<string, unknown>;
}
```

---

#### `subscribePriceUpdates(params)` → `Unsubscribe`

Real-time price feed — fires after each trade with updated option prices.

```ts
const unsubscribe = rain.subscribePriceUpdates({
  marketAddress: '0x...' as `0x${string}`,
  onPriceUpdate: (update) => {
    // update.prices: OptionPrice[] — fresh prices
    // update.triggeredBy: MarketTradeEvent — the event that caused the update
    console.log(update.prices);
  },
  onError: (err) => console.error(err),
});
```

---

#### `destroyWebSocket()` → `Promise<void>`

Clean up WebSocket connections.

```ts
await rain.destroyWebSocket();
```

---

## RainAA — Account Abstraction

Manages Alchemy smart accounts with gas sponsorship.

### Constructor

```ts
import { RainAA } from '@buidlrrr/rain-sdk';
import { arbitrum } from 'viem/chains';

const rainAA = new RainAA({
  walletClient: yourWalletClient,       // viem WalletClient
  alchemyApiKey: 'your-alchemy-key',
  paymasterPolicyId: 'your-policy-id',
  chain: arbitrum,
  rpcUrl: 'https://...',               // optional
});
```

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `connect()` | `Promise<\`0x${string}\`>` | Initialize smart account, returns address |
| `sendTransaction(rawTx)` | `Promise<\`0x${string}\`>` | Send a `RawTransaction`, returns tx hash |
| `disconnect()` | `void` | Reset connection |
| `.address` | `\`0x${string}\`` | Smart account address (throws if not connected) |
| `.client` | Smart wallet client | Underlying AA client (throws if not connected) |

### Typical Flow: Rain + RainAA

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

## Common Patterns

### Buy shares with approval check

```ts
const rain = new Rain({ environment: 'production' });
const marketAddress = '0x...' as `0x${string}`;
const tokenAddress = '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9' as `0x${string}`;
const amount = 10_000_000n; // 10 USDT

// 1. Approve token spending (idempotent — safe to call even if already approved)
const approveTx = rain.buildApprovalTx({
  tokenAddress,
  spender: marketAddress,
});
await provider.sendTransaction(approveTx);

// 2. Buy option
const buyTx = rain.buildBuyOptionRawTx({
  marketContractAddress: marketAddress,
  selectedOption: 0n,
  buyAmountInWei: amount,
});
await provider.sendTransaction(buyTx);
```

### Create market end-to-end

```ts
const rain = new Rain({ environment: 'production' });

const txs = await rain.buildCreateMarketTx({
  marketQuestion: 'Will ETH flip BTC by 2026?',
  marketOptions: ['Yes', 'No', 'Unlikely'],
  marketTags: ['crypto'],
  marketDescription: 'Market for ETH flippening prediction',
  isPublic: true,
  isPublicPoolResolverAi: false,
  creator: '0x...' as `0x${string}`,
  startTime: BigInt(Math.floor(Date.now() / 1000) + 3600),     // 1 hour from now
  endTime: BigInt(Math.floor(Date.now() / 1000) + 604800),     // 1 week from now
  no_of_options: 3n,
  inputAmountWei: 100_000_000n,  // 100 USDT initial liquidity
  barValues: [34, 33, 33],
  baseToken: '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9' as `0x${string}`,
  tokenDecimals: 6,
});

// Execute all transactions in order
for (const tx of txs) {
  const hash = await provider.sendTransaction(tx);
  await provider.waitForTransactionReceipt({ hash });
}
```

### Full analytics dashboard

```ts
const rain = new Rain({
  environment: 'production',
  subgraphUrl: 'https://gateway.thegraph.com/api/subgraphs/id/poBixDnF3hyafnLs9i1qkCpFppAAgmmWYgtsXrfYAWQ',
  subgraphApiKey: 'your-key',
});

const [stats, markets, leaderboard] = await Promise.all([
  rain.getProtocolStats(),
  rain.getPublicMarkets({ limit: 10, sortBy: 'Liquidity', status: 'Live' }),
  rain.getLeaderboard({ timeframe: '7d', sortBy: 'volume', limit: 10 }),
]);
```

---

## Key Conventions

- **Prices** are in `1e18` scale (bigint). Divide by `10n ** 18n` for decimal.
- **Token amounts** are in base token wei. USDT on Arbitrum = 6 decimals, so `10_000_000n` = 10 USDT.
- **Market IDs** are MongoDB-style strings (e.g., `'698c8f116e985bbfacc7fc01'`).
- **Option indices** are 0-indexed everywhere except `buildChooseWinnerTx` and `buildResolveMarketTx` where `winningOption` is 1-indexed.
- **Timestamps** are unix seconds as `bigint`.
- **All addresses** use viem's `\`0x${string}\`` type.
- The SDK never sends transactions — it only builds unsigned `RawTransaction` objects.

## Common Token Addresses (Arbitrum One)

| Token | Address |
|-------|---------|
| USDT  | `0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9` |
| USDC  | `0xaf88d065e77c8cC2239327C5EDb3A432268e5831` |
