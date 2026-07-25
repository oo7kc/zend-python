"""Quickstart walkthrough of the Zend SDK."""

from __future__ import annotations

import os

from zend import Zend

zend = Zend(os.environ.get("ZEND_API_KEY"))


def main() -> None:
    # SMS — every option (keep only what you need)
    sms = zend.messages.send(
        to="+233201234567",
        body="Hello from Zend!",
        preferred_channels=["sms"],
        sender_id="MyBrand",
        fallback_enabled=True,
        priority="high",
        delivery_priority="speed",
        webhook_url="https://your-app.com/webhooks/zend",
        # scheduled_for="2026-08-01T09:00:00Z",
    )
    if sms.error:
        raise sms.error
    assert sms.data is not None
    print(f"Message {sms.data.id} ({sms.data.status})")

    # WhatsApp with a template, falling back to SMS
    _ = zend.messages.send(
        to="+233201234567",
        template_id="welcome",
        template_params={"first_name": "John"},
        preferred_channels=["whatsapp", "sms"],
        fallback_enabled=True,
        sender_id="MyBrand",
    )

    # Bulk send
    _ = zend.messages.send_bulk(
        messages=[
            {"to": "+233201234567", "body": "Hi Ama!"},
            {
                "to": "+233207654321",
                "body": "Your code is 123456",
                "template_params": {"code": "123456"},
            },
        ],
        preferred_channels=["sms"],
        sender_id="MyBrand",
        fallback_enabled=True,
        webhook_url="https://your-app.com/webhooks/zend",
    )

    # Email
    email = zend.emails.send(
        **{
            "from": "you@example.com",
            "to": "user@gmail.com",
            "subject": "Hello world",
            "html": "<p>It works!</p>",
            "text": "It works!",
        }
    )
    if email.error:
        raise email.error
    assert email.data is not None
    print(f"Email {email.data.id} sent")

    # Voice — text-to-speech with all options
    _ = zend.voice.send(
        recipients=["+233201234567"],
        text="Your order has shipped.",
        voice="female",
        retry=True,
        callback_url="https://your-app.com/webhooks/voice",
        fallback={
            "sms": True,
            "sms_text": "Your order has shipped.",
            "sender_id": "MyBrand",
        },
    )

    # Voice — a pre-recorded audio file
    _ = zend.voice.send(
        recipients=["+233201234567"],
        voice_url="https://cdn.example.com/message.mp3",
        fallback={"sms": True, "sms_text": "You have a new message."},
    )

    # Templates (read-only)
    templates = zend.templates.list(
        category="transactional",
        status="active",
        limit=20,
        offset=0,
    )
    print(f"You have {templates.data.total if templates.data else 0} templates")

    _ = zend.close()


if __name__ == "__main__":
    main()
