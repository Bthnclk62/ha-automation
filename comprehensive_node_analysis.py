#!/usr/bin/env python3
"""
COMPREHENSIVE NODE ANALYSIS
Analyzes EVERY SINGLE NODE in detail
"""

import json
import re

def analyze_all_nodes(workflow_path):
    """Analyze every single node"""

    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    nodes = workflow.get('nodes', [])

    print("=" * 120)
    print("COMPREHENSIVE NODE ANALYSIS - EVERY NODE CHECKED")
    print("=" * 120)
    print()

    # Categorize nodes by module
    create_nodes = []
    update_nodes = []
    sync_nodes = []
    other_nodes = []

    for node in nodes:
        name = node.get('name', '').lower()

        if any(x in name for x in ['create', 'camp. id', 'write campaign', 'write ad']):
            create_nodes.append(node)
        elif any(x in name for x in ['update', 'build cbo', 'build abo', 'build final ad set update']):
            update_nodes.append(node)
        elif any(x in name for x in ['sync', 'fetch from meta']):
            sync_nodes.append(node)
        else:
            other_nodes.append(node)

    print(f"📊 Node Distribution:")
    print(f"   CREATE Module: {len(create_nodes)} nodes")
    print(f"   UPDATE Module: {len(update_nodes)} nodes")
    print(f"   SYNC Module: {len(sync_nodes)} nodes")
    print(f"   Other: {len(other_nodes)} nodes")
    print()

    issues = []

    # ========================================
    # 1. ANALYZE CREATE MODULE
    # ========================================
    print("=" * 120)
    print("1️⃣  CREATE MODULE ANALYSIS")
    print("=" * 120)
    print()

    for idx, node in enumerate(create_nodes, 1):
        name = node.get('name')
        node_type = node.get('type')

        print(f"{idx}. {name}")
        print(f"   Type: {node_type}")

        if node_type == 'n8n-nodes-base.code':
            params = node.get('parameters', {})
            code = params.get('jsCode', '')
            mode = params.get('mode', 'runOnceForEachItem')

            print(f"   Mode: {mode}")

            # Check for date handling
            has_date = 'start_time' in code.lower() or 'end_time' in code.lower()
            has_conversion = 'Date.UTC' in code or 'convertExcelDateToISO' in code

            if has_date:
                if has_conversion:
                    print(f"   ✅ Handles dates WITH conversion")
                else:
                    print(f"   ⚠️  Handles dates but NO conversion function")
                    issues.append(f"{name}: Handles dates but no conversion")

            # Check for budget conversion
            has_budget = 'budget' in code.lower()
            has_budget_conversion = '* 100' in code or '*100' in code

            if has_budget:
                if has_budget_conversion:
                    print(f"   ✅ Budget conversion: TRY → kuruş (x100)")
                else:
                    print(f"   ⚠️  Budget handling but no x100 conversion")
                    issues.append(f"{name}: Budget without x100 conversion")

            # Check error handling
            has_error_handling = 'try' in code.lower() and 'catch' in code.lower()
            if has_error_handling:
                print(f"   ✅ Error handling: try-catch")
            else:
                print(f"   ⚠️  No error handling")
                issues.append(f"{name}: No try-catch")

        elif node_type == 'n8n-nodes-base.httpRequest':
            params = node.get('parameters', {})
            url = params.get('url', '')
            json_body = params.get('jsonBody', '')

            print(f"   URL: {url[:60]}...")
            print(f"   Body: {json_body[:60]}...")

            # Check for retry
            options = params.get('options', {})
            retry = options.get('retry', {})
            if retry and retry.get('retry'):
                print(f"   ✅ Retry: Enabled")
            else:
                print(f"   ⚠️  No retry configured")
                issues.append(f"{name}: No retry logic")

        print()

    # ========================================
    # 2. ANALYZE UPDATE MODULE
    # ========================================
    print("=" * 120)
    print("2️⃣  UPDATE MODULE ANALYSIS")
    print("=" * 120)
    print()

    for idx, node in enumerate(update_nodes, 1):
        name = node.get('name')
        node_type = node.get('type')

        print(f"{idx}. {name}")
        print(f"   Type: {node_type}")

        if node_type == 'n8n-nodes-base.code':
            params = node.get('parameters', {})
            code = params.get('jsCode', '')

            # Special check for AdSet UPDATE nodes
            if 'Build Final Ad Set UPDATE Body' in name:
                print(f"\n   🔍 CRITICAL CHECK: AdSet UPDATE Body")

                # Check for non-editable fields
                non_editable_fields = [
                    'billing_event',
                    'optimization_goal',
                    'bid_strategy',
                    'targeting'
                ]

                found_non_editable = []
                for field in non_editable_fields:
                    if field in code:
                        found_non_editable.append(field)

                if found_non_editable:
                    print(f"   ❌ SENDS NON-EDITABLE FIELDS: {', '.join(found_non_editable)}")
                    issues.append(f"{name}: Sends non-editable fields - {', '.join(found_non_editable)}")
                else:
                    print(f"   ✅ Only editable fields")

                # Check for date conversion
                has_date_conversion = 'convertExcelDateToISO' in code or 'Date.UTC' in code
                if has_date_conversion:
                    print(f"   ✅ Date conversion present")
                else:
                    print(f"   ❌ NO DATE CONVERSION")
                    issues.append(f"{name}: Missing date conversion")

                # Check what it outputs
                if '_finalBody' in code:
                    print(f"   ✅ Outputs: _finalBody")
                else:
                    print(f"   ❌ Does NOT output _finalBody")
                    issues.append(f"{name}: Missing _finalBody output")

        print()

    # ========================================
    # 3. ANALYZE SYNC MODULE
    # ========================================
    print("=" * 120)
    print("3️⃣  SYNC MODULE ANALYSIS")
    print("=" * 120)
    print()

    for idx, node in enumerate(sync_nodes, 1):
        name = node.get('name')
        node_type = node.get('type')

        print(f"{idx}. {name}")
        print(f"   Type: {node_type}")

        if node_type == 'n8n-nodes-base.code':
            params = node.get('parameters', {})
            code = params.get('jsCode', '')

            # Check if it handles sync checkbox
            if 'sync' in code.lower():
                print(f"   ✅ Handles sync checkbox")

            # Check error handling
            has_error = 'try' in code.lower() and 'catch' in code.lower()
            if has_error:
                print(f"   ✅ Error handling")
            else:
                print(f"   ⚠️  No error handling")

        print()

    # ========================================
    # 4. SPECIAL NODES ANALYSIS
    # ========================================
    print("=" * 120)
    print("4️⃣  SPECIAL NODES ANALYSIS")
    print("=" * 120)
    print()

    # Check Mapping node
    mapping_node = next((n for n in nodes if n.get('name') == 'Mapping'), None)
    if mapping_node:
        print("📋 Mapping Node")
        params = mapping_node.get('parameters', {})
        assignments = params.get('assignments', {}).get('assignments', [])

        print(f"   Total mappings: {len(assignments)}")

        # Check for critical fields
        critical_fields = ['campaign_name', 'objective', 'status', 'daily_budget', 'start_time', 'end_time']
        mapped = [a.get('name') for a in assignments]

        for field in critical_fields:
            if field in mapped:
                print(f"   ✅ {field}")
            else:
                print(f"   ⚠️  Missing: {field}")
        print()

    # Check Date & Time nodes
    print("📅 Date & Time Nodes")
    date_nodes = [n for n in nodes if n.get('type') == 'n8n-nodes-base.dateTime']

    for node in date_nodes:
        name = node.get('name')
        params = node.get('parameters', {})
        date_expr = params.get('date', '')
        output_field = params.get('outputFieldName', '')

        print(f"   {name}")
        print(f"      Input: {date_expr[:80]}...")
        print(f"      Output: {output_field}")

        if 'Start Date' in date_expr:
            print(f"      ✅ Reads 'Start Date' column")
        if 'End Date' in date_expr:
            print(f"      ✅ Reads 'End Date' column")
        if 'Date.UTC(1899, 11, 30)' in date_expr:
            print(f"      ✅ Excel serial date conversion")
        print()

    # ========================================
    # SUMMARY
    # ========================================
    print("=" * 120)
    print("ANALYSIS SUMMARY")
    print("=" * 120)
    print()

    if issues:
        print(f"❌ FOUND {len(issues)} ISSUES:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    else:
        print("✅ NO CRITICAL ISSUES FOUND")

    print()

    # Save detailed report
    report = {
        'total_nodes': len(nodes),
        'create_nodes': len(create_nodes),
        'update_nodes': len(update_nodes),
        'sync_nodes': len(sync_nodes),
        'issues_found': len(issues),
        'issues': issues
    }

    with open('/home/user/ha-automation/comprehensive_analysis_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print("📊 Detailed report saved to: comprehensive_analysis_report.json")
    print()

    return issues

if __name__ == "__main__":
    workflow_path = "/home/user/ha-automation/Hotel Agent - Automationv1 son.json"
    issues = analyze_all_nodes(workflow_path)

    if issues:
        print(f"\n⚠️  Total issues to fix: {len(issues)}")
    else:
        print(f"\n✅ All checks passed!")
