/**
 * Custom hook for leaderboard data fetching
 */
import { useLeaderboardStore } from '@/context/store'
import { apiService } from '@/utils/api'
import { useCallback, useEffect } from 'react'

export const useLeaderboard = (limit: number = 100, offset: number = 0) => {
  const { setEntries, setLoading, setError } = useLeaderboardStore()

  const fetchLeaderboard = useCallback(async () => {
    setLoading(true)
    try {
      const entries = await apiService.getTopLeaderboard(limit, offset)
      setEntries(entries)
      setError(null)
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch leaderboard'
      setError(message)
    } finally {
      setLoading(false)
    }
  }, [limit, offset, setEntries, setLoading, setError])

  useEffect(() => {
    fetchLeaderboard()
  }, [fetchLeaderboard])

  return { fetchLeaderboard }
}
