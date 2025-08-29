import express from 'express';
import { audioController } from '../controllers/audioController.js';

const router = express.Router();

// Audio endpoints
router.post('/upload', audioController.uploadAudio);
router.get('/play/:id', audioController.playAudio);
router.delete('/:id', audioController.deleteAudio);

export default router;