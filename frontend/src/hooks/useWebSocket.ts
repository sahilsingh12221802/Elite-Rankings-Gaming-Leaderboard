/**
 * Custom hook for WebSocket connection management
 */
import { useLeaderboardStore } from '@/context/store'
import { apiService } from '@/utils/api'
import { WebSocketEvent, wsService } from '@/utils/websocket'
import { useCallback, useEffect } from 'react'

export const useWebSocket = (userId: number | null | undefined) => {
  const { setEntries, setError } = useLeaderboardStore()

  // Fetch fresh leaderboard data
  const fetchLeaderboard = useCallback(async () => {
    try {
      const entries = await apiService.getTopLeaderboard(100, 0)
      setEntries(entries)
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error)
    }
  }, [setEntries])

  useEffect(() => {
    // Connect even when no specific user is selected so UI receives global updates
    const connectUserId = userId ?? 0

    let unsubscribe: (() => void) | null = null

    const connect = async () => {
      try {
        await wsService.connect(connectUserId)

        unsubscribe = wsService.subscribe((event: WebSocketEvent) => {
          if (event.event_type === 'leaderboard_snapshot') {
            setEntries(event.entries)
          } else if (event.event_type === 'leaderboard_update') {
            // Refresh leaderboard when any player's rank changes
            console.log('Ranking updated:', event)
            fetchLeaderboard()
          }
        })
      } catch (error) {
        setError(error instanceof Error ? error.message : 'Connection failed')
      }
    }

    connect()

    return () => {
      if (unsubscribe) unsubscribe()
      wsService.disconnect()
    }
  }, [userId, setEntries, setError, fetchLeaderboard])

  const disconnect = useCallback(() => {
    wsService.disconnect()
  }, [])

  return { isConnected: wsService.isConnected(), disconnect }
}
