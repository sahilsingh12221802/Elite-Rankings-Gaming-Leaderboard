/**
 * LeaderboardCard - Individual player ranking card
 */
import { LeaderboardEntry } from '@/utils/api'
import { formatNumber, getRankColor, getRankEmoji } from '@/utils/formatting'
import { motion } from 'framer-motion'
import React from 'react'

interface LeaderboardCardProps {
  entry: LeaderboardEntry
  index: number
  isHighlighted?: boolean
  onClick?: () => void
}

export const LeaderboardCard: React.FC<LeaderboardCardProps> = ({
  entry,
  index,
  isHighlighted = false,
  onClick,
}) => {
  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
        delay: index * 0.05,
      },
    },
    hover: {
      scale: 1.02,
      x: 8,
      boxShadow: '0 0 40px rgba(0, 255, 136, 0.4)',
    },
  }

  const getRankBg = () => {
    switch (entry.rank) {
      case 1:
        return 'from-yellow-900 to-yellow-800'
      case 2:
        return 'from-gray-700 to-gray-600'
      case 3:
        return 'from-orange-900 to-orange-800'
      default:
        return 'from-slate-800 to-slate-700'
    }
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      whileHover="hover"
      onClick={onClick}
      className={`
        relative overflow-hidden rounded-xl p-4 cursor-pointer
        transition-all duration-300
        ${isHighlighted ? 'ring-2 ring-neon-secondary' : ''}
      `}
      style={{
        background: 'rgba(20, 20, 30, 0.8)',
        border: '1px solid rgba(0, 255, 136, 0.2)',
      }}
    >
      {/* Background gradient */}
      <div
        className={`absolute inset-0 bg-gradient-to-r ${getRankBg()} opacity-10 -z-10`}
      />

      {/* Neon border accent */}
      <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-neon-primary to-neon-secondary" />

      <div className="flex items-center gap-4">
        {/* Rank */}
        <div className="flex flex-col items-center justify-center w-16">
          <span className="text-3xl">{getRankEmoji(entry.rank)}</span>
          <span className={`text-2xl font-bold ${getRankColor(entry.rank)}`}>
            #{entry.rank}
          </span>
        </div>

        {/* Player Info */}
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-bold text-neon-primary truncate neon-glow">
            {entry.username}
          </h3>
          <div className="flex gap-4 text-sm text-text-secondary mt-1">
            <span>🎮 {entry.games_played} games</span>
            <span>📈 {(entry.win_rate * 100).toFixed(1)}% win</span>
          </div>
        </div>

        {/* Score Display */}
        <div className="text-right">
          <div className="text-3xl font-bold gradient-text neon-glow">
            {formatNumber(entry.total_score)}
          </div>
          <span className="text-xs text-neon-secondary">PTS</span>
        </div>
      </div>

      {/* Last updated indicator */}
      <div className="absolute bottom-1 right-2 text-xs text-text-secondary opacity-50">
        ●
      </div>
    </motion.div>
  )
}
