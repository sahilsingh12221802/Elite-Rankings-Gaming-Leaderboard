/**
 * API service for backend communication
 */
import axios, { AxiosInstance } from 'axios'

interface ScoreSubmitRequest {
  user_id: number
  score: number
  game_mode: 'classic' | 'ranked' | 'tournament' | 'survival'
  duration_ms?: number
  metadata?: Record<string, any>
}

interface ScoreSubmitResponse {
  session_id: number
  user_id: number
  score: number
  new_total_score: number
  new_rank: number
  rank_change: number
  message: string
}

interface LeaderboardEntry {
  rank: number
  user_id: number
  username: string
  total_score: number
  games_played: number
  win_rate: number
  last_updated: string
}

interface UserRank {
  user_id: number
  username: string
  rank: number
  total_score: number
  games_played: number
  win_rate: number
  percentile: number
  last_updated: string
}

class APIService {
  private client: AxiosInstance

  constructor(baseURL: string = '/api') {
    this.client = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }

  async submitScore(request: ScoreSubmitRequest): Promise<ScoreSubmitResponse> {
    const response = await this.client.post<ScoreSubmitResponse>(
      '/leaderboard/submit',
      request
    )
    return response.data
  }

  async getTopLeaderboard(limit: number = 100, offset: number = 0): Promise<LeaderboardEntry[]> {
    const response = await this.client.get<{ entries: LeaderboardEntry[]; total_entries: number }>(
      '/leaderboard/top',
      { params: { limit, offset } }
    )
    return response.data.entries
  }

  async getUserRank(userId: number): Promise<UserRank> {
    const response = await this.client.get<UserRank>(
      `/leaderboard/rank/${userId}`
    )
    return response.data
  }

  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get<{ status: string }>(
      '/leaderboard/health'
    )
    return response.data
  }
}

export const apiService = new APIService()
export type { LeaderboardEntry, ScoreSubmitRequest, ScoreSubmitResponse, UserRank }

