import express from 'express';
import { chatController } from '../controllers/chatController.js';

const router = express.Router();

// Chat endpoints
router.post('/message', chatController.sendMessage);
router.post('/stream', chatController.streamMessage);
router.get('/history', chatController.getChatHistory);
router.delete('/history', chatController.clearHistory);

export default router;