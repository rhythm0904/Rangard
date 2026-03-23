// src/store/authStore.js
// Global authentication state using Zustand.
// Persists token to localStorage so users stay logged in on refresh.

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set) => ({
       token: localStorage.getItem("token") || null,
user: null,
isAuthenticated: !!localStorage.getItem("token"),
setAuth: (token, user) => {
  localStorage.setItem("token", token);

  set({
    token,
    user,
    isAuthenticated: true   // 🔥 ADD THIS (MAIN FIX)
  });
},

      setUser: (user) => set({ user }),

      logout: () =>
        set({ token: null, user: null, isAuthenticated: false }),
    }),
    {
      name: 'rangard-auth', // localStorage key
      partialize: (state) => ({ token: state.token, user: state.user }),
    }
  )
)
