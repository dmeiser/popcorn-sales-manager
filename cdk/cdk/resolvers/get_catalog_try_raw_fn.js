import { util } from '@aws-appsync/utils';

export function request(ctx) {
    // If a catalog is already in stash, skip lookup and do not call the data source
    if (ctx.stash && ctx.stash.catalog) {
        return null;
    }

    const rawCatalogId = ctx.stash.catalogId || (ctx.args && ctx.args.input && ctx.args.input.catalogId);
    if (!rawCatalogId) {
        // Nothing to do here - allow next function to attempt prefixed lookup
        return null;
    }

    // Try direct GetItem with the raw id first
    console.log('GetCatalogTryRaw: attempting raw GetItem for', rawCatalogId);
    return {
        operation: 'GetItem',
        key: util.dynamodb.toMapValues({ catalogId: rawCatalogId }),
        consistentRead: true
    };
}

export function response(ctx) {
    if (ctx.error) {
        // Propagate unexpected errors
        util.error(ctx.error.message, ctx.error.type);
    }

    // If we found an item, stash it for downstream functions and short-circuit
    if (ctx.result && Object.keys(ctx.result).length > 0) {
        console.log('GetCatalogTryRaw: found catalog for', ctx.stash.catalogId || 'raw');
        ctx.stash.catalog = ctx.result;
        return ctx.result;
    }

    // Not found — let the pipeline continue to the prefixed attempt
    // Do not reference variables from the request scope here; use stash or args instead
    console.log('GetCatalogTryRaw: No catalog found for raw id:', ctx.stash && ctx.stash.catalogId ? ctx.stash.catalogId : (ctx.args && ctx.args.input && ctx.args.input.catalogId) || 'unknown');
    return ctx.prev && ctx.prev.result ? ctx.prev.result : null;
}
