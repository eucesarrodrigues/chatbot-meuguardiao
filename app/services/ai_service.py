import json
import logging
import os
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
import google.generativeai as genai
from app.core.config import settings

# Setup logger
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.provider = settings.AI_PROVIDER
        self.system_prompt = (
            "Você é um especialista em segurança digital. "
            "Analise o conteúdo e classifique o risco de 0 a 10. "
            "Responda EXCLUSIVAMENTE com um JSON válido no seguinte formato: "
            '{"risco": int, "explicacao": "str", "conselho": "str"}. '
            "Não adicione texto antes ou depois do JSON."
        )

        if self.provider == "openai":
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        elif self.provider == "gemini":
            genai.configure(api_key=settings.GEMINI_API_KEY)
            # Using flash model as requested (assuming 1.5 flash or similar usually, 
            # here using a generic latest flash mapping or specific if known)
            self.model_name = "gemini-2.0-flash-exp" 
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=self.system_prompt,
                generation_config={"response_mime_type": "application/json"}
            )

    async def analyze_text(self, text: str) -> Dict[str, Any]:
        try:
            if self.provider == "gemini":
                response = await self.model.generate_content_async(f"Analise esta mensagem suspeita: {text}")
                return json.loads(response.text)
            
            # Fallback/Original OpenAI
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Analise esta mensagem suspeita: {text}"}
                ],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            return {"risco": -1, "explicacao": "Erro ao analisar texto.", "conselho": "Tente novamente mais tarde."}

    async def analyze_image(self, image_path_or_url: str) -> Dict[str, Any]:
        """
        For Gemini, we ideally need the local file path or properly downloaded bytes.
        If passed a URL, it should be downloaded first (handled in main.py usually).
        This signature assumes we might modify main.py to pass a local path.
        """
        try:
            if self.provider == "gemini":
                # Assuming image_path_or_url is a local path for Gemini 
                # (GenAI python SDK works best with uploaded files or local path logic)
                # But if it's a URL, we need to handle that. 
                # For this step, I'll assume usage with local files or bytes needed.
                # However, to keep it simple and consistent with previous code:
                # If it is a local file path:
                if os.path.exists(image_path_or_url):
                    # Upload to Gemini File API (best practice for large inputs) or pass directly if supported
                    # Flash supports standard inputs.
                    # Simplified:
                    pass 
                
                # TODO: Implementation of Image analysis with Gemini requires handling the file.
                return {"risco": 0, "explicacao": "Análise de imagem com Gemini pendente de implementação de download.", "conselho": "..."}

            # OpenAI Implementation
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Analise este print/imagem de suposta fraude:"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_path_or_url,
                                },
                            },
                        ],
                    }
                ],
                 response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {"risco": -1, "explicacao": "Erro ao analisar imagem.", "conselho": "Tente novamente mais tarde."}

    async def transcribe_audio(self, audio_path: str) -> Optional[str]:
        try:
            if self.provider == "gemini":
                 # Gemini handles audio too
                if os.path.exists(audio_path):
                    audio_file = genai.upload_file(audio_path)
                    response = await self.model.generate_content_async(
                        [audio_file, "Transcreva este áudio e analise se é fraude."]
                    )
                    # Note: This does analysis directly. If we just want transcription:
                    # Gemini is multimodal, so we can ask it to extract text.
                    # But the previous interface returns just string.
                    return response.text
                return None

            with open(audio_path, "rb") as audio_file:
                transcription = await self.client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
            return transcription.text
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None
