/**
 * WebSocket service for real-time leaderboard updates
 */
import { LeaderboardEntry } from './api'

interface LeaderboardUpdateEvent {
  event_type: 'leaderboard_update'
  user_id: number
  username: string
  new_rank: number
  old_rank?: number
  total_score: number
  rank_change: number
  timestamp: string
}

interface LeaderboardSnapshotEvent {
  event_type: 'leaderboard_snapshot'
  entries: LeaderboardEntry[]
  timestamp: string
}

type WebSocketEvent = LeaderboardUpdateEvent | LeaderboardSnapshotEvent

class WebSocketService {
  private ws: WebSocket | null = null
  private url: string
  private userId: number | null = null
  private listeners: Set<(event: WebSocketEvent) => void> = new Set()
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 3000

  constructor() {
    // Derive WebSocket URL from current page origin
    // This ensures it works behind proxies and different ports
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const host = window.location.host
    this.url = `${protocol}://${host}`
    console.log('[WebSocket] Base URL:', this.url)
  }

  connect(userId: number, onError?: (error: Error) => void): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.userId = userId
        const wsUrl = `${this.url}/ws/leaderboard/${userId}`
        console.log('[WebSocket] Connecting to:', wsUrl)
        this.ws = new WebSocket(wsUrl)

        this.ws.onopen = () => {
          console.log('[WebSocket] Connected successfully to user', userId)
          this.reconnectAttempts = 0
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data) as WebSocketEvent
            console.log('[WebSocket] Message received:', data.event_type)
            this.notifyListeners(data)
          } catch (error) {
            console.error('[WebSocket] Failed to parse message:', error)
          }
        }

        this.ws.onerror = (error) => {
          console.error('[WebSocket] Connection error:', error)
          onError?.(new Error('WebSocket connection error'))
          reject(new Error('WebSocket connection failed'))
        }

        this.ws.onclose = () => {
          console.log('[WebSocket] Connection closed')
          this.attemptReconnect()
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts && this.userId) {
      this.reconnectAttempts++
      console.log(
        `Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`
      )
      setTimeout(() => {
        this.connect(this.userId!).catch(console.error)
      }, this.reconnectDelay * this.reconnectAttempts)
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  subscribe(listener: (event: WebSocketEvent) => void): () => void {
    this.listeners.add(listener)
    return () => {
      this.listeners.delete(listener)
    }
  }

  private notifyListeners(event: WebSocketEvent) {
    this.listeners.forEach((listener) => {
      try {
        listener(event)
      } catch (error) {
        console.error('Error in WebSocket listener:', error)
      }
    })
  }

  sendPing() {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send('ping')
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

export const wsService = new WebSocketService()
export type { LeaderboardSnapshotEvent, LeaderboardUpdateEvent, WebSocketEvent }

