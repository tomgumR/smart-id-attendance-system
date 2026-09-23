import React, { useEffect, useState } from 'react'
import { Download, Search } from 'lucide-react'
import { api, json } from '../api'

export default function Professor() {
  const [rows, setRows] = useState([])
  const [summary, setSummary] = useState({})
  const [filters, setFilters] = useState({ search: '', department: '', start_date: '', end_date: '' })
  const params = () => new URLSearchParams(Object.entries(filters).filter(([, value]) => value)).toString()
  const load = () => {
    json(`/attendance?${params()}`).then(setRows)
    json('/attendance/summary').then(setSummary)
  }

  useEffect(() => {
    load()
  }, [])

  async function download() {
    const response = await api(`/attendance/export?${params()}`)
    const url = URL.createObjectURL(await response.blob())
    const link = document.createElement('a')
    link.href = url
    link.download = 'attendance.csv'
    link.click()
    URL.revokeObjectURL(url)
  }

  return <>
    <header>
      <div><p className="eyebrow">ACADEMIC OVERVIEW</p><h1>Attendance dashboard</h1><p>Review daily presence and verification evidence.</p></div>
      <button className="secondary" onClick={download}><Download size={17} /> Export CSV</button>
    </header>
    <div className="stats">
      <Stat label="Registered" value={summary.total_registered} />
      <Stat label="Present today" value={summary.present} />
      <Stat label="Absent today" value={summary.absent} />
      <Stat label="Attendance" value={`${summary.attendance_percentage || 0}%`} accent />
    </div>
    <section className="panel">
      <div className="filters">
        <label className="search"><Search /><input placeholder="Search name or student ID" value={filters.search} onChange={event => setFilters({ ...filters, search: event.target.value })} /></label>
        <input placeholder="Department" value={filters.department} onChange={event => setFilters({ ...filters, department: event.target.value })} />
        <input type="date" value={filters.start_date} onChange={event => setFilters({ ...filters, start_date: event.target.value })} />
        <input type="date" value={filters.end_date} onChange={event => setFilters({ ...filters, end_date: event.target.value })} />
        <button className="primary" onClick={load}>Apply</button>
      </div>
      <div className="table-wrap"><table>
        <thead><tr><th>Student</th><th>Department</th><th>Date & time</th><th>Method</th><th>ID score</th><th>Guard</th></tr></thead>
        <tbody>
          {rows.map(row => <tr key={row.id}>
            <td><b>{row.name}</b><small>{row.student_id}</small></td>
            <td>{row.department}</td>
            <td>{new Date(row.timestamp).toLocaleString()}</td>
            <td><span className="pill">ID only</span></td>
            <td>{row.similarity_score.toFixed(3)}</td>
            <td>{row.security_username}</td>
          </tr>)}
          {!rows.length && <tr><td colSpan="6" className="no-data">No records match these filters.</td></tr>}
        </tbody>
      </table></div>
    </section>
  </>
}

function Stat({ label, value, accent }) {
  return <section className={`stat ${accent ? 'accent' : ''}`}><small>{label}</small><b>{value ?? 0}</b></section>
}
