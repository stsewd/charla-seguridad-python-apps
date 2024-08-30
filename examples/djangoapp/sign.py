import hashlib
import hmac

WEBHOOK_SECRET = "very-secret-and-random-value"
payload = '{"name": "test"}\n'

digest = hmac.new(
    key=WEBHOOK_SECRET.encode(),
    msg=payload.encode(),
    digestmod=hashlib.sha256,
)
print(digest.hexdigest())
