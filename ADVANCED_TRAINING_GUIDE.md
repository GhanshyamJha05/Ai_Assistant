# 🧠 YourDaddy AI - Ultimate Fine-Tuning Guide

Hi there! If you're reading this, you are the friend tasked with taking our massive 2.5 million line dataset and turning it into a hyper-intelligent, OS-controlling AI model. 

We have prepared everything for you. The raw dataset was 1.3 GB, but we compressed it into highly efficient `.jsonl.gz` files located in `data/training/`.

Follow this step-by-step guide to train the model from **Absolute Zero to a working GGUF model** using **Unsloth** (the fastest fine-tuning library).

---

## 🛠️ Step 1: Where to Train?
Training a model on 2.5 million lines requires a GPU. Do **not** try to train this on a standard laptop CPU.
1. Go to **[Google Colab](https://colab.research.google.com/)** (Free T4 GPU is okay, A100 is better).
2. Create a New Notebook.
3. Go to **Runtime -> Change runtime type** -> Select **T4 GPU** (or A100 if you have Colab Pro).

## 📥 Step 2: Install Unsloth & Dependencies
In the first cell of your notebook, run this to install Unsloth (which makes Llama-3 training 2x faster and uses 70% less VRAM):

```python
%%capture
!pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
!pip install --no-deps "xformers<0.0.27" "trl<0.9.0" peft accelerate bitsandbytes
```

## 🤖 Step 3: Load the Base Model (Llama-3 8B)
We will use Llama-3 8B as the base model because it's brilliant at understanding Hindi/Hinglish natively.

```python
from unsloth import FastLanguageModel
import torch

max_seq_length = 2048 # Good for OS commands
dtype = None
load_in_4bit = True # Saves memory

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/llama-3-8b-Instruct-bnb-4bit",
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

# Add LoRA adapters (This is what we actually train, not the whole model)
model = FastLanguageModel.get_peft_model(
    model,
    r = 16, 
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 3407,
    use_rslora = False,
)
```

## 📂 Step 4: Load Our Massive Dataset
Upload `ultimate_windows_dataset_v3.jsonl.gz` from the GitHub repo to your Colab environment.

```python
from datasets import load_dataset

# HuggingFace datasets natively reads .gz compressed files! No extraction needed.
dataset = load_dataset("json", data_files="ultimate_windows_dataset_v3.jsonl.gz", split="train")

def format_chat_template(examples):
    # This formats our JSON data into Llama-3's strict ChatML format
    texts = []
    for messages in examples["messages"]:
        texts.append(tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False))
    return { "text" : texts, }

dataset = dataset.map(format_chat_template, batched = True)
```

## 🔥 Step 5: Start Training!
We use the HuggingFace `SFTTrainer`. 

```python
from trl import SFTTrainer
from transformers import TrainingArguments

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    dataset_num_proc = 2,
    packing = False, # Can make training 5x faster for short sequences
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        max_steps = 1000, # Start with 1000 steps to test, then increase for full dataset
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "outputs",
    ),
)

trainer_stats = trainer.train()
```

## 📦 Step 6: Export to GGUF (For Local PC)
Once training is done, we need to export it to `.gguf` format so your friend (the developer) can run it offline on their Windows laptop using Ollama!

```python
# Save locally to Colab
model.save_pretrained("yourdaddy_lora_model")
tokenizer.save_pretrained("yourdaddy_lora_model")

# Export to 4-bit GGUF (This takes about 10-15 minutes in Colab)
model.push_to_hub_gguf(
    "your_huggingface_username/YourDaddy-OS-Model", 
    tokenizer, 
    quantization_method = "q4_k_m",
    token = "YOUR_HUGGINGFACE_TOKEN"
)
```

## 🚀 Step 7: Run it on Your Windows PC!
Now that the model is trained and uploaded to HuggingFace as a `.gguf`, the core team can download it and run it inside the Desktop app.

1. Download [Ollama](https://ollama.com/) on the Windows PC.
2. Create a file named `Modelfile` on your desktop:
```dockerfile
FROM hf.co/your_huggingface_username/YourDaddy-OS-Model:Q4_K_M
TEMPLATE """{{ if .System }}<|start_header_id|>system<|end_header_id|>
{{ .System }}<|eot_id|>{{ end }}{{ if .Prompt }}<|start_header_id|>user<|end_header_id|>
{{ .Prompt }}<|eot_id|>{{ end }}<|start_header_id|>assistant<|end_header_id|>
"""
```
3. Run `ollama create yourdaddy -f Modelfile`
4. Run `ollama run yourdaddy`

**Congratulations! The AI is now ready to control your OS!**
