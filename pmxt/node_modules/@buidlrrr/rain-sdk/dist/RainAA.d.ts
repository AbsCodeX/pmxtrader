import { RainConfig } from './types.js';
import { RawTransaction } from './tx/types.js';
export declare class RainAA {
    private config;
    private _client;
    private _address;
    constructor(config: RainConfig);
    /**
     * Initializes the Smart Account
     */
    connect(): Promise<`0x${string}`>;
    /**
     * Returns smart account address
     */
    get address(): `0x${string}`;
    /**
     * Returns smart account client
     */
    get client(): any;
    /**
     * Sends a raw transaction from the smart account.
     */
    sendTransaction(rawTx: RawTransaction): Promise<`0x${string}`>;
    /**
     * Reset connection (optional)
     */
    disconnect(): void;
}
