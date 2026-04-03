// src/store/scansStore.js
import { create } from 'zustand'
import { scansApi } from '../services/api'

export const useScansStore = create((set, get) => ({
  scans: [],
  analytics: null,
  loading: false,
  uploading: false,
  uploadProgress: 0,

  fetchScans: async () => {
    set({ loading: true })
    try {
      const res = await scansApi.list()
      set({ scans: res.data })
    } catch (e) {
      console.error('fetchScans:', e)
    } finally {
      set({ loading: false })
    }
  },

  fetchAnalytics: async () => {
    try {
      const res = await scansApi.analytics()
      set({ analytics: res.data })
    } catch (e) {
      console.error('fetchAnalytics:', e)
    }
  },

  uploadFile: async (file, onProgress) => {
    set({ uploading: true, uploadProgress: 0 })
    try {
      const res = await scansApi.upload(file, (pct) => {
        set({ uploadProgress: pct })
      })
      // Prepend the new scan to the list
      const newScan = {
        id: res.data.scan_id,
        filename: file.name,
        threat_level: res.data.threat_level,
        confidence: res.data.confidence,
        status: 'complete',
        created_at: new Date().toISOString(),
        is_quarantined: res.data.quarantined,
        has_blockchain: !!res.data.blockchain_tx,
      }
      set((state) => ({ scans: [newScan, ...state.scans] }))
      return res.data
    } finally {
      set({ uploading: false, uploadProgress: 0 })
    }
  },

  downloadReport: async (scanId, filename) => {
    const res = await scansApi.downloadReport(scanId)
    const url = URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }))
    const a = document.createElement('a')
    a.href = url
    a.download = `rangard-report-${filename}.pdf`
    a.click()
    URL.revokeObjectURL(url)
  },
}))
