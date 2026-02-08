with open('database.py', 'r') as f:
    content = f.read()

content = content.replace('\\"', '"')

with open('database.py', 'w') as f:
    f.write(content)

print('Fixed database.py')