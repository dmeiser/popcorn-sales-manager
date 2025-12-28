import { util } from '@aws-appsync/utils';

export function request(ctx) {
  // No-op request for None datasource
  // Returning null tells AppSync to skip any datasource invocation for this function
  return null;
}

export function response(ctx) {
  // Log helpful diagnostics about final pipeline state
  console.log('LogCreateOrderState: ctx.args=', JSON.stringify(ctx.args || {}));
  console.log('LogCreateOrderState: ctx.identity=', JSON.stringify(ctx.identity || {}));
  console.log('LogCreateOrderState: ctx.stash=', JSON.stringify(ctx.stash || {}));
  console.log('LogCreateOrderState: ctx.prev.result=', JSON.stringify(ctx.prev && ctx.prev.result ? ctx.prev.result : null));

  // Pass through result unchanged
  return ctx.prev && ctx.prev.result ? ctx.prev.result : null;
}
