export interface LoginParams {
    /** Signed message (personal_sign of the lowercased wallet address) */
    signature: string;
    /** EOA wallet address */
    walletAddress: string;
    /** Smart account / AA wallet address */
    smartWalletAddress: string;
    /** Optional referral code */
    referredBy?: string;
}
export interface LoginResult {
    /** JWT access token */
    accessToken: string;
    /** Backend user ID */
    userId: string;
}
