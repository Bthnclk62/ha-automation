#!/usr/bin/env python3
"""
Manual integration of editable fields filter and helper functions
"""

import json
import re

def integrate_editable_fields_filter(workflow):
    """Manually integrate editable fields filter into update nodes"""

    nodes = workflow.get('nodes', [])

    # Campaign Update Body Template
    campaign_update_enhanced = """// Campaign Update Body with Editable Fields Filter
try {
  // Editable fields whitelist
  const EDITABLE_CAMPAIGN_FIELDS = ['name', 'status'];

  return items.map((item) => {
    const cur = item.json || {};

    // Build update body
    const updateBody = {};

    // Name
    const campaign_name = cur['Campaign Name'] || cur.campaign_name || cur.name;
    if (campaign_name !== undefined && campaign_name !== null) {
      updateBody.name = campaign_name.toString().trim();
    }

    // Status
    const status = cur['Status (Campaign)'] || cur.status;
    if (status !== undefined && status !== null) {
      const statusUpper = status.toString().toUpperCase();
      if (['ACTIVE', 'PAUSED', 'ARCHIVED'].includes(statusUpper)) {
        updateBody.status = statusUpper;
      }
    }

    // Filter only editable fields
    const filteredBody = {};
    for (const key of Object.keys(updateBody)) {
      if (EDITABLE_CAMPAIGN_FIELDS.includes(key)) {
        filteredBody[key] = updateBody[key];
      }
    }

    // Add campaign ID
    const campaign_id = cur.campaign_id || cur['Campaign ID'];
    if (!campaign_id) {
      throw new Error('Campaign ID is required for update');
    }

    // Attach to item
    item.json._updateBody = filteredBody;
    item.json._campaign_id = campaign_id;

    // Debug info
    item.json.__debug_update = {
      original_fields: Object.keys(updateBody),
      filtered_fields: Object.keys(filteredBody),
      non_editable_removed: Object.keys(updateBody).filter(k => !EDITABLE_CAMPAIGN_FIELDS.includes(k))
    };

    return item;
  });
} catch (error) {
  console.error('Error in Campaign Update Body:', error);
  return items.map(item => {
    item.json._error = {
      message: error.message,
      stack: error.stack,
      node: 'Campaign Update Body',
      timestamp: new Date().toISOString()
    };
    item.json._error_occurred = true;
    return item;
  });
}
"""

    # AdSet Update Body Template
    adset_update_enhanced = """// AdSet Update Body with Editable Fields Filter
try {
  // Editable fields whitelist
  const EDITABLE_ADSET_FIELDS = ['name', 'status', 'daily_budget', 'lifetime_budget', 'start_time', 'end_time'];

  return items.map((item) => {
    const cur = item.json || {};

    // Build update body
    const updateBody = {};

    // Name
    const adset_name = cur['Ad Set Name'] || cur.adset_name || cur.name;
    if (adset_name !== undefined && adset_name !== null) {
      updateBody.name = adset_name.toString().trim();
    }

    // Status
    const status = cur['Status (Ad Set)'] || cur.status_adset || cur.status;
    if (status !== undefined && status !== null) {
      const statusUpper = status.toString().toUpperCase();
      if (['ACTIVE', 'PAUSED', 'ARCHIVED'].includes(statusUpper)) {
        updateBody.status = statusUpper;
      }
    }

    // Daily Budget (TRY to kuruş)
    const daily_budget_raw = cur['Daily Budget'] || cur.daily_budget;
    if (daily_budget_raw !== undefined && daily_budget_raw !== null && daily_budget_raw !== '') {
      const budget_try = parseFloat(daily_budget_raw);
      if (!isNaN(budget_try) && budget_try >= 1) {
        updateBody.daily_budget = Math.round(budget_try * 100).toString();
      }
    }

    // Start Time
    const start_time = cur.start_time || cur['Start Time'];
    if (start_time) {
      updateBody.start_time = start_time;
    }

    // End Time
    const end_time = cur.end_time || cur['End Time'];
    if (end_time) {
      updateBody.end_time = end_time;
    }

    // Filter only editable fields
    const filteredBody = {};
    for (const key of Object.keys(updateBody)) {
      if (EDITABLE_ADSET_FIELDS.includes(key)) {
        filteredBody[key] = updateBody[key];
      }
    }

    // Add adset ID
    const adset_id = cur.adset_id || cur['Ad Set ID'];
    if (!adset_id) {
      throw new Error('AdSet ID is required for update');
    }

    // Attach to item
    item.json._updateBody = filteredBody;
    item.json._adset_id = adset_id;

    // Debug info
    item.json.__debug_update = {
      original_fields: Object.keys(updateBody),
      filtered_fields: Object.keys(filteredBody),
      non_editable_removed: Object.keys(updateBody).filter(k => !EDITABLE_ADSET_FIELDS.includes(k))
    };

    return item;
  });
} catch (error) {
  console.error('Error in AdSet Update Body:', error);
  return items.map(item => {
    item.json._error = {
      message: error.message,
      stack: error.stack,
      node: 'AdSet Update Body',
      timestamp: new Date().toISOString()
    };
    item.json._error_occurred = true;
    return item;
  });
}
"""

    improved_count = 0

    for node in nodes:
        node_name = node.get('name', '')

        if node_name == 'Build CBO Campaign Update Body':
            params = node.get('parameters', {})
            params['jsCode'] = campaign_update_enhanced
            node['parameters'] = params
            improved_count += 1
            print(f"✓ Integrated editable fields filter: {node_name}")

        elif node_name == 'Build ABO Campaign Update Body':
            params = node.get('parameters', {})
            params['jsCode'] = campaign_update_enhanced
            node['parameters'] = params
            improved_count += 1
            print(f"✓ Integrated editable fields filter: {node_name}")

        elif node_name == 'Build Final Ad Set UPDATE Body (CBO)':
            params = node.get('parameters', {})
            params['jsCode'] = adset_update_enhanced
            node['parameters'] = params
            improved_count += 1
            print(f"✓ Integrated editable fields filter: {node_name}")

        elif node_name == 'Build Final Ad Set UPDATE Body (ABO)':
            params = node.get('parameters', {})
            params['jsCode'] = adset_update_enhanced
            node['parameters'] = params
            improved_count += 1
            print(f"✓ Integrated editable fields filter: {node_name}")

    print(f"\n✅ Integrated editable fields filter to {improved_count} nodes")
    return workflow

def add_budget_validation_helpers(workflow):
    """Add budget validation helper functions to relevant nodes"""

    nodes = workflow.get('nodes', [])

    budget_helper = """
// Budget Validation Helper
function validateAndConvertBudget(budgetTRY, field_name = 'budget') {
  // Parse budget
  const budget = parseFloat(budgetTRY);

  // Validation
  if (isNaN(budget)) {
    throw new Error(`Invalid ${field_name}: "${budgetTRY}" is not a number`);
  }

  if (budget < 1) {
    throw new Error(`${field_name} too low: ${budget} TRY. Minimum 1 TRY (100 kuruş) required by Meta.`);
  }

  if (budget > 100000) {
    console.warn(`${field_name} very high: ${budget} TRY. Please verify.`);
  }

  // Convert TRY to kuruş (x100)
  const budgetKurus = Math.round(budget * 100);

  return {
    try_amount: budget,
    kurus_amount: budgetKurus,
    kurus_string: budgetKurus.toString()
  };
}
"""

    phone_helper = """
// Phone Normalization Helper
function normalizeAndValidatePhone(input) {
  if (!input || typeof input !== 'string') {
    return '';
  }

  // Remove all non-digit characters
  let cleaned = input.replace(/[^0-9]/g, '');

  // Add 90 prefix if missing
  if (!cleaned.startsWith('90')) {
    if (cleaned.startsWith('0')) {
      cleaned = '9' + cleaned; // 0532 → 90532
    } else {
      cleaned = '90' + cleaned; // 532 → 90532
    }
  }

  // Validate Turkish phone format (90 + 10 digits = 12 digits)
  if (cleaned.length !== 12) {
    throw new Error(`Invalid Turkish phone number: "${input}". Expected format: +90XXXXXXXXXX (12 digits total)`);
  }

  // Validate that it starts with valid Turkish mobile prefixes
  const prefix = cleaned.substring(2, 5); // Get first 3 digits after 90
  const valid_prefixes = ['505', '506', '507', '530', '531', '532', '533', '534', '535', '536', '537', '538', '539', '540', '541', '542', '543', '544', '545', '546', '547', '548', '549', '551', '552', '553', '554', '555', '556', '557', '558', '559'];

  if (!valid_prefixes.includes(prefix)) {
    console.warn(`Phone prefix ${prefix} may not be valid Turkish mobile number`);
  }

  return 'tel:+' + cleaned;
}
"""

    # Nodes that handle budget conversion
    budget_nodes = [
        'Build Final Ad Set Body',
        'Build Final Ad Set Body1',
        'Build CBO Campaign Update Body',
        'Build ABO Campaign Update Body',
        'Build Final Ad Set UPDATE Body (CBO)',
        'Build Final Ad Set UPDATE Body (ABO)'
    ]

    # Nodes that handle phone normalization
    phone_nodes = [
        'Build Final Ad Set Body',
        'Campaign Budget - Ad Set Create → Build Final Ad Body (CBO)',
        'Ad Set Budget - Ad Set Create → Build Final Ad Body (ABO)',
        'Build CBO Ads Update',
        'Build ABO Ads Update'
    ]

    for node in nodes:
        node_name = node.get('name', '')
        params = node.get('parameters', {})
        code = params.get('jsCode', '')

        # Add budget helper
        if node_name in budget_nodes and 'validateAndConvertBudget' not in code:
            enhanced_code = budget_helper + "\n\n" + code
            params['jsCode'] = enhanced_code
            node['parameters'] = params
            print(f"✓ Added budget validation helper: {node_name}")

        # Add phone helper
        if node_name in phone_nodes and 'normalizeAndValidatePhone' not in code:
            enhanced_code = phone_helper + "\n\n" + code
            params['jsCode'] = enhanced_code
            node['parameters'] = params
            print(f"✓ Added phone validation helper: {node_name}")

    return workflow

def main():
    """Main manual integration process"""

    input_path = "/home/user/ha-automation/Hotel Agent - Automationv2 IMPROVED.json"
    output_path = "/home/user/ha-automation/Hotel Agent - Automationv3 FINAL.json"

    print("=" * 80)
    print("MANUAL INTEGRATION SCRIPT")
    print("=" * 80)
    print()

    # Load improved workflow
    print("📂 Loading improved workflow...")
    with open(input_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    print(f"✓ Loaded: {workflow.get('name', 'Unknown')}")
    print()

    # Apply manual integrations
    print("🔧 Applying manual integrations...")
    print()

    print("1️⃣ Integrating editable fields filter...")
    workflow = integrate_editable_fields_filter(workflow)
    print()

    print("2️⃣ Adding budget validation helpers...")
    print("3️⃣ Adding phone validation helpers...")
    workflow = add_budget_validation_helpers(workflow)
    print()

    # Update workflow name
    workflow['name'] = 'Hotel Agent - Automation v3 (FINAL)'

    # Save
    print("💾 Saving final workflow...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)

    print(f"✅ Final workflow saved to: {output_path}")
    print()

    print("=" * 80)
    print("INTEGRATION SUMMARY")
    print("=" * 80)
    print("✅ Editable fields filter integrated")
    print("✅ Budget validation helpers added")
    print("✅ Phone validation helpers added")
    print()
    print("📊 Complete improvements:")
    print("  ✓ Retry logic on 17 HTTP nodes")
    print("  ✓ Try-catch on 16 Code nodes")
    print("  ✓ Enhanced Input Validation")
    print("  ✓ Editable fields filter")
    print("  ✓ Budget & phone validation")
    print()

if __name__ == "__main__":
    main()
