#!/usr/bin/env python3
"""
Extract and analyze HTTP Request nodes for Meta API configurations
"""

import json

def analyze_http_nodes(workflow_path):
    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    nodes = workflow.get('nodes', [])
    http_nodes = [n for n in nodes if n.get('type') == 'n8n-nodes-base.httpRequest']

    print("=" * 80)
    print(f"META API - HTTP REQUEST NODES ANALYSIS ({len(http_nodes)} nodes)")
    print("=" * 80)
    print()

    issues = []

    for idx, node in enumerate(http_nodes, 1):
        name = node.get('name', 'Unknown')
        params = node.get('parameters', {})

        url = params.get('url', 'N/A')
        method = params.get('method', 'GET')
        auth = params.get('authentication', 'none')

        print(f"{idx}. {name}")
        print(f"   Method: {method}")
        print(f"   URL: {url[:100]}...")
        print(f"   Auth: {auth}")

        # Check for retry logic
        options = params.get('options', {})
        retry = options.get('retry', {})

        if retry and retry.get('retry'):
            max_retries = retry.get('maxRetries', 0)
            wait_time = retry.get('waitBetweenRetries', 0)
            print(f"   ✓ Retry: ON (max: {max_retries}, wait: {wait_time}ms)")
        else:
            print(f"   ⚠️  Retry: OFF")
            issues.append(f"{name}: No retry configured")

        # Check timeout
        timeout = options.get('timeout', 10000)
        print(f"   Timeout: {timeout}ms")

        # Check for response handling
        response_format = params.get('responseFormat', 'autodetect')
        print(f"   Response Format: {response_format}")

        # Check body content type
        body_content_type = params.get('bodyContentType', 'json')
        print(f"   Body Type: {body_content_type}")

        print()

    print("=" * 80)
    print("HTTP NODES SUMMARY")
    print("=" * 80)
    print(f"Total HTTP nodes: {len(http_nodes)}")
    print(f"Nodes without retry: {len(issues)}")

    if issues:
        print("\n⚠️  RECOMMENDATIONS:")
        print("- Add retry logic to all HTTP nodes")
        print("- Use exponential backoff (2s, 4s, 8s, 16s)")
        print("- Set max retries to 3-4")

    return issues

if __name__ == "__main__":
    workflow_path = "/home/user/ha-automation/Hotel Agent - Automationv1 son.json"
    issues = analyze_http_nodes(workflow_path)

    with open('/home/user/ha-automation/http_analysis.json', 'w') as f:
        json.dump({'issues': issues}, f, indent=2)

    print("\n📊 Analysis saved to: http_analysis.json")
