#!/usr/bin/env python3
"""
Deep Code Analysis - Extracts and analyzes all Code nodes
"""

import json
import re

def extract_code_nodes(workflow_path):
    """Extract all Code node contents for review"""

    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    nodes = workflow.get('nodes', [])
    code_nodes = [n for n in nodes if n.get('type') == 'n8n-nodes-base.code']

    print("=" * 80)
    print(f"FOUND {len(code_nodes)} CODE NODES")
    print("=" * 80)
    print()

    issues = []
    findings = {
        'budget_conversion': [],
        'phone_normalization': [],
        'utm_params': [],
        'error_handling': [],
        'validation': []
    }

    for idx, node in enumerate(code_nodes, 1):
        name = node.get('name', 'Unknown')
        node_id = node.get('id', 'N/A')
        params = node.get('parameters', {})
        code = params.get('jsCode', '')

        print(f"\n{'='*80}")
        print(f"CODE NODE #{idx}: {name}")
        print(f"ID: {node_id}")
        print(f"{'='*80}")
        print(code)
        print()

        # Analyze budget conversion
        if 'budget' in code.lower() or '*100' in code or '* 100' in code:
            findings['budget_conversion'].append({
                'node': name,
                'has_conversion': True,
                'code_snippet': code[:200]
            })
            print(f"  ✓ Budget conversion detected")

        # Analyze phone normalization
        if 'phone' in code.lower() or 'tel:' in code.lower() or '+90' in code:
            findings['phone_normalization'].append({
                'node': name,
                'has_normalization': True,
                'code_snippet': code[:200]
            })
            print(f"  ✓ Phone normalization detected")

        # Analyze UTM parameters
        if 'utm_' in code.lower() or 'utmSource' in code or 'utmMedium' in code:
            findings['utm_params'].append({
                'node': name,
                'has_utm': True,
                'code_snippet': code[:200]
            })
            print(f"  ✓ UTM parameters detected")

        # Check for error handling
        if 'try' in code and 'catch' in code:
            findings['error_handling'].append({
                'node': name,
                'has_error_handling': True
            })
            print(f"  ✓ Error handling present")
        else:
            issues.append(f"⚠️  {name}: No try-catch error handling")
            print(f"  ⚠️  No error handling")

        # Check for validation
        if 'validate' in code.lower() or 'if (' in code or 'if(' in code:
            findings['validation'].append({
                'node': name,
                'has_validation': True
            })
            print(f"  ✓ Input validation detected")

    print("\n" + "="*80)
    print("FINDINGS SUMMARY")
    print("="*80)

    for category, items in findings.items():
        if items:
            print(f"\n{category.upper().replace('_', ' ')}:")
            for item in items:
                print(f"  - {item['node']}")

    if issues:
        print("\n" + "="*80)
        print("POTENTIAL ISSUES")
        print("="*80)
        for issue in issues:
            print(issue)

    return findings, issues

def analyze_http_nodes(workflow_path):
    """Analyze HTTP Request nodes for Meta API calls"""

    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    nodes = workflow.get('nodes', [])
    http_nodes = [n for n in nodes if 'httpRequest' in n.get('type', '').lower()]

    print("\n" + "="*80)
    print(f"FOUND {len(http_nodes)} HTTP REQUEST NODES")
    print("="*80)

    for idx, node in enumerate(http_nodes, 1):
        name = node.get('name', 'Unknown')
        params = node.get('parameters', {})

        url = params.get('url', 'N/A')
        method = params.get('method', 'GET')

        print(f"\n{idx}. {name}")
        print(f"   Method: {method}")
        print(f"   URL: {url}")

        # Check for authentication
        auth = params.get('authentication', 'none')
        print(f"   Auth: {auth}")

        # Check for retry logic
        options = params.get('options', {})
        retry = options.get('retry', {})
        if retry:
            print(f"   Retry: {retry}")
        else:
            print(f"   ⚠️  No retry logic configured")

def analyze_router_logic(workflow_path):
    """Analyze Switch/IF nodes for routing logic"""

    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    nodes = workflow.get('nodes', [])
    router_nodes = [n for n in nodes if n.get('type') in ['n8n-nodes-base.if', 'n8n-nodes-base.switch']]

    print("\n" + "="*80)
    print(f"FOUND {len(router_nodes)} ROUTER NODES")
    print("="*80)

    for idx, node in enumerate(router_nodes, 1):
        name = node.get('name', 'Unknown')
        node_type = node.get('type', 'Unknown')
        params = node.get('parameters', {})

        print(f"\n{idx}. {name} ({node_type})")

        if node_type == 'n8n-nodes-base.switch':
            rules = params.get('rules', {})
            print(f"   Rules: {json.dumps(rules, indent=2)}")
        elif node_type == 'n8n-nodes-base.if':
            conditions = params.get('conditions', {})
            print(f"   Conditions: {json.dumps(conditions, indent=2)}")

if __name__ == "__main__":
    workflow_path = "/home/user/ha-automation/Hotel Agent - Automationv1 son.json"

    print("\n🔍 DEEP CODE ANALYSIS\n")

    findings, issues = extract_code_nodes(workflow_path)
    analyze_http_nodes(workflow_path)
    analyze_router_logic(workflow_path)

    # Save findings
    with open('/home/user/ha-automation/code_analysis.json', 'w', encoding='utf-8') as f:
        json.dump({
            'findings': findings,
            'issues': issues
        }, f, indent=2, ensure_ascii=False)

    print("\n📊 Detailed analysis saved to: code_analysis.json")
