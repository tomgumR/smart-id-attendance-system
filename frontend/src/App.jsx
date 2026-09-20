import React, { createContext, useContext, useEffect, useState } from 'react'
import { Camera, GraduationCap, LogOut, ShieldCheck, Users } from 'lucide-react'
import { json } from './api'
import Login from './pages/Login'
import Guard from './pages/Guard'
import Professor from './pages/Professor'
import Admin from './pages/Admin'

export const Auth = createContext(null)
export const useAuth = () => useContext(Auth)

export default function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  useEffect(() => { if (!localStorage.getItem('token')) return setLoading(false); json('/auth/me').then(setUser).catch(() => localStorage.removeItem('token')).finally(() => setLoading(false)) }, [])
  const logout = () => { localStorage.removeItem('token'); setUser(null) }
  if (loading) return <div className="center"><div className="spinner" /></div>
  if (!user) return <Auth.Provider value={{ setUser }}><Login /></Auth.Provider>
  return <Auth.Provider value={{ user, logout }}>
    <div className="app-shell">
      <aside>
        <div className="brand"><ShieldCheck size={26}/><div>Smart ID<span>Attendance</span></div></div>
        <nav>
          {user.role === 'SECURITY' && <a className="active"><Camera/>Scanner</a>}
          {user.role === 'PROFESSOR' && <a className="active"><GraduationCap/>Dashboard</a>}
          {user.role === 'ADMIN' && <a className="active"><Users/>Administration</a>}
        </nav>
        <button className="profile" onClick={logout}><span><b>{user.username}</b><small>{user.role}</small></span><LogOut size={18}/></button>
      </aside>
      <main>{user.role === 'SECURITY' ? <Guard/> : user.role === 'PROFESSOR' ? <Professor/> : <Admin/>}</main>
    </div>
  </Auth.Provider>
}
