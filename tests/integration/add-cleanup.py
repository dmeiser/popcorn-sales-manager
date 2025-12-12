#!/usr/bin/env python3
"""
Add cleanup calls to integration tests.
For each test that creates a resource, add a delete call at the end.
"""

import re
import sys
from pathlib import Path

def add_cleanup_to_test(test_content: str, file_path: str) -> str:
    """Add cleanup mutations to a test."""
    lines = test_content.split('\n')
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        result.append(line)
        
        # Track resources created in this test
        creates = {
            'profile': [],
            'season': [],
            'catalog': [],
            'order': [],
            'invite': []
        }
        
        # Look for variable assignments after CREATE mutations
        if 'profileId' in line and '=' in line and ('createSellerProfile' in line or '.profileId' in line):
            match = re.search(r'(?:const|let)\s+(\w+)\s*=', line)
            if match:
                creates['profile'].append(match.group(1))
        
        if 'seasonId' in line and '=' in line and ('createSeason' in line or '.seasonId' in line):
            match = re.search(r'(?:const|let)\s+(\w+)\s*=', line)
            if match:
                creates['season'].append(match.group(1))
        
        if 'catalogId' in line and '=' in line and ('createCatalog' in line or '.catalogId' in line):
            match = re.search(r'(?:const|let)\s+(\w+)\s*=', line)
            if match:
                creates['catalog'].append(match.group(1))
        
        if 'orderId' in line and '=' in line and ('createOrder' in line or '.orderId' in line):
            match = re.search(r'(?:const|let)\s+(\w+)\s*=', line)
            if match:
                creates['order'].append(match.group(1))
        
        if 'inviteCode' in line and '=' in line and ('createProfileInvite' in line or '.inviteCode' in line):
            match = re.search(r'(?:const|let)\s+(\w+)\s*=', line)
            if match:
                creates['invite'].append(match.group(1))
        
        i += 1
    
    return '\n'.join(result)

def main():
    test_dir = Path('resolvers')
    
    for test_file in test_dir.glob('*.test.ts'):
        print(f"Processing {test_file.name}...")
        
        content = test_file.read_text()
        
        # Check if file already has cleanup
        if 'DELETE_' in content and 'mutate({ mutation: DELETE_' in content:
            print(f"  ✓ {test_file.name} already has cleanup")
            continue
        
        # Add cleanup
        modified = add_cleanup_to_test(content, str(test_file))
        
        if modified != content:
            test_file.write_text(modified)
            print(f"  ✓ Added cleanup to {test_file.name}")
        else:
            print(f"  - No changes needed for {test_file.name}")

if __name__ == '__main__':
    main()
