/**
 * Utility functions for formatting and animations
 */

export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'decimal',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(num)
}

export const getRankColor = (rank: number): string => {
  if (rank === 1) return 'text-yellow-400'
  if (rank === 2) return 'text-gray-300'
  if (rank === 3) return 'text-orange-400'
  return 'text-neon-primary'
}

export const getRankEmoji = (rank: number): string => {
  if (rank === 1) return '👑'
  if (rank === 2) return '🥈'
  if (rank === 3) return '🥉'
  return '⭐'
}

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

export const calculatePercentile = (percentile: number): string => {
  const rounded = Math.round(percentile)
  if (rounded >= 95) return 'S-Tier 🔥'
  if (rounded >= 90) return 'A-Tier 🎯'
  if (rounded >= 75) return 'B-Tier ✨'
  if (rounded >= 50) return 'C-Tier 🎮'
  return 'D-Tier 📈'
}
