import React, { useState } from 'react'
import { ArrowLeft, GraduationCap, Shield, ShieldCheck, UserCog } from 'lucide-react'
import { json } from '../api'
import { useAuth } from '../App'

const roles = [
  { key: 'ADMIN', label: 'Admin', description: 'Manage students and system access', icon: UserCog },
  { key: 'SECURITY', label: 'Guard', description: 'Verify IDs and record attendance', icon: Shield },
  { key: 'PROFESSOR', label: 'Professor', description: 'Review attendance and reports', icon: GraduationCap },
]

export default function Login() {
  const { setUser } = useAuth()
  const [selectedRole, setSelectedRole] = useState(null)
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const SelectedIcon = selectedRole?.icon

  function chooseRole(role) {
    setSelectedRole(role)
    setForm({ username: '', password: '' })
    setError('')
  }

  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      const result = await json('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ ...form, role: selectedRole.key }),
      })
      localStorage.setItem('token', result.access_token)
      setUser(await json('/auth/me'))
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return <div className="login-wrap">
    <div className="login-shell">
      <div className="login-brand"><span><ShieldCheck /></span><b>Smart ID Attendance</b></div>
      <section className="login-card">
        {!selectedRole ? <>
          <div className="login-heading"><p>Welcome</p><h1>Login as</h1><span>Choose your assigned role to continue.</span></div>
          <div className="role-grid">
            {roles.map(role => {
              const Icon = role.icon
              return <button type="button" className="role-card" key={role.key} onClick={() => chooseRole(role)}>
                <span className="role-icon"><Icon /></span>
                <b>{role.label}</b>
                <small>{role.description}</small>
              </button>
            })}
          </div>
        </> : <>
          <button type="button" className="back-button" onClick={() => chooseRole(null)}><ArrowLeft /> Choose another role</button>
          <div className="login-heading form-heading">
            <span className="role-icon"><SelectedIcon /></span>
            <h1>{selectedRole.label} Login</h1>
            <span>Enter your account credentials to continue.</span>
          </div>
          <form onSubmit={submit}>
            <label>Username<input autoFocus autoComplete="username" required value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} /></label>
            <label>Password<input type="password" autoComplete="current-password" required value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} /></label>
            {error && <div className="error" role="alert">{error}</div>}
            <button className="primary" disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</button>
          </form>
        </>}
      </section>
    </div>
  </div>
}
