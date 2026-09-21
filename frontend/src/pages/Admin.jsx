import React, { useEffect, useState } from 'react'
import { GraduationCap, Trash2, UserPlus, Users } from 'lucide-react'
import { api, json } from '../api'

export default function Admin() {
  const [registry, setRegistry] = useState('students')
  const [students, setStudents] = useState([])
  const [professors, setProfessors] = useState([])
  const [studentMessage, setStudentMessage] = useState('')
  const [professorMessage, setProfessorMessage] = useState('')
  const [busy, setBusy] = useState(false)

  const loadStudents = () => json('/students').then(setStudents).catch(error => setStudentMessage(error.message))
  const loadProfessors = () => json('/admin/professors').then(setProfessors).catch(error => setProfessorMessage(error.message))

  useEffect(() => {
    loadStudents()
    loadProfessors()
  }, [])

  async function registerStudent(event) {
    event.preventDefault()
    const form = event.currentTarget
    setBusy(true)
    setStudentMessage('')
    try {
      await api('/students', { method: 'POST', body: new FormData(form) })
      form.reset()
      setStudentMessage('Student registered and face embedding saved.')
      loadStudents()
    } catch (error) {
      setStudentMessage(error.message)
    } finally {
      setBusy(false)
    }
  }

  async function registerProfessor(event) {
    event.preventDefault()
    const formElement = event.currentTarget
    setBusy(true)
    setProfessorMessage('')
    const form = new FormData(formElement)
    try {
      await api('/admin/users', {
        method: 'POST',
        body: JSON.stringify({ username: form.get('username'), password: form.get('password'), role: 'PROFESSOR' }),
      })
      formElement.reset()
      setProfessorMessage('Professor account created.')
      loadProfessors()
    } catch (error) {
      setProfessorMessage(error.message)
    } finally {
      setBusy(false)
    }
  }

  async function deleteProfessor(professor) {
    if (!window.confirm(`Delete professor account “${professor.username}”?`)) return
    setProfessorMessage('')
    try {
      await api(`/admin/professors/${professor.id}`, { method: 'DELETE' })
      setProfessorMessage('Professor account deleted.')
      loadProfessors()
    } catch (error) {
      setProfessorMessage(error.message)
    }
  }

  return <>
    <header className="admin-header">
      <div>
        <p className="eyebrow">ADMINISTRATION</p>
        <h1>{registry === 'students' ? 'Student registry' : 'Professor registry'}</h1>
        <p>{registry === 'students' ? 'Register consented photographs and manage local identities.' : 'Create and manage professor login accounts.'}</p>
      </div>
      <div className="registry-tabs" aria-label="Registry type">
        <button className={registry === 'students' ? 'active' : ''} onClick={() => setRegistry('students')}><Users /> Students</button>
        <button className={registry === 'professors' ? 'active' : ''} onClick={() => setRegistry('professors')}><GraduationCap /> Professors</button>
      </div>
    </header>

    {registry === 'students' ? <StudentRegistry students={students} message={studentMessage} busy={busy} onSubmit={registerStudent} /> :
      <ProfessorRegistry professors={professors} message={professorMessage} busy={busy} onSubmit={registerProfessor} onDelete={deleteProfessor} />}
  </>
}

function StudentRegistry({ students, message, busy, onSubmit }) {
  return <div className="admin-grid">
    <section className="panel form-panel">
      <h2><UserPlus /> Register student</h2>
      <form onSubmit={onSubmit} className="student-form">
        <label>Student ID<input name="student_id" required /></label>
        <label>Full name<input name="name" required /></label>
        <label>Department<input name="department" required /></label>
        <label>Academic year<input name="year" type="number" min="1" max="8" required /></label>
        <label className="wide">Registered photograph<input name="photo" type="file" accept="image/jpeg,image/png" required /><small>Use one clear, front-facing face with consent.</small></label>
        {message && <div className="notice wide">{message}</div>}
        <button className="primary wide" disabled={busy}>{busy ? 'Processing face…' : 'Register student'}</button>
      </form>
    </section>
    <section className="panel">
      <h2><Users /> Registered <span>{students.length}</span></h2>
      <div className="student-list">
        {students.map(student => <article key={student.id}>
          <img src={`http://localhost:8000${student.photo_url}`} alt="" />
          <div><b>{student.name}</b><small>{student.student_id} · {student.department} · Year {student.year}</small></div>
        </article>)}
        {!students.length && <p className="no-data">No students registered yet.</p>}
      </div>
    </section>
  </div>
}

function ProfessorRegistry({ professors, message, busy, onSubmit, onDelete }) {
  return <div className="admin-grid">
    <section className="panel form-panel">
      <h2><UserPlus /> Add professor</h2>
      <form onSubmit={onSubmit} className="professor-form">
        <label>Username<input name="username" minLength="3" maxLength="80" autoComplete="off" required /></label>
        <label>Password<input name="password" type="password" minLength="8" maxLength="128" autoComplete="new-password" required /></label>
        {message && <div className="notice">{message}</div>}
        <button className="primary" disabled={busy}>{busy ? 'Creating account…' : 'Add professor'}</button>
      </form>
    </section>
    <section className="panel">
      <h2><GraduationCap /> Professors <span>{professors.length}</span></h2>
      <div className="professor-list">
        {professors.map(professor => <article key={professor.id}>
          <span className="professor-avatar"><GraduationCap /></span>
          <div><b>{professor.username}</b><small>Professor account</small></div>
          <button className="delete-account" onClick={() => onDelete(professor)} aria-label={`Delete ${professor.username}`}><Trash2 /></button>
        </article>)}
        {!professors.length && <p className="no-data">No professor accounts yet.</p>}
      </div>
    </section>
  </div>
}
