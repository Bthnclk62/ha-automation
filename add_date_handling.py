#!/usr/bin/env python3
"""
Add Date Handling to Update Modules
Fixes start_time and end_time not being processed in UPDATE flow
"""

import json

def add_date_handling_to_update_nodes(workflow_path, output_path):
    """Add date conversion to update body nodes"""

    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    nodes = workflow.get('nodes', [])

    print("=" * 80)
    print("ADDING DATE HANDLING TO UPDATE MODULES")
    print("=" * 80)
    print()

    # Date conversion helper function (to be added to update nodes)
    date_helper = """
// Date Conversion Helper (Excel Serial Date to ISO 8601)
function convertExcelDateToISO(excelDate) {
  if (!excelDate || excelDate === '') return '';

  // If already in ISO format, return as is
  if (typeof excelDate === 'string' && excelDate.includes('T')) {
    return excelDate;
  }

  // Convert Excel serial date to ISO 8601
  const num = Number(excelDate);
  if (isNaN(num)) return '';

  // Excel serial date: days since 1899-12-30
  const epochStart = Date.UTC(1899, 11, 30);
  const millisPerDay = 86400000;
  const date = new Date(epochStart + num * millisPerDay);

  return date.toISOString();
}
"""

    # Updated AdSet UPDATE Body (CBO) with date handling
    adset_update_cbo_fixed = """// Build Final Ad Set UPDATE Body (CBO) - FIXED WITH DATE HANDLING
// Mode: Run Once for Each Item
// Output: item.json._adsetUpdateBody, item.json._adsetId

const row = item.json || {};

// Date Conversion Helper (Excel Serial Date to ISO 8601)
function convertExcelDateToISO(excelDate) {
  if (!excelDate || excelDate === '') return '';

  // If already in ISO format, return as is
  if (typeof excelDate === 'string' && excelDate.includes('T')) {
    return excelDate;
  }

  // Convert Excel serial date to ISO 8601
  const num = Number(excelDate);
  if (isNaN(num)) return '';

  // Excel serial date: days since 1899-12-30
  const epochStart = Date.UTC(1899, 11, 30);
  const millisPerDay = 86400000;
  const date = new Date(epochStart + num * millisPerDay);

  return date.toISOString();
}

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

// CRITICAL FIX: Start Time - convert from Excel serial date
const startDateRaw = row['Start Date'] || row['Start Time'] || row.start_time || row.start_date || '';
if (startDateRaw !== '' && startDateRaw != null) {
  const startTimeISO = convertExcelDateToISO(startDateRaw);
  if (startTimeISO) {
    body.start_time = startTimeISO;
  }
}

// CRITICAL FIX: End Time - convert from Excel serial date
const endDateRaw = row['End Date'] || row['End Time'] || row.end_time || row.end_date || '';
if (endDateRaw !== '' && endDateRaw != null) {
  const endTimeISO = convertExcelDateToISO(endDateRaw);
  if (endTimeISO) {
    body.end_time = endTimeISO;
  }
}

// AdSet ID (required)
const adsetId = row['Ad Set ID'] || row.adset_id || '';

// Output
item.json._adsetUpdateBody = body;
item.json._adsetId = String(adsetId || '').trim();

// Debug
item.json.__debug_adset_update = {
  fields_to_update: Object.keys(body),
  adset_id: item.json._adsetId,
  start_date_raw: startDateRaw,
  end_date_raw: endDateRaw,
  start_time_iso: body.start_time || 'N/A',
  end_time_iso: body.end_time || 'N/A'
};

return item;
"""

    # Updated AdSet UPDATE Body (ABO) with date handling
    adset_update_abo_fixed = adset_update_cbo_fixed.replace('(CBO)', '(ABO)')

    # Apply fixes
    fixes_applied = 0

    for node in nodes:
        node_name = node.get('name', '')
        params = node.get('parameters', {})

        if node_name == 'Build Final Ad Set UPDATE Body (CBO)':
            params['jsCode'] = adset_update_cbo_fixed
            node['parameters'] = params
            fixes_applied += 1
            print(f"✅ Added date handling to: {node_name}")
            print(f"   - Converts Excel serial date to ISO 8601")
            print(f"   - Handles both 'Start Date' and 'Start Time' columns")
            print()

        elif node_name == 'Build Final Ad Set UPDATE Body (ABO)':
            params['jsCode'] = adset_update_abo_fixed
            node['parameters'] = params
            fixes_applied += 1
            print(f"✅ Added date handling to: {node_name}")
            print(f"   - Converts Excel serial date to ISO 8601")
            print(f"   - Handles both 'End Date' and 'End Time' columns")
            print()

    print(f"✅ Applied date handling to {fixes_applied} nodes")
    print()

    # Update workflow name
    workflow['name'] = 'Hotel Agent - Automation v4 (ALL FIXES)'

    # Save
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)

    print(f"💾 Saved to: {output_path}")
    print()
    print("=" * 80)
    print("DATE HANDLING FIXES SUMMARY")
    print("=" * 80)
    print("✅ Excel serial date → ISO 8601 conversion added")
    print("✅ Handles both column names: 'Start Date' and 'Start Time'")
    print("✅ Handles both column names: 'End Date' and 'End Time'")
    print("✅ Works for both CREATE and UPDATE flows")
    print("✅ Debug info added to track conversions")
    print()

if __name__ == "__main__":
    input_path = "/home/user/ha-automation/Hotel Agent - Automationv4 CRITICAL-FIXES.json"
    output_path = "/home/user/ha-automation/Hotel Agent - Automationv4 ALL-FIXES.json"

    add_date_handling_to_update_nodes(input_path, output_path)
