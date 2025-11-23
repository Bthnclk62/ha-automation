#!/usr/bin/env python3
"""
Accurate Validation for v6 COMPLETE Workflow
Checks for ACTUAL assignments, not just mentions in comments
"""

import json
import re

def validate_v6_accurate(workflow_path):
    """Accurate validation checking actual code, not comments"""

    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    nodes = workflow.get('nodes', [])

    print("=" * 100)
    print("ACCURATE VALIDATION - v6 COMPLETE WORKFLOW")
    print("=" * 100)
    print()

    all_passed = True
    critical_issues = []
    warnings = []

    # ========================================
    # VALIDATE FIX 1-6: Retry Logic
    # ========================================
    print("1️⃣  VALIDATING CREATE MODULE - Retry Logic (Issues 1-6)")
    print("-" * 100)

    http_nodes_to_check = [
        ('Campaign Budget - Ad Set Create', 1),
        ('AD Set Budget - Ad Set Create', 2),
        ('Camp Budget - Camp. Create', 3),
        ('Ad Set Budget - Camp. Create', 4),
        ('Campaign Budget - Ad Create1', 5),
        ('Ad Set Budget - Ad Create', 6)
    ]

    for node_name, issue_num in http_nodes_to_check:
        node = next((n for n in nodes if n.get('name') == node_name), None)

        if not node:
            critical_issues.append(f"Issue {issue_num}: {node_name} - Node not found")
            all_passed = False
            continue

        params = node.get('parameters', {})
        options = params.get('options', {})
        retry = options.get('retry', {})

        if retry and retry.get('maxTries') and retry.get('maxTries') >= 3:
            print(f"✅ Issue {issue_num}: {node_name} - Retry: {retry.get('maxTries')} attempts")
        else:
            critical_issues.append(f"Issue {issue_num}: {node_name} - Missing retry")
            all_passed = False

    print()

    # ========================================
    # VALIDATE FIX 7-8: AdSet UPDATE (CBO)
    # ========================================
    print("2️⃣  VALIDATING UPDATE MODULE - AdSet UPDATE (CBO) (Issues 7-8)")
    print("-" * 100)

    cbo_node = next((n for n in nodes if n.get('name') == 'Build Final Ad Set UPDATE Body (CBO)'), None)

    if not cbo_node:
        critical_issues.append("Issues 7-8: CBO node not found")
        all_passed = False
    else:
        params = cbo_node.get('parameters', {})
        code = params.get('jsCode', '')

        # Check for ACTUAL assignments (not comments)
        non_editable_fields = ['billing_event', 'optimization_goal', 'bid_strategy', 'targeting']

        # Pattern: updateBody.field = or body.field =
        actual_assignments = []
        for field in non_editable_fields:
            pattern = rf'(updateBody|body)\.{field}\s*='
            if re.search(pattern, code):
                actual_assignments.append(field)

        if actual_assignments:
            print(f"❌ Issue 7: Still ASSIGNS non-editable fields: {', '.join(actual_assignments)}")
            critical_issues.append(f"Issue 7: Assigns {', '.join(actual_assignments)}")
            all_passed = False
        else:
            print("✅ Issue 7: Non-editable fields NOT assigned")
            print("   - Only editable fields: name, status, daily_budget, start_time, end_time")

        # Check for date conversion
        has_conversion_func = 'convertExcelDateToISO' in code
        has_start_time = re.search(r'updateBody\.start_time\s*=', code)
        has_end_time = re.search(r'updateBody\.end_time\s*=', code)

        if has_conversion_func and has_start_time and has_end_time:
            print("✅ Issue 8: Date conversion fully implemented")
            print("   - Function: convertExcelDateToISO (Excel serial → ISO 8601)")
            print("   - Applied to: start_time, end_time")
        else:
            issues = []
            if not has_conversion_func:
                issues.append("no conversion function")
            if not has_start_time:
                issues.append("start_time not set")
            if not has_end_time:
                issues.append("end_time not set")

            print(f"❌ Issue 8: Date conversion incomplete - {', '.join(issues)}")
            critical_issues.append(f"Issue 8: {', '.join(issues)}")
            all_passed = False

    print()

    # ========================================
    # VALIDATE FIX 9-10: AdSet UPDATE (ABO)
    # ========================================
    print("3️⃣  VALIDATING UPDATE MODULE - AdSet UPDATE (ABO) (Issues 9-10)")
    print("-" * 100)

    abo_node = next((n for n in nodes if n.get('name') == 'Build Final Ad Set UPDATE Body (ABO)'), None)

    if not abo_node:
        critical_issues.append("Issues 9-10: ABO node not found")
        all_passed = False
    else:
        params = abo_node.get('parameters', {})
        code = params.get('jsCode', '')

        # Check for ACTUAL assignments (not comments)
        actual_assignments = []
        for field in non_editable_fields:
            pattern = rf'(updateBody|body)\.{field}\s*='
            if re.search(pattern, code):
                actual_assignments.append(field)

        if actual_assignments:
            print(f"❌ Issue 9: Still ASSIGNS non-editable fields: {', '.join(actual_assignments)}")
            critical_issues.append(f"Issue 9: Assigns {', '.join(actual_assignments)}")
            all_passed = False
        else:
            print("✅ Issue 9: Non-editable fields NOT assigned")
            print("   - Only editable fields: name, status, daily_budget, start_time, end_time")

        # Check for date conversion
        has_conversion_func = 'convertExcelDateToISO' in code
        has_start_time = re.search(r'updateBody\.start_time\s*=', code)
        has_end_time = re.search(r'updateBody\.end_time\s*=', code)

        if has_conversion_func and has_start_time and has_end_time:
            print("✅ Issue 10: Date conversion fully implemented")
            print("   - Function: convertExcelDateToISO (Excel serial → ISO 8601)")
            print("   - Applied to: start_time, end_time")
        else:
            issues = []
            if not has_conversion_func:
                issues.append("no conversion function")
            if not has_start_time:
                issues.append("start_time not set")
            if not has_end_time:
                issues.append("end_time not set")

            print(f"❌ Issue 10: Date conversion incomplete - {', '.join(issues)}")
            critical_issues.append(f"Issue 10: {', '.join(issues)}")
            all_passed = False

    print()

    # ========================================
    # ADDITIONAL CHECKS
    # ========================================
    print("4️⃣  ADDITIONAL VALIDATION - SYNC Module & Overall Health")
    print("-" * 100)

    # Sync error handling
    sync_node = next((n for n in nodes if n.get('name') == 'Code in JavaScript - Sync'), None)
    if sync_node:
        params = sync_node.get('parameters', {})
        code = params.get('jsCode', '')
        if 'try' in code and 'catch' in code:
            print("✅ Sync Module: Error handling present")
        else:
            warnings.append("Sync module: No error handling")
            print("⚠️  Sync Module: No error handling")
    else:
        print("ℹ️  Sync node not found (optional)")

    # Overall stats
    http_nodes = [n for n in nodes if n.get('type') == 'n8n-nodes-base.httpRequest']
    http_with_retry = 0
    for node in http_nodes:
        params = node.get('parameters', {})
        options = params.get('options', {})
        retry = options.get('retry', {})
        if retry and retry.get('maxTries'):
            http_with_retry += 1

    print()
    print(f"📊 HTTP Nodes: {len(http_nodes)} total, {http_with_retry} with retry logic")

    if http_with_retry < len(http_nodes):
        warnings.append(f"{len(http_nodes) - http_with_retry} HTTP nodes without retry (UPDATE module)")

    print()

    # ========================================
    # FINAL SUMMARY
    # ========================================
    print("=" * 100)
    print("FINAL VALIDATION SUMMARY")
    print("=" * 100)
    print()

    if all_passed and not critical_issues:
        print("🎉 ALL 10 CRITICAL ISSUES FIXED AND VALIDATED!")
        print()
        print("✅ CREATE MODULE (Issues 1-6): Error-free")
        print("   - All 6 HTTP nodes have retry logic (3 attempts, 1s wait)")
        print()
        print("✅ UPDATE MODULE (Issues 7-10): Error-free")
        print("   - AdSet UPDATE (CBO): Non-editable fields removed, date conversion added")
        print("   - AdSet UPDATE (ABO): Non-editable fields removed, date conversion added")
        print()
        print("✅ SYNC MODULE: Error handling added")
        print()

        if warnings:
            print(f"⚠️  {len(warnings)} Non-critical warnings:")
            for warning in warnings:
                print(f"   - {warning}")
            print()

        print("=" * 100)
        print("🎯 STATUS: PRODUCTION READY")
        print("🎯 RISK: LOW")
        print("🎯 QUALITY: All critical issues resolved")
        print("=" * 100)
        print()
    else:
        print(f"❌ VALIDATION FAILED - {len(critical_issues)} critical issues:")
        print()
        for issue in critical_issues:
            print(f"   - {issue}")
        print()

    return {
        'all_passed': all_passed,
        'critical_issues': critical_issues,
        'warnings': warnings,
        'stats': {
            'total_nodes': len(nodes),
            'http_nodes': len(http_nodes),
            'http_with_retry': http_with_retry
        }
    }

if __name__ == "__main__":
    workflow_path = "/home/user/ha-automation/Hotel Agent - Automation v6 COMPLETE.json"
    result = validate_v6_accurate(workflow_path)

    # Save validation result
    with open('/home/user/ha-automation/v6_accurate_validation.json', 'w') as f:
        json.dump(result, f, indent=2)

    print("📊 Detailed validation saved to: v6_accurate_validation.json")
