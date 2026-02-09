/**
 * UserRankCard - Displays the current user's ranking
 */
import { UserRank } from '@/utils/api'
import { calculatePercentile, formatNumber, getRankColor, getRankEmoji } from '@/utils/formatting'
import { motion } from 'framer-motion'
import React from 'react'

interface UserRankCardProps {
  userRank: UserRank
}

export const UserRankCard: React.FC<UserRankCardProps> = ({ userRank }) => {
  const containerVariants = {
    hidden: { opacity: 0, scale: 0.9 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: { duration: 0.5 },
    },
  }

  const pulseVariants = {
    pulse: {
      boxShadow: [
        '0 0 20px rgba(0, 255, 136, 0.3)',
        '0 0 40px rgba(0, 255, 136, 0.6)',
        '0 0 20px rgba(0, 255, 136, 0.3)',
      ],
      transition: {
        duration: 2,
        repeat: Infinity,
      },
    },
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="rounded-xl overflow-hidden p-6"
      style={{
        background: 'linear-gradient(135deg, rgba(0, 255, 136, 0.1) 0%, rgba(0, 212, 255, 0.1) 100%)',
        border: '2px solid rgba(0, 255, 136, 0.3)',
      }}
    >
      <motion.div variants={pulseVariants} animate="pulse">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Rank Display */}
          <div className="text-center">
            <div className="text-4xl mb-2">{getRankEmoji(userRank.rank)}</div>
            <p className="text-text-secondary text-sm uppercase tracking-wider">Rank</p>
            <p className={`text-4xl font-bold mt-2 ${getRankColor(userRank.rank)}`}>
              {userRank.rank}
            </p>
          </div>

          {/* Score */}
          <div className="text-center">
            <p className="text-text-secondary text-sm uppercase tracking-wider">Total Score</p>
            <p className="text-4xl font-bold mt-2 gradient-text neon-glow">
              {formatNumber(userRank.total_score)}
            </p>
          </div>

          {/* Games Played */}
          <div className="text-center">
            <p className="text-text-secondary text-sm uppercase tracking-wider">Games Played</p>
            <p className="text-4xl font-bold mt-2 text-neon-secondary">
              {userRank.games_played}
            </p>
          </div>

          {/* Percentile/Tier */}
          <div className="text-center">
            <p className="text-text-secondary text-sm uppercase tracking-wider">Tier</p>
            <p className="text-2xl font-bold mt-2 text-neon-primary">
              {calculatePercentile(userRank.percentile)}
            </p>
            <p className="text-xs text-neon-secondary mt-1">
              Top {(100 - userRank.percentile).toFixed(1)}%
            </p>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}
