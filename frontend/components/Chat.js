import React, {useState, useRef, useEffect} from 'react'
import ReactMarkdown from 'react-markdown'

export default function Chat({patientId, threadId}){
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const controllerRef = useRef(null)

  const send = async () => {
    if(!input) return
    const userMsg = {role: 'human', content: input}
    setMessages(prev=>[...prev, {role:'human', text: input}])
    setInput('')

    let res
    try{
      res = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        mode: 'cors',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({message: input, patient_id: patientId, thread_id: threadId})
      })
    }catch(err){
      console.error('Fetch error:', err)
      alert('Network error when contacting backend: '+ (err.message || err))
      return
    }

    if(!res.body) return
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let aiText = ''
    let emergencyFlag = false
    setMessages(prev=>[...prev, {role:'ai', text: ''}])
    while(true){
      const {done, value} = await reader.read()
      if(done) break
      const chunk = decoder.decode(value)
      // SSE may send multiple "data: {...}\n\n" blocks. Extract JSON data fields.
      const parts = chunk.split(/\n\n/).filter(Boolean)
      for(const p of parts){
        const line = p.trim()
        if(line.startsWith('data:')){
          const jsonPart = line.replace(/^data:\s*/,'')
          try{
            const obj = JSON.parse(jsonPart)
            aiText += obj.chunk
            if(obj.emergency) emergencyFlag = true
            setMessages(prev=>{
              const copy = [...prev]
              // update last ai message
              for(let i=copy.length-1;i>=0;i--){
                if(copy[i].role==='ai'){
                  copy[i] = {role:'ai', text: aiText, emergency: emergencyFlag}
                  break
                }
              }
              return copy
            })
          }catch(e){
            // ignore
          }
        }
      }
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {messages.map((m, idx)=> (
          <div key={idx} className={m.role==='human'? 'text-right':'text-left'}>
            <div className={m.role==='human'? 'inline-block bg-blue-500 text-white p-3 rounded':'inline-block p-3 rounded border'} style={{backgroundColor: m.emergency ? '#fee2e2' : undefined, borderColor: m.emergency ? '#fca5a5' : undefined}}>
              <div className="flex items-center gap-2">
                {m.emergency ? <span className="text-sm font-semibold text-red-700 bg-red-100 px-2 py-0.5 rounded">Clinical Intervention Required</span> : null}
              </div>
              <ReactMarkdown>{m.text}</ReactMarkdown>
            </div>
          </div>
        ))}
      </div>
      <div className="p-4 border-t bg-white flex">
        <input value={input} onChange={(e)=>setInput(e.target.value)} placeholder="Message the assistant..." className="flex-1 mr-2 p-2 border rounded" />
        <button onClick={send} className="px-4 py-2 bg-blue-600 text-white rounded">Send</button>
      </div>
    </div>
  )
}
