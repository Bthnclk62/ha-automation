#!/usr/bin/env python3
"""
Create Production-Ready Workflow
MINIMAL CHANGES - Only fix critical bugs
"""

import json
import copy

def create_production_workflow(source_path, output_path):
    """Create production workflow with MINIMAL targeted fixes"""

    # Load ORIGINAL workflow
    with open(source_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    nodes = workflow.get('nodes', [])

    print("=" * 100)
    print("CREATING PRODUCTION WORKFLOW - MINIMAL TARGETED FIXES")
    print("=" * 100)
    print()

    # FIXED CODE for "Build Final Ad Set UPDATE Body (CBO)"
    adset_update_cbo_fixed = """/**
 * Build Final Ad Set UPDATE Body (CBO) - PRODUCTION FIX
 *
 * FIXES:
 * 1. Only sends EDITABLE fields per Meta API spec
 * 2. Converts Excel serial dates to ISO 8601
 * 3. Proper error handling
 *
 * Meta API Editable Fields for AdSet UPDATE:
 * - name
 * - status
 * - daily_budget
 * - lifetime_budget
 * - start_time
 * - end_time
 *
 * NON-Editable (removed from update):
 * - billing_event
 * - optimization_goal
 * - bid_strategy
 * - targeting
 */

try {
  const row = item.json || {};

  // Helper: Convert Excel serial date to ISO 8601
  function convertExcelDateToISO(excelDate) {
    if (!excelDate || excelDate === '') return '';

    // If already ISO format, return as-is
    if (typeof excelDate === 'string' && excelDate.includes('T')) {
      return excelDate;
    }

    const num = Number(excelDate);
    if (isNaN(num)) return '';

    // Excel serial: days since 1899-12-30
    const epochStart = Date.UTC(1899, 11, 30);
    const millisPerDay = 86400000;
    const date = new Date(epochStart + num * millisPerDay);

    return date.toISOString();
  }

  // Helper: Clean cell values
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

  // Get AdSet ID (required)
  const adsetId = row['Ad Set ID'] || row.adset_id || '';
  if (!adsetId) {
    throw new Error('AdSet ID is required for update');
  }

  // Build update body - ONLY EDITABLE FIELDS
  const updateBody = {};

  // 1. Name (optional)
  const adsetName = clean(row['Ad Set Name'] || row.adset_name || row.name || '');
  if (adsetName) {
    updateBody.name = adsetName;
  }

  // 2. Status (optional)
  const statusRaw = row['Status (Ad Set)'] || row.status_adset || row.status || '';
  const status = String(statusRaw).trim().toUpperCase();
  if (status && ['ACTIVE', 'PAUSED', 'ARCHIVED', 'DELETED'].includes(status)) {
    updateBody.status = status;
  }

  // 3. Daily Budget (optional, TRY to kuruş)
  const dailyBudgetRaw = row['Daily Budget'] || row.daily_budget || '';
  if (dailyBudgetRaw !== '' && dailyBudgetRaw != null) {
    const budgetTRY = parseFloat(dailyBudgetRaw);
    if (!isNaN(budgetTRY) && budgetTRY >= 1) {
      // Convert TRY to kuruş (x100)
      const budgetKurus = Math.round(budgetTRY * 100);
      updateBody.daily_budget = String(budgetKurus);
    }
  }

  // 4. Start Time (optional, with date conversion)
  const startDateRaw = row['Start Date'] || row.start_time || '';
  if (startDateRaw !== '' && startDateRaw != null) {
    const startTimeISO = convertExcelDateToISO(startDateRaw);
    if (startTimeISO) {
      updateBody.start_time = startTimeISO;
    }
  }

  // 5. End Time (optional, with date conversion)
  const endDateRaw = row['End Date'] || row.end_time || '';
  if (endDateRaw !== '' && endDateRaw != null) {
    const endTimeISO = convertExcelDateToISO(endDateRaw);
    if (endTimeISO) {
      updateBody.end_time = endTimeISO;
    }
  }

  // Output
  item.json._finalBody = updateBody;
  item.json._adsetId = adsetId;

  // Debug info
  item.json.__debug_adset_update = {
    adset_id: adsetId,
    fields_to_update: Object.keys(updateBody),
    start_date_raw: startDateRaw,
    end_date_raw: endDateRaw,
    start_time_iso: updateBody.start_time || 'not set',
    end_time_iso: updateBody.end_time || 'not set'
  };

  return item;

} catch (error) {
  console.error('Error in Build Final Ad Set UPDATE Body (CBO):', error);

  item.json._error = {
    message: error.message,
    stack: error.stack,
    node: 'Build Final Ad Set UPDATE Body (CBO)',
    timestamp: new Date().toISOString()
  };
  item.json._error_occurred = true;

  return item;
}
"""

    # FIXED CODE for "Build Final Ad Set UPDATE Body (ABO)" - same as CBO but for ABO context
    adset_update_abo_fixed = adset_update_cbo_fixed.replace('(CBO)', '(ABO)')

    # Apply fixes
    fixes_applied = 0

    for node in nodes:
        node_name = node.get('name', '')

        if node_name == 'Build Final Ad Set UPDATE Body (CBO)':
            params = node.get('parameters', {})
            params['jsCode'] = adset_update_cbo_fixed
            node['parameters'] = params
            fixes_applied += 1
            print(f"✅ Fixed: {node_name}")
            print("   - Removed non-editable fields (billing_event, optimization_goal, targeting)")
            print("   - Added date conversion (Excel serial → ISO 8601)")
            print("   - Added error handling")
            print()

        elif node_name == 'Build Final Ad Set UPDATE Body (ABO)':
            params = node.get('parameters', {})
            params['jsCode'] = adset_update_abo_fixed
            node['parameters'] = params
            fixes_applied += 1
            print(f"✅ Fixed: {node_name}")
            print("   - Removed non-editable fields (billing_event, optimization_goal, targeting)")
            print("   - Added date conversion (Excel serial → ISO 8601)")
            print("   - Added error handling")
            print()

    print(f"✅ Applied {fixes_applied} TARGETED fixes")
    print()

    # Update workflow metadata
    workflow['name'] = 'Hotel Agent - Automation v5 PRODUCTION (Minimal Fixes)'

    # Save
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)

    print(f"💾 Saved to: {output_path}")
    print()

    print("=" * 100)
    print("PRODUCTION WORKFLOW SUMMARY")
    print("=" * 100)
    print()
    print("✅ FIXED Issues:")
    print("   1. AdSet UPDATE - Removed non-editable fields")
    print("   2. Date conversion - Excel serial → ISO 8601")
    print("   3. Error handling - Try-catch added")
    print()
    print("✅ UNCHANGED:")
    print("   - All CREATE flows (working)")
    print("   - All SYNC flows (working)")
    print("   - Campaign UPDATE (working)")
    print("   - Ad UPDATE (working)")
    print()
    print("🎯 Changes: MINIMAL - Only 2 nodes modified")
    print("🎯 Risk: LOW - Targeted fixes only")
    print("🎯 Testing: Focus on AdSet UPDATE with dates")
    print()

if __name__ == "__main__":
    source = "/home/user/ha-automation/Hotel Agent - Automationv1 son.json"
    output = "/home/user/ha-automation/Hotel Agent - Automation v5 PRODUCTION.json"

    create_production_workflow(source, output)
