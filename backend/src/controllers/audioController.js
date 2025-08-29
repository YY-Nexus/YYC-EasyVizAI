import multer from 'multer';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';
import { logger } from '../utils/logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Create uploads directory
const uploadsDir = path.join(__dirname, '../../uploads/audio');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

// Configure multer for audio uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadsDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const fileFilter = (req, file, cb) => {
  // Accept audio files only
  if (file.mimetype.startsWith('audio/')) {
    cb(null, true);
  } else {
    cb(new Error('Only audio files are allowed'), false);
  }
};

const upload = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB limit
  }
});

export const audioController = {
  async uploadAudio(req, res, next) {
    try {
      // Check if audio upload is enabled
      if (process.env.ENABLE_AUDIO_UPLOAD !== 'true') {
        return res.status(403).json({
          error: 'Audio Upload Disabled',
          message: 'Audio upload feature is currently disabled'
        });
      }

      // Use multer middleware
      upload.single('audio')(req, res, (err) => {
        if (err) {
          logger.error('Audio upload error:', err);
          return res.status(400).json({
            error: 'Upload Error',
            message: err.message
          });
        }

        if (!req.file) {
          return res.status(400).json({
            error: 'No File',
            message: 'No audio file provided'
          });
        }

        logger.info('Audio file uploaded', {
          filename: req.file.filename,
          originalName: req.file.originalname,
          size: req.file.size,
          mimetype: req.file.mimetype
        });

        res.json({
          id: req.file.filename.replace(path.extname(req.file.filename), ''),
          filename: req.file.filename,
          originalName: req.file.originalname,
          size: req.file.size,
          mimetype: req.file.mimetype,
          uploadedAt: new Date().toISOString(),
          playUrl: `/api/v1/audio/play/${req.file.filename.replace(path.extname(req.file.filename), '')}`
        });
      });

    } catch (error) {
      logger.error('Error in uploadAudio:', error);
      next(error);
    }
  },

  async playAudio(req, res, next) {
    try {
      const { id } = req.params;
      
      // Find the audio file (we need to check different extensions)
      const audioExtensions = ['.mp3', '.wav', '.m4a', '.ogg', '.webm'];
      let audioFile = null;
      
      for (const ext of audioExtensions) {
        const filePath = path.join(uploadsDir, `audio-${id}${ext}`);
        if (fs.existsSync(filePath)) {
          audioFile = filePath;
          break;
        }
      }

      if (!audioFile) {
        return res.status(404).json({
          error: 'Audio Not Found',
          message: 'Audio file not found'
        });
      }

      logger.info('Audio file requested', { id, audioFile });

      // Stream the audio file
      const stat = fs.statSync(audioFile);
      const fileSize = stat.size;
      const range = req.headers.range;

      if (range) {
        // Support range requests for audio streaming
        const parts = range.replace(/bytes=/, "").split("-");
        const start = parseInt(parts[0], 10);
        const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;
        const chunksize = (end - start) + 1;
        const file = fs.createReadStream(audioFile, { start, end });
        const head = {
          'Content-Range': `bytes ${start}-${end}/${fileSize}`,
          'Accept-Ranges': 'bytes',
          'Content-Length': chunksize,
          'Content-Type': 'audio/mpeg',
        };
        res.writeHead(206, head);
        file.pipe(res);
      } else {
        const head = {
          'Content-Length': fileSize,
          'Content-Type': 'audio/mpeg',
        };
        res.writeHead(200, head);
        fs.createReadStream(audioFile).pipe(res);
      }

    } catch (error) {
      logger.error('Error in playAudio:', error);
      next(error);
    }
  },

  async deleteAudio(req, res, next) {
    try {
      const { id } = req.params;
      
      // Find and delete the audio file
      const audioExtensions = ['.mp3', '.wav', '.m4a', '.ogg', '.webm'];
      let deleted = false;
      
      for (const ext of audioExtensions) {
        const filePath = path.join(uploadsDir, `audio-${id}${ext}`);
        if (fs.existsSync(filePath)) {
          fs.unlinkSync(filePath);
          deleted = true;
          logger.info('Audio file deleted', { id, filePath });
          break;
        }
      }

      if (!deleted) {
        return res.status(404).json({
          error: 'Audio Not Found',
          message: 'Audio file not found'
        });
      }

      res.json({
        message: 'Audio file deleted successfully',
        id,
        deletedAt: new Date().toISOString()
      });

    } catch (error) {
      logger.error('Error in deleteAudio:', error);
      next(error);
    }
  }
};