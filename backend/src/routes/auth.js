import express from 'express';
import { authController } from '../controllers/authController.js';

const router = express.Router();

// Authentication endpoints (placeholder for future registration)
router.post('/register', authController.register);
router.post('/login', authController.login);
router.post('/logout', authController.logout);
router.get('/me', authController.getCurrentUser);

export default router;