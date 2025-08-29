'use client'

import { useState } from 'react'
import { ChatPanel } from '@/components/ChatPanel'
import { AudioPlayer } from '@/components/AudioPlayer'
import { Header } from '@/components/Header'
import { motion } from 'framer-motion'

export default function Home() {
  const [isAudioPlayerVisible, setIsAudioPlayerVisible] = useState(false)

  return (
    <main className="min-h-screen">
      <Header />
      
      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            YYC³ EasyVizAI
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            AI-powered chat and visualization platform. Start a conversation or upload audio to begin your experience.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
          {/* Chat Panel */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="lg:col-span-2"
          >
            <ChatPanel />
          </motion.div>

          {/* Audio Player and Controls */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="space-y-6"
          >
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold mb-4 text-gray-800">Audio Controls</h2>
              <button
                onClick={() => setIsAudioPlayerVisible(!isAudioPlayerVisible)}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                {isAudioPlayerVisible ? 'Hide Audio Player' : 'Show Audio Player'}
              </button>
            </div>

            {isAudioPlayerVisible && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.3 }}
              >
                <AudioPlayer />
              </motion.div>
            )}

            {/* App Info */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold mb-4 text-gray-800">Features</h2>
              <ul className="space-y-2 text-gray-600">
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                  AI Chat Interface
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                  Audio Upload & Playback
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-purple-500 rounded-full mr-3"></span>
                  Real-time WebSocket
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-orange-500 rounded-full mr-3"></span>
                  No Registration Required
                </li>
              </ul>
            </div>
          </motion.div>
        </div>
      </div>
    </main>
  )
}