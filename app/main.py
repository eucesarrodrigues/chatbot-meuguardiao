from fastapi import FastAPI, BackgroundTasks, Request, HTTPException
from tortoise.contrib.fastapi import register_tortoise
import logging
from typing import Dict, Any

from app.core.config import settings
from app.models.database import User, AnalysisLog
from app.services.ai_service import AIService
from app.services.whatsapp_service import WhatsAppService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME)

ai_service = AIService()
whatsapp_service = WhatsAppService()

async def process_message(payload: Dict[str, Any]):
    """
    Background task to process incoming WhatsApp messages.
    """
    try:
        data = payload.get("data", {})
        message_type = data.get("messageType")
        
        # Extract sender info
        remote_jid = data.get("key", {}).get("remoteJid", "")
        if not remote_jid:
            logger.warning("No remoteJid found in payload")
            return
            
        phone = remote_jid.split("@")[0]
        push_name = data.get("pushName", "Unknown")

        # Get or create user
        user, _ = await User.get_or_create(phone=phone, defaults={"name": push_name})

        # Process content based on type
        analysis_result = None
        content_to_log = ""
        media_type = "text"

        if message_type == "conversation" or message_type == "extendedTextMessage":
            text = data.get("message", {}).get("conversation") or data.get("message", {}).get("extendedTextMessage", {}).get("text")
            if text:
                content_to_log = text
                analysis_result = await ai_service.analyze_text(text)

        elif message_type == "imageMessage":
            media_type = "image"
            # Logic to download image would go here. 
            # For MVP, assuming we get a public URL or base64. 
            # Evolution API often sends a url in the payload or needs a separate call to get the media.
            # Simplified for this step as per common Evolution API patterns (using url if available or assuming text for now if not implemented)
            # TODO: Implement full media download flow. For now, we skip if no URL.
            logger.info("Image processing pending implementation details of file handling.")
            return 

        elif message_type == "audioMessage":
             media_type = "audio"
             # similarly requires download
             logger.info("Audio processing pending implementation details of file handling.")
             return

        if analysis_result:
            # Log to DB
            await AnalysisLog.create(
                user=user,
                message_content=content_to_log,
                media_type=media_type,
                risk_score=analysis_result.get("risco", 0),
                explanation=analysis_result.get("explicacao", ""),
                advice=analysis_result.get("conselho", "")
            )

            # Send response
            response_text = (
                f"*Análise do Guardião* 🛡️\n\n"
                f"🚨 *Risco:* {analysis_result.get('risco')}/10\n"
                f"🧐 *Explicação:* {analysis_result.get('explicacao')}\n\n"
                f"💡 *Conselho:* {analysis_result.get('conselho')}"
            )
            await whatsapp_service.send_text(remote_jid, response_text)

    except Exception as e:
        logger.error(f"Error processing message: {e}")

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint called by Evolution API.
    """
    try:
        payload = await request.json()
        
        # Verify if it's a message upsert event (Evolution API specific)
        event = payload.get("event")
        if event == "messages.upsert":
            background_tasks.add_task(process_message, payload)
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/")
async def health_check():
    return {"status": "running", "app": settings.APP_NAME}

# Register Tortoise ORM
register_tortoise(
    app,
    db_url=settings.DATABASE_URL,
    modules={"models": ["app.models.database"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
