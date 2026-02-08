import os

# Fix models
models_dir = 'app/models'
for filename in os.listdir(models_dir):
    if filename.endswith('.py'):
        filepath = os.path.join(models_dir, filename)
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        original_content = content
        content = content.replace('\\"', '"')
        
        if content != original_content:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f'Fixed {filepath}')

# Fix API files
api_dir = 'app/api'
for filename in os.listdir(api_dir):
    if filename.endswith('.py'):
        filepath = os.path.join(api_dir, filename)
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        original_content = content
        content = content.replace('\\"', '"')
        
        if content != original_content:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f'Fixed {filepath}')

# Fix other app files
for root, dirs, files in os.walk('app'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            
            with open(filepath, 'r') as f:
                content = f.read()
            
            original_content = content
            content = content.replace('\\"', '"')
            
            if content != original_content:
                with open(filepath, 'w') as f:
                    f.write(content)
                print(f'Fixed {filepath}')

print('All Python files fixed!')