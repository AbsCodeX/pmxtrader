export async function loginUser(params) {
    const { signature, walletAddress, smartWalletAddress, referredBy, apiUrl } = params;
    const res = await fetch(`${apiUrl}/auth/login-or-register-with-walletAddress`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            sign: signature,
            walletAddress,
            userSmartAddress: smartWalletAddress,
            ...(referredBy ? { referredBy } : {}),
        }),
    });
    if (!res.ok) {
        const text = await res.text().catch(() => res.statusText);
        throw new Error(`Login failed (${res.status}): ${text}`);
    }
    const data = await res.json();
    const accessToken = data?.token;
    const userId = data?.user?._id;
    if (!accessToken || !userId) {
        throw new Error('Login response missing token or user id');
    }
    return { accessToken, userId };
}
