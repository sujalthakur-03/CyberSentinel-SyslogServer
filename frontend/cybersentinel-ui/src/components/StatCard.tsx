/**
 * Statistics Card Component
 * Displays a statistic with icon, title, and value
 */
import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  color?: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  subtitle?: string;
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon: Icon,
  color = '#3b82f6',
  trend,
  subtitle
}) => {
  return (
    <div className="stat-card">
      <div className="stat-card-header">
        <div className="stat-card-icon" style={{ backgroundColor: `${color}20`, color }}>
          <Icon size={24} />
        </div>
        <div className="stat-card-content">
          <h3 className="stat-card-title">{title}</h3>
          <p className="stat-card-value">{value}</p>
          {subtitle && <p className="stat-card-subtitle">{subtitle}</p>}
          {trend && (
            <div className={`stat-card-trend ${trend.isPositive ? 'positive' : 'negative'}`}>
              <span>{trend.isPositive ? '↑' : '↓'}</span>
              <span>{Math.abs(trend.value)}%</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StatCard;
