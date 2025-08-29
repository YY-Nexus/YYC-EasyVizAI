/**
 * Audio Player Component
 * Advanced audio player with support for local and remote audio files
 * Based on the existing design documentation
 */
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Howl, Howler } from 'howler';
import { 
  Play, 
  Pause, 
  SkipBack, 
  SkipForward, 
  Volume2, 
  VolumeX,
  Repeat,
  Shuffle
} from 'lucide-react';

export interface AudioTrack {
  id: string;
  title: string;
  artist?: string;
  src: string;
  duration?: number;
}

export interface AudioPlayerProps {
  playlist?: AudioTrack[];
  currentTrack?: AudioTrack;
  autoplay?: boolean;
  showPlaylist?: boolean;
  theme?: 'cloud' | 'bamboo' | 'amber';
  onTrackChange?: (track: AudioTrack) => void;
  onPlayStateChange?: (isPlaying: boolean) => void;
  className?: string;
}

export const AudioPlayer: React.FC<AudioPlayerProps> = ({
  playlist = [],
  currentTrack,
  autoplay = false,
  showPlaylist = true,
  theme = 'cloud',
  onTrackChange,
  onPlayStateChange,
  className = ''
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.7);
  const [isMuted, setIsMuted] = useState(false);
  const [isRepeat, setIsRepeat] = useState(false);
  const [isShuffle, setIsShuffle] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  
  const soundRef = useRef<Howl | null>(null);
  const progressRef = useRef<HTMLDivElement>(null);
  const animationRef = useRef<number>();

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

  // Update progress
  const updateProgress = useCallback(() => {
    if (soundRef.current && isPlaying) {
      const seek = soundRef.current.seek() as number;
      setCurrentTime(seek);
      animationRef.current = requestAnimationFrame(updateProgress);
    }
  }, [isPlaying]);

  // Load track
  const loadTrack = useCallback(async (track: AudioTrack, index: number) => {
    setLoading(true);
    
    // Stop current sound
    if (soundRef.current) {
      soundRef.current.unload();
    }

    try {
      const sound = new Howl({
        src: [track.src],
        format: ['mp3', 'wav', 'ogg'],
        preload: true,
        onload: () => {
          setDuration(sound.duration());
          setLoading(false);
          if (autoplay) {
            play();
          }
        },
        onplay: () => {
          setIsPlaying(true);
          onPlayStateChange?.(true);
          updateProgress();
        },
        onpause: () => {
          setIsPlaying(false);
          onPlayStateChange?.(false);
          if (animationRef.current) {
            cancelAnimationFrame(animationRef.current);
          }
        },
        onstop: () => {
          setIsPlaying(false);
          setCurrentTime(0);
          onPlayStateChange?.(false);
          if (animationRef.current) {
            cancelAnimationFrame(animationRef.current);
          }
        },
        onend: () => {
          if (isRepeat) {
            sound.seek(0);
            sound.play();
          } else {
            nextTrack();
          }
        },
        onerror: (id, error) => {
          console.error('Audio load error:', error);
          setLoading(false);
        }
      });

      soundRef.current = sound;
      setCurrentIndex(index);
      onTrackChange?.(track);

    } catch (error) {
      console.error('Failed to load track:', error);
      setLoading(false);
    }
  }, [autoplay, isRepeat, onTrackChange, onPlayStateChange, updateProgress]);

  // Play/pause
  const togglePlayback = useCallback(() => {
    if (!soundRef.current) return;

    if (isPlaying) {
      soundRef.current.pause();
    } else {
      soundRef.current.play();
    }
  }, [isPlaying]);

  const play = useCallback(() => {
    if (soundRef.current) {
      soundRef.current.play();
    }
  }, []);

  const pause = useCallback(() => {
    if (soundRef.current) {
      soundRef.current.pause();
    }
  }, []);

  // Previous track
  const previousTrack = useCallback(() => {
    if (playlist.length === 0) return;
    
    let nextIndex;
    if (isShuffle) {
      nextIndex = Math.floor(Math.random() * playlist.length);
    } else {
      nextIndex = (currentIndex - 1 + playlist.length) % playlist.length;
    }
    
    loadTrack(playlist[nextIndex], nextIndex);
  }, [playlist, currentIndex, isShuffle, loadTrack]);

  // Next track
  const nextTrack = useCallback(() => {
    if (playlist.length === 0) return;
    
    let nextIndex;
    if (isShuffle) {
      nextIndex = Math.floor(Math.random() * playlist.length);
    } else {
      nextIndex = (currentIndex + 1) % playlist.length;
    }
    
    loadTrack(playlist[nextIndex], nextIndex);
  }, [playlist, currentIndex, isShuffle, loadTrack]);

  // Seek
  const seek = useCallback((percentage: number) => {
    if (soundRef.current && duration > 0) {
      const seekTime = duration * percentage;
      soundRef.current.seek(seekTime);
      setCurrentTime(seekTime);
    }
  }, [duration]);

  // Volume control
  const changeVolume = useCallback((newVolume: number) => {
    setVolume(newVolume);
    if (soundRef.current) {
      soundRef.current.volume(isMuted ? 0 : newVolume);
    }
    Howler.volume(isMuted ? 0 : newVolume);
  }, [isMuted]);

  // Mute toggle
  const toggleMute = useCallback(() => {
    const newMuted = !isMuted;
    setIsMuted(newMuted);
    if (soundRef.current) {
      soundRef.current.volume(newMuted ? 0 : volume);
    }
    Howler.volume(newMuted ? 0 : volume);
  }, [isMuted, volume]);

  // Format time
  const formatTime = (time: number): string => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  // Initialize with current track or first track
  useEffect(() => {
    if (currentTrack) {
      const index = playlist.findIndex(track => track.id === currentTrack.id);
      loadTrack(currentTrack, index >= 0 ? index : 0);
    } else if (playlist.length > 0) {
      loadTrack(playlist[0], 0);
    }
  }, [currentTrack, playlist]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (soundRef.current) {
        soundRef.current.unload();
      }
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  // Progress bar click handler
  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!progressRef.current) return;
    
    const rect = progressRef.current.getBoundingClientRect();
    const percentage = (e.clientX - rect.left) / rect.width;
    seek(percentage);
  };

  const currentTrackData = playlist[currentIndex] || currentTrack;

  return (
    <div className={`audio-player ${theme} ${className}`} style={{ 
      background: colors.secondary,
      borderRadius: '12px',
      padding: '20px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
    }}>
      {/* Track Info */}
      {currentTrackData && (
        <div className="track-info" style={{ marginBottom: '16px', textAlign: 'center' }}>
          <h3 style={{ 
            margin: '0 0 4px 0', 
            color: colors.accent,
            fontSize: '18px',
            fontWeight: '600'
          }}>
            {currentTrackData.title}
          </h3>
          {currentTrackData.artist && (
            <p style={{ 
              margin: 0, 
              color: '#666',
              fontSize: '14px'
            }}>
              {currentTrackData.artist}
            </p>
          )}
        </div>
      )}

      {/* Progress Bar */}
      <div className="progress-container" style={{ marginBottom: '16px' }}>
        <div className="time-info" style={{ 
          display: 'flex', 
          justifyContent: 'space-between',
          marginBottom: '8px',
          fontSize: '12px',
          color: '#666'
        }}>
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
        
        <div 
          ref={progressRef}
          className="progress-bar"
          onClick={handleProgressClick}
          style={{
            height: '6px',
            background: '#e0e0e0',
            borderRadius: '3px',
            cursor: 'pointer',
            position: 'relative'
          }}
        >
          <div 
            className="progress-fill"
            style={{
              height: '100%',
              background: colors.primary,
              borderRadius: '3px',
              width: `${duration > 0 ? (currentTime / duration) * 100 : 0}%`,
              transition: 'width 0.1s ease'
            }}
          />
        </div>
      </div>

      {/* Controls */}
      <div className="controls" style={{ 
        display: 'flex', 
        alignItems: 'center',
        justifyContent: 'center',
        gap: '12px',
        marginBottom: '16px'
      }}>
        <button
          onClick={() => setIsShuffle(!isShuffle)}
          style={{
            background: 'none',
            border: 'none',
            color: isShuffle ? colors.primary : '#666',
            cursor: 'pointer',
            padding: '8px'
          }}
        >
          <Shuffle size={18} />
        </button>

        <button
          onClick={previousTrack}
          disabled={playlist.length <= 1}
          style={{
            background: 'none',
            border: 'none',
            color: playlist.length > 1 ? colors.accent : '#ccc',
            cursor: playlist.length > 1 ? 'pointer' : 'not-allowed',
            padding: '8px'
          }}
        >
          <SkipBack size={20} />
        </button>

        <button
          onClick={togglePlayback}
          disabled={loading || !currentTrackData}
          style={{
            background: colors.primary,
            border: 'none',
            borderRadius: '50%',
            width: '48px',
            height: '48px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1
          }}
        >
          {loading ? (
            <div style={{ 
              width: '16px', 
              height: '16px', 
              border: '2px solid white',
              borderTop: '2px solid transparent',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }} />
          ) : isPlaying ? (
            <Pause size={20} />
          ) : (
            <Play size={20} />
          )}
        </button>

        <button
          onClick={nextTrack}
          disabled={playlist.length <= 1}
          style={{
            background: 'none',
            border: 'none',
            color: playlist.length > 1 ? colors.accent : '#ccc',
            cursor: playlist.length > 1 ? 'pointer' : 'not-allowed',
            padding: '8px'
          }}
        >
          <SkipForward size={20} />
        </button>

        <button
          onClick={() => setIsRepeat(!isRepeat)}
          style={{
            background: 'none',
            border: 'none',
            color: isRepeat ? colors.primary : '#666',
            cursor: 'pointer',
            padding: '8px'
          }}
        >
          <Repeat size={18} />
        </button>
      </div>

      {/* Volume Control */}
      <div className="volume-control" style={{ 
        display: 'flex', 
        alignItems: 'center',
        gap: '8px',
        justifyContent: 'center'
      }}>
        <button
          onClick={toggleMute}
          style={{
            background: 'none',
            border: 'none',
            color: colors.accent,
            cursor: 'pointer',
            padding: '4px'
          }}
        >
          {isMuted || volume === 0 ? <VolumeX size={18} /> : <Volume2 size={18} />}
        </button>
        
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={volume}
          onChange={(e) => changeVolume(parseFloat(e.target.value))}
          style={{
            width: '100px',
            accentColor: colors.primary
          }}
        />
      </div>

      {/* Playlist */}
      {showPlaylist && playlist.length > 1 && (
        <div className="playlist" style={{ 
          marginTop: '16px',
          maxHeight: '200px',
          overflowY: 'auto',
          borderTop: `1px solid ${colors.primary}20`,
          paddingTop: '16px'
        }}>
          <h4 style={{ 
            margin: '0 0 12px 0',
            color: colors.accent,
            fontSize: '14px',
            fontWeight: '600'
          }}>
            播放列表
          </h4>
          {playlist.map((track, index) => (
            <div
              key={track.id}
              onClick={() => loadTrack(track, index)}
              style={{
                padding: '8px 12px',
                cursor: 'pointer',
                borderRadius: '6px',
                background: index === currentIndex ? colors.primary + '20' : 'transparent',
                marginBottom: '4px',
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '14px'
              }}
            >
              <span style={{ 
                color: index === currentIndex ? colors.primary : colors.accent,
                fontWeight: index === currentIndex ? '600' : 'normal'
              }}>
                {track.title}
              </span>
              {track.artist && (
                <span style={{ color: '#666', fontSize: '12px' }}>
                  {track.artist}
                </span>
              )}
            </div>
          ))}
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