import os

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

print('All models fixed!')