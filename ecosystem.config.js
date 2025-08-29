#!/usr/bin/env bash

# PM2 Ecosystem Configuration for YYC³ EasyVizAI

module.exports = {
  apps: [
    {
      name: 'easyvizai-backend',
      script: 'src/server.js',
      cwd: './backend',
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      max_memory_restart: '200M',
      env: {
        NODE_ENV: 'production',
        PORT: 8000
      },
      env_development: {
        NODE_ENV: 'development',
        PORT: 8000,
        LOG_LEVEL: 'debug'
      },
      log_file: './logs/combined.log',
      out_file: './logs/out.log',
      error_file: './logs/error.log',
      time: true,
      autorestart: true,
      max_restarts: 5,
      min_uptime: '10s'
    },
    {
      name: 'easyvizai-frontend',
      script: 'npm',
      args: 'start',
      cwd: './frontend',
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      max_memory_restart: '150M',
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      },
      log_file: './logs/frontend.log',
      time: true,
      autorestart: true,
      max_restarts: 5,
      min_uptime: '10s'
    }
  ]
};