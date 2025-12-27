export const ensurePrefixed = (prefix: string, id?: string | null) => {
  if (!id) return id || null;
  const wanted = `${prefix}#`;
  return id.startsWith(wanted) ? id : `${wanted}${id}`;
};

export const ensureProfileId = (id?: string | null) => ensurePrefixed("PROFILE", id);
export const ensureCampaignId = (id?: string | null) => ensurePrefixed("CAMPAIGN", id);
export const ensureCatalogId = (id?: string | null) => ensurePrefixed("CATALOG", id);
export const ensureProductId = (id?: string | null) => ensurePrefixed("PRODUCT", id);
export const ensureOrderId = (id?: string | null) => ensurePrefixed("ORDER", id);
export const ensureAccountId = (id?: string | null) => ensurePrefixed("ACCOUNT", id);
