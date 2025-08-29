/**
 * Main Application Component
 * Demonstrates TTS and Voice Reminder functionality
 */
import React, { useState, useEffect } from 'react';
import { TTSComponent } from './components/TTSComponent';
import { AudioPlayer, AudioTrack } from './components/AudioPlayer';
import { voiceReminderService, VoiceReminder, ReminderEvent } from './services/VoiceReminderService';
import { Bell, Settings, Music, MessageSquare, Volume2, Check, X } from 'lucide-react';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'tts' | 'player' | 'reminders'>('tts');
  const [theme, setTheme] = useState<'cloud' | 'bamboo' | 'amber'>('cloud');
  const [reminders, setReminders] = useState<VoiceReminder[]>([]);
  const [queueStatus, setQueueStatus] = useState({ count: 0, isPlaying: false });
  const [demoAudioTracks] = useState<AudioTrack[]>([
    {
      id: 'demo1',
      title: '欢迎使用EasyVizAI',
      artist: 'AI助手 - 女声 - 快乐',
      src: '/api/tts/generate/'  // This will be populated dynamically
    },
    {
      id: 'demo2',
      title: '任务完成提醒',
      artist: 'AI助手 - 女声 - 兴奋',
      src: '/api/tts/generate/'
    }
  ]);

  const themeColors = {
    cloud: { primary: '#4A90E2', secondary: '#E8F4FD', accent: '#2E5BBA', name: '云蓝' },
    bamboo: { primary: '#7CB342', secondary: '#F1F8E9', accent: '#558B2F', name: '竹绿' },
    amber: { primary: '#FFB300', secondary: '#FFF8E1', accent: '#F57F17', name: '琥珀' }
  };

  const colors = themeColors[theme];

  // Load reminders on component mount
  useEffect(() => {
    setReminders(voiceReminderService.getReminders());
    
    // Update queue status periodically
    const interval = setInterval(() => {
      setQueueStatus(voiceReminderService.getQueueStatus());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // Demo event triggers
  const triggerDemoEvent = async (eventType: string) => {
    const demoEvents: Record<string, ReminderEvent> = {
      'welcome': { type: 'app.welcome', emotion: 'happy' },
      'task_completed': { type: 'task.completed', emotion: 'excited' },
      'error': { type: 'error.occurred', emotion: 'urgent', priority: 'high' },
      'data_saved': { type: 'data.saved', emotion: 'calm' },
      'report_ready': { type: 'report.ready', emotion: 'excited', priority: 'medium' }
    };

    const event = demoEvents[eventType];
    if (event) {
      await voiceReminderService.triggerReminder(event);
    }
  };

  // Custom reminder trigger
  const triggerCustomReminder = async () => {
    try {
      await voiceReminderService.createAndTriggerCustomReminder(
        '这是一个自定义语音提醒示例！',
        { emotion: 'happy', priority: 'medium' }
      );
    } catch (error) {
      console.error('Failed to trigger custom reminder:', error);
    }
  };

  // Toggle reminder status
  const toggleReminder = (id: string, enabled: boolean) => {
    voiceReminderService.toggleReminder(id, enabled);
    setReminders(voiceReminderService.getReminders());
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
      padding: '20px'
    }}>
      {/* Header */}
      <div style={{
        background: 'white',
        borderRadius: '16px',
        padding: '24px',
        marginBottom: '24px',
        boxShadow: '0 4px 16px rgba(0,0,0,0.1)'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '16px'
        }}>
          <h1 style={{
            margin: 0,
            color: colors.accent,
            fontSize: '32px',
            fontWeight: '700'
          }}>
            YYC³ EasyVizAI 有声交互系统
          </h1>
          
          {/* Theme Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ color: colors.accent, fontSize: '14px', fontWeight: '500' }}>主题:</span>
            {Object.entries(themeColors).map(([key, color]) => (
              <button
                key={key}
                onClick={() => setTheme(key as any)}
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  border: theme === key ? `3px solid ${color.accent}` : `2px solid ${color.primary}`,
                  background: color.primary,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '10px',
                  fontWeight: '600'
                }}
                title={color.name}
              >
                {color.name.charAt(0)}
              </button>
            ))}
          </div>
        </div>

        {/* Navigation Tabs */}
        <div style={{
          display: 'flex',
          gap: '8px',
          borderBottom: `2px solid ${colors.primary}20`
        }}>
          {[
            { id: 'tts', label: '文本转语音', icon: MessageSquare },
            { id: 'player', label: '音频播放器', icon: Music },
            { id: 'reminders', label: '语音提醒', icon: Bell }
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as any)}
              style={{
                padding: '12px 24px',
                border: 'none',
                background: activeTab === id ? colors.primary : 'transparent',
                color: activeTab === id ? 'white' : colors.accent,
                borderRadius: '8px 8px 0 0',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '16px',
                fontWeight: '600',
                transition: 'all 0.3s ease'
              }}
            >
              <Icon size={18} />
              {label}
            </button>
          ))}
        </div>

        {/* Queue Status */}
        {queueStatus.count > 0 && (
          <div style={{
            marginTop: '16px',
            padding: '12px 16px',
            background: colors.primary + '10',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '14px',
            color: colors.accent
          }}>
            <Volume2 size={16} />
            {queueStatus.isPlaying ? '正在播放语音提醒...' : `队列中有 ${queueStatus.count} 个语音提醒`}
          </div>
        )}
      </div>

      {/* Main Content */}
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {activeTab === 'tts' && (
          <TTSComponent
            theme={theme}
            defaultText="欢迎使用EasyVizAI有声交互系统！这是一个功能强大的文本转语音工具。"
            onTTSGenerated={(result) => {
              console.log('TTS Generated:', result);
            }}
            onError={(error) => {
              console.error('TTS Error:', error);
            }}
          />
        )}

        {activeTab === 'player' && (
          <div style={{
            background: 'white',
            borderRadius: '16px',
            padding: '24px',
            boxShadow: '0 4px 16px rgba(0,0,0,0.1)'
          }}>
            <h2 style={{
              margin: '0 0 24px 0',
              color: colors.accent,
              fontSize: '24px',
              fontWeight: '700',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <Music size={24} />
              音频播放器演示
            </h2>
            
            <AudioPlayer
              playlist={demoAudioTracks}
              theme={theme}
              showPlaylist={true}
              onTrackChange={(track) => {
                console.log('Track changed:', track);
              }}
              onPlayStateChange={(isPlaying) => {
                console.log('Play state:', isPlaying);
              }}
            />
          </div>
        )}

        {activeTab === 'reminders' && (
          <div style={{
            background: 'white',
            borderRadius: '16px',
            padding: '24px',
            boxShadow: '0 4px 16px rgba(0,0,0,0.1)'
          }}>
            <h2 style={{
              margin: '0 0 24px 0',
              color: colors.accent,
              fontSize: '24px',
              fontWeight: '700',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <Bell size={24} />
              语音提醒管理
            </h2>

            {/* Demo Event Triggers */}
            <div style={{
              marginBottom: '32px',
              padding: '20px',
              background: colors.secondary,
              borderRadius: '12px'
            }}>
              <h3 style={{
                margin: '0 0 16px 0',
                color: colors.accent,
                fontSize: '18px',
                fontWeight: '600'
              }}>
                演示事件触发
              </h3>
              
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '12px'
              }}>
                {[
                  { id: 'welcome', label: '欢迎消息', color: colors.primary },
                  { id: 'task_completed', label: '任务完成', color: '#28a745' },
                  { id: 'error', label: '错误提示', color: '#dc3545' },
                  { id: 'data_saved', label: '数据保存', color: colors.accent },
                  { id: 'report_ready', label: '报告就绪', color: '#17a2b8' }
                ].map(({ id, label, color }) => (
                  <button
                    key={id}
                    onClick={() => triggerDemoEvent(id)}
                    style={{
                      padding: '12px 16px',
                      border: 'none',
                      background: color,
                      color: 'white',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      fontSize: '14px',
                      fontWeight: '500',
                      transition: 'opacity 0.2s ease'
                    }}
                    onMouseOver={(e) => { e.currentTarget.style.opacity = '0.8'; }}
                    onMouseOut={(e) => { e.currentTarget.style.opacity = '1'; }}
                  >
                    {label}
                  </button>
                ))}
                
                <button
                  onClick={triggerCustomReminder}
                  style={{
                    padding: '12px 16px',
                    border: `2px solid ${colors.primary}`,
                    background: 'white',
                    color: colors.primary,
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: '500'
                  }}
                >
                  自定义提醒
                </button>
              </div>
            </div>

            {/* Reminder Settings */}
            <div>
              <h3 style={{
                margin: '0 0 16px 0',
                color: colors.accent,
                fontSize: '18px',
                fontWeight: '600'
              }}>
                提醒设置
              </h3>
              
              <div style={{ display: 'grid', gap: '12px' }}>
                {reminders.map((reminder) => (
                  <div
                    key={reminder.id}
                    style={{
                      padding: '16px',
                      border: `1px solid ${colors.primary}20`,
                      borderRadius: '8px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      background: reminder.enabled ? 'white' : '#f8f9fa'
                    }}
                  >
                    <div>
                      <div style={{
                        fontWeight: '600',
                        color: colors.accent,
                        marginBottom: '4px'
                      }}>
                        {reminder.text}
                      </div>
                      <div style={{
                        fontSize: '12px',
                        color: '#666',
                        display: 'flex',
                        gap: '12px'
                      }}>
                        <span>触发: {reminder.trigger}</span>
                        <span>情感: {reminder.emotion}</span>
                        <span>优先级: {reminder.priority}</span>
                      </div>
                    </div>
                    
                    <button
                      onClick={() => toggleReminder(reminder.id, !reminder.enabled)}
                      style={{
                        padding: '8px',
                        border: 'none',
                        background: reminder.enabled ? '#28a745' : '#dc3545',
                        color: 'white',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}
                    >
                      {reminder.enabled ? <Check size={16} /> : <X size={16} />}
                      {reminder.enabled ? '启用' : '禁用'}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;