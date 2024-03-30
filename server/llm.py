import llama_cpp
from llama_cpp.llama_types import List
from transformers import GemmaTokenizerFast

class Tokenizer(llama_cpp.BaseLlamaTokenizer):
    tokenizer = GemmaTokenizerFast.from_pretrained('../../gemma-7b-it/')

    def tokenize(self, text: bytes, add_bos: bool = True, special: bool = True) -> List[int]:
        return self.tokenizer.encode(text.decode("utf-8", errors="ignore"), add_special_tokens=special)
    
    def detokenize(self, tokens: List[int], prev_tokens: List[int] | None = None) -> bytes:
        return self.tokenizer.decode(tokens).encode("utf-8", errors="ignore")
    
    def encode(self, text: str, add_bos: bool = True, special: bool = True) -> List[int]:
        return self.tokenize(text.encode("utf-8", errors="ignore"), add_special_tokens=special)
    
    def decode(self, tokens: List[int]) -> str:
        return self.detokenize(tokens).decode("utf-8", errors="ignore")
        
tokenizer = Tokenizer()

model = llama_cpp.Llama(
    model_path="../../gemma-7b-it/gemma-7b-it.gguf",
    chat_format="gemma",
    use_mlock=True,
    n_ctx=0,
    n_gpu_layers=-1,
    n_threads=6,
    n_threads_batch=6,
    tokenizer=tokenizer
)