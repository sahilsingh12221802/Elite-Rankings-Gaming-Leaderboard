/**
 * Main App component - Entry point for the leaderboard application
 */
import { RankingBoard, ScoreSubmissionForm, UserRankCard } from '@/components'
import { useLeaderboardStore } from '@/context/store'
import { useLeaderboard, useWebSocket } from '@/hooks'
import '@/styles/globals.css'
import { apiService } from '@/utils/api'
import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

function App() {
  const [selectedUserId, setSelectedUserId] = useState<number | undefined>(undefined)
  const { userRank, setUserRank } = useLeaderboardStore()

  // Load initial leaderboard data and get manual refresh function
  const { fetchLeaderboard } = useLeaderboard(100)

  // Connect to WebSocket for real-time updates
  const { isConnected } = useWebSocket(selectedUserId)

  // Fetch user rank when selected
  useEffect(() => {
    const fetchUserRank = async () => {
      if (selectedUserId === undefined || selectedUserId === null) {
        setUserRank(null)
        return
      }

      try {
        const rank = await apiService.getUserRank(selectedUserId)
        setUserRank(rank)
      } catch (error) {
        console.error('Failed to fetch user rank:', error)
      }
    }

    fetchUserRank()
  }, [selectedUserId, setUserRank])

  return (
    <div className="min-h-screen bg-dark-bg text-text-primary overflow-x-hidden">
      {/* Background effects */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-neon-primary opacity-5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-neon-secondary opacity-5 rounded-full blur-3xl" />
      </div>

      {/* Main container */}
      <div className="relative max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-6xl md:text-7xl font-bold mb-4">
            <span className="gradient-text neon-glow">
              ELITE RANKINGS
            </span>
          </h1>
          <div className="flex items-center justify-center space-x-3">
            <p className="text-text-secondary font-mono text-lg">
              Real-time multiplayer gaming leaderboard system
            </p>
            <div className="flex items-center space-x-2">
              <span
                className={`inline-block w-3 h-3 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-500'}`}
                aria-hidden
              />
              <span className="text-sm font-mono text-text-secondary">
                {isConnected ? 'WS Connected' : 'WS Disconnected'}
              </span>
            </div>
          </div>
        </motion.div>

        {/* Main grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left column - Leaderboard */}
          <div className="lg:col-span-2">
            <RankingBoard
              onUserSelect={setSelectedUserId}
              selectedUserId={selectedUserId}
            />
          </div>

          {/* Right column - User rank and submission */}
          <div className="space-y-6">
            {/* User rank display */}
            {userRank !== null && userRank !== undefined && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                key={userRank.user_id}
              >
                <UserRankCard userRank={userRank} />
              </motion.div>
            )}

            {/* Score submission form */}
            <ScoreSubmissionForm
              onSuccess={() => {
                // Refresh leaderboard immediately after submission
                fetchLeaderboard()
              }}
            />

            {/* Stats panel */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="rounded-xl overflow-hidden p-4"
              style={{
                background: 'linear-gradient(135deg, rgba(0, 255, 136, 0.05) 0%, rgba(0, 212, 255, 0.05) 100%)',
                border: '1px solid rgba(0, 255, 136, 0.15)',
              }}
            >
              <h3 className="text-sm font-mono text-neon-secondary mb-4 uppercase tracking-wider">
                System Status
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-text-secondary">Status</span>
                  <span className="text-neon-primary">● Online</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-secondary">Latency</span>
                  <span className="text-neon-secondary">&lt;50ms</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-secondary">Last Update</span>
                  <span className="text-neon-secondary">Now</span>
                </div>
              </div>
            </motion.div>
          </div>
        </div>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-16 pt-8 border-t border-neon-primary border-opacity-10 text-center text-text-secondary text-sm"
        >
          <p>🎮 Gaming Leaderboard v1.0.0 | Real-time • Scalable • Production-Ready</p>
        </motion.footer>
      </div>
    </div>
  )
}

export default App
