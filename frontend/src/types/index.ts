export interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
}

export interface AudioFile {
  id: string
  filename: string
  originalName: string
  size: number
  uploadedAt: string
  playUrl: string
  mimetype: string
}

export interface APIResponse<T = any> {
  data?: T
  error?: string
  message?: string
  timestamp: string
}

export interface ChatResponse {
  response: string
  model: string
  tokens: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
  timestamp: string
}