# SQLCoder-7B-2 via Hugging Face Transformers

## Overview
Replaced Ollama with direct Hugging Face Transformers implementation of SQLCoder-7B-2.

## What Changed

### Before (Ollama)
- Required separate Ollama service running
- API calls to localhost:11434
- 30-60 second response times
- 4.1 GB model download via Ollama

### After (Transformers)
- Model loads directly in Python
- No external service needed
- Faster inference (GPU accelerated)
- ~14 GB model download from Hugging Face

## Installation

### 1. Install Dependencies
```bash
pip install transformers torch accelerate
```

### 2. Model Download
The model will auto-download on first run (~14 GB):
- Model: `defog/sqlcoder-7b-2`
- Location: `~/.cache/huggingface/`

### 3. GPU Support (Optional but Recommended)
For CUDA GPU acceleration:
```bash
# Check if CUDA is available
python -c "import torch; print(torch.cuda.is_available())"

# If False, install CUDA-enabled PyTorch
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

## Configuration

### .env File
```env
LLM_PROVIDER=sqlcoder
LLM_MODEL=defog/sqlcoder-7b-2
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=200
```

## How It Works

### Code Flow
1. **Model Loading** (on startup):
   ```python
   from transformers import AutoTokenizer, AutoModelForCausalLM
   tokenizer = AutoTokenizer.from_pretrained("defog/sqlcoder-7b-2")
   model = AutoModelForCausalLM.from_pretrained(
       "defog/sqlcoder-7b-2",
       torch_dtype=torch.float16,  # GPU
       device_map="auto"
   )
   ```

2. **SQL Generation** (per query):
   ```python
   prompt = f"""### Database Schema:
   {schema_info}
   
   ### Question:
   {nl_query}
   
   ### SQL Query:
   """
   
   inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
   outputs = model.generate(**inputs, max_new_tokens=200)
   sql = tokenizer.decode(outputs[0], skip_special_tokens=True)
   ```

3. **Variations**: Generate 2 additional SQL variations using rules

## Performance

### GPU (CUDA)
- **First Load**: 30-60 seconds (model loading)
- **Inference**: 2-5 seconds per query
- **Memory**: 8-16 GB VRAM

### CPU
- **First Load**: 60-120 seconds
- **Inference**: 30-60 seconds per query
- **Memory**: 16-32 GB RAM

## Advantages vs Ollama

| Feature | Transformers | Ollama |
|---------|-------------|--------|
| **Setup** | pip install | Separate app install |
| **Service** | None needed | Must run Ollama server |
| **GPU Support** | Native CUDA | Limited |
| **Speed (GPU)** | 2-5s | 30-60s |
| **Memory** | 8-16 GB VRAM | 4 GB disk |
| **Customization** | Full control | Limited |

## System Requirements

### Minimum (CPU)
- 16 GB RAM
- 20 GB disk space
- Python 3.8+

### Recommended (GPU)
- NVIDIA GPU with 8+ GB VRAM
- 16 GB RAM
- 20 GB disk space
- CUDA 11.8+

## Troubleshooting

### Issue: Out of Memory
```
RuntimeError: CUDA out of memory
```

**Solution**: Use CPU mode or smaller batch size
```python
# In llm_client.py, change:
torch_dtype=torch.float32  # Instead of float16
device_map="cpu"  # Instead of "auto"
```

### Issue: Model Download Fails
```
HTTPError: 403 Client Error
```

**Solution**: Login to Hugging Face
```bash
pip install huggingface-hub
huggingface-cli login
```

### Issue: Slow on CPU
```
Generation takes 60+ seconds
```

**Solution**: 
1. Install CUDA-enabled PyTorch
2. Or use mock mode for development
3. Or reduce max_tokens to 100

## Testing

### Quick Test
```python
python test_sqlcoder_transformers.py
```

### Expected Output
```
Loading SQLCoder model: defog/sqlcoder-7b-2 on cuda...
SQLCoder model loaded successfully on cuda
Generating SQL with SQLCoder-7B-2...
SQLCoder generated: SELECT name FROM sys.tables WHERE type = 'U';
```

## Migration from Ollama

### What to Remove
1. Uninstall Ollama (optional)
2. Remove `ollama pull sqlcoder:7b` models
3. No need to run Ollama service

### What to Keep
- All other code remains the same
- Mock mode still works as fallback
- RL agent, caching, optimizer unchanged

## Production Considerations

### Model Caching
- Model loads once on startup
- Stays in memory for fast inference
- ~8-16 GB VRAM/RAM usage

### Scaling
- Single model instance per server
- Use GPU for production
- Consider model quantization for lower memory

### Alternatives
- **Smaller Model**: Use `defog/sqlcoder-3b` (less accurate, faster)
- **Quantized**: Use 8-bit or 4-bit quantization
- **Cloud**: Use Hugging Face Inference API

## Next Steps

1. Install dependencies: `pip install transformers torch accelerate`
2. Start server: `python run_api.py`
3. Wait for model download (~14 GB, one-time)
4. Test with Postman or test script
5. Monitor GPU/CPU usage

## Summary

✅ **Removed**: Ollama service dependency  
✅ **Added**: Direct Transformers integration  
✅ **Benefit**: Faster inference with GPU  
✅ **Trade-off**: Larger initial download  
✅ **Fallback**: Mock mode still available
