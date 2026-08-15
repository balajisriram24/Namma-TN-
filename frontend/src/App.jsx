import React, {useEffect, useMemo, useRef, useState} from "react";
import {AlertTriangle, ArrowRight, Bot, CheckCircle2, ChevronRight, CircleDot, Droplets, FileText, Lightbulb, LogOut, MapPin, MessageCircle, RefreshCw, Route, Search, Send, Trash2, Waves, User} from "lucide-react";
import {analyzeMessage, createComplaint, getComplaint, getComplaints, updateComplaint, register, login, me, myComplaints} from "./api";

const categories = {
  water: {label: "Water", icon: Droplets, color: "blue", topic: "Water supply, leaks, contamination, or blocked pipelines in your area."},
  road: {label: "Road", icon: Route, color: "amber", topic: "Damaged roads, potholes, road cracks, or unsafe traffic conditions."},
  drainage: {label: "Drainage", icon: Waves, color: "purple", topic: "Blocked drains, waterlogging, overflowing drainage lines, or poor drainage flow."},
  waste: {label: "Waste", icon: Trash2, color: "green", topic: "Garbage dumping, overflowing bins, unclean public spaces, or waste collection problems."},
  streetlight: {label: "Streetlight", icon: Lightbulb, color: "gold", topic: "Non-working streetlights, dark roads, or unsafe evening lighting conditions."},
  flooding: {label: "Flooding", icon: Waves, color: "cyan", topic: "Flooded streets, water accumulation after rain, or blocked stormwater channels."}
};

function Header({page, setPage, user, onLogout}) {
  const [showProfile, setShowProfile] = useState(false);
  
  return <header className="topbar">
    <div className="brand"><div className="brand-mark">N</div><div><strong>NammaTN</strong><span>AI Civic Connect</span></div></div>
    <nav>
      {user && user.role === "admin" ? (
        <button className={page==="admin" ? "active" : ""} onClick={()=>setPage("admin")}>Authority Dashboard</button>
      ) : (
        <button className={page==="citizen" ? "active" : ""} onClick={()=>setPage("citizen")}>Citizen</button>
      )}
    </nav>
    <div className="auth-actions">
      {user ? (
        <div className="profile-menu">
          <button className="profile-button" onClick={() => setShowProfile(!showProfile)}>
            <div className="profile-avatar">{user.name?.charAt(0).toUpperCase() || "U"}</div>
          </button>
          {showProfile && (
            <div className="profile-dropdown">
              <div className="profile-header">
                <div className="profile-avatar-large">{user.name?.charAt(0).toUpperCase() || "U"}</div>
                <div className="profile-info">
                  <div className="profile-name">{user.name}</div>
                  <div className="profile-email">{user.email}</div>
                  <div className="profile-role">{user.role === "admin" ? "👨‍💼 Administrator" : "👤 Citizen"}</div>
                </div>
              </div>
              <div className="profile-divider"></div>
              <button className="profile-logout" onClick={() => { onLogout(); setShowProfile(false); }}>
                <LogOut size={16} /> Logout
              </button>
            </div>
          )}
        </div>
      ) : (
        <>
          <button className="link" onClick={()=>setPage("login")}>Login</button>
          <button className="link" onClick={()=>setPage("register")}>Register</button>
        </>
      )}
    </div>
  </header>
}

function Chat({user, onRequireAuth}) {
  const [messages,setMessages] = useState([{from:"bot", text:"Vanakkam! 👋 Tell me your civic problem in Tamil, Tanglish, or English."}]);
  const [text,setText] = useState("");
  const [analysis,setAnalysis] = useState(null);
  const [details,setDetails] = useState({district:"",area:"",duration:""});
  const [busy,setBusy] = useState(false);
  const [created,setCreated] = useState(null);
  const [proofImage,setProofImage] = useState("");
  const [selectedTopic, setSelectedTopic] = useState("water");
  const [cameraOpen, setCameraOpen] = useState(false);
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  function handleProofImage(file){
    if(!file) return;
    if(!file.type.startsWith("image/")){
      setMessages(m=>[...m,{from:"bot",text:"Please upload a valid image file."}]);
      return;
    }
    const reader = new FileReader();
    reader.onload = () => setProofImage(String(reader.result));
    reader.readAsDataURL(file);
  }

  async function openCamera(){
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setMessages(m=>[...m,{from:"bot",text:"Camera is not supported in this browser. Please upload a file instead."}]);
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
        audio: false
      });
      streamRef.current = stream;
      setCameraOpen(true);
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
    } catch (error) {
      setMessages(m=>[...m,{from:"bot",text:"Camera access was blocked. Please allow camera permission or upload a file."}]);
    }
  }

  function closeCamera(){
    const stream = streamRef.current;
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setCameraOpen(false);
  }

  function captureCameraPhoto(){
    const video = videoRef.current;
    if (!video) return;
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth || 1280;
    canvas.height = video.videoHeight || 720;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    setProofImage(canvas.toDataURL("image/jpeg", 0.9));
    closeCamera();
  }

  async function send(){
    const message=text.trim();
    if(!message || busy) return;
    setMessages(m=>[...m,{from:"user",text:message}]);
    setText(""); setBusy(true); setAnalysis(null);
    try{
      const result=await analyzeMessage(message);
      setAnalysis({message,result});
      setMessages(m=>[...m,{from:"bot",text:`I understand this as ${categories[result.category]?.label || "Other"} with ${result.severity} priority. Please provide your district and area below.`}]);
    }catch(e){setMessages(m=>[...m,{from:"bot",text:e.message}] )}
    finally{setBusy(false)}
  }

  async function submit(){
    if(!analysis || !details.district.trim() || !details.area.trim()) return;
    if(!user){
      setMessages(m=>[...m,{from:"bot", text:"Please log in or register before submitting a complaint."}]);
      onRequireAuth?.();
      return;
    }
    setBusy(true);
    try{
      const c=await createComplaint({
        message:analysis.message, category:analysis.result.category, severity:analysis.result.severity,
        ...details,
        proof_image: proofImage
      });
      setCreated(c);
      setMessages(m=>[...m,{from:"bot",text:`✅ Complaint created successfully. Your ID is ${c.complaint_id}. Save this ID to track your complaint.`}]);
      setAnalysis(null); setDetails({district:"",area:"",duration:""}); setProofImage("");
    }catch(e){setMessages(m=>[...m,{from:"bot",text:e.message}])}
    finally{setBusy(false)}
  }

  return <div className="chat-layout">
    <section className="chat-card">
      <div className="chat-head"><div className="bot-avatar"><Bot size={19}/></div><div><b>TN Civic Assistant</b><span>AI-powered · Online</span></div><div className="online-dot"/></div>
      <div className="messages">{messages.map((m,i)=><div key={i} className={`message ${m.from}`}>{m.text}</div>)}{busy&&<div className="message bot typing">Thinking…</div>}</div>
      {analysis && <div className="detail-panel">
        <div className="panel-title">Complete your report</div>
        <div className="ai-summary"><span>AI category</span><b>{categories[analysis.result.category]?.label || "Other"} · {analysis.result.severity}</b></div>
        <div className="field-grid">
          <input placeholder="District e.g. Thanjavur" value={details.district} onChange={e=>setDetails({...details,district:e.target.value})}/>
          <input placeholder="Area / locality e.g. Thiruvaiyaru" value={details.area} onChange={e=>setDetails({...details,area:e.target.value})}/>
          <input placeholder="Duration e.g. 3 days" value={details.duration} onChange={e=>setDetails({...details,duration:e.target.value})}/>
        </div>
        <div className="proof-box">
          <label>Proof photo (optional)</label>
          <div className="proof-actions">
            <button type="button" className="secondary small" onClick={()=>fileInputRef.current?.click()}>Upload file</button>
            <button type="button" className="secondary small" onClick={openCamera}>Use camera</button>
            {proofImage && <button type="button" className="link-button" onClick={()=>setProofImage("")}>Remove</button>}
          </div>
          <input ref={fileInputRef} type="file" accept="image/*" hidden onChange={e=>{const file=e.target.files?.[0]; handleProofImage(file); e.target.value="";}}/>
          {proofImage && <img className="proof-preview" src={proofImage} alt="Complaint proof" />}
        </div>
        <button className="primary wide" disabled={busy||!details.district||!details.area} onClick={submit}>Create Civic Complaint <ArrowRight size={17}/></button>
      </div>}
      {cameraOpen && <div className="camera-modal"><div className="camera-panel"><div className="camera-header"><b>Take a photo</b><button type="button" className="link-button" onClick={closeCamera}>Close</button></div><video ref={videoRef} autoPlay playsInline muted className="camera-video" /><div className="camera-actions"><button type="button" className="primary" onClick={captureCameraPhoto}>Capture</button></div></div></div>}
      <div className="composer"><textarea value={text} onChange={e=>setText(e.target.value)} onKeyDown={e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();send()}}} placeholder="Describe your problem… e.g. enga street la 3 days ah water varala"/><button className="send" onClick={send} disabled={busy}><Send size={18}/></button></div>
    </section>
    <aside className="side-card">
      <div className="eyebrow">WHAT YOU CAN REPORT</div>
      <h3>Six everyday civic issues.</h3>
      <p>Just describe the problem. AI will structure it for you.</p>
      <div className="category-list">{Object.entries(categories).map(([key,c])=>{const Icon=c.icon; return <button type="button" className={`category ${selectedTopic===key ? "selected" : ""}`} key={key} onClick={()=>setSelectedTopic(key)}><span className={`cat-icon ${c.color}`}><Icon size={18}/></span><span>{c.label}</span><ChevronRight size={15}/></button>})}</div>
      <div className="topic-info"><strong>{categories[selectedTopic].label}</strong><span>{categories[selectedTopic].topic}</span></div>
      <div className="trust"><CheckCircle2 size={17}/><span>Prototype · Not an official government service</span></div>
    </aside>
  </div>
}

function Tracker(){
  const [id,setId]=useState(""); const [result,setResult]=useState(null); const [error,setError]=useState(""); const [busy,setBusy]=useState(false);
  async function track(){setBusy(true);setError("");setResult(null);try{setResult(await getComplaint(id.trim()))}catch(e){setError(e.message)}finally{setBusy(false)}}
  return <section className="tracker">
    <div><div className="eyebrow">COMPLAINT TRACKING</div><h2>Know what’s happening.</h2><p>Enter your NammaTN complaint ID to check the latest status.</p></div>
    <div className="track-form"><div className="input-icon"><Search size={17}/><input value={id} onChange={e=>setId(e.target.value)} placeholder="TN-WTR-260812-AB12" /></div><button className="primary" onClick={track} disabled={busy||!id}>Track <ArrowRight size={16}/></button></div>
    {result&&<div className="track-result"><div><b>{result.complaint_id}</b><span>{result.area}, {result.district}</span></div><span className={`status ${result.status.toLowerCase().replaceAll(" ","-")}`}>{result.status}</span>{result.proof_image && <div className="proof-inline"><div className="proof-label">Complaint proof</div><img className="proof-preview compact" src={result.proof_image} alt="Complaint proof" /></div>}</div>}
    {error&&<div className="error">{error}</div>}
  </section>
}

function MyComplaints(){
  const [items,setItems]=useState([]); const [loading,setLoading]=useState(true); const [error,setError]=useState("");
  async function load(){setLoading(true);setError("");try{setItems(await myComplaints())}catch(e){setError(e.message)}finally{setLoading(false)}}
  useEffect(()=>{load()},[]);
  return <section className="my-complaints"><div className="eyebrow">MY COMPLAINTS</div>{loading?"Loading…":items.length===0?"No complaints yet":<div className="list">{items.map(x=><div key={x.complaint_id} className="item"><b>{x.complaint_id}</b><div>{x.area}, {x.district}</div><div>{x.category} · {x.severity} · <span className={`status ${x.status.toLowerCase().replaceAll(" ","-")}`}>{x.status}</span></div>{x.proof_image && <div className="proof-inline"><div className="proof-label">Complaint proof</div><img className="proof-preview compact" src={x.proof_image} alt="Complaint proof" /></div>}</div>)}</div>}{error&&<div className="error">{error}</div>}</section>
}

function Login({onLogin}){
  const [email,setEmail]=useState(""); const [password,setPassword]=useState(""); const [err,setErr]=useState(""); const [loading,setLoading]=useState(false);
  async function submit(e){e.preventDefault(); setErr(""); setLoading(true); try{const res=await login({email,password}); localStorage.setItem("token", res.token); onLogin(res.user); }catch(e){setErr(e.message)} finally{setLoading(false)} }
  return <main className="auth-container"><div className="auth-box"><div className="auth-header"><div className="brand-mark-auth">N</div><h1>Sign In</h1><p>Welcome back to NammaTN Civic Connect</p></div><form onSubmit={submit} className="auth-form-inner"><div className="form-group"><label>Email Address</label><input type="email" placeholder="you@example.com" value={email} onChange={e=>setEmail(e.target.value)} required/></div><div className="form-group"><label>Password</label><input type="password" placeholder="••••••••" value={password} onChange={e=>setPassword(e.target.value)} required/></div>{err&&<div className="form-error">{err}</div>}<button className="primary wide" type="submit" disabled={loading}>{loading?"Signing in...":"Sign In"}</button></form><div className="auth-footer"><span>New to NammaTN?</span><a href="#" onClick={e=>{e.preventDefault(); window.location.hash="register"}}>Create an account</a></div></div></main>
}

function Register({onLogin}){
  const [name,setName]=useState(""); const [email,setEmail]=useState(""); const [phone,setPhone]=useState(""); const [password,setPassword]=useState(""); const [confirm,setConfirm]=useState(""); const [err,setErr]=useState(""); const [loading,setLoading]=useState(false);
  async function submit(e){e.preventDefault(); setErr(""); if(password!==confirm){setErr("Passwords do not match");return} setLoading(true); try{const res=await register({name,email,phone,password}); localStorage.setItem("token", res.token); onLogin(res.user);}catch(e){setErr(e.message)} finally{setLoading(false)} }
  return <main className="auth-container"><div className="auth-box"><div className="auth-header"><div className="brand-mark-auth">N</div><h1>Create Account</h1><p>Join NammaTN to report civic issues</p></div><form onSubmit={submit} className="auth-form-inner"><div className="form-group"><label>Full Name</label><input type="text" placeholder="Your name" value={name} onChange={e=>setName(e.target.value)} required/></div><div className="form-group"><label>Email Address</label><input type="email" placeholder="you@example.com" value={email} onChange={e=>setEmail(e.target.value)} required/></div><div className="form-group"><label>Phone Number</label><input type="tel" placeholder="+91 XXXXX XXXXX" value={phone} onChange={e=>setPhone(e.target.value)} required/></div><div className="form-group"><label>Password</label><input type="password" placeholder="••••••••" value={password} onChange={e=>setPassword(e.target.value)} required/></div><div className="form-group"><label>Confirm Password</label><input type="password" placeholder="••••••••" value={confirm} onChange={e=>setConfirm(e.target.value)} required/></div>{err&&<div className="form-error">{err}</div>}<button className="primary wide" type="submit" disabled={loading}>{loading?"Creating account...":"Create Account"}</button></form><div className="auth-footer"><span>Already have an account?</span><a href="#" onClick={e=>{e.preventDefault(); window.location.hash="login"}}>Sign in</a></div></div></main>
}

function Citizen({user, onRequireAuth}){
  return <main><section className="hero"><div className="hero-copy"><div className="eyebrow">TAMIL NADU · CIVIC SUPPORT</div><h1>One message.<br/><em>One clear report.</em></h1><p>Tell NammaTN what’s wrong in your neighbourhood. Our AI assistant understands Tamil, Tanglish, and English, then turns your message into a structured civic complaint.</p><div className="hero-points"><span><CheckCircle2 size={16}/> AI understands natural language</span><span><CheckCircle2 size={16}/> Track every complaint</span></div></div><Chat user={user} onRequireAuth={onRequireAuth}/></section><Tracker/></main>
}

function Admin(){
  const [data,setData]=useState([]); const [loading,setLoading]=useState(true);
  async function load(){setLoading(true);try{setData(await getComplaints())}finally{setLoading(false)}}
  useEffect(()=>{load()},[]);
  const stats=useMemo(()=>({total:data.length,high:data.filter(x=>x.severity==="high").length,pending:data.filter(x=>x.status==="Submitted").length,resolved:data.filter(x=>x.status==="Resolved").length}),[data]);
  async function status(id,s){await updateComplaint(id,s);load()}
  return <main className="dashboard"><div className="dashboard-title"><div><div className="eyebrow">OPERATIONS</div><h1>Citizen reports</h1><p>Monitor, prioritize, and update local civic complaints.</p></div><button className="secondary" onClick={load}><RefreshCw size={16}/> Refresh</button></div>
    <div className="stats">{[["Total",stats.total],["High priority",stats.high],["Pending",stats.pending],["Resolved",stats.resolved]].map(x=><div className="stat" key={x[0]}><span>{x[0]}</span><b>{x[1]}</b></div>)}</div>
    <div className="table-card">{loading?<div className="empty">Loading reports…</div>:data.length===0?<div className="empty"><FileText size={30}/><b>No complaints yet</b><span>Create a report from the Citizen page.</span></div>:<table><thead><tr><th>Complaint</th><th>Issue</th><th>Location</th><th>Priority</th><th>Status</th><th>Proof</th><th>Action</th></tr></thead><tbody>{data.map(x=><tr key={x.complaint_id}><td><b>{x.complaint_id}</b><small>{new Date(x.created_at).toLocaleString()}</small></td><td><b>{categories[x.category]?.label || x.category}</b><small>{x.message}</small></td><td><MapPin size={14}/> {x.area}, {x.district}</td><td><span className={`priority ${x.severity}`}>{x.severity}</span></td><td><span className={`status ${x.status.toLowerCase().replaceAll(" ","-")}`}>{x.status}</span></td><td>{x.proof_image ? <div className="proof-inline"><div className="proof-label">Complaint proof</div><img className="admin-proof" src={x.proof_image} alt="Complaint proof" /></div> : <span className="muted-text">No image</span>}</td><td>{x.status!=="Resolved"&&<button className="tiny" onClick={()=>status(x.complaint_id,x.status==="Submitted"?"In Progress":"Resolved")}>{x.status==="Submitted"?"Assign":"Resolve"}</button>}</td></tr>)}</tbody></table>}</div>
  </main>
}

export default function App(){
  const [page,setPage]=useState("citizen");
  const [user,setUser]=useState(null);
  useEffect(()=>{
    const token = localStorage.getItem("token");
    if(token){ me().then(u=>setUser(u)).catch(()=>{localStorage.removeItem("token")}) }
  },[])
  function handleLogout(){ localStorage.removeItem("token"); setUser(null); setPage("citizen") }
  return <><Header page={page} setPage={setPage} user={user} onLogout={handleLogout}/>{page==="login"?<Login onLogin={u=>{setUser(u);setPage("citizen")}}/>:page==="register"?<Register onLogin={u=>{setUser(u);setPage("citizen")}}/>:page==="citizen"?<main><section className="hero"><div className="hero-copy"><div className="eyebrow">TAMIL NADU · CIVIC SUPPORT</div><h1>One message.<br/><em>One clear report.</em></h1><p>Tell NammaTN what’s wrong in your neighbourhood. Our AI assistant understands Tamil, Tanglish, and English, then turns your message into a structured civic complaint.</p><div className="hero-points"><span><CheckCircle2 size={16}/> AI understands natural language</span><span><CheckCircle2 size={16}/> Track every complaint</span></div></div><Chat user={user} onRequireAuth={()=>setPage("login")}/></section><Tracker/>{user && <MyComplaints/>}</main>:<Admin/>}<footer>NammaTN – AI Civic Connect · Student-built prototype</footer></>
}
