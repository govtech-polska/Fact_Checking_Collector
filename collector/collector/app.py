from datetime import datetime, timezone
from uuid import uuid4

from fastapi import Depends, FastAPI
from starlette import status

from collector.consts import NewsOrigin
from collector.db import get_db, t_news_draft
from collector.schema import (
    ChatbotVerificationRequestSchema,
    MobileVerificationRequestSchema,
    VerificationRequestSchema,
)
from collector.services import RecaptchaService
from collector.storage import get_bucket, get_file_url

app = FastAPI()


@app.get("/")
def health_check() -> None:
    return


@app.post("/verification-request", status_code=status.HTTP_201_CREATED)
def create_verification_request(
    payload: VerificationRequestSchema = Depends(),
    db=Depends(get_db),
    bucket=Depends(get_bucket),
    recaptcha_service: RecaptchaService = Depends(),
):
    recaptcha_service.verify_response(payload.recaptcha)

    image_name = f"{str(uuid4())}.jpg"
    news_draft = dict(
        id=str(uuid4()).replace("-", ""),
        reporter_email=payload.email,
        comment=payload.comment,
        url=payload.url,
        text=payload.text,
        screenshot_url=get_file_url(bucket, image_name),
        reported_at=datetime.now(tz=timezone.utc),
        origin=NewsOrigin.PLUGIN.value,
    )

    db.execute(t_news_draft.insert().values(news_draft))

    bucket.upload_fileobj(
        payload.image.file, image_name, ExtraArgs={"ACL": "public-read"},
    )

    return news_draft


@app.post("/chatbot-verification-request", status_code=status.HTTP_201_CREATED)
def create_chatbot_verification_request(
    payload: ChatbotVerificationRequestSchema, db=Depends(get_db),
):
    news_draft = dict(
        id=str(uuid4()).replace("-", ""),
        reporter_email=payload.email,
        comment=payload.question,
        url=payload.source,
        reported_at=datetime.now(tz=timezone.utc),
        screenshot_url="",
        text="",
        origin=NewsOrigin.CHATBOT.value,
    )

    db.execute(t_news_draft.insert().values(news_draft))

    return dict(
        id=news_draft["id"],
        reporter_email=news_draft["reporter_email"],
        question=news_draft["comment"],
        source=news_draft["url"],
        reported_at=news_draft["reported_at"],
    )


@app.post("/mobile-verification-request", status_code=status.HTTP_201_CREATED)
def create_mobile_verification_request(
    payload: MobileVerificationRequestSchema = Depends(),
    db=Depends(get_db),
    bucket=Depends(get_bucket),
):
    image_name = f"{str(uuid4())}.jpg"
    screenshot_url = get_file_url(bucket, image_name) if payload.image else ""

    news_draft = dict(
        id=str(uuid4()).replace("-", ""),
        reporter_email=payload.email,
        comment=payload.comment,
        url=payload.url,
        reported_at=datetime.now(tz=timezone.utc),
        screenshot_url=screenshot_url,
        text="",
        origin=NewsOrigin.MOBILE.value,
    )

    db.execute(t_news_draft.insert().values(news_draft))

    if payload.image:
        bucket.upload_fileobj(
            payload.image.file, image_name, ExtraArgs={"ACL": "public-read"},
        )

    return dict(
        id=news_draft["id"],
        reporter_email=news_draft["reporter_email"],
        comment=news_draft["comment"],
        url=news_draft["url"],
        reported_at=news_draft["reported_at"],
        screenshot_url=screenshot_url,
    )
