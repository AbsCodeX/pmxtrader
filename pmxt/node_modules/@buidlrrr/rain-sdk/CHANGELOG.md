# Changelog

## 2.0.0

### Breaking

- **`Rain.buildApprovalTx` requires an explicit `amount`** — The previous default of `ethers.MaxUint256` has been removed. Infinite approvals defeat spending-cap enforcement in ERC-4337 session-key policies (e.g. Alchemy Modular Account v2's `erc20-token-transfer` permission), forcing integrators onto weaker `functions-on-contract` permissions with no spend tracking. Callers must now pass the exact required amount per call. `ApproveTxParams.amount` is now a required `bigint`; values `<= 0n` are rejected. Internal callers in `buildCreateMarketTx` and `buildDisputeTx`/`buildAppealTx` now pass the exact required amount automatically.

---

## 1.1.2

### Fixes

- **Lazy-load account-kit deps** — `@account-kit/infra`, `@account-kit/wallet-client`, and `@alchemy/aa-core` are now dynamically imported inside `RainAA.connect()` instead of at the top level. Server-side consumers who only need the stateless `Rain` class can now import the SDK without installing browser-only account-kit dependencies.

---

## 1.1.1

### Fixes

- Updated deployer addresses to new contracts

---

## 1.1.0

### New Features

- **Dispute, Appeal & Extend Time** — `buildDisputeTx`, `buildAppealTx`, `buildExtendTimeTx` for post-resolution flows
- **Cancel All Orders** — `buildCancelAllOrdersTx` to batch-cancel all open orders on a market
- **Login** — `login` method for wallet-based authentication
- **RainSocket** — real-time WebSocket client via `socket.io` for live market updates
- **getUserInvestments** — fetch all investments for a wallet across markets
- **getMarketById** — fetch market details by MongoDB ID directly

### AI Agent Tools

- Added focused Claude Code skills for market creation, trading, and data queries (`skills/`)
- Added Claude Code skill package (`rain-sdk.skill`)

### Fixes

- Added `zod` as dependency for AA SDK peer resolution

---

## 1.0.3

### AI Agent Support

- Added `AGENTS.md` — machine-readable reference for AI coding agents with full method signatures, types, and examples

---

## 1.0.2

### Breaking

- Renamed package from `rain-sdk` to `@buidlrrr/rain-sdk`

---

## 1.0.1

### New Features

- **Market Queries** — `getPublicMarkets`, `getMarketDetails`, `getMarketPrices`, `getMarketVolume`, `getMarketLiquidity`, `getMarketAddress`, `getMarketId`, `getProtocolStats`
- **Positions** — `getPositions`, `getPositionByMarket`, `getLPPosition`, `getPortfolioValue`
- **Trading** — `buildBuyOptionRawTx`, `buildLimitBuyOptionTx`, `buildSellOptionTx`, `buildCancelBuyOrdersTx`, `buildCancelSellOrdersTx`
- **Liquidity** — `buildAddLiquidityTx`
- **Resolution** — `buildCloseMarketTx`, `buildChooseWinnerTx`, `buildResolveMarketTx`
- **Claims** — `buildClaimTx`
- **Smart Accounts** — `getSmartAccountBalance`, `getEOAFromSmartAccount`, `buildDepositToSmartAccountTx`, `buildWithdrawFromSmartAccountTx`
- **Transaction History** — `getTransactions`, `getTransactionDetails`, `getMarketTransactions`, `getTradeHistory` (subgraph)
- **Analytics** — `getPriceHistory` (OHLCV candles), `getPnL`, `getLeaderboard` (subgraph)
- **WebSocket** — `subscribeToMarketEvents`, `subscribePriceUpdates`, `destroyWebSocket`
- **Approval** — `buildApprovalTx`
- **Market Creation** — `buildCreateMarketTx` with IPFS metadata upload

### Infrastructure

- Multicall utility for batched on-chain reads
- Per-environment subgraph URLs and default RPC endpoints
- 137 unit tests via vitest

---

## 1.0.0

Initial release. Core transaction builders for buy, limit buy, claim, and market creation.
