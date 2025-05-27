import { useState, useRef, useCallback } from 'react';

export const useAudioPlayer = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const playAudio = useCallback(async (audioBlob: Blob) => {
    try {
      // Parar áudio atual se estiver tocando
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }

      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audioRef.current = audio;

      audio.addEventListener('loadedmetadata', () => {
        setDuration(audio.duration);
      });

      audio.addEventListener('timeupdate', () => {
        setCurrentTime(audio.currentTime);
      });

      audio.addEventListener('ended', () => {
        setIsPlaying(false);
        setCurrentTime(0);
        URL.revokeObjectURL(audioUrl);
      });

      audio.addEventListener('error', (e) => {
        console.error('Erro ao reproduzir áudio:', e);
        setIsPlaying(false);
        URL.revokeObjectURL(audioUrl);
      });

      setIsPlaying(true);
      await audio.play();
    } catch (error) {
      console.error('Erro ao reproduzir áudio:', error);
      setIsPlaying(false);
    }
  }, []);

  const pauseAudio = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  }, []);

  const stopAudio = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
      setCurrentTime(0);
    }
  }, []);

  const seekTo = useCallback((time: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime = time;
      setCurrentTime(time);
    }
  }, []);

  return {
    isPlaying,
    currentTime,
    duration,
    playAudio,
    pauseAudio,
    stopAudio,
    seekTo,
  };
};
