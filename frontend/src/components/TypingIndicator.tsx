'use client'

import { motion } from 'framer-motion'

export function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="flex justify-start"
    >
      <div className="flex max-w-[80%]">
        <div className="mr-3">
          <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center">
            <div className="w-4 h-4 text-white">🤖</div>
          </div>
        </div>
        <div className="px-4 py-3 bg-gray-100 rounded-lg">
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}