/**
 * Text-to-Speech (TTS) Component
 * Provides interface for converting text to speech with voice and emotion options
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Mic, MicOff, Download, Volume2, Settings, MessageSquare } from 'lucide-react';
import { AudioPlayer, AudioTrack } from './AudioPlayer';

export interface TTSVoice {
  language: string;
  voices: string[];
}

export interface TTSOptions {
  language: string;
  voice_type: string;
  emotion: string;
  use_cache: boolean;
}

export interface TTSResult {
  audio_url: string;
  cache_key: string;
  cached: boolean;
  language: string;
  voice_type: string;
  emotion: string;
}

export interface TTSComponentProps {
  apiBaseUrl?: string;
  defaultText?: string;
  theme?: 'cloud' | 'bamboo' | 'amber';
  onTTSGenerated?: (result: TTSResult) => void;
  onError?: (error: string) => void;
  className?: string;
}

export const TTSComponent: React.FC<TTSComponentProps> = ({
  apiBaseUrl = '/api',
  defaultText = '',
  theme = 'cloud',
  onTTSGenerated,
  onError,
  className = ''
}) => {
  const [text, setText] = useState(defaultText);
  const [isLoading, setIsLoading] = useState(false);
  const [availableVoices, setAvailableVoices] = useState<Record<string, string[]>>({});
  const [availableEmotions, setAvailableEmotions] = useState<string[]>([]);
  const [ttsOptions, setTTSOptions] = useState<TTSOptions>({
    language: 'zh-CN',
    voice_type: 'female',
    emotion: 'neutral',
    use_cache: true
  });
  const [generatedAudio, setGeneratedAudio] = useState<TTSResult | null>(null);
  const [showSettings, setShowSettings] = useState(false);

  // Theme colors
  const themeColors = {
    cloud: {
      primary: '#4A90E2',
      secondary: '#E8F4FD',
      accent: '#2E5BBA'
    },
    bamboo: {
      primary: '#7CB342',
      secondary: '#F1F8E9',
      accent: '#558B2F'
    },
    amber: {
      primary: '#FFB300',
      secondary: '#FFF8E1',
      accent: '#F57F17'
    }
  };

  const colors = themeColors[theme];

  // Emotion labels in Chinese
  const emotionLabels: Record<string, string> = {
    neutral: '中性',
    happy: '快乐',
    sad: '悲伤',
    excited: '兴奋',
    calm: '平静',
    urgent: '紧急'
  };

  // Voice type labels in Chinese
  const voiceTypeLabels: Record<string, string> = {
    female: '女声',
    male: '男声',
    child: '童声'
  };

  // Language labels
  const languageLabels: Record<string, string> = {
    'zh-CN': '中文',
    'en-US': '英语'
  };

  // Fetch available voices on component mount
  useEffect(() => {
    fetchVoices();
  }, []);

  const fetchVoices = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/tts/voices/`);
      const data = await response.json();
      
      if (data.success) {
        setAvailableVoices(data.data.voices);
        setAvailableEmotions(data.data.emotions);
        
        // Update default language if needed
        if (data.data.default_language && data.data.default_language !== ttsOptions.language) {
          setTTSOptions(prev => ({
            ...prev,
            language: data.data.default_language
          }));
        }
      }
    } catch (error) {
      console.error('Failed to fetch voices:', error);
      onError?.('获取语音选项失败');
    }
  };

  const generateTTS = async () => {
    if (!text.trim()) {
      onError?.('请输入要转换的文本');
      return;
    }

    setIsLoading(true);
    
    try {
      const response = await fetch(`${apiBaseUrl}/tts/generate/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text.trim(),
          ...ttsOptions
        }),
      });

      const data = await response.json();

      if (data.success) {
        setGeneratedAudio(data.data);
        onTTSGenerated?.(data.data);
      } else {
        onError?.(data.error || '语音生成失败');
      }
    } catch (error) {
      console.error('TTS generation error:', error);
      onError?.('语音生成失败，请稍后重试');
    } finally {
      setIsLoading(false);
    }
  };

  const previewVoice = async () => {
    setIsLoading(true);
    
    try {
      const response = await fetch(`${apiBaseUrl}/tts/preview/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          language: ttsOptions.language,
          voice_type: ttsOptions.voice_type,
          emotion: ttsOptions.emotion
        }),
      });

      const data = await response.json();

      if (data.success) {
        setGeneratedAudio(data.data);
      } else {
        onError?.(data.error || '语音预览失败');
      }
    } catch (error) {
      console.error('Voice preview error:', error);
      onError?.('语音预览失败');
    } finally {
      setIsLoading(false);
    }
  };

  const downloadAudio = () => {
    if (!generatedAudio) return;
    
    const link = document.createElement('a');
    link.href = generatedAudio.audio_url;
    link.download = `tts_${generatedAudio.cache_key}.mp3`;
    link.click();
  };

  // Convert generated audio to AudioTrack format
  const audioTrack: AudioTrack | undefined = generatedAudio ? {
    id: generatedAudio.cache_key,
    title: text.length > 50 ? text.substring(0, 50) + '...' : text,
    artist: `${languageLabels[generatedAudio.language]} - ${voiceTypeLabels[generatedAudio.voice_type]} - ${emotionLabels[generatedAudio.emotion]}`,
    src: generatedAudio.audio_url
  } : undefined;

  return (
    <div className={`tts-component ${theme} ${className}`} style={{
      background: colors.secondary,
      borderRadius: '16px',
      padding: '24px',
      boxShadow: '0 4px 16px rgba(0,0,0,0.1)'
    }}>
      {/* Header */}
      <div className="header" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '24px'
      }}>
        <h2 style={{
          margin: 0,
          color: colors.accent,
          fontSize: '24px',
          fontWeight: '700',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <MessageSquare size={24} />
          文本转语音
        </h2>
        <button
          onClick={() => setShowSettings(!showSettings)}
          style={{
            background: 'none',
            border: 'none',
            color: colors.primary,
            cursor: 'pointer',
            padding: '8px',
            borderRadius: '6px',
            display: 'flex',
            alignItems: 'center',
            gap: '4px'
          }}
        >
          <Settings size={18} />
          设置
        </button>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="settings-panel" style={{
          background: 'white',
          borderRadius: '12px',
          padding: '20px',
          marginBottom: '20px',
          border: `1px solid ${colors.primary}20`
        }}>
          <h3 style={{
            margin: '0 0 16px 0',
            color: colors.accent,
            fontSize: '16px',
            fontWeight: '600'
          }}>
            语音设置
          </h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            {/* Language Selection */}
            <div>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                color: colors.accent,
                fontSize: '14px',
                fontWeight: '500'
              }}>
                语言
              </label>
              <select
                value={ttsOptions.language}
                onChange={(e) => setTTSOptions(prev => ({
                  ...prev,
                  language: e.target.value
                }))}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  borderRadius: '8px',
                  border: `1px solid ${colors.primary}40`,
                  fontSize: '14px'
                }}
              >
                {Object.entries(availableVoices).map(([lang, voices]) => (
                  <option key={lang} value={lang}>
                    {languageLabels[lang] || lang}
                  </option>
                ))}
              </select>
            </div>

            {/* Voice Type Selection */}
            <div>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                color: colors.accent,
                fontSize: '14px',
                fontWeight: '500'
              }}>
                声音类型
              </label>
              <select
                value={ttsOptions.voice_type}
                onChange={(e) => setTTSOptions(prev => ({
                  ...prev,
                  voice_type: e.target.value
                }))}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  borderRadius: '8px',
                  border: `1px solid ${colors.primary}40`,
                  fontSize: '14px'
                }}
              >
                {availableVoices[ttsOptions.language]?.map(voice => (
                  <option key={voice} value={voice}>
                    {voiceTypeLabels[voice] || voice}
                  </option>
                ))}
              </select>
            </div>

            {/* Emotion Selection */}
            <div>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                color: colors.accent,
                fontSize: '14px',
                fontWeight: '500'
              }}>
                情感色彩
              </label>
              <select
                value={ttsOptions.emotion}
                onChange={(e) => setTTSOptions(prev => ({
                  ...prev,
                  emotion: e.target.value
                }))}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  borderRadius: '8px',
                  border: `1px solid ${colors.primary}40`,
                  fontSize: '14px'
                }}
              >
                {availableEmotions.map(emotion => (
                  <option key={emotion} value={emotion}>
                    {emotionLabels[emotion] || emotion}
                  </option>
                ))}
              </select>
            </div>

            {/* Cache Option */}
            <div>
              <label style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                color: colors.accent,
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer'
              }}>
                <input
                  type="checkbox"
                  checked={ttsOptions.use_cache}
                  onChange={(e) => setTTSOptions(prev => ({
                    ...prev,
                    use_cache: e.target.checked
                  }))}
                  style={{ accentColor: colors.primary }}
                />
                使用缓存
              </label>
            </div>
          </div>

          {/* Preview Voice */}
          <div style={{ marginTop: '16px' }}>
            <button
              onClick={previewVoice}
              disabled={isLoading}
              style={{
                background: colors.primary + '20',
                border: `1px solid ${colors.primary}`,
                borderRadius: '8px',
                padding: '8px 16px',
                color: colors.primary,
                cursor: isLoading ? 'not-allowed' : 'pointer',
                fontSize: '14px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <Volume2 size={16} />
              试听语音
            </button>
          </div>
        </div>
      )}

      {/* Text Input */}
      <div className="text-input" style={{ marginBottom: '20px' }}>
        <label style={{
          display: 'block',
          marginBottom: '8px',
          color: colors.accent,
          fontSize: '16px',
          fontWeight: '600'
        }}>
          输入文本
        </label>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="请输入要转换为语音的文本..."
          rows={4}
          style={{
            width: '100%',
            padding: '12px',
            borderRadius: '8px',
            border: `1px solid ${colors.primary}40`,
            fontSize: '14px',
            resize: 'vertical',
            fontFamily: 'inherit'
          }}
        />
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginTop: '8px',
          fontSize: '12px',
          color: '#666'
        }}>
          <span>{text.length} 字符</span>
          {text.length > 1000 && (
            <span style={{ color: '#ff6b6b' }}>
              建议文本长度不超过1000字符
            </span>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="actions" style={{
        display: 'flex',
        gap: '12px',
        marginBottom: '20px'
      }}>
        <button
          onClick={generateTTS}
          disabled={isLoading || !text.trim()}
          style={{
            background: colors.primary,
            border: 'none',
            borderRadius: '8px',
            padding: '12px 24px',
            color: 'white',
            cursor: isLoading || !text.trim() ? 'not-allowed' : 'pointer',
            fontSize: '16px',
            fontWeight: '600',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            opacity: isLoading || !text.trim() ? 0.6 : 1
          }}
        >
          {isLoading ? (
            <>
              <div style={{
                width: '16px',
                height: '16px',
                border: '2px solid white',
                borderTop: '2px solid transparent',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }} />
              生成中...
            </>
          ) : (
            <>
              <Mic size={18} />
              生成语音
            </>
          )}
        </button>

        {generatedAudio && (
          <button
            onClick={downloadAudio}
            style={{
              background: 'none',
              border: `1px solid ${colors.primary}`,
              borderRadius: '8px',
              padding: '12px 20px',
              color: colors.primary,
              cursor: 'pointer',
              fontSize: '14px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <Download size={16} />
            下载
          </button>
        )}
      </div>

      {/* Audio Player */}
      {audioTrack && (
        <div className="audio-player-section">
          <h3 style={{
            margin: '0 0 12px 0',
            color: colors.accent,
            fontSize: '16px',
            fontWeight: '600'
          }}>
            播放器
          </h3>
          <AudioPlayer
            currentTrack={audioTrack}
            playlist={[audioTrack]}
            theme={theme}
            showPlaylist={false}
            autoplay={false}
          />
        </div>
      )}

      {/* Cache Status */}
      {generatedAudio && (
        <div style={{
          marginTop: '16px',
          padding: '12px',
          background: generatedAudio.cached ? colors.primary + '10' : colors.accent + '10',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '14px'
        }}>
          <span style={{ color: colors.accent }}>
            {generatedAudio.cached ? '✓ 使用缓存音频' : '✓ 新生成音频'}
          </span>
          <span style={{ color: '#666', fontSize: '12px' }}>
            ID: {generatedAudio.cache_key.substring(0, 8)}...
          </span>
        </div>
      )}

      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};