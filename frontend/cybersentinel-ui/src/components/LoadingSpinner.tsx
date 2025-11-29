/**
 * Loading Spinner Component
 * Displays a loading spinner with optional text
 */
import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  text?: string;
  fullScreen?: boolean;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'medium',
  text,
  fullScreen = false
}) => {
  const sizeMap = {
    small: 24,
    medium: 48,
    large: 64,
  };

  const spinner = (
    <div className="loading-spinner">
      <Loader2 size={sizeMap[size]} className="spinner-icon" />
      {text && <p className="loading-text">{text}</p>}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="loading-spinner-fullscreen">
        {spinner}
      </div>
    );
  }

  return spinner;
};

export default LoadingSpinner;
