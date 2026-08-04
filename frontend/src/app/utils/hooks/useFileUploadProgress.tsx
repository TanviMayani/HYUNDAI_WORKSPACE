import { useState, useEffect } from 'react';

interface UseFileUploadProgressProps {
  size: number; // Size of the file or item in bytes
  interval?: number; // Update interval in milliseconds (default: 25)
}

const useFileUploadProgress = ({ size, interval = 25 }: UseFileUploadProgressProps) => {
  const [currentProgress, setCurrentProgress] = useState(0);

  useEffect(() => {
    const fileSizeMB = size / (1024 * 1024);
    const progressDuration = fileSizeMB * 100;
    const step = (100 / progressDuration) * interval;
    let progress = 0;

    const intervalId = setInterval(() => {
      progress = Math.min(progress + step, 100);
      setCurrentProgress(progress);
      if (progress >= 100) {
        clearInterval(intervalId);
      }
    }, interval);

    return () => clearInterval(intervalId);
  }, [size, interval]);

  return currentProgress;
};

export default useFileUploadProgress;
