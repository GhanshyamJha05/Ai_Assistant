!git clone --depth 1 https://github.com/hiyouga/LLaMA-Factory.git
%cd LLaMA-Factory
!pip install -e ".[torch,metrics]"
!pip install unsloth

import os, shutil, json, gzip, glob

print("\n🔍 Preparing Dataset...")
# Auto-detect uploaded dataset in Kaggle
found_files = glob.glob('/kaggle/**/*windows*.jsonl*', recursive=True)
valid_files = [f for f in found_files if 'LLaMA-Factory' not in f]

if not valid_files: 
    raise FileNotFoundError("❌ ERROR: Dataset Kaggle pe attach nahi hua hai. Upload check karein.")

root_file = valid_files[0]
is_gzipped = root_file.endswith('.gz')
print(f"✅ Found dataset at: {root_file}")

data_file_in = '/kaggle/working/LLaMA-Factory/data/alpaca_windows_dataset_temp.jsonl'
data_file_out = '/kaggle/working/LLaMA-Factory/data/alpaca_windows_dataset.jsonl'

if is_gzipped:
    print("📦 Extracting gzip file...")
    with gzip.open(root_file, 'rt', encoding='utf-8') as f_in, open(data_file_in, 'w', encoding='utf-8') as f_out:
        shutil.copyfileobj(f_in, f_out)
else:
    shutil.copy(root_file, data_file_in)

print("⚙️ Converting dataset to Alpaca format...")
with open(data_file_in, 'r', encoding='utf-8') as infile, open(data_file_out, 'w', encoding='utf-8') as outfile:
    count = 0
    for line in infile:
        if not line.strip(): continue
        try:
            item = json.loads(line)
            msgs = item.get("messages", [])
            sys_txt, usr_txt, ast_txt = "", "", ""
            for m in msgs:
                if m.get("role") == "system": sys_txt = m.get("content", "")
                elif m.get("role") == "user": usr_txt = m.get("content", "")
                elif m.get("role") == "assistant":
                    if "tool_calls" in m and len(m["tool_calls"]) > 0:
                        ast_txt = json.dumps(m["tool_calls"][0].get("function", {}))
                    else: ast_txt = m.get("content", "")
            
            # Skip empty outputs to avoid training errors
            if not ast_txt: continue
            
            outfile.write(json.dumps({"instruction": sys_txt, "input": usr_txt, "output": ast_txt}, ensure_ascii=False) + '\n')
            count += 1
            # 10k limit removed to allow full dataset usage
        except Exception: 
            continue

# Update dataset_info.json for LLaMA-Factory
filepath = '/kaggle/working/LLaMA-Factory/data/dataset_info.json'
with open(filepath, 'r', encoding='utf-8') as f: 
    info = json.load(f)
info['pulsar_windows_data'] = {"file_name": "alpaca_windows_dataset.jsonl"}
with open(filepath, 'w', encoding='utf-8') as f: 
    json.dump(info, f, indent=2)

print(f"✅ Dataset Setup Complete! Converted {count} valid examples.")

# Create Headless Training Configuration
print("\n📝 Creating Configuration File...")
yaml_config = """
### model
model_name_or_path: unsloth/llama-3-8b-Instruct-bnb-4bit

### method
stage: sft
do_train: true
finetuning_type: lora
lora_target: all

### dataset
dataset: pulsar_windows_data
template: llama3
cutoff_len: 1024
max_samples: 1000000
overwrite_cache: true
preprocessing_num_workers: 16

### output
output_dir: saves/llama3-8b/lora/sft
logging_steps: 10
save_steps: 1000
plot_loss: true
overwrite_output_dir: true

### train
per_device_train_batch_size: 1
gradient_accumulation_steps: 8
learning_rate: 1.0e-4
num_train_epochs: 3.0
lr_scheduler_type: cosine
warmup_ratio: 0.1
bf16: true
ddp_timeout: 180000000
"""

with open('/kaggle/working/LLaMA-Factory/train_config.yaml', 'w', encoding='utf-8') as f:
    f.write(yaml_config.strip())

# Launch Headless Training
print("\n🚀 STARTING HEADLESS TRAINING...")
%env DISABLE_VERSION_CHECK=1
!llamafactory-cli train /kaggle/working/LLaMA-Factory/train_config.yaml
