import React, { useState } from 'react'
import { ShieldCheck } from 'lucide-react'
import { json } from '../api'
import { useAuth } from '../App'

export default function Login() {
  const { setUser } = useAuth(); const [form, setForm] = useState({username:'', password:''}); const [error, setError] = useState(''); const [busy,setBusy]=useState(false)
  async function submit(e) { e.preventDefault(); setBusy(true); setError(''); try { const result=await json('/auth/login',{method:'POST',body:JSON.stringify(form)}); localStorage.setItem('token',result.access_token); setUser(await json('/auth/me')) } catch(err){setError(err.message)} finally{setBusy(false)} }
  return <div className="login-wrap"><section className="login-copy"><div className="brand light"><ShieldCheck/> Smart ID Attendance</div><div><p className="eyebrow">UNIVERSITY ACCESS SYSTEM</p><h1>Attendance that<br/>recognizes <em>people.</em></h1><p>Local, private face matching from student ID cards—with no OCR and no cloud API.</p></div><small>Computer Vision • Secure by design • Built for the classroom</small></section><section className="login-card"><form onSubmit={submit}><div className="mark"><ShieldCheck/></div><h2>Welcome back</h2><p>Sign in with your assigned account</p><label>Username<input autoFocus value={form.username} onChange={e=>setForm({...form,username:e.target.value})}/></label><label>Password<input type="password" value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/></label>{error&&<div className="error">{error}</div>}<button className="primary" disabled={busy}>{busy?'Signing in…':'Sign in'}</button><small className="hint">Development accounts are created by the seed script.</small></form></section></div>
}
