import { util } from '@aws-appsync/utils';

export function request(ctx) {
    const rawCatalogId = ctx.stash.catalogId;
    if (!rawCatalogId) {
        util.error('Catalog ID not found in stash', 'BadRequest');
    }
    // Normalize to DB format: ensure it starts with CATALOG#
    const catalogId = (typeof rawCatalogId === 'string' && rawCatalogId.startsWith('CATALOG#')) ? rawCatalogId : 'CATALOG#' + rawCatalogId;
    // Save normalized id back to stash so downstream functions see the DB key
    ctx.stash.catalogId = catalogId;
    // Direct GetItem on catalogs table
    return {
        operation: 'GetItem',
        key: util.dynamodb.toMapValues({ catalogId: catalogId }),
        consistentRead: true
    };
}

export function response(ctx) {
    if (ctx.error) {
        util.error(ctx.error.message, ctx.error.type);
    }
    if (!ctx.result) {
        // Include the looked-up catalogId in the error to aid debugging
        util.error('Catalog not found for id: ' + ctx.stash.catalogId, 'NotFound');
    }
    
    // Store catalog in stash for CreateOrderFn
    ctx.stash.catalog = ctx.result;
    
    return ctx.result;
}
