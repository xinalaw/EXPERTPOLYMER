export interface User {
  id: number
  username: string
  first_name?: string | null
  last_name?: string | null
  email: string
  organization?: string | null
  role: string
  director_id?: number | null
}

export interface AnalysisResult {
  id: number
  user_id: number
  original_filename: string
  image_path?: string | null
  processed_image_path?: string | null
  result: string
  confidence?: number | null
  width?: number | null
  height?: number | null
  created_at: string
  result_data?: {
    particles_detected?: number
    processing_time_ms?: number
    model?: { name?: string; version?: string; type?: string }
    expert?: {
      score?: number
      verdict?: string
      conclusion?: string
      inputs?: { sphericity?: number; smoothness?: number; uniformity?: number }
    }
    composition?: Record<string, number>
    avg_circularity?: number
    dispersity?: number
    size_stats?: { min_px?: number; max_px?: number; mean_px?: number; std_px?: number }
    detections?: readonly { label?: string; confidence?: number }[]
  } | null
}
