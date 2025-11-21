#!/usr/bin/env python3
"""
Workflow Analyzer - n8n Hotel Agent Meta Ads Automation
Analyzes the workflow structure, nodes, connections, and potential issues
"""

import json
import sys
from collections import defaultdict

def analyze_workflow(workflow_path):
    """Analyze n8n workflow structure"""

    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    print("=" * 80)
    print("HOTEL AGENT - META ADS AUTOMATION WORKFLOW ANALYSIS")
    print("=" * 80)
    print()

    # Basic info
    print(f"Workflow Name: {workflow.get('name', 'N/A')}")
    print(f"Total Nodes: {len(workflow.get('nodes', []))}")
    print(f"Total Connections: {len(workflow.get('connections', {}))}")
    print()

    # Analyze nodes
    nodes = workflow.get('nodes', [])
    node_types = defaultdict(int)
    node_list = []

    print("=" * 80)
    print("NODE INVENTORY")
    print("=" * 80)

    for idx, node in enumerate(nodes, 1):
        node_name = node.get('name', 'Unknown')
        node_type = node.get('type', 'Unknown')
        node_id = node.get('id', 'N/A')
        position = node.get('position', [0, 0])

        node_types[node_type] += 1
        node_list.append({
            'name': node_name,
            'type': node_type,
            'id': node_id,
            'position': position
        })

        print(f"{idx}. {node_name}")
        print(f"   Type: {node_type}")
        print(f"   ID: {node_id}")
        print(f"   Position: {position}")
        print()

    # Node type summary
    print("=" * 80)
    print("NODE TYPE SUMMARY")
    print("=" * 80)
    for node_type, count in sorted(node_types.items(), key=lambda x: x[1], reverse=True):
        print(f"{node_type}: {count}")
    print()

    # Analyze connections
    connections = workflow.get('connections', {})
    print("=" * 80)
    print("CONNECTION ANALYSIS")
    print("=" * 80)

    total_connections = 0
    disconnected_nodes = set([n['name'] for n in node_list])

    for source_node, outputs in connections.items():
        if source_node in disconnected_nodes:
            disconnected_nodes.remove(source_node)

        for output_type, connections_list in outputs.items():
            for conn_list in connections_list:
                for conn in conn_list:
                    target_node = conn.get('node', 'Unknown')
                    if target_node in disconnected_nodes:
                        disconnected_nodes.remove(target_node)

                    total_connections += 1
                    print(f"{source_node} -> {target_node} (type: {output_type})")

    print()
    print(f"Total Connections: {total_connections}")
    print()

    # Find disconnected nodes
    if disconnected_nodes:
        print("=" * 80)
        print("⚠️  DISCONNECTED NODES DETECTED")
        print("=" * 80)
        for node_name in disconnected_nodes:
            print(f"❌ {node_name}")
        print()
    else:
        print("✅ All nodes are connected")
        print()

    # Analyze specific node types
    print("=" * 80)
    print("MODULE DETECTION")
    print("=" * 80)

    modules = {
        'trigger': [],
        'create_campaign': [],
        'create_adset': [],
        'create_ad': [],
        'update': [],
        'sync': [],
        'error_handling': [],
        'sheets_write': []
    }

    for node in nodes:
        name = node.get('name', '').lower()
        node_type = node.get('type', '')

        if 'trigger' in node_type.lower():
            modules['trigger'].append(node.get('name'))
        if 'campaign' in name and 'create' in name:
            modules['create_campaign'].append(node.get('name'))
        if 'adset' in name or 'ad set' in name:
            modules['create_adset'].append(node.get('name'))
        if 'ad' in name and 'create' in name and 'adset' not in name:
            modules['create_ad'].append(node.get('name'))
        if 'update' in name:
            modules['update'].append(node.get('name'))
        if 'sync' in name:
            modules['sync'].append(node.get('name'))
        if 'error' in name or 'catch' in name:
            modules['error_handling'].append(node.get('name'))
        if 'sheets' in node_type.lower() and 'update' in node.get('parameters', {}).get('operation', '').lower():
            modules['sheets_write'].append(node.get('name'))

    for module_name, nodes_list in modules.items():
        if nodes_list:
            print(f"\n{module_name.upper()}:")
            for node_name in nodes_list:
                print(f"  - {node_name}")

    print()
    print("=" * 80)
    print("CRITICAL CHECKS")
    print("=" * 80)

    issues = []

    # Check for HTTP Request nodes (Meta API calls)
    http_nodes = [n for n in nodes if 'httpRequest' in n.get('type', '').lower()]
    print(f"Meta API HTTP Request nodes: {len(http_nodes)}")

    # Check for Code nodes (transformations)
    code_nodes = [n for n in nodes if n.get('type') == 'n8n-nodes-base.code']
    print(f"Code/Transformation nodes: {len(code_nodes)}")

    # Check for IF/Switch nodes (routing)
    router_nodes = [n for n in nodes if n.get('type') in ['n8n-nodes-base.if', 'n8n-nodes-base.switch']]
    print(f"Router nodes (IF/Switch): {len(router_nodes)}")

    # Check for Google Sheets nodes
    sheets_nodes = [n for n in nodes if 'googleSheets' in n.get('type', '')]
    print(f"Google Sheets nodes: {len(sheets_nodes)}")

    print()

    if disconnected_nodes:
        issues.append(f"❌ {len(disconnected_nodes)} disconnected nodes found")

    if len(http_nodes) == 0:
        issues.append("⚠️  No HTTP Request nodes found (Meta API calls missing?)")

    if len(code_nodes) == 0:
        issues.append("⚠️  No Code nodes found (transformations missing?)")

    if issues:
        print("=" * 80)
        print("ISSUES SUMMARY")
        print("=" * 80)
        for issue in issues:
            print(issue)
    else:
        print("✅ No critical issues detected")

    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

    return {
        'total_nodes': len(nodes),
        'total_connections': total_connections,
        'disconnected_nodes': list(disconnected_nodes),
        'node_types': dict(node_types),
        'modules': modules,
        'issues': issues
    }

if __name__ == "__main__":
    workflow_path = "/home/user/ha-automation/Hotel Agent - Automationv1 son.json"
    result = analyze_workflow(workflow_path)

    # Save analysis result
    with open('/home/user/ha-automation/workflow_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("\n📊 Analysis saved to: workflow_analysis.json")
