// src/components/Navbar.jsx — RANGARD
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuthStore } from '../store/authStore'

const LINKS = [
  { path: '/',          label: 'Home' },
  { path: '/dashboard', label: 'Dashboard' },
  { path: '/upload',    label: 'Scan File' },
  { path: '/reports',   label: 'Reports' },
]

export default function Navbar() {
  const location = useLocation()
  const navigate  = useNavigate()
  const { user, logout } = useAuthStore()
  const handleLogout = () => { logout(); navigate('/') }

  return (
    <motion.nav
      initial={{ y: -56, opacity: 0 }}
      animate={{ y: 0,   opacity: 1 }}
      transition={{ duration: 0.5, ease: [0.22,1,0.36,1] }}
      style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 1000,
        background: 'rgba(4,6,15,0.97)',
        borderBottom: '1px solid #162040',
        backdropFilter: 'blur(24px)',
        WebkitBackdropFilter: 'blur(24px)',
        height: 56, display: 'flex', alignItems: 'center',
        justifyContent: 'space-between', padding: '0 24px',
      }}
    >
      {/* Logo */}
      <Link to="/" style={{ display:'flex', alignItems:'center', gap:9, textDecoration:'none' }}>
        <svg width="30" height="30" viewBox="0 0 56 56">
          <defs>
            <linearGradient id="navShieldGrad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%"   stopColor="#00e5ff"/>
              <stop offset="50%"  stopColor="#7c3aed"/>
              <stop offset="100%" stopColor="#f0047f"/>
            </linearGradient>
          </defs>
          <polygon points="28,4 46,14 46,38 28,50 10,38 10,14" fill="url(#navShieldGrad)" opacity=".9"/>
          <polygon points="28,4 46,14 46,38 28,50 10,38 10,14" fill="none" stroke="rgba(0,229,255,0.45)" strokeWidth="1.1"/>
          <polygon points="28,12 38,18 38,36 28,44 18,36 18,18" fill="rgba(4,6,15,0.55)" stroke="rgba(255,255,255,0.07)" strokeWidth="1"/>
          <rect x="22" y="26" width="12" height="10" rx="2" fill="white" opacity=".9"/>
          <path d="M24 26 L24 22.5 C24 19.5 32 19.5 32 22.5 L32 26" fill="none" stroke="white" strokeWidth="2.1" strokeLinecap="round" opacity=".88"/>
          <circle cx="28" cy="31" r="2" fill="url(#navShieldGrad)"/>
        </svg>
        <span style={{
          fontSize: 15, fontWeight: 900, letterSpacing: '.12em',
          background: 'linear-gradient(135deg,#00e5ff,#7c3aed)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
        }}>RANGARD</span>
      </Link>

      {/* Nav links */}
      <div style={{ display:'flex', gap:2 }}>
        {LINKS.map(({ path, label }) => {
          const active = location.pathname === path
          return (
            <Link key={path} to={path} style={{ textDecoration:'none', position:'relative' }}>
              <span style={{
                display: 'inline-block', padding: '6px 13px', borderRadius: 8,
                fontSize: 11.5, fontWeight: 500, letterSpacing: '.02em',
                color: active ? '#00e5ff' : '#8896b0',
                background: active ? 'rgba(0,229,255,0.07)' : 'transparent',
                border: active ? '1px solid rgba(0,229,255,0.14)' : '1px solid transparent',
                transition: 'all .2s', cursor: 'pointer',
              }}>
                {label}
              </span>
            </Link>
          )
        })}
      </div>

      {/* Right side */}
      <div style={{ display:'flex', alignItems:'center', gap:14 }}>
        <div style={{ display:'flex', alignItems:'center', gap:5, fontSize:10.5, color:'#00f5a0',
          background:'rgba(0,245,160,0.07)', border:'1px solid rgba(0,245,160,0.16)',
          borderRadius:20, padding:'5px 11px' }}>
          <span className="status-dot" style={{ flexShrink:0 }}/>
          System active
        </div>
        {user && (
          <span
            onClick={handleLogout}
            style={{ fontSize:11, color:'#3d4f6b', cursor:'pointer', transition:'color .2s' }}
            onMouseEnter={e=>e.target.style.color='#f0047f'}
            onMouseLeave={e=>e.target.style.color='#3d4f6b'}
          >
            Sign out
          </span>
        )}
      </div>
    </motion.nav>
  )
}
