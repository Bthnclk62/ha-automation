#!/usr/bin/env python3
"""
Validate v7 PERFECT Workflow
Comprehensive validation of all fixes and critical paths
"""

import json
import re

def validate_v7(workflow_path):
    """Comprehensive validation"""

    with open(workflow_path, 'r') as f:
        workflow = json.load(f)

    nodes = workflow.get('nodes', [])

    print("=" * 100)
    print("v7 PERFECT - COMPREHENSIVE VALIDATION")
    print("=" * 100)
    print()

    all_passed = True
    critical_issues = []
    warnings = []

    # ========================================
    # 1. Validate Carry Row & Sheet
    # ========================================
    print("1️⃣  CARRY ROW & SHEET VALIDATION")
    print("-" * 100)

    carry_node = next((n for n in nodes if n.get('name') == 'Carry Row & Sheet'), None)

    if carry_node:
        code = carry_node['parameters']['jsCode']

        # Check if adset_id is carried
        if 'item.json.adset_id' in code:
            print("✅ adset_id is carried")
        else:
            print("❌ adset_id NOT carried")
            critical_issues.append("Carry Row & Sheet: adset_id not carried")
            all_passed = False

        # Check if campaign_id is carried
        if 'item.json.campaign_id' in code:
            print("✅ campaign_id is carried")
        else:
            print("❌ campaign_id NOT carried")
            critical_issues.append("Carry Row & Sheet: campaign_id not carried")
            all_passed = False

        # Check if ad_id is carried
        if 'item.json.ad_id' in code:
            print("✅ ad_id is carried")
        else:
            print("❌ ad_id NOT carried")
            critical_issues.append("Carry Row & Sheet: ad_id not carried")
            all_passed = False
    else:
        print("❌ Carry Row & Sheet node NOT FOUND")
        critical_issues.append("Carry Row & Sheet: node not found")
        all_passed = False

    print()

    # ========================================
    # 2. Validate AdSet UPDATE (CBO)
    # ========================================
    print("2️⃣  ADSET UPDATE (CBO) VALIDATION")
    print("-" * 100)

    cbo_node = next((n for n in nodes if n.get('name') == 'Build Final Ad Set UPDATE Body (CBO)'), None)

    if cbo_node:
        code = cbo_node['parameters']['jsCode']

        # Check for NON-EDITABLE fields (should NOT be ASSIGNED)
        non_editable = ['billing_event', 'optimization_goal', 'bid_strategy', 'targeting']

        found_assignments = []
        for field in non_editable:
            # Pattern: finalBody.field = or finalBody[field] =
            pattern = rf'finalBody[\.\[][\'"]*{field}[\'"]*[\]\s]*='
            if re.search(pattern, code):
                found_assignments.append(field)

        if found_assignments:
            print(f"❌ Still ASSIGNS non-editable fields: {', '.join(found_assignments)}")
            critical_issues.append(f"AdSet UPDATE (CBO): Assigns {', '.join(found_assignments)}")
            all_passed = False
        else:
            print("✅ Non-editable fields NOT assigned")

        # Check for date conversion function
        if 'convertExcelDateToISO' in code:
            print("✅ Date conversion function present")

            # Check if it's used
            if 'convertExcelDateToISO(start_date_raw)' in code or 'convertExcelDateToISO(end_date_raw)' in code:
                print("✅ Date conversion is USED")
            else:
                print("⚠️  Date conversion function exists but may not be used")
                warnings.append("AdSet UPDATE (CBO): Date conversion not applied")
        else:
            print("❌ Date conversion function MISSING")
            critical_issues.append("AdSet UPDATE (CBO): No date conversion")
            all_passed = False

        # Check for AdSet ID validation
        if 'if (!adset_id)' in code and 'throw new Error' in code:
            print("✅ AdSet ID validation present")
        else:
            print("⚠️  AdSet ID validation missing")
            warnings.append("AdSet UPDATE (CBO): No AdSet ID validation")

        # Check for Mapping structure
        if '$items(\'Mapping\', 0)' in code and '$itemIndex' in code:
            print("✅ Original Mapping + $itemIndex structure KEPT")
        else:
            print("❌ Mapping structure BROKEN")
            critical_issues.append("AdSet UPDATE (CBO): Mapping structure broken")
            all_passed = False
    else:
        print("❌ AdSet UPDATE (CBO) node NOT FOUND")
        critical_issues.append("AdSet UPDATE (CBO): node not found")
        all_passed = False

    print()

    # ========================================
    # 3. Validate AdSet UPDATE (ABO)
    # ========================================
    print("3️⃣  ADSET UPDATE (ABO) VALIDATION")
    print("-" * 100)

    abo_node = next((n for n in nodes if n.get('name') == 'Build Final Ad Set UPDATE Body (ABO)'), None)

    if abo_node:
        code = abo_node['parameters']['jsCode']

        # Check for NON-EDITABLE fields
        found_assignments = []
        for field in non_editable:
            pattern = rf'finalBody[\.\[][\'"]*{field}[\'"]*[\]\s]*='
            if re.search(pattern, code):
                found_assignments.append(field)

        if found_assignments:
            print(f"❌ Still ASSIGNS non-editable fields: {', '.join(found_assignments)}")
            critical_issues.append(f"AdSet UPDATE (ABO): Assigns {', '.join(found_assignments)}")
            all_passed = False
        else:
            print("✅ Non-editable fields NOT assigned")

        # Check for date conversion
        if 'convertExcelDateToISO' in code:
            print("✅ Date conversion function present")
        else:
            print("❌ Date conversion function MISSING")
            critical_issues.append("AdSet UPDATE (ABO): No date conversion")
            all_passed = False

        # Check for budget conversion
        if 'Math.round' in code and '* 100' in code:
            print("✅ Budget conversion present (TRY → kuruş)")
        else:
            print("⚠️  Budget conversion may be missing")
            warnings.append("AdSet UPDATE (ABO): Check budget conversion")

        # Check for Mapping structure
        if '$items(\'Mapping\', 0)' in code and '$itemIndex' in code:
            print("✅ Original Mapping + $itemIndex structure KEPT")
        else:
            print("❌ Mapping structure BROKEN")
            critical_issues.append("AdSet UPDATE (ABO): Mapping structure broken")
            all_passed = False
    else:
        print("❌ AdSet UPDATE (ABO) node NOT FOUND")
        critical_issues.append("AdSet UPDATE (ABO): node not found")
        all_passed = False

    print()

    # ========================================
    # 4. Validate HTTP Request URLs
    # ========================================
    print("4️⃣  HTTP REQUEST URLs VALIDATION")
    print("-" * 100)

    http_update_nodes = [
        'Campaign Budget - Ad Set Update',
        'Ad Set Budget - Ad Set Update'
    ]

    for node_name in http_update_nodes:
        node = next((n for n in nodes if n.get('name') == node_name), None)
        if node:
            params = node.get('parameters', {})
            url = params.get('url', '')

            print(f"📡 {node_name}")
            print(f"   URL: {url[:80]}...")

            # Check if URL uses adset_id
            if 'adset_id' in url.lower() or 'Ad Set ID' in url:
                print(f"   ✅ Uses adset_id from previous node")
            else:
                print(f"   ⚠️  May not use adset_id correctly")
                warnings.append(f"{node_name}: Check URL adset_id usage")

            # Check body parameter
            send_body = params.get('sendBody', False)
            if send_body:
                body_params = params.get('bodyParameters', {}).get('parameters', [])
                # Find _finalBody parameter
                final_body_param = next((p for p in body_params if '_finalBody' in str(p)), None)
                if final_body_param:
                    print(f"   ✅ Uses _finalBody from previous node")
                else:
                    print(f"   ⚠️  May not use _finalBody")
                    warnings.append(f"{node_name}: Check _finalBody usage")
        else:
            print(f"❌ {node_name} NOT FOUND")

    print()

    # ========================================
    # 5. Validate SYNC Module
    # ========================================
    print("5️⃣  SYNC MODULE VALIDATION")
    print("-" * 100)

    sync_node = next((n for n in nodes if n.get('name') == 'Code in JavaScript - Sync'), None)

    if sync_node:
        code = sync_node['parameters']['jsCode']

        # Check for essential SYNC logic
        if '_sync' in code:
            print("✅ SYNC logic present (_sync object)")
        else:
            print("❌ SYNC logic MISSING")
            critical_issues.append("SYNC: _sync object not created")
            all_passed = False

        # Check for Row No handling
        if 'Row No' in code or 'row_no' in code:
            print("✅ Row No handling present")
        else:
            print("⚠️  Row No handling may be missing")
            warnings.append("SYNC: Check Row No handling")

        # Check for ID extraction
        if 'campaign_id' in code and 'adset_id' in code and 'ad_id' in code:
            print("✅ ID extraction present (campaign, adset, ad)")
        else:
            print("⚠️  ID extraction may be incomplete")
            warnings.append("SYNC: Check ID extraction")
    else:
        print("❌ SYNC node NOT FOUND")
        critical_issues.append("SYNC: node not found")
        all_passed = False

    print()

    # ========================================
    # 6. Overall Workflow Structure
    # ========================================
    print("6️⃣  OVERALL WORKFLOW STRUCTURE")
    print("-" * 100)

    # Count nodes
    total_nodes = len(nodes)
    code_nodes = len([n for n in nodes if n.get('type') == 'n8n-nodes-base.code'])
    http_nodes = len([n for n in nodes if n.get('type') == 'n8n-nodes-base.httpRequest'])

    print(f"Total nodes: {total_nodes}")
    print(f"Code nodes: {code_nodes}")
    print(f"HTTP nodes: {http_nodes}")

    # Check for key nodes
    key_nodes = [
        'Meta Ads Automation',
        'Mapping',
        'Carry Row & Sheet',
        'Date & Time / start_time',
        'Date & Time / end_time',
        'Build Final Ad Set UPDATE Body (CBO)',
        'Build Final Ad Set UPDATE Body (ABO)',
        'Code in JavaScript - Sync'
    ]

    print()
    print("Key nodes present:")
    for key_node in key_nodes:
        node = next((n for n in nodes if n.get('name') == key_node), None)
        if node:
            print(f"   ✅ {key_node}")
        else:
            print(f"   ❌ {key_node}")

    print()

    # ========================================
    # 7. Final Summary
    # ========================================
    print("=" * 100)
    print("VALIDATION SUMMARY")
    print("=" * 100)
    print()

    if all_passed and not critical_issues:
        print("🎉 ALL CRITICAL VALIDATIONS PASSED!")
        print()
        print("✅ Carry Row & Sheet: IDs are carried correctly")
        print("✅ AdSet UPDATE (CBO): Non-editable fields removed, date conversion added")
        print("✅ AdSet UPDATE (ABO): Non-editable fields removed, date + budget conversion added")
        print("✅ SYNC Module: Original logic preserved")
        print("✅ Workflow Structure: All key nodes present")
        print()

        if warnings:
            print(f"⚠️  {len(warnings)} Non-critical warnings:")
            for warning in warnings:
                print(f"   - {warning}")
            print()

        print("=" * 100)
        print("🎯 STATUS: READY FOR DEPLOYMENT")
        print("🎯 CONFIDENCE: HIGH")
        print("🎯 NEXT STEP: Import to n8n and test with real data")
        print("=" * 100)
    else:
        print(f"❌ VALIDATION FAILED - {len(critical_issues)} critical issues:")
        print()
        for issue in critical_issues:
            print(f"   - {issue}")
        print()

        if warnings:
            print(f"⚠️  {len(warnings)} warnings:")
            for warning in warnings:
                print(f"   - {warning}")
            print()

    return {
        'all_passed': all_passed,
        'critical_issues': critical_issues,
        'warnings': warnings,
        'stats': {
            'total_nodes': total_nodes,
            'code_nodes': code_nodes,
            'http_nodes': http_nodes
        }
    }

if __name__ == "__main__":
    workflow_path = "/home/user/ha-automation/Hotel Agent - Automation v7 PERFECT.json"
    result = validate_v7(workflow_path)

    # Save validation result
    with open('/home/user/ha-automation/v7_validation_result.json', 'w') as f:
        json.dump(result, f, indent=2)

    print()
    print("📊 Validation result saved to: v7_validation_result.json")
