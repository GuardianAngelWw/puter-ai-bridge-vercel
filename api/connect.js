// This is a serverless function that validates a session
export default async function handler(req, res) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { sessionId } = req.body;

    // Validate required parameters
    if (!sessionId) {
      return res.status(400).json({ error: 'Session ID is required' });
    }

    // Create a script to validate the session
    const script = `
      (function() {
        try {
          if (!window.puterBridge) {
            return { error: 'Bridge not initialized' };
          }
          
          const isValid = window.puterBridge.isSessionValid('${sessionId}');
          
          if (isValid) {
            return { success: true, message: 'Session is valid and authenticated' };
          } else {
            return { error: 'Session is not valid or not authenticated' };
          }
        } catch (error) {
          return { error: error.message || 'Unknown error' };
        }
      })();
    `;

    // Return the script to execute
    res.setHeader('Content-Type', 'application/json');
    res.status(200).json({
      execute: script,
      sessionId,
      _requestType: 'connect'
    });

  } catch (error) {
    console.error('Connect API error:', error);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
}