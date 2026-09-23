import React, { useEffect, useRef, useState } from 'react'
import { Camera, CheckCircle2, Clock3, Upload, XCircle } from 'lucide-react'
import { api, json } from '../api'
import WebcamCapture from '../components/WebcamCapture'

export default function Guard() {
  const [idFile, setIdFile] = useState(null)
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [recent, setRecent] = useState([])
  const camera = useRef()

  const refresh = () => json('/attendance/today').then(setRecent).catch(() => {})

  useEffect(() => {
    refresh()
  }, [])

  async function scan() {
    setBusy(true)
    setResult(null)
    try {
      const image = idFile || await camera.current?.capture()
      if (!image) throw new Error('Start the camera or choose an ID image.')
      const form = new FormData()
      form.append('image', image, 'id.jpg')
      const response = await api('/verification/id-image', { method: 'POST', body: form })
      setResult(await response.json())
      refresh()
    } catch (error) {
      setResult({ status: 'ERROR', message: error.message })
    } finally {
      setBusy(false)
    }
  }

  return <>
    <header>
      <div>
        <p className="eyebrow">SECURITY CONSOLE</p>
        <h1>Attendance scanner</h1>
        <p>Position the student ID inside the guide.</p>
      </div>
    </header>
    <div className="guard-grid">
      <section className="panel scanner">
        <WebcamCapture ref={camera} />
        <div className="scan-actions">
          <label className="secondary"><Upload size={17} /> Upload ID<input type="file" accept="image/*" onChange={event => setIdFile(event.target.files[0])} /></label>
          <button className="primary" onClick={scan} disabled={busy}><Camera size={18} />{busy ? 'Verifying…' : 'Verify & mark present'}</button>
        </div>
      </section>
      <section className={`panel result ${result?.status?.toLowerCase() || ''}`}>
        {!result ? <div className="empty">
          <div className="pulse"><Camera /></div>
          <h3>Ready to scan</h3>
          <p>Results appear here after verification.</p>
        </div> : <>
          <div className="result-icon">{['RECORDED', 'DUPLICATE'].includes(result.status) ? <CheckCircle2 /> : <XCircle />}</div>
          <p className="eyebrow">{result.status}</p>
          <h2>{result.student?.name || 'Verification failed'}</h2>
          {result.student && <>
            <p>{result.student.student_id} · {result.student.department}</p>
            <img className="avatar" src={`http://localhost:8000${result.student.photo_url}`} alt="" />
            <div className="scores"><span>ID similarity <b>{result.similarity_score?.toFixed(3)}</b></span></div>
          </>}
          <p className="message">{result.message}</p>
        </>}
      </section>
    </div>
    <section className="panel recent">
      <h2><Clock3 /> Today’s recent attendance</h2>
      <AttendanceRows rows={recent} />
    </section>
  </>
}

function AttendanceRows({ rows }) {
  return <div className="table-wrap"><table>
    <thead><tr><th>Student</th><th>Department</th><th>Time</th><th>Method</th><th>Similarity</th></tr></thead>
    <tbody>
      {rows.map(row => <tr key={row.id}>
        <td><b>{row.name}</b><small>{row.student_id}</small></td>
        <td>{row.department}</td>
        <td>{new Date(row.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</td>
        <td><span className="pill">ID only</span></td>
        <td>{row.similarity_score.toFixed(3)}</td>
      </tr>)}
      {!rows.length && <tr><td colSpan="5" className="no-data">No attendance recorded today.</td></tr>}
    </tbody>
  </table></div>
}
