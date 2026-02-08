import os

def fix_quotes_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace escaped quotes in docstrings
    fixed_content = content.replace('\\"\\"\\"', '"""')
    
    if content != fixed_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f'Fixed quotes: {filepath}')

# Find our application Python files only (exclude venv)
for root, dirs, files in os.walk('.'):
    if 'venv' in root or '.git' in root:
        continue
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            fix_quotes_in_file(filepath)

print('Application files fixed!')