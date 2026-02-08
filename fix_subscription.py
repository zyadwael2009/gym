with open('app/models/subscription.py', 'r') as f:
    content = f.read()

content = content.replace('\\"', '"')

with open('app/models/subscription.py', 'w') as f:
    f.write(content)

print('Fixed subscription.py')