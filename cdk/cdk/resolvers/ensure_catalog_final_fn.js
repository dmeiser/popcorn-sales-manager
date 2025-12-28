import { util } from '@aws-appsync/utils';

export function request(ctx) {
    // If catalog already in stash, nothing to do — skip calling data source
    if (ctx.stash && ctx.stash.catalog) {
        return null;
    }

    // If stash already has normalized catalogId, nothing to do (get_catalog will fetch) — skip calling data source
    if (ctx.stash && ctx.stash.catalogId) {
        return null;
    }

    const campaignId = ctx.args.input && ctx.args.input.campaignId;
    if (!campaignId) {
        console.log('EnsureCatalogFinal: no campaignId in args, skipping');
        return null;
    }

    // Query campaignId-index to find the campaign and extract catalogId
    return {
        operation: 'Query',
        index: 'campaignId-index',
        query: {
            expression: 'campaignId = :campaignId',
            expressionValues: util.dynamodb.toMapValues({ ':campaignId': campaignId })
        },
        limit: 1
    };
}

export function response(ctx) {
    if (ctx.error) {
        // Propagate unexpected errors
        util.error(ctx.error.message, ctx.error.type);
    }

    const items = ctx.result && ctx.result.items ? ctx.result.items : [];
    if (items.length === 0) {
        console.log('EnsureCatalogFinal: campaign lookup returned no items for campaignId=', ctx.args && ctx.args.input && ctx.args.input.campaignId);
        return null;
    }

    const campaign = items[0];
    // Normalize catalogId and stash it if present
    if (campaign.catalogId) {
        const rawCatalogId = campaign.catalogId;
        const normalizedCatalogId = (typeof rawCatalogId === 'string' && rawCatalogId.startsWith('CATALOG#')) ? rawCatalogId : 'CATALOG#' + rawCatalogId;
        ctx.stash.catalogId = normalizedCatalogId;
        console.log('EnsureCatalogFinal: Set stash.catalogId to', normalizedCatalogId, 'from campaign', campaign.campaignId);
    } else {
        console.log('EnsureCatalogFinal: campaign has no catalogId', JSON.stringify(campaign));
    }

    ctx.stash.campaign = campaign;
    return campaign;
}
