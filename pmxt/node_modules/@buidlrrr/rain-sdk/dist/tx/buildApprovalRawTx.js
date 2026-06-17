import { encodeFunctionData } from "viem";
import { ERC20Abi } from "../abi/ERC20Abi.js";
import { APPROVE_TOKEN } from "../constants/contractmethods.js";
export function buildApproveRawTx(params) {
    const { tokenAddress, spender, amount } = params;
    if (!tokenAddress)
        throw new Error("token address is required");
    if (!spender)
        throw new Error("spender address is required");
    if (amount === undefined || amount === null) {
        throw new Error("amount is required; pass a finite bigint (infinite approvals are no longer supported)");
    }
    if (amount <= 0n)
        throw new Error("amount must be greater than 0");
    return {
        to: tokenAddress,
        data: encodeFunctionData({
            abi: ERC20Abi,
            functionName: APPROVE_TOKEN,
            args: [spender, amount],
        }),
        value: 0n,
    };
}
