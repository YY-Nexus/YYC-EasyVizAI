/**
 * Voice Reminder Service
 * Manages voice notifications and reminders based on application events
 */
import { TTSResult } from '../components/TTSComponent';

export interface VoiceReminder {
  id: string;
  text: string;
  trigger: string;
  language?: string;
  voice_type?: string;
  emotion?: string;
  delay?: number;
  priority: 'low' | 'medium' | 'high';
  enabled: boolean;
}

export interface ReminderEvent {
  type: string;
  context?: any;
  emotion?: string;
  priority?: 'low' | 'medium' | 'high';
}

export class VoiceReminderService {
  private reminders: Map<string, VoiceReminder> = new Map();
  private audioQueue: Array<{ audio: TTSResult; priority: string }> = [];
  private isPlaying = false;
  private apiBaseUrl: string;
  private defaultOptions = {
    language: 'zh-CN',
    voice_type: 'female',
    emotion: 'neutral'
  };

  constructor(apiBaseUrl = '/api') {
    this.apiBaseUrl = apiBaseUrl;
    this.initializeDefaultReminders();
  }

  /**
   * Initialize default reminders for common application events
   */
  private initializeDefaultReminders() {
    const defaultReminders: VoiceReminder[] = [
      {
        id: 'task_completed',
        text: '任务已完成！恭喜您！',
        trigger: 'task.completed',
        emotion: 'happy',
        priority: 'medium',
        enabled: true
      },
      {
        id: 'task_failed',
        text: '任务执行遇到问题，请检查并重试。',
        trigger: 'task.failed',
        emotion: 'sad',
        priority: 'high',
        enabled: true
      },
      {
        id: 'welcome',
        text: '欢迎使用EasyVizAI！我是您的智能助手。',
        trigger: 'app.welcome',
        emotion: 'happy',
        priority: 'low',
        enabled: true
      },
      {
        id: 'data_saved',
        text: '数据已成功保存。',
        trigger: 'data.saved',
        emotion: 'calm',
        priority: 'low',
        enabled: true
      },
      {
        id: 'error_occurred',
        text: '系统遇到错误，请稍后重试。',
        trigger: 'error.occurred',
        emotion: 'urgent',
        priority: 'high',
        enabled: true
      },
      {
        id: 'report_ready',
        text: '您的分析报告已生成完成，可以查看了。',
        trigger: 'report.ready',
        emotion: 'excited',
        priority: 'medium',
        enabled: true
      },
      {
        id: 'session_timeout_warning',
        text: '您的会话即将过期，请保存您的工作。',
        trigger: 'session.timeout_warning',
        emotion: 'urgent',
        priority: 'high',
        delay: 0,
        enabled: true
      }
    ];

    defaultReminders.forEach(reminder => {
      this.addReminder(reminder);
    });
  }

  /**
   * Add a voice reminder
   */
  addReminder(reminder: VoiceReminder): void {
    this.reminders.set(reminder.id, reminder);
  }

  /**
   * Remove a voice reminder
   */
  removeReminder(id: string): void {
    this.reminders.delete(id);
  }

  /**
   * Update reminder settings
   */
  updateReminder(id: string, updates: Partial<VoiceReminder>): void {
    const reminder = this.reminders.get(id);
    if (reminder) {
      this.reminders.set(id, { ...reminder, ...updates });
    }
  }

  /**
   * Get all reminders
   */
  getReminders(): VoiceReminder[] {
    return Array.from(this.reminders.values());
  }

  /**
   * Enable/disable a reminder
   */
  toggleReminder(id: string, enabled: boolean): void {
    this.updateReminder(id, { enabled });
  }

  /**
   * Trigger a voice reminder based on event
   */
  async triggerReminder(event: ReminderEvent): Promise<void> {
    const reminders = Array.from(this.reminders.values())
      .filter(reminder => 
        reminder.enabled && 
        reminder.trigger === event.type
      );

    if (reminders.length === 0) return;

    // Get the highest priority reminder
    const priorityOrder = { high: 3, medium: 2, low: 1 };
    const reminder = reminders.sort((a, b) => 
      priorityOrder[b.priority] - priorityOrder[a.priority]
    )[0];

    try {
      // Generate TTS with context-aware emotion
      const emotion = event.emotion || reminder.emotion || this.defaultOptions.emotion;
      const ttsResult = await this.generateTTS(reminder.text, {
        ...this.defaultOptions,
        ...reminder,
        emotion
      });

      // Queue the audio for playback
      await this.queueAudio(ttsResult, reminder.priority, reminder.delay);

    } catch (error) {
      console.error('Failed to trigger voice reminder:', error);
    }
  }

  /**
   * Generate TTS for reminder text
   */
  private async generateTTS(text: string, options: any): Promise<TTSResult> {
    const response = await fetch(`${this.apiBaseUrl}/tts/generate/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        language: options.language || this.defaultOptions.language,
        voice_type: options.voice_type || this.defaultOptions.voice_type,
        emotion: options.emotion || this.defaultOptions.emotion,
        use_cache: true
      }),
    });

    const data = await response.json();
    if (!data.success) {
      throw new Error(data.error || 'TTS generation failed');
    }

    return data.data;
  }

  /**
   * Queue audio for playback
   */
  private async queueAudio(audio: TTSResult, priority: string, delay = 0): Promise<void> {
    // Add to queue
    this.audioQueue.push({ audio, priority });
    
    // Sort queue by priority
    const priorityOrder = { high: 3, medium: 2, low: 1 };
    this.audioQueue.sort((a, b) => 
      priorityOrder[b.priority as keyof typeof priorityOrder] - 
      priorityOrder[a.priority as keyof typeof priorityOrder]
    );

    // Apply delay if specified
    if (delay > 0) {
      setTimeout(() => this.processQueue(), delay);
    } else {
      this.processQueue();
    }
  }

  /**
   * Process audio queue
   */
  private async processQueue(): Promise<void> {
    if (this.isPlaying || this.audioQueue.length === 0) return;

    this.isPlaying = true;
    const { audio } = this.audioQueue.shift()!;

    try {
      await this.playAudio(audio.audio_url);
    } catch (error) {
      console.error('Failed to play reminder audio:', error);
    } finally {
      this.isPlaying = false;
      // Process next item in queue
      if (this.audioQueue.length > 0) {
        setTimeout(() => this.processQueue(), 500); // Small delay between reminders
      }
    }
  }

  /**
   * Play audio using HTML5 Audio API
   */
  private playAudio(audioUrl: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const audio = new Audio(audioUrl);
      
      audio.onended = () => resolve();
      audio.onerror = () => reject(new Error('Audio playback failed'));
      
      // Set volume based on reminder settings
      audio.volume = this.getVolume();
      
      audio.play().catch(reject);
    });
  }

  /**
   * Get volume based on time and user preferences
   */
  private getVolume(): number {
    const hour = new Date().getHours();
    
    // Reduce volume during night hours (22:00 - 08:00)
    if (hour >= 22 || hour < 8) {
      return 0.3;
    }
    
    // Normal volume during day
    return 0.7;
  }

  /**
   * Clear all queued reminders
   */
  clearQueue(): void {
    this.audioQueue = [];
  }

  /**
   * Get queue status
   */
  getQueueStatus(): { count: number; isPlaying: boolean } {
    return {
      count: this.audioQueue.length,
      isPlaying: this.isPlaying
    };
  }

  /**
   * Bulk trigger reminders for multiple events
   */
  async triggerMultipleReminders(events: ReminderEvent[]): Promise<void> {
    // Sort events by priority
    const priorityOrder = { high: 3, medium: 2, low: 1 };
    const sortedEvents = events.sort((a, b) => 
      priorityOrder[b.priority || 'low'] - priorityOrder[a.priority || 'low']
    );

    // Process events with delays to avoid overwhelming the user
    for (let i = 0; i < sortedEvents.length; i++) {
      const delay = i * 2000; // 2 second delay between events
      setTimeout(() => {
        this.triggerReminder(sortedEvents[i]);
      }, delay);
    }
  }

  /**
   * Create custom reminder on the fly
   */
  async createAndTriggerCustomReminder(
    text: string, 
    options: {
      emotion?: string;
      priority?: 'low' | 'medium' | 'high';
      delay?: number;
      voice_type?: string;
      language?: string;
    } = {}
  ): Promise<void> {
    const customReminder: VoiceReminder = {
      id: `custom_${Date.now()}`,
      text,
      trigger: 'custom',
      emotion: options.emotion || 'neutral',
      priority: options.priority || 'medium',
      delay: options.delay || 0,
      voice_type: options.voice_type,
      language: options.language,
      enabled: true
    };

    try {
      const ttsResult = await this.generateTTS(text, {
        ...this.defaultOptions,
        ...options
      });

      await this.queueAudio(ttsResult, customReminder.priority, customReminder.delay);
    } catch (error) {
      console.error('Failed to create custom reminder:', error);
      throw error;
    }
  }
}

// Global voice reminder service instance
export const voiceReminderService = new VoiceReminderService();