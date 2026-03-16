
// src/pages/LandingPage.jsx — RANGARD Home Page
import { useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'

const FEATURES = [
  { num:'01', cat:'Detection',  icon:'🧠', title:'AI Behavioural Analysis', chips:['Zero-day threats','Real-time','High accuracy'],   foot:'Powered by ML',         bar:'92%', grad:'rgba(0,229,255,0.16)',   border:'rgba(0,229,255,0.14)',   hoverBorder:'rgba(0,229,255,0.45)',   glow:'0 12px 44px rgba(0,229,255,0.12)',   chip:{background:'rgba(0,229,255,0.08)',color:'#00e5ff',border:'1px solid rgba(0,229,255,0.18)'}, bar_color:'linear-gradient(90deg,#00e5ff,rgba(0,229,255,0.2))',   arrow:'#00e5ff' },
  { num:'02', cat:'Versioning', icon:'⛓️', title:'Blockchain File Proof',   chips:['Immutable proof','Ethereum','Verifiable'],        foot:'On-chain anchoring',    bar:'78%', grad:'rgba(124,58,237,0.16)',  border:'rgba(124,58,237,0.14)',  hoverBorder:'rgba(124,58,237,0.45)',  glow:'0 12px 44px rgba(124,58,237,0.12)',  chip:{background:'rgba(124,58,237,0.08)',color:'#a78bfa',border:'1px solid rgba(124,58,237,0.18)'}, bar_color:'linear-gradient(90deg,#a78bfa,rgba(124,58,237,0.2))',  arrow:'#a78bfa' },
  { num:'03', cat:'Containment',icon:'🔒', title:'Instant Quarantine',       chips:['Encrypted isolation','1-click restore','Instant'], foot:'Zero spread guarantee', bar:'99%', grad:'rgba(240,4,127,0.16)',   border:'rgba(240,4,127,0.14)',   hoverBorder:'rgba(240,4,127,0.45)',   glow:'0 12px 44px rgba(240,4,127,0.12)',   chip:{background:'rgba(240,4,127,0.08)',color:'#f0047f',border:'1px solid rgba(240,4,127,0.18)'}, bar_color:'linear-gradient(90deg,#f0047f,rgba(240,4,127,0.2))',   arrow:'#f0047f' },
  { num:'04', cat:'Alerts',     icon:'📡', title:'ThreatPulse',              chips:['Instant alerts','Full details','Dashboard link'],  foot:'Never miss a threat',   bar:'85%', grad:'rgba(0,245,160,0.14)',   border:'rgba(0,245,160,0.14)',   hoverBorder:'rgba(0,245,160,0.45)',   glow:'0 12px 44px rgba(0,245,160,0.12)',   chip:{background:'rgba(0,245,160,0.08)',color:'#00f5a0',border:'1px solid rgba(0,245,160,0.18)'}, bar_color:'linear-gradient(90deg,#00f5a0,rgba(0,245,160,0.2))',   arrow:'#00f5a0' },
  { num:'05', cat:'Results',    icon:'🎯', title:'Live Scan Results',         chips:['Confidence ring','Pattern list','TX proof'],       foot:'Animated in real time',  bar:'88%', grad:'rgba(255,215,0,0.14)',   border:'rgba(255,215,0,0.14)',   hoverBorder:'rgba(255,215,0,0.45)',   glow:'0 12px 44px rgba(255,215,0,0.1)',    chip:{background:'rgba(255,215,0,0.08)',color:'#ffd700',border:'1px solid rgba(255,215,0,0.18)'}, bar_color:'linear-gradient(90deg,#ffd700,rgba(255,215,0,0.2))',   arrow:'#ffd700' },
  { num:'06', cat:'Reporting',  icon:'📊', title:'Threat Reports',            chips:['PDF export','Radar charts','Full history'],         foot:'Complete audit trail',   bar:'74%', grad:'rgba(255,107,53,0.14)',  border:'rgba(255,107,53,0.14)',  hoverBorder:'rgba(255,107,53,0.45)',  glow:'0 12px 44px rgba(255,107,53,0.1)',   chip:{background:'rgba(255,107,53,0.08)',color:'#ff6b35',border:'1px solid rgba(255,107,53,0.18)'}, bar_color:'linear-gradient(90deg,#ff6b35,rgba(255,107,53,0.2))',  arrow:'#ff6b35' },
]
const THREAT = [
  {label:'Clean',   pct:'83%',icon:'🟢',bg:'rgba(0,245,160,0.07)',  bc:'rgba(0,245,160,0.16)',  hov:'rgba(0,245,160,0.18)',  glow:'rgba(0,245,160,0.3)',  color:'#00f5a0'},
  {label:'Low',     pct:'8%', icon:'🔵',bg:'rgba(0,229,255,0.07)',  bc:'rgba(0,229,255,0.16)',  hov:'rgba(0,229,255,0.18)',  glow:'rgba(0,229,255,0.3)',  color:'#00e5ff'},
  {label:'Medium',  pct:'5%', icon:'🟡',bg:'rgba(255,215,0,0.07)',  bc:'rgba(255,215,0,0.16)',  hov:'rgba(255,215,0,0.18)',  glow:'rgba(255,215,0,0.25)', color:'#ffd700'},
  {label:'High',    pct:'3%', icon:'🟠',bg:'rgba(255,107,53,0.07)', bc:'rgba(255,107,53,0.16)', hov:'rgba(255,107,53,0.18)', glow:'rgba(255,107,53,0.25)',color:'#ff6b35'},
  {label:'Critical',pct:'1%', icon:'🔴',bg:'rgba(240,4,127,0.07)',  bc:'rgba(240,4,127,0.16)',  hov:'rgba(240,4,127,0.18)',  glow:'rgba(240,4,127,0.3)',  color:'#f0047f'},
]
const LETTERS = ['R','A','N','G','A','R','D']
const GRADS = [160,153,146,138,146,153,160]

export default function LandingPage() {
  const cvs = useRef(null)
  const raf = useRef(null)

  useEffect(() => {
    const canvas = cvs.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const resize = () => { canvas.width = canvas.offsetWidth; canvas.height = canvas.offsetHeight }
    resize()
    window.addEventListener('resize', resize)
    const stars = Array.from({length:140},()=>({
      x:Math.random()*canvas.width, y:Math.random()*canvas.height,
      r:Math.random()*1.4+.3, speed:Math.random()*.32+.05,
      opacity:Math.random()*.5+.12,
      hue:[195,270,330][Math.floor(Math.random()*3)]
    }))
    const draw = () => {
      ctx.clearRect(0,0,canvas.width,canvas.height)
      stars.forEach(s => {
        s.y -= s.speed
        if (s.y<0){s.y=canvas.height;s.x=Math.random()*canvas.width}
        ctx.beginPath(); ctx.arc(s.x,s.y,s.r,0,Math.PI*2)
        ctx.fillStyle = `hsla(${s.hue},88%,72%,${s.opacity})`; ctx.fill()
      })
      raf.current = requestAnimationFrame(draw)
    }
    draw()
    return () => { cancelAnimationFrame(raf.current); window.removeEventListener('resize',resize) }
  }, [])

  return (
    <div style={{background:'#04060f',minHeight:'100vh'}}>
      <style>{`
        @keyframes glowpulse{0%,100%{opacity:.5}50%{opacity:1}}
        @keyframes orbit{to{transform:rotate(360deg)}}
        @keyframes corepulse{0%,100%{opacity:.5;transform:scale(.93)}50%{opacity:1;transform:scale(1.07)}}
        .rgl{display:inline-block;font-size:88px;font-weight:900;line-height:1;cursor:default;
          transition:transform .32s cubic-bezier(.34,1.7,.64,1),filter .32s;letter-spacing:.04em}
        .rgl:hover{transform:translateY(-14px) scale(1.22) rotate(-3deg);
          filter:drop-shadow(0 0 22px rgba(0,229,255,1)) drop-shadow(0 0 44px rgba(124,58,237,.8)) brightness(1.4)}
        .fcard{border-radius:14px;overflow:hidden;cursor:default;
          transition:transform .3s cubic-bezier(.34,1.2,.64,1),border-color .3s,box-shadow .3s;
          background:linear-gradient(135deg,#080d1a,#04060f)}
        .fcard:hover{transform:translateY(-7px) scale(1.015)}
      `}</style>

      {/* Hero */}
      <div style={{position:'relative',overflow:'hidden',minHeight:560,display:'flex',flexDirection:'column',alignItems:'center',padding:'50px 20px 38px'}}>
        <canvas ref={cvs} style={{position:'absolute',inset:0,width:'100%',height:'100%',pointerEvents:'none',zIndex:0}}/>
        <div style={{position:'absolute',inset:0,zIndex:1,pointerEvents:'none',
          backgroundImage:'linear-gradient(rgba(0,229,255,0.032) 1px,transparent 1px),linear-gradient(90deg,rgba(0,229,255,0.032) 1px,transparent 1px)',
          backgroundSize:'52px 52px',WebkitMaskImage:'radial-gradient(ellipse 90% 80% at 50% 50%,black 5%,transparent 78%)',maskImage:'radial-gradient(ellipse 90% 80% at 50% 50%,black 5%,transparent 78%)'}}/>
        <div style={{position:'absolute',inset:0,zIndex:1,pointerEvents:'none',
          background:'radial-gradient(ellipse 70% 50% at 50% -5%,rgba(0,229,255,0.07) 0%,transparent 55%),radial-gradient(ellipse 50% 40% at 85% 100%,rgba(124,58,237,0.06) 0%,transparent 50%)'}}/>

        {/* RANGARD title */}
        <motion.div initial={{opacity:0,y:28}} animate={{opacity:1,y:0}} transition={{duration:.8,ease:[.22,1,.36,1]}}
          style={{position:'relative',zIndex:10,marginBottom:10}}>
          <div style={{position:'absolute',inset:-24,background:'radial-gradient(ellipse 80% 60% at 50% 50%,rgba(0,229,255,0.09),rgba(124,58,237,0.06),transparent 70%)',animation:'glowpulse 4s ease-in-out infinite',pointerEvents:'none'}}/>
          <div style={{display:'flex',alignItems:'center',gap:3}}>
            {LETTERS.map((l,i)=>(
              <span key={i} className="rgl" style={{
                WebkitTextFillColor:'transparent',backgroundClip:'text',WebkitBackgroundClip:'text',
                backgroundImage:`linear-gradient(${GRADS[i]}deg,#ffffff 0%,#00e5ff ${22+i*5}%,#7c3aed ${52+i*3}%,#f0047f 100%)`,
                filter:'drop-shadow(0 0 36px rgba(0,229,255,0.25)) drop-shadow(0 0 72px rgba(124,58,237,0.16))'
              }}>{l}</span>
            ))}
          </div>
        </motion.div>

        {/* Tagline */}
        <motion.div initial={{opacity:0}} animate={{opacity:1}} transition={{delay:.42,duration:.6}}
          style={{position:'relative',zIndex:10,marginBottom:28,display:'flex',alignItems:'center',gap:10}}>
          <span style={{width:32,height:1,background:'linear-gradient(90deg,transparent,rgba(0,229,255,0.5))',display:'inline-block'}}/>
          <span style={{fontSize:12,letterSpacing:'.22em',textTransform:'uppercase',color:'#8896b0'}}>Stop ransomware before it strikes</span>
          <span style={{width:32,height:1,background:'linear-gradient(90deg,rgba(0,229,255,0.5),transparent)',display:'inline-block'}}/>
        </motion.div>

        {/* Orbit orb */}
        <motion.div initial={{opacity:0,scale:.8}} animate={{opacity:1,scale:1}} transition={{delay:.52,duration:.7}}
          style={{position:'relative',width:112,height:112,marginBottom:24,zIndex:10}}>
          {[[0,'rgba(0,229,255,0.18)',8,'normal'],[9,'rgba(124,58,237,0.14)',6,'reverse'],[18,'rgba(240,4,127,0.1)',10,'normal']].map(([ins,bc,dur,dir],i)=>(
            <div key={i} style={{position:'absolute',inset:ins,borderRadius:'50%',border:`1px solid ${bc}`,animation:`orbit ${dur}s linear infinite ${dir==='reverse'?'reverse':''}`}}/>
          ))}
          <div style={{position:'absolute',inset:26,borderRadius:'50%',background:'radial-gradient(circle,rgba(0,229,255,0.25),rgba(124,58,237,0.15),transparent)',animation:'corepulse 3s ease-in-out infinite'}}/>
          {[['#00e5ff',7,4,56],['#7c3aed',5,6,48],['#f0047f',4,5,52]].map(([color,size,dur,r],i)=>(
            <div key={i} style={{position:'absolute',width:size,height:size,borderRadius:'50%',background:color,boxShadow:`0 0 ${size*2}px ${color}`,top:'50%',left:'50%',marginTop:-size/2,marginLeft:-size/2,transformOrigin:`${-r+size/2}px 0`,animation:`orbit ${dur}s linear infinite`}}/>
          ))}
        </motion.div>

        {/* Threat meter */}
        <motion.div initial={{opacity:0,y:14}} animate={{opacity:1,y:0}} transition={{delay:.62,duration:.55}}
          style={{display:'flex',width:'100%',maxWidth:480,gap:0,zIndex:10,marginBottom:26}}>
          {THREAT.map((t,i)=>(
            <div key={i} style={{flex:1,padding:'10px 5px',textAlign:'center',background:t.bg,border:`1px solid ${t.bc}`,
              borderRadius:i===0?'10px 0 0 10px':i===4?'0 10px 10px 0':0,cursor:'default',transition:'all .22s'}}
              onMouseEnter={e=>{const el=e.currentTarget;el.style.background=t.hov;el.style.borderColor=t.color;el.style.boxShadow=`0 0 16px ${t.glow}`;el.style.transform='scaleY(1.09)';el.style.zIndex='2'}}
              onMouseLeave={e=>{const el=e.currentTarget;el.style.background=t.bg;el.style.borderColor=t.bc;el.style.boxShadow='none';el.style.transform='none';el.style.zIndex='1'}}>
              <div style={{fontSize:14,marginBottom:2}}>{t.icon}</div>
              <div style={{fontSize:9,fontWeight:700,letterSpacing:'.08em',textTransform:'uppercase',color:t.color}}>{t.label}</div>
              <div style={{fontSize:16,fontWeight:800,color:t.color,marginTop:1}}>{t.pct}</div>
            </div>
          ))}
        </motion.div>

        {/* CTAs */}
        <motion.div initial={{opacity:0,y:10}} animate={{opacity:1,y:0}} transition={{delay:.72,duration:.5}}
          style={{display:'flex',gap:12,justifyContent:'center',zIndex:10}}>
          <Link to="/upload"><button className="btn-primary" style={{fontSize:14,padding:'13px 32px'}}>Start scanning free →</button></Link>
          <Link to="/dashboard"><button className="btn-secondary" style={{fontSize:13,padding:'13px 26px'}}>View live demo</button></Link>
        </motion.div>
      </div>

      {/* Feature cards */}
      <div style={{padding:'28px 22px 40px',background:'linear-gradient(180deg,#04060f,rgba(8,13,26,.85))'}}>
        <div style={{textAlign:'center',fontSize:10,fontWeight:700,color:'#3d4f6b',letterSpacing:'.2em',textTransform:'uppercase',marginBottom:20}}>Platform capabilities</div>
        <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:12,maxWidth:960,margin:'0 auto'}}>
          {FEATURES.map((f,i)=>(
            <motion.div key={i} initial={{opacity:0,y:24}} animate={{opacity:1,y:0}}
              transition={{delay:.07*i,duration:.48,ease:[.22,1,.36,1]}}
              className="fcard" style={{border:`1px solid ${f.border}`}}
              onMouseEnter={e=>{e.currentTarget.style.borderColor=f.hoverBorder;e.currentTarget.style.boxShadow=f.glow}}
              onMouseLeave={e=>{e.currentTarget.style.borderColor=f.border;e.currentTarget.style.boxShadow='none'}}>
              <div style={{padding:'20px 18px 15px',position:'relative',zIndex:1}}>
                <div style={{display:'flex',alignItems:'center',gap:12,marginBottom:12}}>
                  <div style={{width:46,height:46,borderRadius:13,display:'flex',alignItems:'center',justifyContent:'center',fontSize:21,flexShrink:0,background:`linear-gradient(135deg,${f.grad},rgba(0,0,0,0.05))`,border:`1px solid ${f.border}`}}>{f.icon}</div>
                  <div>
                    <div style={{fontSize:9,fontWeight:700,letterSpacing:'.12em',textTransform:'uppercase',color:f.chip.color,opacity:.5,marginBottom:3}}>{f.num} · {f.cat}</div>
                    <div style={{fontSize:13.5,fontWeight:700,color:'#eef0f8',letterSpacing:'-.01em',lineHeight:1.25}}>{f.title}</div>
                  </div>
                </div>
                <div style={{height:3,background:'rgba(255,255,255,0.05)',borderRadius:2,overflow:'hidden',marginBottom:11}}>
                  <motion.div initial={{width:0}} whileInView={{width:f.bar}} viewport={{once:true}}
                    transition={{duration:1.1,ease:[.22,1,.36,1],delay:.08*i}}
                    style={{height:'100%',borderRadius:2,background:f.bar_color}}/>
                </div>
                <div style={{display:'flex',gap:5,flexWrap:'wrap'}}>
                  {f.chips.map((c,ci)=><span key={ci} style={{...f.chip,padding:'3px 9px',borderRadius:20,fontSize:10,fontWeight:600}}>{c}</span>)}
                </div>
              </div>
              <div style={{padding:'10px 18px',borderTop:'1px solid #162040',display:'flex',alignItems:'center',justifyContent:'space-between'}}>
                <span style={{fontSize:10,color:'#3d4f6b'}}>{f.foot}</span>
                <span style={{fontSize:13,color:f.arrow,transition:'transform .22s'}} className="fc-arrow">→</span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
