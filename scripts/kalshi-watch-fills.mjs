#!/usr/bin/env node
/**
 * Stream authenticated Kalshi user fill notifications over WebSocket.
 * Channel: "fill" — https://docs.kalshi.com/websockets/user-fills
 *
 * PMXT Kalshi watch:* does not expose user fills yet; this script talks to
 * Kalshi directly using credentials from pmxt/.env.
 */
import crypto from "crypto";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { createRequire } from "module";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const ENV_FILE = path.join(ROOT, "pmxt", ".env");

const require = createRequire(import.meta.url);
const WebSocket = require(path.join(ROOT, "pmxt", "node_modules", "ws"));
const dotenv = require(path.join(ROOT, "pmxt", "node_modules", "dotenv"));

const PROD_WS = "wss://external-api-ws.kalshi.com/trade-api/ws/v2";
const DEMO_WS = "wss://external-api-ws.demo.kalshi.co/trade-api/ws/v2";

function loadKalshiEnv() {
  dotenv.config({ path: ENV_FILE, quiet: true });
}

function signRequest(privateKey, timestamp, method, wsPath) {
  const payload = `${timestamp}${method}${wsPath}`;
  const key = privateKey.includes("\\n")
    ? privateKey.replace(/\\n/g, "\n")
    : privateKey;
  const signer = crypto.createSign("SHA256");
  signer.update(payload);
  return signer.sign(
    {
      key,
      padding: crypto.constants.RSA_PKCS1_PSS_PADDING,
      saltLength: crypto.constants.RSA_PSS_SALTLEN_DIGEST,
    },
    "base64",
  );
}

function parseArgs(argv) {
  const opts = {
    marketTickers: [],
    maxMessages: undefined,
    timeoutMs: undefined,
    alertFile: undefined,
    demo: false,
    compact: false,
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    switch (arg) {
      case "--market-ticker":
      case "--market":
        opts.marketTickers.push(argv[++i]);
        break;
      case "--max-messages":
        opts.maxMessages = Number(argv[++i]);
        break;
      case "--timeout-ms":
        opts.timeoutMs = Number(argv[++i]);
        break;
      case "--alert-file":
        opts.alertFile = argv[++i];
        break;
      case "--demo":
        opts.demo = true;
        break;
      case "--compact":
        opts.compact = true;
        break;
      case "--help":
      case "-h":
        printHelp();
        process.exit(0);
        break;
      default:
        throw new Error(`Unknown argument: ${arg}`);
    }
  }
  return opts;
}

function printHelp() {
  console.log(`Usage: kalshi-watch-fills.mjs [options]

Options:
  --market-ticker TICKER   Filter fills to one market (repeatable)
  --max-messages N         Exit after N fill events
  --timeout-ms MS          Exit if no fill within MS (still verifies subscribe)
  --alert-file PATH        Append JSONL fill records to PATH
  --demo                   Use Kalshi demo WebSocket endpoint
  --compact                Print one-line summaries instead of JSON
`);
}

function normalizeFill(message) {
  const data = message.data || message.msg || {};
  const priceRaw =
    data.yes_price_dollars ??
    data.yes_price ??
    data.price_dollars ??
    data.price;
  const amountRaw = data.count_fp ?? data.count ?? data.quantity;
  const tsMs =
    data.ts_ms ??
    (data.ts ? Number(data.ts) * (Number(data.ts) < 1e11 ? 1000 : 1) : undefined) ??
    (data.created_time ? Date.parse(data.created_time) : undefined) ??
    Date.now();

  const side =
    data.action === "buy" || data.action === "sell"
      ? data.action
      : data.side === "yes"
        ? "buy"
        : data.side === "no"
          ? "sell"
          : "unknown";

  return {
    ts: new Date(tsMs).toISOString(),
    type: "fill",
    fillId: data.trade_id || data.fill_id || data.id,
    orderId: data.order_id,
    marketTicker: data.market_ticker || data.ticker,
    side,
    outcomeSide: data.side || data.purchased_side,
    price:
      priceRaw != null
        ? typeof priceRaw === "string"
          ? parseFloat(priceRaw)
          : priceRaw > 1
            ? priceRaw / 100
            : priceRaw
        : null,
    amount:
      amountRaw != null
        ? typeof amountRaw === "string"
          ? parseFloat(amountRaw)
          : amountRaw
        : null,
    isTaker: data.is_taker ?? null,
    postPosition:
      data.post_position_fp != null
        ? parseFloat(data.post_position_fp)
        : data.post_position ?? null,
    subaccount: data.subaccount ?? null,
    source: "kalshi-ws-fill",
    docs: "https://docs.kalshi.com/websockets/user-fills",
  };
}

function formatCompact(fill) {
  return `[${fill.ts}] FILL ${fill.marketTicker} ${fill.side} ${fill.outcomeSide} ${fill.amount} @ ${fill.price}${fill.isTaker ? " (taker)" : ""}`;
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  loadKalshiEnv();
  const apiKey = process.env.KALSHI_API_KEY;
  const privateKey = process.env.KALSHI_PRIVATE_KEY;

  if (!apiKey || !privateKey) {
    console.error("Missing KALSHI_API_KEY or KALSHI_PRIVATE_KEY in pmxt/.env");
    process.exit(1);
  }

  const wsUrl = opts.demo ? DEMO_WS : PROD_WS;
  const wsPath = new URL(wsUrl).pathname;
  const timestamp = Date.now().toString();
  const headers = {
    "KALSHI-ACCESS-KEY": apiKey,
    "KALSHI-ACCESS-TIMESTAMP": timestamp,
    "KALSHI-ACCESS-SIGNATURE": signRequest(privateKey, timestamp, "GET", wsPath),
    "Content-Type": "application/json",
  };

  if (opts.alertFile) {
    fs.mkdirSync(path.dirname(path.resolve(opts.alertFile)), { recursive: true });
  }

  let fillCount = 0;
  let subscribed = false;
  let msgId = 1;
  let timeoutHandle;

  const finish = (code = 0) => {
    if (timeoutHandle) clearTimeout(timeoutHandle);
    try {
      ws.close();
    } catch {
      /* ignore */
    }
    process.exit(code);
  };

  const ws = new WebSocket(wsUrl, { headers });

  ws.on("open", () => {
    const params = { channels: ["fill"] };
    if (opts.marketTickers.length > 0) {
      params.market_tickers = opts.marketTickers;
    }
    ws.send(
      JSON.stringify({
        id: msgId++,
        cmd: "subscribe",
        params,
      }),
    );
  });

  ws.on("message", (raw) => {
    let message;
    try {
      message = JSON.parse(raw.toString());
    } catch {
      return;
    }

    const msgType = message.type;

    if (msgType === "subscribed") {
      subscribed = true;
      const markets =
        opts.marketTickers.length > 0
          ? opts.marketTickers.join(", ")
          : "all markets";
      console.error(`Subscribed to Kalshi fill channel (${markets})`);
      if (opts.timeoutMs != null && opts.maxMessages == null) {
        timeoutHandle = setTimeout(() => {
          console.error(`No fills within ${opts.timeoutMs}ms — connection OK`);
          finish(0);
        }, opts.timeoutMs);
      }
      return;
    }

    if (msgType === "error") {
      console.error("Kalshi WS error:", message.msg || message.data || message);
      finish(1);
      return;
    }

    if (msgType !== "fill") {
      return;
    }

    if (timeoutHandle) {
      clearTimeout(timeoutHandle);
      timeoutHandle = undefined;
    }

    const fill = normalizeFill(message);
    const line = opts.compact ? formatCompact(fill) : JSON.stringify(fill);
    console.log(line);

    if (opts.alertFile) {
      fs.appendFileSync(opts.alertFile, `${JSON.stringify(fill)}\n`);
    }

    fillCount += 1;
    if (opts.maxMessages != null && fillCount >= opts.maxMessages) {
      finish(0);
    }
  });

  ws.on("error", (err) => {
    console.error(`WebSocket error: ${err.message}`);
    finish(1);
  });

  ws.on("close", () => {
    if (!subscribed) {
      finish(1);
    }
  });

  process.on("SIGINT", () => finish(0));
  process.on("SIGTERM", () => finish(0));
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
