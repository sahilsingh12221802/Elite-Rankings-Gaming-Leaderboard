/**
 * ScoreSubmissionForm - Submit a new game score
 */
import { apiService } from '@/utils/api'
import { motion } from 'framer-motion'
import React, { useState } from 'react'

interface ScoreSubmissionFormProps {
  onSuccess?: () => void
  onError?: (error: string) => void
}

type GameMode = 'classic' | 'ranked' | 'tournament' | 'survival'

export const ScoreSubmissionForm: React.FC<ScoreSubmissionFormProps> = ({
  onSuccess,
  onError,
}) => {
  const [userId, setUserId] = useState('')
  const [score, setScore] = useState('')
  const [gameMode, setGameMode] = useState<GameMode>('classic')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')

    try {
      if (!userId || !score) {
        throw new Error('Please fill in all fields')
      }

      const response = await apiService.submitScore({
        user_id: parseInt(userId),
        score: parseFloat(score),
        game_mode: gameMode,
      })

      setMessage(response.message)
      setUserId('')
      setScore('')
      setGameMode('classic')
      onSuccess?.()
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Failed to submit score'
      setMessage(`Error: ${errorMsg}`)
      onError?.(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  const formVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5 },
    },
  }

  return (
    <motion.div
      variants={formVariants}
      initial="hidden"
      animate="visible"
      className="w-full rounded-xl overflow-hidden p-6"
      style={{
        background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 255, 136, 0.1) 100%)',
        border: '2px solid rgba(0, 255, 136, 0.2)',
      }}
    >
      <h3 className="text-2xl font-bold gradient-text neon-glow mb-4">
        📊 Submit Score
      </h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* User ID */}
        <div>
          <label className="block text-sm font-mono text-neon-secondary mb-2">
            Player ID
          </label>
          <input
            type="number"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="Enter your player ID"
            className="w-full px-4 py-2 rounded-lg bg-dark-bg-tertiary border border-neon-primary border-opacity-30 text-text-primary focus:outline-none focus:border-neon-primary placeholder-text-secondary"
            disabled={loading}
          />
        </div>

        {/* Score */}
        <div>
          <label className="block text-sm font-mono text-neon-secondary mb-2">
            Score
          </label>
          <input
            type="number"
            value={score}
            onChange={(e) => setScore(e.target.value)}
            placeholder="Enter your score"
            step="0.01"
            className="w-full px-4 py-2 rounded-lg bg-dark-bg-tertiary border border-neon-primary border-opacity-30 text-text-primary focus:outline-none focus:border-neon-primary placeholder-text-secondary"
            disabled={loading}
          />
        </div>

        {/* Game Mode */}
        <div>
          <label className="block text-sm font-mono text-neon-secondary mb-2">
            Game Mode
          </label>
          <select
            value={gameMode}
            onChange={(e) => setGameMode(e.target.value as GameMode)}
            className="w-full px-4 py-2 rounded-lg bg-dark-bg-tertiary border border-neon-primary border-opacity-30 text-text-primary focus:outline-none focus:border-neon-primary"
            disabled={loading}
          >
            <option value="classic">Classic 🎮</option>
            <option value="ranked">Ranked ⭐</option>
            <option value="tournament">Tournament 🏆</option>
            <option value="survival">Survival 💪</option>
          </select>
        </div>

        {/* Submit Button */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          type="submit"
          disabled={loading}
          className="w-full px-6 py-3 rounded-lg bg-neon-primary text-dark-bg-secondary font-bold uppercase tracking-wider transition-all disabled:opacity-50"
          style={{
            boxShadow: '0 0 20px rgba(0, 255, 136, 0.3)',
          }}
        >
          {loading ? '⏳ Submitting...' : '🎯 Submit Score'}
        </motion.button>

        {/* Message */}
        {message && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className={`p-3 rounded-lg text-sm font-mono ${
              message.startsWith('Error')
                ? 'bg-neon-danger bg-opacity-10 text-neon-danger'
                : 'bg-neon-primary bg-opacity-10 text-neon-primary'
            }`}
          >
            {message}
          </motion.div>
        )}
      </form>
    </motion.div>
  )
}
