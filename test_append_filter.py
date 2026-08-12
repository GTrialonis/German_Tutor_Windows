import os, shutil, datetime

base_dir = os.path.dirname(os.path.abspath(__file__))
filter_path = os.path.join(base_dir, 'Voc-Filter_VOC.txt')

# Backup existing filter file if present
if os.path.exists(filter_path):
    ts = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    backup_path = filter_path + f'.bak.{ts}'
    shutil.copy2(filter_path, backup_path)
    print('Backup created at:', backup_path)
else:
    print('No existing Voc-Filter_VOC.txt found; a new file will be created.')

# Simulated AI-generated vocabulary
auto_vocabulary = '''Haus, das = house
Baum, der = tree
Liebe, die = love
Haus, das = house
Neu = new
'''

existing = set()
if os.path.exists(filter_path):
    with open(filter_path, 'r', encoding='utf-8-sig') as f:
        for ln in f:
            s = ln.strip()
            if s:
                existing.add(s)

new_entries = []
for ln in auto_vocabulary.splitlines():
    s = ln.strip()
    if not s:
        continue
    if s not in existing:
        new_entries.append(s)
        existing.add(s)

if new_entries:
    with open(filter_path, 'a', encoding='utf-8-sig') as f:
        for item in new_entries:
            f.write(item + '\n')
    print('Appended entries:')
    for it in new_entries:
        print('-', it)
else:
    print('No new entries to append.')

# Show last 20 lines of filter file
if os.path.exists(filter_path):
    with open(filter_path, 'r', encoding='utf-8-sig') as f:
        lines = [ln.rstrip('\n') for ln in f.readlines()]
    print('\nFilter file now has', len(lines), 'lines. Last up to 20 lines:')
    for ln in lines[-20:]:
        print(ln)
else:
    print('Filter file not found after operation (unexpected).')
