import React, {useEffect, useState} from 'react'

export default function PatientSidebar({patientId}){
  const [profile, setProfile] = useState(null)

  useEffect(()=>{
    if(!patientId) return
    let mounted = true
    const fetchProfile = ()=>{
      fetch(`http://localhost:8000/patient/${patientId}`)
        .then(r=>r.json())
        .then(d=>{ if(mounted) setProfile(d.profile) })
        .catch(()=>{ if(mounted) setProfile(null) })
    }

    fetchProfile()
    // poll for updates every 2 seconds to show real-time profile changes
    const iv = setInterval(fetchProfile,2000)
    return ()=>{ mounted=false; clearInterval(iv) }
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
