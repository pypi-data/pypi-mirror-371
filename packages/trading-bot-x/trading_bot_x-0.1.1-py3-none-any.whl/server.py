import os
import logging
import asyncio
import hmac
from typing import List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field


class ModelManager:
    """Manage loading and inference model state."""

    def __init__(self) -> None:
        self.tokenizer = None
        self.model = None
        self.device = None
        self.torch = None

    def load_model(self) -> str:
        """Load the tokenizer and model into instance attributes.

        Returns "primary" if the main model is loaded, "fallback" if the
        fallback model is loaded instead.
        """

        try:
            import torch as torch_module
        except ImportError as exc:
            raise RuntimeError(
                "torch is required to load the model. Install it with 'pip install torch'."
            ) from exc

        device_local = "cuda" if torch_module.cuda.is_available() else "cpu"

        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:
            raise RuntimeError(
                "transformers is required to load the model. Install it with 'pip install transformers'."
            ) from exc

        model_name = os.getenv("GPT_MODEL", "openai/gpt-oss-20b")
        fallback_model = os.getenv("GPT_MODEL_FALLBACK", "sshleifer/tiny-gpt2")

        try:
            tokenizer_local = AutoTokenizer.from_pretrained(
                model_name,
                revision="10e9d713f8e4a9281c59c40be6c58537480635ea",
                trust_remote_code=False,
            )
            model_local = (
                AutoModelForCausalLM.from_pretrained(
                    model_name,
                    revision="10e9d713f8e4a9281c59c40be6c58537480635ea",
                    trust_remote_code=False,
                )
                .to(device_local)
            )
        except Exception:
            logging.exception("Failed to load model '%s'", model_name)
        else:
            self.tokenizer = tokenizer_local
            self.model = model_local
            self.device = device_local
            self.torch = torch_module
            return "primary"

        try:
            tokenizer_local = AutoTokenizer.from_pretrained(
                fallback_model,
                revision="5f91d94bd9cd7190a9f3216ff93cd1dd95f2c7be",
                trust_remote_code=False,
            )
            model_local = (
                AutoModelForCausalLM.from_pretrained(
                    fallback_model,
                    revision="5f91d94bd9cd7190a9f3216ff93cd1dd95f2c7be",
                    trust_remote_code=False,
                )
                .to(device_local)
            )
        except Exception:
            logging.exception("Failed to load fallback model '%s'", fallback_model)
            raise RuntimeError("Failed to load both primary and fallback models")
        else:
            self.tokenizer = tokenizer_local
            self.model = model_local
            self.device = device_local
            self.torch = torch_module
            logging.info("Loaded fallback model '%s'", fallback_model)
            return "fallback"

    async def load_model_async(self) -> None:
        """Asynchronously load the model without blocking the event loop.

        Raises:
            RuntimeError: If both primary and fallback models fail to load.
        """
        await asyncio.to_thread(self.load_model)


model_manager = ModelManager()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await model_manager.load_model_async()
    yield


app = FastAPI(lifespan=lifespan)

API_KEYS = {k.strip() for k in os.getenv("API_KEYS", "").split(",") if k.strip()}


@app.middleware("http")
async def check_api_key(request: Request, call_next):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return Response(status_code=401)
    token = auth[7:]
    for key in API_KEYS:
        if hmac.compare_digest(token, key):
            break
    else:
        return Response(status_code=401)
    return await call_next(request)




def generate_text(
    manager: ModelManager,
    prompt: str,
    *,
    temperature: float = 0.7,
    max_new_tokens: int = 16,
) -> str:
    """Generate text from *prompt* using the loaded model."""
    if manager.tokenizer is None or manager.model is None:
        raise RuntimeError("Model is not loaded")
    inputs = manager.tokenizer(prompt, return_tensors="pt").to(manager.device)
    with manager.torch.no_grad():
        outputs = manager.model.generate(
            **inputs,
            temperature=temperature,
            max_new_tokens=max_new_tokens,
        )
    text = manager.tokenizer.decode(outputs[0], skip_special_tokens=True)
    if text.startswith(prompt):
        text = text[len(prompt) :]
    return text


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(16, ge=1, le=512)


class CompletionRequest(BaseModel):
    prompt: str
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(16, ge=1, le=512)


@app.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest):
    if model_manager.tokenizer is None or model_manager.model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded")
    prompt = "\n".join(message.content for message in req.messages)
    text = generate_text(
        model_manager,
        prompt,
        temperature=req.temperature,
        max_new_tokens=req.max_tokens,
    )
    return {"choices": [{"message": {"role": "assistant", "content": text}}]}


@app.post("/v1/completions")
async def completions(req: CompletionRequest):
    if model_manager.tokenizer is None or model_manager.model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded")
    text = generate_text(
        model_manager,
        req.prompt,
        temperature=req.temperature,
        max_new_tokens=req.max_tokens,
    )
    return {"choices": [{"text": text}]}
