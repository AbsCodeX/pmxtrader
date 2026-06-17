export function normalizeBarValues(values) {
    const transformedBarValues = [
        ...values.map((value) => Math.floor(value * 100)),
    ];
    const totalRounded = transformedBarValues.reduce((sum, val) => sum + val, 0);
    const difference = 10000 - totalRounded;
    if (difference !== 0) {
        transformedBarValues[transformedBarValues.length - 1] += difference;
    }
    return transformedBarValues;
}
export async function uploadMetaData(params) {
    const { marketQuestion, marketOptions, marketTags, marketDescription, isPublic, isPublicPoolResolverAi, startTime, endTime, no_of_options, creator, apiUrl, } = params;
    const formattedStartDate = new Date(Number(startTime) * 1000).toISOString();
    const formattedEndDate = new Date(Number(endTime) * 1000).toISOString();
    const metadata = {
        question: marketQuestion,
        options: Array.isArray(marketOptions) ? marketOptions : [],
        tags: marketTags,
        isPrivate: !isPublic,
        startDate: formattedStartDate,
        endDate: formattedEndDate,
        poolDescription: marketDescription,
        isAiResolver: isPublicPoolResolverAi,
        contractData: {
            pool_owner: creator,
            start_time: Number(startTime),
            end_time: Number(endTime),
            no_of_options: Number(no_of_options),
        },
    };
    const res = await fetch(`${apiUrl}/ipfs/upload`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(metadata),
    });
    if (!res.ok) {
        throw new Error(`Failed to upload metadata: ${res.status}`);
    }
    const data = await res.json();
    return data?.data?.ipfsHash;
}
