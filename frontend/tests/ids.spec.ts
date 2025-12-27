import { describe, it, expect } from 'vitest';
import { ensureProfileId, ensureCampaignId, ensureCatalogId, ensureOrderId } from '../src/lib/ids';

describe('ID helpers', () => {
  it('adds PROFILE# prefix when missing', () => {
    expect(ensureProfileId('abc')).toBe('PROFILE#abc');
    expect(ensureProfileId('PROFILE#abc')).toBe('PROFILE#abc');
    expect(ensureProfileId(undefined)).toBeNull();
    expect(ensureProfileId(null)).toBeNull();
  });

  it('adds CAMPAIGN# prefix when missing', () => {
    expect(ensureCampaignId('c1')).toBe('CAMPAIGN#c1');
    expect(ensureCampaignId('CAMPAIGN#c1')).toBe('CAMPAIGN#c1');
  });

  it('adds CATALOG# prefix when missing', () => {
    expect(ensureCatalogId('cat')).toBe('CATALOG#cat');
  });

  it('adds ORDER# prefix when missing', () => {
    expect(ensureOrderId('ord')).toBe('ORDER#ord');
  });
});
