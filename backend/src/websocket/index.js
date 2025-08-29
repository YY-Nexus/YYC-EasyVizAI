import { logger } from '../utils/logger.js';

const clients = new Map();

export function setupWebSocket(wss) {
  wss.on('connection', (ws, req) => {
    const url = new URL(req.url, `http://${req.headers.host}`);
    const topics = url.searchParams.get('topics')?.split(',') || [];
    const accessToken = url.searchParams.get('access_token');
    
    const clientId = generateClientId();
    
    logger.info('WebSocket client connected', { 
      clientId, 
      topics, 
      userAgent: req.headers['user-agent'],
      origin: req.headers.origin 
    });

    // Store client information
    clients.set(clientId, {
      ws,
      topics,
      accessToken,
      connectedAt: new Date().toISOString(),
      lastPing: Date.now()
    });

    // Send welcome message
    ws.send(JSON.stringify({
      type: 'connection',
      clientId,
      message: 'Connected to YYC³ EasyVizAI WebSocket',
      timestamp: new Date().toISOString()
    }));

    // Handle incoming messages
    ws.on('message', (data) => {
      try {
        const message = JSON.parse(data.toString());
        handleWebSocketMessage(clientId, message);
      } catch (error) {
        logger.error('WebSocket message parsing error:', error);
        ws.send(JSON.stringify({
          type: 'error',
          message: 'Invalid message format',
          timestamp: new Date().toISOString()
        }));
      }
    });

    // Handle pings
    ws.on('ping', () => {
      const client = clients.get(clientId);
      if (client) {
        client.lastPing = Date.now();
        ws.pong();
      }
    });

    // Handle client disconnect
    ws.on('close', () => {
      logger.info('WebSocket client disconnected', { clientId });
      clients.delete(clientId);
    });

    // Handle errors
    ws.on('error', (error) => {
      logger.error('WebSocket error:', { clientId, error: error.message });
      clients.delete(clientId);
    });
  });

  // Cleanup inactive connections
  setInterval(() => {
    const now = Date.now();
    const timeout = 60000; // 1 minute timeout

    clients.forEach((client, clientId) => {
      if (now - client.lastPing > timeout) {
        logger.info('Cleaning up inactive WebSocket client', { clientId });
        client.ws.terminate();
        clients.delete(clientId);
      }
    });
  }, 30000); // Check every 30 seconds

  logger.info('WebSocket server initialized');
}

function handleWebSocketMessage(clientId, message) {
  const client = clients.get(clientId);
  if (!client) return;

  logger.info('WebSocket message received', { clientId, type: message.type });

  switch (message.type) {
    case 'ping':
      client.lastPing = Date.now();
      client.ws.send(JSON.stringify({
        type: 'pong',
        timestamp: new Date().toISOString()
      }));
      break;

    case 'subscribe':
      if (message.topics && Array.isArray(message.topics)) {
        client.topics = [...new Set([...client.topics, ...message.topics])];
        client.ws.send(JSON.stringify({
          type: 'subscribed',
          topics: client.topics,
          timestamp: new Date().toISOString()
        }));
        logger.info('Client subscribed to topics', { clientId, topics: message.topics });
      }
      break;

    case 'unsubscribe':
      if (message.topics && Array.isArray(message.topics)) {
        client.topics = client.topics.filter(topic => !message.topics.includes(topic));
        client.ws.send(JSON.stringify({
          type: 'unsubscribed',
          topics: message.topics,
          remainingTopics: client.topics,
          timestamp: new Date().toISOString()
        }));
        logger.info('Client unsubscribed from topics', { clientId, topics: message.topics });
      }
      break;

    case 'chat_message':
      // Broadcast chat message to other clients subscribed to chat topic
      broadcastToTopic('chat', {
        type: 'chat_message',
        clientId,
        message: message.content,
        timestamp: new Date().toISOString()
      }, clientId);
      break;

    default:
      client.ws.send(JSON.stringify({
        type: 'error',
        message: `Unknown message type: ${message.type}`,
        timestamp: new Date().toISOString()
      }));
  }
}

export function broadcastToTopic(topic, data, excludeClientId = null) {
  let sentCount = 0;
  
  clients.forEach((client, clientId) => {
    if (clientId === excludeClientId) return;
    if (!client.topics.includes(topic)) return;
    
    try {
      if (client.ws.readyState === client.ws.OPEN) {
        client.ws.send(JSON.stringify(data));
        sentCount++;
      }
    } catch (error) {
      logger.error('Error broadcasting to client:', { clientId, error: error.message });
    }
  });

  logger.info('Message broadcasted', { topic, sentCount, excludeClientId });
  return sentCount;
}

export function getConnectedClients() {
  return {
    count: clients.size,
    clients: Array.from(clients.entries()).map(([clientId, client]) => ({
      clientId,
      topics: client.topics,
      connectedAt: client.connectedAt,
      lastPing: new Date(client.lastPing).toISOString()
    }))
  };
}

function generateClientId() {
  return 'client_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}