import imp
import os

for root, dirs, files in os.walk(os.path.dirname(__file__)):
  for fname in files:
    if fname.startswith('_') or not fname.endswith('.py'):
      continue
    imp.load_source('cmd', os.path.join(root, fname))
