#!/usr/bin/env python3
"""
Critical Fix Script - Fixes items/item syntax errors and date handling
"""

import json

def fix_workflow_critical_bugs(workflow_path, output_path):
    """Fix critical bugs in workflow"""

    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    nodes = workflow.get('nodes', [])
    fixes_applied = 0

    print("=" * 80)
    print("CRITICAL BUG FIXES")
    print("=" * 80)
    print()

    # Fix 1: Build CBO Campaign Update Body
    cbo_campaign_update_code = """// Build CBO Campaign Update Body - FIXED
// Mode: Run Once for Each Item
// Output: item.json._campaignId, item.json._campaignUpdateBody

const row = item.json || {};

// Clean helper
function clean(v) {
  if (typeof v === 'string') {
    return v
      .replace(/\\u00A0/g, ' ')
      .replace(/\\r?\\n/g, ' ')
      .trim()
      .replace(/^="\\s*|\\s*"$/g, '');
  }
  return v == null ? '' : v;
}

// Normalize status
function normalizeStatus(s) {
  const v = String(s || '').trim().toUpperCase();
  if (!v) return '';
  if (['ACTIVE', 'PAUSED', 'DELETED', 'ARCHIVED'].includes(v)) return v;
  return '';
}

// Budget type check
const budgetTypeRaw = clean(row['Budget'] || row.budget_type || '');
const budgetType = budgetTypeRaw.toLowerCase();
const isCbo = budgetType === 'campaign budget';

if (!isCbo) {
  item.json._skipCampaignUpdate = true;
  item.json._campaignUpdateBody = {};
  return item;
}

// Campaign ID (required)
const campaignId = row['Campaign ID'] || row.campaign_id || row.camp_id || '';

// Editable fields - ONLY name and status per Meta API
const nameRaw = row['Campaign Name'] || row.campaign_name || '';
const statusRaw = row['Status (Campaign)'] || row.status_campaign || row.status || '';

// Build body with only editable fields
const body = {};

const name = clean(nameRaw);
if (name) body.name = name;

const status = normalizeStatus(statusRaw);
if (status) body.status = status;

// Output
item.json._campaignId = String(campaignId || '').trim();
item.json._campaignUpdateBody = body;

return item;
"""

    # Fix 2: Build ABO Campaign Update Body (same as CBO)
    abo_campaign_update_code = """// Build ABO Campaign Update Body - FIXED
// Mode: Run Once for Each Item
// Output: item.json._campaignId, item.json._campaignUpdateBody

const row = item.json || {};

// Clean helper
function clean(v) {
  if (typeof v === 'string') {
    return v
      .replace(/\\u00A0/g, ' ')
      .replace(/\\r?\\n/g, ' ')
      .trim()
      .replace(/^="\\s*|\\s*"$/g, '');
  }
  return v == null ? '' : v;
}

// Normalize status
function normalizeStatus(s) {
  const v = String(s || '').trim().toUpperCase();
  if (!v) return '';
  if (['ACTIVE', 'PAUSED', 'DELETED', 'ARCHIVED'].includes(v)) return v;
  return '';
}

// Budget type check
const budgetTypeRaw = clean(row['Budget'] || row.budget_type || '');
const budgetType = budgetTypeRaw.toLowerCase();
const isAbo = budgetType === 'ad set budget';

if (!isAbo) {
  item.json._skipCampaignUpdate = true;
  item.json._campaignUpdateBody = {};
  return item;
}

// Campaign ID (required)
const campaignId = row['Campaign ID'] || row.campaign_id || row.camp_id || '';

// Editable fields - ONLY name and status per Meta API
const nameRaw = row['Campaign Name'] || row.campaign_name || '';
const statusRaw = row['Status (Campaign)'] || row.status_campaign || row.status || '';

// Build body with only editable fields
const body = {};

const name = clean(nameRaw);
if (name) body.name = name;

const status = normalizeStatus(statusRaw);
if (status) body.status = status;

// Output
item.json._campaignId = String(campaignId || '').trim();
item.json._campaignUpdateBody = body;

return item;
"""

    # Fix 3: Build Final Ad Set UPDATE Body (CBO) - with date handling
    adset_update_cbo_code = """// Build Final Ad Set UPDATE Body (CBO) - FIXED
// Mode: Run Once for Each Item
// Output: item.json._adsetUpdateBody, item.json._adsetId

const row = item.json || {};

// Clean helper
function clean(v) {
  if (typeof v === 'string') {
    return v
      .replace(/\\u00A0/g, ' ')
      .replace(/\\r?\\n/g, ' ')
      .trim()
      .replace(/^="\\s*|\\s*"$/g, '');
  }
  return v == null ? '' : v;
}

// Normalize status
function normalizeStatus(s) {
  const v = String(s || '').trim().toUpperCase();
  if (!v) return '';
  if (['ACTIVE', 'PAUSED', 'DELETED', 'ARCHIVED'].includes(v)) return v;
  return '';
}

// Editable fields for AdSet: name, status, daily_budget, start_time, end_time
const body = {};

// Name
const adsetName = clean(row['Ad Set Name'] || row.adset_name || row.name || '');
if (adsetName) body.name = adsetName;

// Status
const statusRaw = row['Status (Ad Set)'] || row.status_adset || row.status || '';
const status = normalizeStatus(statusRaw);
if (status) body.status = status;

// Daily Budget (TRY to kuruş) - CBO typically doesn't have adset budget, but allow it
const dailyBudgetRaw = row['Daily Budget'] || row.daily_budget || '';
if (dailyBudgetRaw !== '' && dailyBudgetRaw != null) {
  const budgetTRY = parseFloat(dailyBudgetRaw);
  if (!isNaN(budgetTRY) && budgetTRY >= 1) {
    const budgetKurus = Math.round(budgetTRY * 100);
    body.daily_budget = budgetKurus.toString();
  }
}

// CRITICAL FIX: Start Time - get from processed date node
const startTime = row.start_time || row['Start Time'] || '';
if (startTime && startTime !== '') {
  body.start_time = startTime;
}

// CRITICAL FIX: End Time - get from processed date node
const endTime = row.end_time || row['End Time'] || '';
if (endTime && endTime !== '') {
  body.end_time = endTime;
}

// AdSet ID (required)
const adsetId = row['Ad Set ID'] || row.adset_id || '';

// Output
item.json._adsetUpdateBody = body;
item.json._adsetId = String(adsetId || '').trim();

// Debug
item.json.__debug_adset_update = {
  fields_to_update: Object.keys(body),
  adset_id: item.json._adsetId
};

return item;
"""

    # Fix 4: Build Final Ad Set UPDATE Body (ABO)
    adset_update_abo_code = """// Build Final Ad Set UPDATE Body (ABO) - FIXED
// Mode: Run Once for Each Item
// Output: item.json._adsetUpdateBody, item.json._adsetId

const row = item.json || {};

// Clean helper
function clean(v) {
  if (typeof v === 'string') {
    return v
      .replace(/\\u00A0/g, ' ')
      .replace(/\\r?\\n/g, ' ')
      .trim()
      .replace(/^="\\s*|\\s*"$/g, '');
  }
  return v == null ? '' : v;
}

// Normalize status
function normalizeStatus(s) {
  const v = String(s || '').trim().toUpperCase();
  if (!v) return '';
  if (['ACTIVE', 'PAUSED', 'DELETED', 'ARCHIVED'].includes(v)) return v;
  return '';
}

// Editable fields for AdSet: name, status, daily_budget, start_time, end_time
const body = {};

// Name
const adsetName = clean(row['Ad Set Name'] || row.adset_name || row.name || '');
if (adsetName) body.name = adsetName;

// Status
const statusRaw = row['Status (Ad Set)'] || row.status_adset || row.status || '';
const status = normalizeStatus(statusRaw);
if (status) body.status = status;

// Daily Budget (TRY to kuruş) - Important for ABO
const dailyBudgetRaw = row['Daily Budget'] || row.daily_budget || '';
if (dailyBudgetRaw !== '' && dailyBudgetRaw != null) {
  const budgetTRY = parseFloat(dailyBudgetRaw);
  if (!isNaN(budgetTRY) && budgetTRY >= 1) {
    const budgetKurus = Math.round(budgetTRY * 100);
    body.daily_budget = budgetKurus.toString();
  }
}

// CRITICAL FIX: Start Time - get from processed date node
const startTime = row.start_time || row['Start Time'] || '';
if (startTime && startTime !== '') {
  body.start_time = startTime;
}

// CRITICAL FIX: End Time - get from processed date node
const endTime = row.end_time || row['End Time'] || '';
if (endTime && endTime !== '') {
  body.end_time = endTime;
}

// AdSet ID (required)
const adsetId = row['Ad Set ID'] || row.adset_id || '';

// Output
item.json._adsetUpdateBody = body;
item.json._adsetId = String(adsetId || '').trim();

// Debug
item.json.__debug_adset_update = {
  fields_to_update: Object.keys(body),
  adset_id: item.json._adsetId
};

return item;
"""

    # Apply fixes
    for node in nodes:
        node_name = node.get('name', '')
        params = node.get('parameters', {})

        if node_name == 'Build CBO Campaign Update Body':
            # Check mode
            mode = params.get('mode', 'runOnceForEachItem')
            if mode != 'runOnceForEachItem':
                params['mode'] = 'runOnceForEachItem'
                print(f"⚠️  Fixed mode for: {node_name}")

            params['jsCode'] = cbo_campaign_update_code
            node['parameters'] = params
            fixes_applied += 1
            print(f"✅ Fixed: {node_name} (items → item)")

        elif node_name == 'Build ABO Campaign Update Body':
            mode = params.get('mode', 'runOnceForEachItem')
            if mode != 'runOnceForEachItem':
                params['mode'] = 'runOnceForEachItem'
                print(f"⚠️  Fixed mode for: {node_name}")

            params['jsCode'] = abo_campaign_update_code
            node['parameters'] = params
            fixes_applied += 1
            print(f"✅ Fixed: {node_name} (items → item)")

        elif node_name == 'Build Final Ad Set UPDATE Body (CBO)':
            mode = params.get('mode', 'runOnceForEachItem')
            if mode != 'runOnceForEachItem':
                params['mode'] = 'runOnceForEachItem'
                print(f"⚠️  Fixed mode for: {node_name}")

            params['jsCode'] = adset_update_cbo_code
            node['parameters'] = params
            fixes_applied += 1
            print(f"✅ Fixed: {node_name} (items → item + date handling)")

        elif node_name == 'Build Final Ad Set UPDATE Body (ABO)':
            mode = params.get('mode', 'runOnceForEachItem')
            if mode != 'runOnceForEachItem':
                params['mode'] = 'runOnceForEachItem'
                print(f"⚠️  Fixed mode for: {node_name}")

            params['jsCode'] = adset_update_abo_code
            node['parameters'] = params
            fixes_applied += 1
            print(f"✅ Fixed: {node_name} (items → item + date handling)")

    print()
    print(f"✅ Applied {fixes_applied} critical fixes")
    print()

    # Update workflow name
    workflow['name'] = 'Hotel Agent - Automation v4 (CRITICAL FIXES)'

    # Save
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)

    print(f"💾 Saved to: {output_path}")
    print()
    print("=" * 80)
    print("FIXES SUMMARY")
    print("=" * 80)
    print("✅ Build CBO Campaign Update Body - Fixed items → item")
    print("✅ Build ABO Campaign Update Body - Fixed items → item")
    print("✅ Build Final Ad Set UPDATE Body (CBO) - Fixed items → item + dates")
    print("✅ Build Final Ad Set UPDATE Body (ABO) - Fixed items → item + dates")
    print()
    print("🎯 Critical bugs fixed!")
    print("   - items.map() → return item;")
    print("   - Start Time / End Time now processed correctly")
    print("   - Mode verified: runOnceForEachItem")
    print()

if __name__ == "__main__":
    input_path = "/home/user/ha-automation/Hotel Agent - Automationv3 FINAL.json"
    output_path = "/home/user/ha-automation/Hotel Agent - Automationv4 CRITICAL-FIXES.json"

    fix_workflow_critical_bugs(input_path, output_path)
