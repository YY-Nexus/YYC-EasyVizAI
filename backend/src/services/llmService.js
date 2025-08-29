import axios from 'axios';
import { logger } from '../utils/logger.js';
import { EventEmitter } from 'events';

class LLMService {
  constructor() {
    this.defaultModel = process.env.DEFAULT_MODEL || 'gpt-3.5-turbo';
    this.maxTokens = parseInt(process.env.MAX_TOKENS) || 2048;
    this.temperature = parseFloat(process.env.TEMPERATURE) || 0.7;
    this.apiKeys = {
      openai: process.env.OPENAI_API_KEY,
      anthropic: process.env.ANTHROPIC_API_KEY,
      gemini: process.env.GEMINI_API_KEY
    };
  }

  async generateResponse({ message, model = null, context = [], stream = false }) {
    const selectedModel = model || this.defaultModel;
    logger.info('Generating LLM response', { model: selectedModel, stream, contextLength: context.length });

    try {
      // Determine which provider to use based on model
      if (selectedModel.startsWith('gpt-')) {
        return await this.callOpenAI({ message, model: selectedModel, context, stream });
      } else if (selectedModel.startsWith('claude-')) {
        return await this.callAnthropic({ message, model: selectedModel, context, stream });
      } else if (selectedModel.startsWith('gemini-')) {
        return await this.callGemini({ message, model: selectedModel, context, stream });
      } else {
        // Default to OpenAI for unknown models
        return await this.callOpenAI({ message, model: 'gpt-3.5-turbo', context, stream });
      }
    } catch (error) {
      logger.error('LLM generation error:', error);
      throw new Error('Failed to generate AI response: ' + error.message);
    }
  }

  async callOpenAI({ message, model, context, stream }) {
    if (!this.apiKeys.openai || this.apiKeys.openai === 'your_openai_api_key_here') {
      logger.warn('OpenAI API key not configured, returning mock response');
      return this.getMockResponse(message, model, stream);
    }

    const messages = [
      { role: 'system', content: 'You are a helpful AI assistant for the YYC³ EasyVizAI application.' },
      ...context.map(msg => ({ role: msg.role || 'user', content: msg.content })),
      { role: 'user', content: message }
    ];

    const requestConfig = {
      method: 'POST',
      url: 'https://api.openai.com/v1/chat/completions',
      headers: {
        'Authorization': `Bearer ${this.apiKeys.openai}`,
        'Content-Type': 'application/json'
      },
      data: {
        model,
        messages,
        max_tokens: this.maxTokens,
        temperature: this.temperature,
        stream
      }
    };

    if (stream) {
      requestConfig.responseType = 'stream';
      const response = await axios(requestConfig);
      return this.createStreamFromResponse(response.data);
    } else {
      const response = await axios(requestConfig);
      return {
        content: response.data.choices[0].message.content,
        model: response.data.model,
        tokens: response.data.usage
      };
    }
  }

  async callAnthropic({ message, model, context, stream }) {
    if (!this.apiKeys.anthropic || this.apiKeys.anthropic === 'your_anthropic_api_key_here') {
      logger.warn('Anthropic API key not configured, returning mock response');
      return this.getMockResponse(message, model, stream);
    }

    // Anthropic implementation would go here
    logger.warn('Anthropic integration not yet implemented, returning mock response');
    return this.getMockResponse(message, model, stream);
  }

  async callGemini({ message, model, context, stream }) {
    if (!this.apiKeys.gemini || this.apiKeys.gemini === 'your_gemini_api_key_here') {
      logger.warn('Gemini API key not configured, returning mock response');
      return this.getMockResponse(message, model, stream);
    }

    // Gemini implementation would go here
    logger.warn('Gemini integration not yet implemented, returning mock response');
    return this.getMockResponse(message, model, stream);
  }

  getMockResponse(message, model, stream) {
    const mockContent = `This is a mock response to your message: "${message}". 

The YYC³ EasyVizAI system is currently running in development mode. To get real AI responses, please configure your API keys in the environment variables:

- OPENAI_API_KEY for GPT models
- ANTHROPIC_API_KEY for Claude models  
- GEMINI_API_KEY for Gemini models

Model requested: ${model}
Timestamp: ${new Date().toISOString()}`;

    if (stream) {
      return this.createMockStream(mockContent);
    } else {
      return {
        content: mockContent,
        model: `${model} (mock)`,
        tokens: {
          prompt_tokens: message.length / 4, // Rough estimate
          completion_tokens: mockContent.length / 4,
          total_tokens: (message.length + mockContent.length) / 4
        }
      };
    }
  }

  createMockStream(content) {
    const emitter = new EventEmitter();
    const words = content.split(' ');
    
    // Simulate streaming by emitting words with delays
    setTimeout(() => {
      let wordIndex = 0;
      const interval = setInterval(() => {
        if (wordIndex < words.length) {
          emitter.emit('data', {
            content: words[wordIndex] + ' ',
            model: 'mock-stream',
            finished: false
          });
          wordIndex++;
        } else {
          emitter.emit('data', {
            content: '',
            model: 'mock-stream',
            finished: true
          });
          emitter.emit('end');
          clearInterval(interval);
        }
      }, 50); // 50ms delay between words
    }, 100);

    return emitter;
  }

  createStreamFromResponse(stream) {
    const emitter = new EventEmitter();
    
    stream.on('data', (chunk) => {
      const lines = chunk.toString().split('\n');
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') {
            emitter.emit('end');
            return;
          }
          
          try {
            const parsed = JSON.parse(data);
            if (parsed.choices && parsed.choices[0].delta.content) {
              emitter.emit('data', {
                content: parsed.choices[0].delta.content,
                model: parsed.model,
                finished: false
              });
            }
          } catch (e) {
            // Ignore parsing errors for incomplete chunks
          }
        }
      }
    });

    stream.on('end', () => {
      emitter.emit('end');
    });

    stream.on('error', (error) => {
      emitter.emit('error', error);
    });

    return emitter;
  }
}

export const llmService = new LLMService();