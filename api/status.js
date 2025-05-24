// This is a serverless function that returns the status of the bridge
export default async function handler(req, res) {
  // Only allow GET requests
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Create a script to get the status
    const script = `
      (function() {
        try {
          if (!window.puterBridge) {
            return { error: 'Bridge not initialized' };
          }
          
          // Get the total number of active sessions
          const activeSessions = window.puterBridge.activeSessions || {};
          const sessionCount = Object.keys(activeSessions).length;
          const authenticatedCount = Object.values(activeSessions).filter(s => s.authenticated).length;
          
          return { 
            success: true, 
            status: 'online',
            stats: {
              totalSessions: sessionCount,
              authenticatedSessions: authenticatedCount
            }
          };
        } catch (error) {
          return { error: error.message || 'Unknown error' };
        }
      })();
    `;

    // Return the script to execute
    res.setHeader('Content-Type', 'application/json');
    res.status(200).json({
      execute: script,
      _requestType: 'status'
    });

  } catch (error) {
    console.error('Status API error:', error);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
}