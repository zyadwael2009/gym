with open('seed_data.py', 'r') as f:
    content = f.read()

content = content.replace('\\"', '"')

with open('seed_data.py', 'w') as f:
    f.write(content)

print('Fixed seed_data.py')