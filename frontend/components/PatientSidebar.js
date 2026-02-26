import React, {useEffect, useState} from 'react'

export default function PatientSidebar({patientId}){
  const [profile, setProfile] = useState(null)

  useEffect(()=>{
    if(!patientId) return
    let mounted = true
    let interval = 2000
    let iv = null

    const fetchProfile = ()=>{
      fetch(`http://127.0.0.1:8000/patient/${patientId}`)
        .then(r=>{ if(!r.ok) throw new Error('bad status') ; return r.json() })
        .then(d=>{ if(mounted){ setProfile(d.profile); interval = 2000 } })
        .catch(()=>{ if(mounted){ /* exponential backoff on failure */ interval = Math.min(30000, interval * 1.5) } })
        .finally(()=>{ if(mounted){ clearInterval(iv); iv = setInterval(fetchProfile, interval) } })
    }

    fetchProfile()
    // initial poll interval set above; iv will be managed in fetchProfile finalizer
    return ()=>{ mounted=false; if(iv) clearInterval(iv) }
  },[patientId])

  return (
    <div>
      <h3 className="text-lg font-semibold mb-2">Patient Profile</h3>
      <div className="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 p-3 rounded">
        {profile || 'No profile stored.'}
      </div>
    </div>
  )
}
