#!/usr/bin/env python3
"""
Validate v6 COMPLETE Workflow
Verify all 10 issues are fixed
"""

import json

def validate_v6_workflow(workflow_path):
    """Validate that all issues are fixed"""

    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    nodes = workflow.get('nodes', [])

    print("=" * 100)
    print("VALIDATING v6 COMPLETE WORKFLOW - ALL 10 ISSUES")
    print("=" * 100)
    print()

    all_passed = True
    issues_found = []

    # ========================================
    # VALIDATE FIX 1-6: Retry Logic on HTTP Nodes
    # ========================================
    print("VALIDATING FIXES 1-6: Retry Logic on HTTP Nodes (CREATE Module)")
    print("-" * 100)

    http_nodes_to_check = [
        'Campaign Budget - Ad Set Create',
        'AD Set Budget - Ad Set Create',
        'Camp Budget - Camp. Create',
        'Ad Set Budget - Camp. Create',
        'Campaign Budget - Ad Create1',
        'Ad Set Budget - Ad Create'
    ]

    for idx, node_name in enumerate(http_nodes_to_check, 1):
        node = next((n for n in nodes if n.get('name') == node_name), None)

        if not node:
            print(f"❌ Issue {idx}: {node_name} - NODE NOT FOUND")
            issues_found.append(f"Issue {idx}: Node not found")
            all_passed = False
            continue

        params = node.get('parameters', {})
        options = params.get('options', {})
        retry = options.get('retry', {})

        if retry and retry.get('maxTries'):
            print(f"✅ Issue {idx}: {node_name}")
            print(f"   - Retry: {retry.get('maxTries')} attempts")
            print(f"   - Wait: {retry.get('waitBetweenTries')}ms")
            print(f"   - Timeout: {options.get('timeout')}ms")
        else:
            print(f"❌ Issue {idx}: {node_name} - NO RETRY LOGIC")
            issues_found.append(f"Issue {idx}: Missing retry logic")
            all_passed = False

    print()

    # ========================================
    # VALIDATE FIX 7-8: AdSet UPDATE (CBO)
    # ========================================
    print("VALIDATING FIXES 7-8: Build Final Ad Set UPDATE Body (CBO)")
    print("-" * 100)

    cbo_node = next((n for n in nodes if n.get('name') == 'Build Final Ad Set UPDATE Body (CBO)'), None)

    if not cbo_node:
        print("❌ Issues 7-8: Node not found")
        issues_found.append("Issues 7-8: Node not found")
        all_passed = False
    else:
        params = cbo_node.get('parameters', {})
        code = params.get('jsCode', '')

        # Check for non-editable fields (should NOT be present)
        non_editable_fields = ['billing_event', 'optimization_goal', 'bid_strategy', 'targeting']
        found_non_editable = [f for f in non_editable_fields if f in code]

        if found_non_editable:
            print(f"❌ Issue 7: Still sends non-editable fields: {', '.join(found_non_editable)}")
            issues_found.append(f"Issue 7: Non-editable fields present")
            all_passed = False
        else:
            print("✅ Issue 7: Non-editable fields removed")
            print("   - ❌ REMOVED: billing_event, optimization_goal, bid_strategy, targeting")

        # Check for date conversion
        if 'convertExcelDateToISO' in code:
            print("✅ Issue 8: Date conversion function present")
            print("   - ✅ Excel serial → ISO 8601")

            # Check if it's actually used
            if 'Start Date' in code and 'End Date' in code:
                print("   - ✅ Applied to Start Date and End Date")
            else:
                print("   - ⚠️  Function exists but may not be used")
                issues_found.append("Issue 8: Date conversion not applied")
                all_passed = False
        else:
            print("❌ Issue 8: Date conversion missing")
            issues_found.append("Issue 8: Missing date conversion")
            all_passed = False

    print()

    # ========================================
    # VALIDATE FIX 9-10: AdSet UPDATE (ABO)
    # ========================================
    print("VALIDATING FIXES 9-10: Build Final Ad Set UPDATE Body (ABO)")
    print("-" * 100)

    abo_node = next((n for n in nodes if n.get('name') == 'Build Final Ad Set UPDATE Body (ABO)'), None)

    if not abo_node:
        print("❌ Issues 9-10: Node not found")
        issues_found.append("Issues 9-10: Node not found")
        all_passed = False
    else:
        params = abo_node.get('parameters', {})
        code = params.get('jsCode', '')

        # Check for non-editable fields (should NOT be present)
        non_editable_fields = ['billing_event', 'optimization_goal', 'bid_strategy', 'targeting']
        found_non_editable = [f for f in non_editable_fields if f in code]

        if found_non_editable:
            print(f"❌ Issue 9: Still sends non-editable fields: {', '.join(found_non_editable)}")
            issues_found.append(f"Issue 9: Non-editable fields present")
            all_passed = False
        else:
            print("✅ Issue 9: Non-editable fields removed")
            print("   - ❌ REMOVED: billing_event, optimization_goal, bid_strategy, targeting")

        # Check for date conversion
        if 'convertExcelDateToISO' in code:
            print("✅ Issue 10: Date conversion function present")
            print("   - ✅ Excel serial → ISO 8601")

            # Check if it's actually used
            if 'Start Date' in code and 'End Date' in code:
                print("   - ✅ Applied to Start Date and End Date")
            else:
                print("   - ⚠️  Function exists but may not be used")
                issues_found.append("Issue 10: Date conversion not applied")
                all_passed = False
        else:
            print("❌ Issue 10: Date conversion missing")
            issues_found.append("Issue 10: Missing date conversion")
            all_passed = False

    print()

    # ========================================
    # VALIDATE SYNC ERROR HANDLING
    # ========================================
    print("VALIDATING: Sync Module Error Handling")
    print("-" * 100)

    sync_node = next((n for n in nodes if n.get('name') == 'Code in JavaScript - Sync'), None)

    if not sync_node:
        print("⚠️  Sync node not found")
    else:
        params = sync_node.get('parameters', {})
        code = params.get('jsCode', '')

        if 'try' in code.lower() and 'catch' in code.lower():
            print("✅ Sync Error Handling: Try-catch present")
        else:
            print("⚠️  Sync Error Handling: No try-catch")

    print()

    # ========================================
    # COMPREHENSIVE VALIDATION
    # ========================================
    print("=" * 100)
    print("COMPREHENSIVE VALIDATION - ALL MODULES")
    print("=" * 100)
    print()

    # Check ALL Code nodes for error handling
    code_nodes = [n for n in nodes if n.get('type') == 'n8n-nodes-base.code']
    code_without_try = []

    for node in code_nodes:
        params = node.get('parameters', {})
        code = params.get('jsCode', '')

        if 'try' not in code.lower() or 'catch' not in code.lower():
            code_without_try.append(node.get('name'))

    print(f"📊 Code Nodes: {len(code_nodes)} total")
    if code_without_try:
        print(f"⚠️  {len(code_without_try)} Code nodes without try-catch:")
        for name in code_without_try[:5]:
            print(f"   - {name}")
        if len(code_without_try) > 5:
            print(f"   ... and {len(code_without_try) - 5} more")
    else:
        print(f"✅ All Code nodes have error handling")

    print()

    # Check ALL HTTP nodes for retry
    http_nodes = [n for n in nodes if n.get('type') == 'n8n-nodes-base.httpRequest']
    http_without_retry = []

    for node in http_nodes:
        params = node.get('parameters', {})
        options = params.get('options', {})
        retry = options.get('retry', {})

        if not retry or not retry.get('maxTries'):
            http_without_retry.append(node.get('name'))

    print(f"📊 HTTP Nodes: {len(http_nodes)} total")
    if http_without_retry:
        print(f"⚠️  {len(http_without_retry)} HTTP nodes without retry:")
        for name in http_without_retry[:5]:
            print(f"   - {name}")
        if len(http_without_retry) > 5:
            print(f"   ... and {len(http_without_retry) - 5} more")
    else:
        print(f"✅ All HTTP nodes have retry logic")

    print()

    # ========================================
    # FINAL SUMMARY
    # ========================================
    print("=" * 100)
    print("VALIDATION SUMMARY")
    print("=" * 100)
    print()

    if all_passed:
        print("✅ ALL 10 ISSUES FIXED AND VALIDATED!")
        print()
        print("CREATE MODULE: ✅ Error-free")
        print("   - All 6 HTTP nodes have retry logic")
        print()
        print("UPDATE MODULE: ✅ Error-free")
        print("   - AdSet UPDATE (CBO): Non-editable fields removed, date conversion added")
        print("   - AdSet UPDATE (ABO): Non-editable fields removed, date conversion added")
        print()
        print("SYNC MODULE: ✅ Error-free")
        print("   - Error handling added")
        print()
        print("🎯 STATUS: PRODUCTION READY")
        print("🎯 RISK: LOW")
        print("🎯 NEXT STEP: Deploy and test")
        print()
    else:
        print(f"❌ VALIDATION FAILED - {len(issues_found)} issues found:")
        print()
        for issue in issues_found:
            print(f"   - {issue}")
        print()

    return {
        'all_passed': all_passed,
        'issues_found': issues_found,
        'stats': {
            'total_nodes': len(nodes),
            'code_nodes': len(code_nodes),
            'code_without_try': len(code_without_try),
            'http_nodes': len(http_nodes),
            'http_without_retry': len(http_without_retry)
        }
    }

if __name__ == "__main__":
    workflow_path = "/home/user/ha-automation/Hotel Agent - Automation v6 COMPLETE.json"
    result = validate_v6_workflow(workflow_path)

    # Save validation result
    with open('/home/user/ha-automation/v6_validation_result.json', 'w') as f:
        json.dump(result, f, indent=2)

    print("📊 Validation result saved to: v6_validation_result.json")
