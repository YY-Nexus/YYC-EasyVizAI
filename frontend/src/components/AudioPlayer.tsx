'use client'

import { useState, useRef } from 'react'
import { Upload, Play, Pause, Volume2, X, Loader2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface AudioFile {
  id: string
  filename: string
  originalName: string
  size: number
  uploadedAt: string
  playUrl: string
}

export function AudioPlayer() {
  const [audioFile, setAudioFile] = useState<AudioFile | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(1)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)

  const audioRef = useRef<HTMLAudioElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Check file type
    if (!file.type.startsWith('audio/')) {
      setUploadError('Please select an audio file')
      return
    }

    // Check file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      setUploadError('File size must be less than 10MB')
      return
    }

    setIsUploading(true)
    setUploadError(null)

    try {
      const formData = new FormData()
      formData.append('audio', file)

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/audio/upload`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Upload failed')
      }

      const uploadedFile: AudioFile = await response.json()
      setAudioFile(uploadedFile)

      // Load the audio file
      if (audioRef.current) {
        audioRef.current.src = `${process.env.NEXT_PUBLIC_API_URL}${uploadedFile.playUrl}`
        audioRef.current.load()
      }
    } catch (error) {
      console.error('Upload error:', error)
      setUploadError('Failed to upload file. Please try again.')
    } finally {
      setIsUploading(false)
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const togglePlayPause = () => {
    if (!audioRef.current || !audioFile) return

    if (isPlaying) {
      audioRef.current.pause()
    } else {
      audioRef.current.play()
    }
    setIsPlaying(!isPlaying)
  }

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime)
    }
  }

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration)
    }
  }

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value)
    if (audioRef.current) {
      audioRef.current.currentTime = time
      setCurrentTime(time)
    }
  }

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const vol = parseFloat(e.target.value)
    setVolume(vol)
    if (audioRef.current) {
      audioRef.current.volume = vol
    }
  }

  const removeAudioFile = async () => {
    if (!audioFile) return

    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/audio/${audioFile.id}`, {
        method: 'DELETE',
      })
    } catch (error) {
      console.error('Delete error:', error)
    }

    setAudioFile(null)
    setIsPlaying(false)
    setCurrentTime(0)
    setDuration(0)
    if (audioRef.current) {
      audioRef.current.src = ''
    }
  }

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-semibold mb-4 text-gray-800">Audio Player</h2>

      {/* Upload Section */}
      {!audioFile && (
        <div className="mb-6">
          <div
            className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition-colors cursor-pointer"
            onClick={() => fileInputRef.current?.click()}
          >
            {isUploading ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex flex-col items-center"
              >
                <Loader2 className="w-8 h-8 text-blue-600 animate-spin mb-2" />
                <p className="text-gray-600">Uploading...</p>
              </motion.div>
            ) : (
              <>
                <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-600 mb-1">Click to upload audio file</p>
                <p className="text-sm text-gray-400">Supports MP3, WAV, M4A (max 10MB)</p>
              </>
            )}
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept="audio/*"
            onChange={handleFileUpload}
            className="hidden"
          />
          {uploadError && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-red-500 text-sm mt-2"
            >
              {uploadError}
            </motion.p>
          )}
        </div>
      )}

      {/* Player Section */}
      <AnimatePresence>
        {audioFile && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-4"
          >
            {/* File Info */}
            <div className="flex items-center justify-between">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-800 truncate">
                  {audioFile.originalName}
                </p>
                <p className="text-xs text-gray-500">
                  {(audioFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              <button
                onClick={removeAudioFile}
                className="p-1 text-gray-400 hover:text-red-500 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Controls */}
            <div className="flex items-center space-x-4">
              <button
                onClick={togglePlayPause}
                className="p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors"
              >
                {isPlaying ? (
                  <Pause className="w-4 h-4" />
                ) : (
                  <Play className="w-4 h-4" />
                )}
              </button>

              <div className="flex-1">
                <input
                  type="range"
                  min="0"
                  max={duration || 0}
                  value={currentTime}
                  onChange={handleSeek}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>{formatTime(currentTime)}</span>
                  <span>{formatTime(duration)}</span>
                </div>
              </div>
            </div>

            {/* Volume Control */}
            <div className="flex items-center space-x-2">
              <Volume2 className="w-4 h-4 text-gray-500" />
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={volume}
                onChange={handleVolumeChange}
                className="flex-1"
              />
            </div>

            {/* Audio Element */}
            <audio
              ref={audioRef}
              onTimeUpdate={handleTimeUpdate}
              onLoadedMetadata={handleLoadedMetadata}
              onEnded={() => setIsPlaying(false)}
              preload="metadata"
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}