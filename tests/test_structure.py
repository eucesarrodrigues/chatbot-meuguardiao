import sys
import os
import asyncio

# Add app to path
sys.path.append("c:/Users/ximba/Documents/chatbot-meuguardiao")

from app.core.config import settings
from app.models.database import User, AnalysisLog
from app.services.ai_service import AIService
from app.services.whatsapp_service import WhatsAppService
from app.main import app

def test_imports():
    print("✅ Config loaded:", settings.APP_NAME)
    print("✅ Models imported:", User, AnalysisLog)
    print("✅ AI Service imported:", AIService)
    print("✅ WhatsApp Service imported:", WhatsAppService)
    print("✅ FastAPI app imported:", app.title)

if __name__ == "__main__":
    test_imports()
