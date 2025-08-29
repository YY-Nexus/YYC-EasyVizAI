import { logger } from '../utils/logger.js';

export const authController = {
  async register(req, res, next) {
    try {
      // Check if registration is enabled
      if (process.env.ENABLE_REGISTRATION !== 'true') {
        return res.status(403).json({
          error: 'Registration Disabled',
          message: 'Registration is currently disabled. This is a reserved endpoint for future use.'
        });
      }

      // Placeholder implementation for registration
      const { email, password, username } = req.body;

      logger.info('Registration attempt', { email, username });

      // TODO: Implement actual registration logic
      res.status(501).json({
        error: 'Not Implemented',
        message: 'Registration endpoint is reserved for future implementation',
        data: { email, username }
      });

    } catch (error) {
      logger.error('Error in register:', error);
      next(error);
    }
  },

  async login(req, res, next) {
    try {
      // Since we have no-login interface requirement, this is placeholder
      const { email, password } = req.body;

      logger.info('Login attempt', { email });

      res.status(501).json({
        error: 'Not Implemented',
        message: 'Login is not required for current application version. Direct access is enabled.',
        note: 'This endpoint is reserved for future authentication features'
      });

    } catch (error) {
      logger.error('Error in login:', error);
      next(error);
    }
  },

  async logout(req, res, next) {
    try {
      res.json({
        message: 'Logout successful (no-op for current no-login interface)',
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      logger.error('Error in logout:', error);
      next(error);
    }
  },

  async getCurrentUser(req, res, next) {
    try {
      // Since we have no authentication currently, return anonymous user
      res.json({
        user: {
          id: 'anonymous',
          username: 'Anonymous User',
          email: null,
          role: 'guest',
          authenticated: false
        },
        message: 'Current application runs without authentication',
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      logger.error('Error in getCurrentUser:', error);
      next(error);
    }
  }
};