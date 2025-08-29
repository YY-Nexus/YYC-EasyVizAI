import { llmService } from '../services/llmService.js';
import { logger } from '../utils/logger.js';

export const chatController = {
  async sendMessage(req, res, next) {
    try {
      const { message, model = 'gpt-3.5-turbo', context = [] } = req.body;

      if (!message) {
        return res.status(400).json({ error: 'Message is required' });
      }

      logger.info('Chat message received', { 
        messageLength: message.length, 
        model,
        contextLength: context.length 
      });

      const response = await llmService.generateResponse({
        message,
        model,
        context,
        stream: false
      });

      res.json({
        response: response.content,
        model: response.model,
        tokens: response.tokens,
        timestamp: new Date().toISOString()
      });

    } catch (error) {
      logger.error('Error in sendMessage:', error);
      next(error);
    }
  },

  async streamMessage(req, res, next) {
    try {
      const { message, model = 'gpt-3.5-turbo', context = [] } = req.body;

      if (!message) {
        return res.status(400).json({ error: 'Message is required' });
      }

      logger.info('Stream chat message received', { 
        messageLength: message.length, 
        model,
        contextLength: context.length 
      });

      // Set headers for streaming
      res.setHeader('Content-Type', 'text/event-stream');
      res.setHeader('Cache-Control', 'no-cache');
      res.setHeader('Connection', 'keep-alive');
      res.setHeader('Access-Control-Allow-Origin', '*');

      const stream = await llmService.generateResponse({
        message,
        model,
        context,
        stream: true
      });

      // Handle stream chunks
      stream.on('data', (chunk) => {
        res.write(`data: ${JSON.stringify(chunk)}\n\n`);
      });

      stream.on('end', () => {
        res.write('data: [DONE]\n\n');
        res.end();
      });

      stream.on('error', (error) => {
        logger.error('Stream error:', error);
        res.write(`data: ${JSON.stringify({ error: 'Stream error occurred' })}\n\n`);
        res.end();
      });

    } catch (error) {
      logger.error('Error in streamMessage:', error);
      next(error);
    }
  },

  async getChatHistory(req, res, next) {
    try {
      // For now, return empty history (implement persistent storage later)
      res.json({
        history: [],
        count: 0,
        message: 'Chat history will be implemented in future versions'
      });
    } catch (error) {
      logger.error('Error in getChatHistory:', error);
      next(error);
    }
  },

  async clearHistory(req, res, next) {
    try {
      // Placeholder for clearing chat history
      res.json({
        message: 'Chat history cleared (placeholder implementation)',
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      logger.error('Error in clearHistory:', error);
      next(error);
    }
  }
};