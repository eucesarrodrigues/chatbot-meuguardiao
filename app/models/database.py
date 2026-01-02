from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

class User(models.Model):
    id = fields.IntField(pk=True)
    phone = fields.CharField(max_length=20, unique=True, index=True)
    name = fields.CharField(max_length=100, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"

class AnalysisLog(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="logs")
    message_content = fields.TextField(null=True)
    media_type = fields.CharField(max_length=20)  # text, image, audio
    risk_score = fields.IntField()
    explanation = fields.TextField()
    advice = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "analysis_logs"

# Pydantic models for serialization if needed later
User_Pydantic = pydantic_model_creator(User, name="User")
AnalysisLog_Pydantic = pydantic_model_creator(AnalysisLog, name="AnalysisLog")
