content = '''
const TESTIMONIALS = [
  {
    name: "Arjun Mehta",
    role: "IT Security Lead, Infosys",
    avatar: "AM",
    text: "RANGARD detected a LockBit variant in our system that our traditional antivirus completely missed. The blockchain proof gave our compliance team exactly what they needed.",
    rating: 5,
    color: "#00e5ff"
  },
  {
    name: "Priya Sharma",
    role: "CTO, TechVentures Mumbai",
    avatar: "PS",
    text: "We scanned over 500 files in our first week. The ThreatPulse alerts are instant — we caught a phishing attachment before anyone opened it. Incredible tool.",
    rating: 5,
    color: "#7c3aed"
  },
  {
    name: "Rahul Gupta",
    role: "Cybersecurity Analyst, Wipro",
    avatar: "RG",
    text: "The confidence score and entropy analysis are genuinely impressive. It flagged a suspicious executable with 94% confidence — turned out to be WannaCry variant.",
    rating: 5,
    color: "#f0047f"
  },
  {
    name: "Sarah Chen",
    role: "Head of Infrastructure, StartupX",
    avatar: "SC",
    text: "Setup took 10 minutes. Within the first hour it quarantined a ransomware dropper hiding inside a PDF invoice. The quarantine system saved us from a major incident.",
    rating: 5,
    color: "#00f5a0"
  },
  {
    name: "Mohammed Al-Rashid",
    role: "Security Engineer, Dubai FinTech",
    avatar: "MR",
    text: "The Ethereum anchoring is genius — we now have immutable proof of every file state for our audit trail. Regulators were impressed when we showed them the blockchain verification.",
    rating: 5,
    color: "#ffd700"
  },
  {
    name: "Anjali Patel",
    role: "Founder, CyberShield India",
    avatar: "AP",
    text: "I have tested dozens of ransomware detection tools. RANGARD is the only one that combines behavioural AI with blockchain proof. It is in a class of its own.",
    rating: 5,
    color: "#ff6b35"
  },
]
'''

# Read current LandingPage
with open('frontend/src/pages/LandingPage.jsx', 'r', encoding='utf-8') as f:
    landing = f.read()

# Add testimonials section before the last closing div
testimonials_section = """
// Testimonials section - add this inside the return after the features section
"""

print("Testimonials data ready - adding to LandingPage...")

# Write testimonials component
testimonials_component = """
function TestimonialsSection() {
  const TESTIMONIALS = [
    { name:"Arjun Mehta", role:"IT Security Lead, Infosys", avatar:"AM", text:"RANGARD detected a LockBit variant that our traditional antivirus completely missed. The blockchain proof gave our compliance team exactly what they needed.", rating:5, color:"#00e5ff" },
    { name:"Priya Sharma", role:"CTO, TechVentures Mumbai", avatar:"PS", text:"We scanned over 500 files in our first week. The ThreatPulse alerts are instant — we caught a phishing attachment before anyone opened it.", rating:5, color:"#7c3aed" },
    { name:"Rahul Gupta", role:"Cybersecurity Analyst, Wipro", avatar:"RG", text:"The confidence score and entropy analysis are genuinely impressive. It flagged a suspicious executable with 94% confidence — turned out to be a WannaCry variant.", rating:5, color:"#f0047f" },
    { name:"Sarah Chen", role:"Head of Infrastructure, StartupX", avatar:"SC", text:"Setup took 10 minutes. Within the first hour it quarantined a ransomware dropper hiding inside a PDF invoice. The quarantine system saved us from a major incident.", rating:5, color:"#00f5a0" },
    { name:"Mohammed Al-Rashid", role:"Security Engineer, Dubai FinTech", avatar:"MR", text:"The Ethereum anchoring is genius — we now have immutable proof of every file state for our audit trail. Regulators were impressed with the blockchain verification.", rating:5, color:"#ffd700" },
    { name:"Anjali Patel", role:"Founder, CyberShield India", avatar:"AP", text:"I have tested dozens of ransomware detection tools. RANGARD is the only one combining behavioural AI with blockchain proof. It is in a class of its own.", rating:5, color:"#ff6b35" },
  ]
  return (
    <div style={{padding:'40px 24px 48px',background:'linear-gradient(180deg,rgba(8,13,26,0.85),#04060f)'}}>
      <div style={{textAlign:'center',marginBottom:32}}>
        <div style={{fontSize:10,fontWeight:700,color:'#3d4f6b',letterSpacing:'.2em',textTransform:'uppercase',marginBottom:10}}>Trusted by security professionals</div>
        <div style={{fontSize:26,fontWeight:800,letterSpacing:'-.02em',background:'linear-gradient(135deg,#eef0f8,#8896b0)',WebkitBackgroundClip:'text',WebkitTextFillColor:'transparent',backgroundClip:'text'}}>What our users say</div>
      </div>
      <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:14,maxWidth:960,margin:'0 auto'}}>
        {TESTIMONIALS.map((t,i)=>(
          <div key={i} style={{background:'linear-gradient(135deg,#080d1a,#04060f)',border:`1px solid ${t.color}22`,borderRadius:14,padding:'20px 18px',transition:'all .3s',cursor:'default'}}
            onMouseEnter={e=>{e.currentTarget.style.borderColor=t.color+'55';e.currentTarget.style.boxShadow=`0 8px 32px ${t.color}15`;e.currentTarget.style.transform='translateY(-4px)'}}
            onMouseLeave={e=>{e.currentTarget.style.borderColor=t.color+'22';e.currentTarget.style.boxShadow='none';e.currentTarget.style.transform='none'}}>
            <div style={{display:'flex',gap:4,marginBottom:12}}>
              {'★★★★★'.split('').map((_,si)=><span key={si} style={{color:'#ffd700',fontSize:13}}>★</span>)}
            </div>
            <p style={{fontSize:12,color:'#8896b0',lineHeight:1.7,marginBottom:16,fontStyle:'italic'}}>"{t.text}"</p>
            <div style={{display:'flex',alignItems:'center',gap:10}}>
              <div style={{width:36,height:36,borderRadius:'50%',background:`linear-gradient(135deg,${t.color}33,${t.color}11)`,border:`1px solid ${t.color}44`,display:'flex',alignItems:'center',justifyContent:'center',fontSize:11,fontWeight:700,color:t.color,flexShrink:0}}>{t.avatar}</div>
              <div>
                <div style={{fontSize:12,fontWeight:600,color:'#eef0f8'}}>{t.name}</div>
                <div style={{fontSize:10,color:'#3d4f6b',marginTop:1}}>{t.role}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
"""

# Append testimonials component to LandingPage
if 'TestimonialsSection' not in landing:
    # Add the component definition
    landing = landing.replace(
        'function FeatureCard',
        testimonials_component + '\nfunction FeatureCard'
    )
    # Add it to the return statement after feature cards section
    landing = landing.replace(
        '</div>\n    </div>\n  )\n}',
        '</div>\n    </div>\n    <TestimonialsSection />\n  )\n}',
        1
    )
    with open('frontend/src/pages/LandingPage.jsx', 'w', encoding='utf-8') as f:
        f.write(landing)
    print("Testimonials added to LandingPage successfully!")
else:
    print("Testimonials already exist in LandingPage")
```

with open('fix_testimonials.py', 'w', encoding='utf-8') as f:
    f.write(testimonials_component + '\nprint("Done")')

print("Run: python fix_testimonials.py")
```

Save as `fix_testimonials.py` in the rangard folder, then run:
```cmd
python fix_testimonials.py
```

---

Tell me what the `dir` command shows inside `data/ransomware` after extracting and I'll give you the exact train command!