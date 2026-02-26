import React, {useState, useEffect, useRef} from 'react'
import PatientSidebar from '../components/PatientSidebar'
import Chat from '../components/Chat'

export default function Home(){
  const [patientId, setPatientId] = useState('1')
  const [threadId, setThreadId] = useState('1')

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <aside className="w-80 bg-white border-r p-4">
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700">Patient ID</label>
          <input value={patientId} onChange={(e)=>setPatientId(e.target.value)} className="mt-1 block w-full rounded-md border-gray-200 shadow-sm" />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700">Thread ID</label>
          <input value={threadId} onChange={(e)=>setThreadId(e.target.value)} className="mt-1 block w-full rounded-md border-gray-200 shadow-sm" />
        </div>
        <PatientSidebar patientId={patientId} />
      </aside>
      <main className="flex-1 p-6">
        <Chat patientId={patientId} threadId={threadId} />
      </main>
    </div>
  )
}
