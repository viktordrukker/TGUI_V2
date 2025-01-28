# Setting Up Webhook URL for Telegram Bots

## Local Development

1. Install ngrok:
```bash
# On Linux/Mac
brew install ngrok
# Or download from https://ngrok.com/download

# On Windows
choco install ngrok
```

2. Start ngrok tunnel (use the port where your Flask app runs):
```bash
ngrok http 5000
```

3. Get your webhook URL:
```
https://<your-ngrok-subdomain>.ngrok.io/bots/webhook/<bot_token>
```

Example:
If ngrok shows `https://a1b2c3d4.ngrok.io` and your bot token is `123456:ABC-DEF`, your webhook URL would be:
`https://a1b2c3d4.ngrok.io/bots/webhook/123456:ABC-DEF`

## Production Setup

1. Use your domain:
```
https://yourdomain.com/bots/webhook/<bot_token>
```

2. Ensure SSL is enabled (Telegram requires HTTPS)

3. Configure your web server (nginx example):
```nginx
location /bots/webhook/ {
    proxy_pass http://localhost:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## Webhook URL Format

The webhook URL should follow this pattern:
```
https://<domain>/bots/webhook/<bot_token>
```

Where:
- `<domain>` is your ngrok URL or production domain
- `<bot_token>` is your Telegram bot token

## Security Notes

1. Each bot should have a unique webhook path
2. Use HTTPS only
3. Keep your bot token secret
4. Configure firewall rules
5. Monitor webhook requests

## Testing Webhook

1. Using curl:
```bash
curl -F "url=https://your-domain.com/bots/webhook/your-bot-token" https://api.telegram.org/bot<your-bot-token>/setWebhook
```

2. Check webhook status:
```bash
curl https://api.telegram.org/bot<your-bot-token>/getWebhookInfo
```

## Troubleshooting

1. Webhook must use HTTPS
2. Domain must have valid SSL certificate
3. Check firewall settings
4. Verify bot token is correct
5. Check server logs for errors