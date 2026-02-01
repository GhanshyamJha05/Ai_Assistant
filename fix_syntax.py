with open('src/ai_assistant/services/modern_web_backend.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix lines 1873-1877 and 1882
fixes = {
    1872: '        logger.info(f"🔍 Command received: {command[:30]}...")\n',
    1873: '        logger.info(f"🔍 offline_mode flag in request: {data.get(\'offline_mode\')}")\n',
    1874: '        logger.info(f"🔍 use_local_ai: {use_local_ai}")\n',
    1875: '        logger.info(f"🔍 local_ai_initialized: {local_ai_initialized}")\n',
    1876: '        logger.info(f"🔍 local_ai_manager exists: {local_ai_manager is not None}")\n',
    1881: '                logger.info(f"Using local AI for command: {command[:50]}...")\n',
}

for line_num, new_content in fixes.items():
    lines[line_num] = new_content

with open('src/ai_assistant/services/modern_web_backend.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Fixed syntax errors in modern_web_backend.py")
