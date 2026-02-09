/**
 * Global state management for leaderboard
 */
import { LeaderboardEntry, UserRank } from '@/utils/api'
import { create } from 'zustand'

interface LeaderboardStore {
  entries: LeaderboardEntry[]
  userRank: UserRank | null
  loading: boolean
  error: string | null
  selectedUserId: number | undefined
  
  setEntries: (entries: LeaderboardEntry[]) => void
  setUserRank: (rank: UserRank | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setSelectedUserId: (userId: number | undefined) => void
  updateUserRank: (userId: number, newRank: number, oldRank?: number) => void
  reset: () => void
}

export const useLeaderboardStore = create<LeaderboardStore>((set) => ({
  entries: [],
  userRank: null,
  loading: false,
  error: null,
  selectedUserId: undefined,

  setEntries: (entries) => set({ entries }),
  setUserRank: (rank) => set({ userRank: rank }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setSelectedUserId: (userId) => set({ selectedUserId: userId }),
  
  updateUserRank: (userId, newRank) =>
    set((state) => ({
      entries: state.entries.map((entry) =>
        entry.user_id === userId ? { ...entry, rank: newRank } : entry
      ),
    })),

  reset: () =>
    set({
      entries: [],
      userRank: null,
      loading: false,
      error: null,
      selectedUserId: undefined,
    }),
}))
