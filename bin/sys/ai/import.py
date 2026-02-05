from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Загрузка модели (первый запуск скачает ~2.3 ГБ)
model_id = "microsoft/Phi-3-mini-4k-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="cpu",  # или "cuda" если есть NVIDIA GPU
    torch_dtype=torch.float32,  # float16 для GPU
    trust_remote_code=True
)

# Диалог
def chat(query, history=""):
    prompt = f"{history}\nUser: {query}\nAssistant:"
    inputs = tokenizer(prompt, return_tensors="pt")
    
    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        pad_token_id=tokenizer.eos_token_id
    )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response.split("Assistant:")[-1].strip()

# Пример использования
print(chat("Привет! Кто ты?"))
# → "Я — языковая модель Phi-3, созданная Microsoft..."

print(chat("Какие планеты в Солнечной системе?"))