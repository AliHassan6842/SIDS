import os
import glob

def fix():
    for filepath in glob.glob('services/ai-service/src/sids_ai/**/*.py', recursive=True):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        fixed_content = content.replace('\\"\\"\\"', '\"\"\"')
        
        if content != fixed_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"Fixed {filepath}")

if __name__ == '__main__':
    fix()
