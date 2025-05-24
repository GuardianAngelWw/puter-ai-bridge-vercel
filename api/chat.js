import axios from 'axios';

// This is a serverless function that will proxy requests to the Puter AI bridge
export default async function handler(req, res) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { prompt, options, sessionId } = req.body;

    // Validate required parameters
    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required' });
    }

    if (!sessionId) {
      return res.status(400).json({ error: 'Session ID is required' });
    }

    // Create a custom document that will be executed in the browser context
    // This approach allows us to leverage the browser's authenticated session
    const script = `
      (async function() {
        try {
          if (!window.puter) {
            return { error: 'Puter API not available' };
          }
          
          // Check if session is valid
          if (!window.puterBridge || !window.puterBridge.isSessionValid('${sessionId}')) {
            return { error: 'Invalid or unauthenticated session' };
          }
          
          // Call Puter AI
          const response = await puter.ai.chat(${JSON.stringify(prompt)}, ${JSON.stringify(options || {})});
          return { success: true, data: response };
        } catch (error) {
          return { error: error.message || 'Unknown error' };
        }
      })();
    `;

    // We'll use a special cookie to execute the script in the browser context
    // In a real implementation, this would be more complex and secure
    res.setHeader('Content-Type', 'application/json');
    res.status(200).json({
      execute: script,
      sessionId,
      _requestType: 'chat'
    });

  } catch (error) {
    console.error('Chat API error:', error);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
}