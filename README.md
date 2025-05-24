# Puter AI Bridge for Vercel

This is a simplified version of the Puter AI bridge optimized for deployment on Vercel. It creates a bridge between your Telegram bot and Puter AI services, allowing you to use Puter AI from your Telegram bot.

## Quick Start

### 1. Deploy to Vercel

The easiest way to deploy is with the Vercel Deploy button:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FGuardianAngelWw%2Fputer-ai-bridge-vercel)

Alternatively, you can fork this repository and deploy it manually through the Vercel dashboard.

### 2. Open the Deployed Bridge

Once deployed, open your Vercel deployment URL in a browser. You'll see a simple interface with:

1. A "Sign in with Puter" button - click this to authenticate
2. After signing in, you'll see a session ID and the bridge URL

### 3. Configure the Telegram Bot

Clone this repository and navigate to the `bot` directory:

```bash
# Install dependencies
pip install python-telegram-bot requests

# Set environment variables
export TELEGRAM_TOKEN="your_telegram_bot_token"
export BRIDGE_URL="your_vercel_deployment_url"
export SESSION_ID="session_id_from_bridge_interface"

# Run the bot
python telegram_bot.py
```

## How It Works

1. **Authentication**: The web page authenticates with Puter using browser-based authentication
2. **Session Management**: Each authentication generates a unique session ID
3. **API Bridge**: The Vercel serverless functions provide API endpoints for the Telegram bot
4. **Automatic Bridge**: The Telegram bot automatically connects using the configured session ID

## Deployment Options

### Vercel (Recommended)

This repository is optimized for Vercel deployment, which offers:

- Free tier with generous limits
- Automatic HTTPS
- Global CDN
- Serverless functions for the API

### Other Options

You can also deploy to:

- Netlify (similar to Vercel)
- GitHub Pages (static part only)
- Any static hosting with a separate API solution

## Security Considerations

- The session ID provides access to your Puter account through the bridge
- Keep your session ID private
- For production use, implement proper authentication for the bridge API

## Troubleshooting

### Common Issues

- **Authentication Error**: Try clearing your browser cookies and signing in again
- **Bot Can't Connect**: Verify your BRIDGE_URL and SESSION_ID environment variables
- **API Errors**: Make sure you're signed in to the bridge page in your browser

### Checking Status

Use the `/bridge_status` command in your Telegram bot to check the connection status.

## Advanced Usage

### Custom Options

You can pass custom options to the Puter AI API by modifying the `options` parameter in the API calls. See the [Puter AI documentation](https://docs.puter.com/AI/chat/) for available options.

### Multiple Sessions

You can create multiple sessions by opening the bridge in different browsers or private windows. Each session will generate a unique ID that can be used with different bots.