#!/usr/bin/env python3
"""
Comprehensive Workflow Validation
Validates all critical paths: CREATE, UPDATE, SYNC
"""

import json

def validate_workflow_flows(workflow_path):
    """Validate all critical flows in workflow"""

    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    nodes = workflow.get('nodes', [])
    connections = workflow.get('connections', {})

    print("=" * 80)
    print("COMPREHENSIVE WORKFLOW VALIDATION")
    print("=" * 80)
    print()

    # Index nodes by name for quick lookup
    node_index = {node.get('name'): node for node in nodes}

    issues = []
    warnings = []

    # Validate CREATE CBO Flow
    print("1️⃣  VALIDATING CREATE CBO FLOW")
    print("-" * 80)

    create_cbo_path = [
        'Meta Ads Automation',
        '🛡️ Input Validation',
        'Date & Time / start_time',
        'Date & Time / end_time',
        'Mapping',
        'Carry Row & Sheet',
        'Ad set name',
        'Code in JavaScript',
        'Action Router',
        'If Budget Level (Camp Budget)',
        'Camp Budget - Camp. Create',
        'Camp. ID',
        'Write Campaign ID',
        'Build Final Ad Set Body',
        'Campaign Budget - Ad Set Create',
        'Write Ad Set ID',
        'Campaign Budget - Ad Set Create → Build Final Ad Body (CBO)',
        'Campaign Budget - Ad Create1',
        'Write Ad ID',
        'Mark Action NONE (CBO)'
    ]

    missing_nodes = []
    for node_name in create_cbo_path:
        if node_name not in node_index:
            missing_nodes.append(node_name)

    if missing_nodes:
        issues.append(f"CREATE CBO: Missing nodes: {', '.join(missing_nodes)}")
        print(f"❌ Missing nodes: {', '.join(missing_nodes)}")
    else:
        print(f"✅ All {len(create_cbo_path)} nodes exist in CREATE CBO path")

    # Check Date & Time nodes
    date_start = node_index.get('Date & Time / start_time')
    date_end = node_index.get('Date & Time / end_time')

    if date_start:
        params = date_start.get('parameters', {})
        date_expr = params.get('date', '')
        if 'Start Date' in date_expr:
            print("✅ Date & Time / start_time reads 'Start Date' column")
        else:
            warnings.append("Date & Time / start_time may not be reading correct column")
            print("⚠️  Date & Time / start_time column mapping unclear")

    if date_end:
        params = date_end.get('parameters', {})
        date_expr = params.get('date', '')
        if 'End Date' in date_expr:
            print("✅ Date & Time / end_time reads 'End Date' column")
        else:
            warnings.append("Date & Time / end_time may not be reading correct column")
            print("⚠️  Date & Time / end_time column mapping unclear")

    print()

    # Validate UPDATE CBO Flow
    print("2️⃣  VALIDATING UPDATE CBO FLOW")
    print("-" * 80)

    update_cbo_path = [
        'Meta Ads Automation',
        '🛡️ Input Validation',
        'Date & Time / start_time',
        'Date & Time / end_time',
        'Mapping',
        'Carry Row & Sheet',
        'Ad set name',
        'Code in JavaScript',
        'Action Router',
        'If Budget Level (Camp Budget)1',
        'Build CBO Campaign Update Body',
        'Camp Budget - Camp. update',
        'Build Final Ad Set UPDATE Body (CBO)',
        'Campaign Budget - Ad Set Update',
        'Build CBO Ads Update',
        'If CBO ( Ad Name - Status)',
        'Campaign Budget - Ad Update (Ad ID)',
        'Mark Action NONE (CBO)-Name/Status'
    ]

    missing_update = []
    for node_name in update_cbo_path:
        if node_name not in node_index:
            missing_update.append(node_name)

    if missing_update:
        issues.append(f"UPDATE CBO: Missing nodes: {', '.join(missing_update)}")
        print(f"❌ Missing nodes: {', '.join(missing_update)}")
    else:
        print(f"✅ All {len(update_cbo_path)} nodes exist in UPDATE CBO path")

    # Check UPDATE node for items/item bug
    update_cbo_node = node_index.get('Build CBO Campaign Update Body')
    if update_cbo_node:
        params = update_cbo_node.get('parameters', {})
        code = params.get('jsCode', '')
        mode = params.get('mode', 'runOnceForEachItem')

        if mode != 'runOnceForEachItem':
            issues.append("Build CBO Campaign Update Body: Wrong mode (should be runOnceForEachItem)")
            print(f"❌ Mode: {mode} (should be runOnceForEachItem)")
        else:
            print(f"✅ Mode: runOnceForEachItem")

        if 'return items.map' in code:
            issues.append("Build CBO Campaign Update Body: Still has 'items.map' (should be 'return item')")
            print(f"❌ Code has 'items.map' (should use 'return item')")
        elif 'return item' in code:
            print(f"✅ Code correctly uses 'return item'")
        else:
            warnings.append("Build CBO Campaign Update Body: No clear return statement found")
            print(f"⚠️  Return statement unclear")

    # Check AdSet UPDATE for date handling
    adset_update_cbo = node_index.get('Build Final Ad Set UPDATE Body (CBO)')
    if adset_update_cbo:
        params = adset_update_cbo.get('parameters', {})
        code = params.get('jsCode', '')

        if 'convertExcelDateToISO' in code:
            print(f"✅ Date conversion function present")
        else:
            issues.append("Build Final Ad Set UPDATE Body (CBO): Missing date conversion")
            print(f"❌ Missing date conversion function")

        if 'Start Date' in code or 'start_time' in code:
            print(f"✅ Reads start_time/Start Date")
        else:
            warnings.append("AdSet UPDATE may not handle start_time")
            print(f"⚠️  start_time handling unclear")

        if 'End Date' in code or 'end_time' in code:
            print(f"✅ Reads end_time/End Date")
        else:
            warnings.append("AdSet UPDATE may not handle end_time")
            print(f"⚠️  end_time handling unclear")

    print()

    # Validate ABO paths
    print("3️⃣  VALIDATING ABO FLOWS (CREATE & UPDATE)")
    print("-" * 80)

    abo_specific_nodes = [
        'Ad Set Budget - Camp. Create',
        'Camp. ID1',
        'Write Campaign ID1',
        'Build Final Ad Set Body1',
        'AD Set Budget - Ad Set Create',
        'Build ABO Campaign Update Body',
        'Build Final Ad Set UPDATE Body (ABO)'
    ]

    missing_abo = []
    for node_name in abo_specific_nodes:
        if node_name not in node_index:
            missing_abo.append(node_name)

    if missing_abo:
        issues.append(f"ABO: Missing nodes: {', '.join(missing_abo)}")
        print(f"❌ Missing nodes: {', '.join(missing_abo)}")
    else:
        print(f"✅ All {len(abo_specific_nodes)} ABO-specific nodes exist")

    # Check ABO Update nodes
    abo_campaign = node_index.get('Build ABO Campaign Update Body')
    abo_adset = node_index.get('Build Final Ad Set UPDATE Body (ABO)')

    if abo_campaign:
        params = abo_campaign.get('parameters', {})
        code = params.get('jsCode', '')
        if 'return items.map' in code:
            issues.append("Build ABO Campaign Update Body: Has 'items.map' bug")
            print(f"❌ Build ABO Campaign Update Body: items.map bug")
        else:
            print(f"✅ Build ABO Campaign Update Body: Correct syntax")

    if abo_adset:
        params = abo_adset.get('parameters', {})
        code = params.get('jsCode', '')
        if 'convertExcelDateToISO' in code:
            print(f"✅ Build Final Ad Set UPDATE Body (ABO): Has date conversion")
        else:
            issues.append("Build Final Ad Set UPDATE Body (ABO): Missing date conversion")
            print(f"❌ Missing date conversion")

    print()

    # Validate SYNC Flow
    print("4️⃣  VALIDATING SYNC FLOW")
    print("-" * 80)

    sync_nodes = [
        'Sync to Google Sheets',
        'Code in JavaScript - Sync',
        '🔄 Fetch from Meta',
        'Code in JavaScript - Fetch from Meta',
        'Merge1',
        'Code in JavaScript3',
        'Sync to Google Sheets - Fetch from Meta'
    ]

    missing_sync = []
    for node_name in sync_nodes:
        if node_name not in node_index:
            missing_sync.append(node_name)

    if missing_sync:
        issues.append(f"SYNC: Missing nodes: {', '.join(missing_sync)}")
        print(f"❌ Missing nodes: {', '.join(missing_sync)}")
    else:
        print(f"✅ All {len(sync_nodes)} SYNC nodes exist")

    print()

    # Validate HTTP nodes have retry logic
    print("5️⃣  VALIDATING RETRY LOGIC ON HTTP NODES")
    print("-" * 80)

    http_nodes = [n for n in nodes if n.get('type') == 'n8n-nodes-base.httpRequest']
    http_without_retry = []

    for node in http_nodes:
        params = node.get('parameters', {})
        options = params.get('options', {})
        retry = options.get('retry', {})

        if not retry or not retry.get('retry'):
            http_without_retry.append(node.get('name'))

    if http_without_retry:
        warnings.append(f"{len(http_without_retry)} HTTP nodes without retry logic")
        print(f"⚠️  {len(http_without_retry)} HTTP nodes without retry:")
        for name in http_without_retry[:5]:  # Show first 5
            print(f"   - {name}")
        if len(http_without_retry) > 5:
            print(f"   ... and {len(http_without_retry) - 5} more")
    else:
        print(f"✅ All {len(http_nodes)} HTTP nodes have retry logic")

    print()

    # Validate Code nodes have try-catch
    print("6️⃣  VALIDATING ERROR HANDLING ON CODE NODES")
    print("-" * 80)

    code_nodes = [n for n in nodes if n.get('type') == 'n8n-nodes-base.code']
    code_without_try = []

    for node in code_nodes:
        params = node.get('parameters', {})
        code = params.get('jsCode', '')

        if 'try' not in code.lower() or 'catch' not in code.lower():
            code_without_try.append(node.get('name'))

    if code_without_try:
        warnings.append(f"{len(code_without_try)} Code nodes without try-catch")
        print(f"⚠️  {len(code_without_try)} Code nodes without try-catch:")
        for name in code_without_try[:5]:
            print(f"   - {name}")
        if len(code_without_try) > 5:
            print(f"   ... and {len(code_without_try) - 5} more")
    else:
        print(f"✅ All {len(code_nodes)} Code nodes have error handling")

    print()

    # Final Summary
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print()

    print(f"📊 Statistics:")
    print(f"   Total Nodes: {len(nodes)}")
    print(f"   HTTP Nodes: {len(http_nodes)}")
    print(f"   Code Nodes: {len(code_nodes)}")
    print(f"   Connections: {sum(len(v) for v in connections.values())}")
    print()

    if issues:
        print(f"❌ CRITICAL ISSUES ({len(issues)}):")
        for issue in issues:
            print(f"   - {issue}")
        print()

    if warnings:
        print(f"⚠️  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"   - {warning}")
        print()

    if not issues and not warnings:
        print("✅ ALL VALIDATIONS PASSED!")
        print("   Workflow is ready for deployment")
        print()
    elif not issues:
        print("✅ NO CRITICAL ISSUES")
        print("⚠️  Some warnings exist (review recommended)")
        print()
    else:
        print("❌ CRITICAL ISSUES FOUND")
        print("   Workflow needs fixes before deployment")
        print()

    return {
        'issues': issues,
        'warnings': warnings,
        'stats': {
            'total_nodes': len(nodes),
            'http_nodes': len(http_nodes),
            'code_nodes': len(code_nodes),
            'http_without_retry': len(http_without_retry),
            'code_without_try': len(code_without_try)
        }
    }

if __name__ == "__main__":
    workflow_path = "/home/user/ha-automation/Hotel Agent - Automationv4 ALL-FIXES.json"
    result = validate_workflow_flows(workflow_path)

    # Save validation result
    with open('/home/user/ha-automation/validation_result.json', 'w') as f:
        json.dump(result, f, indent=2)

    print("📊 Validation result saved to: validation_result.json")
