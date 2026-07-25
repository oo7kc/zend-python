# usezend

Official Python client for the [Zend](https://tryzend.dev) messaging platform. Send SMS, WhatsApp, email, and voice messages — and manage message templates — from a single, typed client.

📚 **[Read the docs →](https://tryzend.com/docs)**

## Installation

```bash
pip install usezend
```

Requires Python 3.10 or later.

## Usage

Create a client with your API key:

```python
from zend import Zend

zend = Zend("sent_live_...")
```

The API key can also be supplied via the `ZEND_API_KEY` environment variable:

```python
zend = Zend()
```

Override the base URL or request timeout (in **seconds**) — or set `ZEND_BASE_URL`:

```python
zend = Zend(
    "sent_live_...",
    base_url="https://staging.api.tryzend.com",
    timeout=30.0,
)
```

> **Note:** `base_url` defaults to `https://api.tryzend.com`, and `timeout` defaults to 30s.

Prefer a context manager so the underlying HTTP connection pool is closed cleanly:

```python
with Zend("sent_live_...") as zend:
    result = zend.messages.send(to="+233201234567", body="Hello!")
```

Every method returns a `ZendResponse` with `{ data, error }` — see [Errors](#errors) below.

### Async client

```python
from zend import AsyncZend

async with AsyncZend("sent_live_...") as zend:
    sms = await zend.messages.send(to="+233201234567", body="Hello from Zend!")
    if sms.error:
        raise sms.error
    print(sms.data.id)
```

## Send SMS / WhatsApp

```python
sms = zend.messages.send(
    to="+233201234567",
    body="Hello from Zend!",
    preferred_channels=["sms"],
    sender_id="MyBrand",
    fallback_enabled=True,
    priority="high",
    delivery_priority="speed",
    webhook_url="https://your-app.com/webhooks/zend",
)

if sms.error:
    raise sms.error
print(f"Message {sms.data.id} ({sms.data.status})")
```

WhatsApp with a template, falling back to SMS:

```python
zend.messages.send(
    to="+233201234567",
    template_id="welcome",
    template_params={"first_name": "John"},
    preferred_channels=["whatsapp", "sms"],
    fallback_enabled=True,
    sender_id="MyBrand",
)
```

Bulk send:

```python
zend.messages.send_bulk(
    messages=[
        {"to": "+233201234567", "body": "Hi Ama!"},
        {"to": "+233207654321", "body": "Your code is 123456", "template_params": {"code": "123456"}},
    ],
    preferred_channels=["sms"],
    sender_id="MyBrand",
    fallback_enabled=True,
    webhook_url="https://your-app.com/webhooks/zend",
)
```

Other `messages` methods: `get(id)`, `list(params?)`, `cancel(id)`, `retry(id)`.

## Send Email

```python
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
print(f"Email {email.data.id} sent")
```

Or pass `from_=` to avoid the `from` keyword clash:

```python
zend.emails.send(
    from_="you@example.com",
    to="user@gmail.com",
    subject="Hello world",
    html="<p>It works!</p>",
)
```

Attachments — `content` is `bytes` or a base64 string:

```python
zend.emails.send(
    from_="you@example.com",
    to="user@gmail.com",
    subject="Your invoice",
    html="<p>Invoice attached.</p>",
    attachments=[{"filename": "invoice.pdf", "content": pdf_bytes, "content_type": "application/pdf"}],
)
```

Other `emails` methods: `get(id)`, `list(params?)`.

## Send Voice

```python
zend.voice.send(
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
```

Upload a local audio file, then pass the returned URL:

```python
uploaded = zend.voice.upload(open("message.mp3", "rb"), "message.mp3")
if uploaded.error:
    raise uploaded.error
zend.voice.send(recipients=["+233201234567"], voice_url=uploaded.data.url)
```

Other `voice` methods: `get(batch_id)`, `list(params?)`.

## Templates

```python
templates = zend.templates.list(
    category="transactional",
    status="active",
    limit=20,
    offset=0,
)
print(f"You have {templates.data.total if templates.data else 0} templates")

template = zend.templates.get("welcome")
print(template.data.name if template.data else None)
```

## Errors

Every SDK method returns — it never raises for API or network errors. The result is always:

```python
ZendResponse(data=T, error=None) | ZendResponse(data=None, error=ZendError)
```

```python
sms = zend.messages.send(to="+233201234567", body="Hello!")

if sms.error:
    raise sms.error

print(sms.data.id)
```

`ZendError` subclasses include `APIError`, `BadRequestError`, `AuthenticationError`, `RateLimitError`, `ServerError`, `TimeoutError`, and `ApplicationError`. Attributes:

- `name` — e.g. `"api_error"`, `"timeout"`, `"application_error"`
- `status_code` — HTTP status when available
- `code` — provider error code when available

## Full example

See [`examples/quickstart.py`](./examples/quickstart.py) for a complete walkthrough.
