/**
 * RankingBoard - Main leaderboard display component
 */
import { useLeaderboardStore } from '@/context/store'
import { motion } from 'framer-motion'
import React, { useState } from 'react'
import { LeaderboardCard } from './LeaderboardCard'

interface RankingBoardProps {
  onUserSelect?: (userId: number) => void
  selectedUserId?: number
}

export const RankingBoard: React.FC<RankingBoardProps> = ({
  onUserSelect,
  selectedUserId,
}) => {
  const { entries, loading, error } = useLeaderboardStore()
  const [filter, setFilter] = useState<'all' | 'top10' | 'top50'>('all')

  const filteredEntries = entries.slice(
    0,
    filter === 'all' ? entries.length : filter === 'top10' ? 10 : 50
  )

  const boardVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.02,
        delayChildren: 0.1,
      },
    },
  }

  return (
    <div className="w-full">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-4xl font-bold gradient-text neon-glow mb-4">
          🏆 LEADERBOARD
        </h2>

        {/* Filter buttons */}
        <div className="flex gap-2">
          {(['all', 'top10', 'top50'] as const).map((filterOption) => (
            <button
              key={filterOption}
              onClick={() => setFilter(filterOption)}
              className={`px-4 py-2 rounded-lg font-mono uppercase text-sm transition-all ${
                filter === filterOption
                  ? 'bg-neon-primary text-dark-bg-secondary shadow-neon'
                  : 'bg-dark-bg-tertiary text-neon-primary border border-neon-primary border-opacity-30 hover:border-opacity-100'
              }`}
            >
              {filterOption === 'all'
                ? 'All Rankings'
                : filterOption === 'top10'
                  ? 'Top 10'
                  : 'Top 50'}
            </button>
          ))}
        </div>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="text-center py-12">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            className="inline-block"
          >
            <div className="text-4xl">⚙️</div>
          </motion.div>
          <p className="text-text-secondary mt-4">Loading rankings...</p>
        </div>
      )}

      {/* Error state */}
      {error && !loading && (
        <div className="bg-neon-danger bg-opacity-10 border border-neon-danger border-opacity-50 rounded-lg p-4 text-neon-danger">
          <p className="font-bold">⚠️ Error</p>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Rankings list */}
      {!loading && !error && (
        <motion.div
          variants={boardVariants}
          initial="hidden"
          animate="visible"
          className="space-y-3 max-h-[70vh] overflow-y-auto pr-2"
          style={{
            scrollbarWidth: 'thin',
            scrollbarColor: 'rgba(0, 255, 136, 0.3) rgba(20, 20, 30, 0.5)',
          }}
        >
          {filteredEntries.length > 0 ? (
            filteredEntries.map((entry, index) => (
              <LeaderboardCard
                key={`${entry.user_id}-${entry.rank}`}
                entry={entry}
                index={index}
                isHighlighted={selectedUserId === entry.user_id}
                onClick={() => onUserSelect?.(entry.user_id)}
              />
            ))
          ) : (
            <div className="text-center py-12">
              <p className="text-text-secondary">No rankings available</p>
            </div>
          )}
        </motion.div>
      )}
    </div>
  )
}
