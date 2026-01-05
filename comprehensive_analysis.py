#!/usr/bin/env python3
"""
COMPREHENSIVE WORKFLOW ANALYSIS
Analyzes EVERY node, EVERY parameter, EVERY mapping
"""

import json
from collections import defaultdict

def deep_analyze_workflow(workflow_path):
    """Complete deep analysis of workflow"""

    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    nodes = workflow.get('nodes', [])
    connections = workflow.get('connections', {})

    print("=" * 100)
    print("COMPREHENSIVE WORKFLOW DEEP ANALYSIS")
    print("=" * 100)
    print()

    # 1. Analyze Google Sheets Trigger - what columns are available?
    sheets_trigger = next((n for n in nodes if n.get('type') == 'n8n-nodes-base.googleSheetsTrigger'), None)

    if sheets_trigger:
        print("1️⃣  GOOGLE SHEETS TRIGGER ANALYSIS")
        print("-" * 100)
        params = sheets_trigger.get('parameters', {})
        doc_id = params.get('documentId', {}).get('value', 'N/A')
        sheet_name = params.get('sheetName', {}).get('cachedResultName', 'N/A')
        options = params.get('options', {})
        range_def = options.get('dataLocationOnSheet', {}).get('values', {}).get('range', 'N/A')

        print(f"   Document ID: {doc_id}")
        print(f"   Sheet Name: {sheet_name}")
        print(f"   Range: {range_def}")
        print()

        # Try to find column mappings in downstream nodes
        print("   Looking for column references in workflow...")
        all_column_refs = set()

        for node in nodes:
            params = node.get('parameters', {})
            code = params.get('jsCode', '')

            # Extract column references from code
            import re
            # Look for patterns like: item.json['Column Name'] or row['Column Name']
            patterns = [
                r"json\['([^']+)'\]",
                r'json\["([^"]+)"\]',
                r"row\['([^']+)'\]",
                r'row\["([^"]+)"\]'
            ]

            for pattern in patterns:
                matches = re.findall(pattern, code)
                all_column_refs.update(matches)

        print(f"\n   📊 Found {len(all_column_refs)} unique column references:")
        for col in sorted(all_column_refs):
            print(f"      - {col}")
        print()

    # 2. Analyze Date & Time nodes
    print("2️⃣  DATE & TIME NODES ANALYSIS")
    print("-" * 100)

    date_nodes = [n for n in nodes if n.get('type') == 'n8n-nodes-base.dateTime']

    for node in date_nodes:
        name = node.get('name', 'Unknown')
        params = node.get('parameters', {})
        operation = params.get('operation', 'N/A')
        date_expr = params.get('date', 'N/A')
        format_type = params.get('format', 'N/A')
        custom_format = params.get('customFormat', 'N/A')
        output_field = params.get('outputFieldName', 'N/A')

        print(f"   Node: {name}")
        print(f"   Operation: {operation}")
        print(f"   Date Expression: {date_expr[:100]}...")
        print(f"   Format Type: {format_type}")
        print(f"   Custom Format: {custom_format}")
        print(f"   Output Field: {output_field}")
        print()

    # 3. Analyze ALL HTTP Request nodes (Meta API calls)
    print("3️⃣  HTTP REQUEST NODES (META API) DETAILED ANALYSIS")
    print("-" * 100)

    http_nodes = [n for n in nodes if n.get('type') == 'n8n-nodes-base.httpRequest']

    for idx, node in enumerate(http_nodes, 1):
        name = node.get('name', 'Unknown')
        params = node.get('parameters', {})

        method = params.get('method', 'GET')
        url = params.get('url', 'N/A')
        body_type = params.get('specifyBody', 'N/A')
        json_body = params.get('jsonBody', 'N/A')

        print(f"\n   {idx}. {name}")
        print(f"      Method: {method}")
        print(f"      URL: {url[:80]}...")
        print(f"      Body Type: {body_type}")

        if json_body != 'N/A':
            print(f"      JSON Body Expression: {json_body[:100]}...")

            # Check if it's a reference to a variable
            if '$json' in json_body:
                print(f"      ⚠️  Uses dynamic JSON from previous node")
        print()

    # 4. Analyze ALL Code nodes
    print("4️⃣  CODE NODES DETAILED ANALYSIS")
    print("-" * 100)

    code_nodes = [n for n in nodes if n.get('type') == 'n8n-nodes-base.code']

    for idx, node in enumerate(code_nodes, 1):
        name = node.get('name', 'Unknown')
        params = node.get('parameters', {})
        mode = params.get('mode', 'runOnceForEachItem')
        code = params.get('jsCode', '')

        print(f"\n   {idx}. {name}")
        print(f"      Mode: {mode}")
        print(f"      Code Length: {len(code)} characters")

        # Check for common issues
        issues = []

        if mode == 'runOnceForEachItem' and 'items.map' in code:
            issues.append("❌ Uses items.map() in runOnceForEachItem mode")

        if 'start_time' in code.lower() or 'end_time' in code.lower():
            if 'convertExcelDateToISO' not in code and 'Date.UTC' not in code:
                issues.append("⚠️  Handles dates but no conversion function")

        if 'try' not in code.lower() or 'catch' not in code.lower():
            issues.append("⚠️  No error handling")

        if issues:
            for issue in issues:
                print(f"      {issue}")
        else:
            print(f"      ✅ No obvious issues")

        # Extract what fields this node produces
        outputs = []
        import re
        output_pattern = r'item\.json\.([a-zA-Z_][a-zA-Z0-9_]*)\s*='
        output_matches = re.findall(output_pattern, code)

        if output_matches:
            print(f"      Outputs: {', '.join(set(output_matches[:5]))}")

        print()

    # 5. Connection flow analysis
    print("5️⃣  CONNECTION FLOW ANALYSIS")
    print("-" * 100)

    # Build node name to connections map
    node_map = {n.get('name'): n for n in nodes}

    # Trace CREATE CBO flow
    print("\n   CREATE CBO Flow:")
    create_cbo_trace = [
        'Meta Ads Automation',
        'Date & Time / start_time',
        'Date & Time / end_time',
        'Mapping',
        'If Budget Level (Camp Budget)',
        'Camp Budget - Camp. Create',
        'Camp. ID',
        'Write Campaign ID',
        'Build Final Ad Set Body',
        'Campaign Budget - Ad Set Create',
        'Write Ad Set ID',
        'Campaign Budget - Ad Set Create → Build Final Ad Body (CBO)',
        'Campaign Budget - Ad Create1',
        'Write Ad ID'
    ]

    for node_name in create_cbo_trace:
        if node_name in node_map:
            print(f"      ✅ {node_name}")
        else:
            print(f"      ❌ {node_name} - MISSING!")

    # Trace UPDATE CBO flow
    print("\n   UPDATE CBO Flow:")
    update_cbo_trace = [
        'Meta Ads Automation',
        'Action Router',
        'If Budget Level (Camp Budget)1',
        'Build CBO Campaign Update Body',
        'Camp Budget - Camp. update',
        'Build Final Ad Set UPDATE Body (CBO)',
        'Campaign Budget - Ad Set Update',
        'Build CBO Ads Update'
    ]

    for node_name in update_cbo_trace:
        if node_name in node_map:
            print(f"      ✅ {node_name}")
        else:
            print(f"      ❌ {node_name} - MISSING!")

    print()

    # 6. Specific problematic node analysis
    print("6️⃣  PROBLEMATIC NODE: 'Campaign Budget - Ad Set Update'")
    print("-" * 100)

    problem_node = next((n for n in nodes if n.get('name') == 'Campaign Budget - Ad Set Update'), None)

    if problem_node:
        params = problem_node.get('parameters', {})

        print(f"   Type: {problem_node.get('type')}")
        print(f"   Method: {params.get('method')}")
        print(f"   URL: {params.get('url')}")
        print(f"   Send Body: {params.get('sendBody')}")
        print(f"   Body Type: {params.get('specifyBody')}")
        print(f"   JSON Body: {params.get('jsonBody')}")

        json_body_expr = params.get('jsonBody', '')
        if json_body_expr:
            print(f"\n   JSON Body Expression Analysis:")
            print(f"   {json_body_expr}")

            if '$json' in json_body_expr:
                print(f"\n   ⚠️  This expects a field from previous node!")
                print(f"   Previous node should output: {json_body_expr}")
    else:
        print("   ❌ Node not found!")

    print()

    # Save detailed analysis
    analysis = {
        'total_nodes': len(nodes),
        'http_nodes': len(http_nodes),
        'code_nodes': len(code_nodes),
        'date_nodes': len(date_nodes),
        'columns_found': sorted(list(all_column_refs)),
        'http_node_names': [n.get('name') for n in http_nodes],
        'code_node_names': [n.get('name') for n in code_nodes]
    }

    with open('/home/user/ha-automation/deep_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)

    print("=" * 100)
    print("ANALYSIS COMPLETE")
    print("=" * 100)
    print(f"📊 Saved to: deep_analysis.json")
    print()

if __name__ == "__main__":
    workflow_path = "/home/user/ha-automation/Hotel Agent - Automationv1 son.json"
    deep_analyze_workflow(workflow_path)
