import express from 'express';
import chatRoutes from './chat.js';
import authRoutes from './auth.js';
import audioRoutes from './audio.js';

const router = express.Router();

// Mount route modules
router.use('/chat', chatRoutes);
router.use('/auth', authRoutes);
router.use('/audio', audioRoutes);

// API info endpoint
router.get('/', (req, res) => {
  res.json({
    name: 'YYC³ EasyVizAI API',
    version: '1.0.0',
    description: 'AI Web Application Backend Service',
    endpoints: {
      chat: '/api/v1/chat',
      auth: '/api/v1/auth',
      audio: '/api/v1/audio',
      health: '/health'
    },
    timestamp: new Date().toISOString()
  });
});

export default router;