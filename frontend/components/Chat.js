import React, {useState, useRef, useEffect} from 'react'
import ReactMarkdown from 'react-markdown'

export default function Chat({patientId, threadId}){
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [errorBanner, setErrorBanner] = useState('')
  const controllerRef = useRef(null)

  const send = async () => {
    if(!input || sending) return
    setErrorBanner('')
    setSending(true)
    controllerRef.current = new AbortController()

    setMessages(prev=>[...prev, {role:'human', text: input}])
    setInput('')

    let res
    try{
      res = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        mode: 'cors',
        signal: controllerRef.current.signal,
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({message: input, patient_id: patientId, thread_id: threadId})
      })
    }catch(err){
      console.error('Fetch error:', err)
      setErrorBanner('Network error: '+ (err.message || err))
      setSending(false)
      return
    }

    if(!res.body){ setSending(false); return }
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let aiText = ''
    let emergencyFlag = false
    // append placeholder ai message
    setMessages(prev=>[...prev, {role:'ai', text: ''}])

    let buffer = ''
    try{
      while(true){
        const {done, value} = await reader.read()
        if(done) break
        buffer += decoder.decode(value, {stream:true})
        // process complete SSE data blocks
        const chunks = buffer.split(/\n\n/)
        buffer = chunks.pop() || ''
        for(const part of chunks){
          const line = part.trim()
          if(!line) continue
          if(line.startsWith('data:')){
            const jsonPart = line.replace(/^data:\s*/,'')
            try{
              const obj = JSON.parse(jsonPart)
              if(obj.chunk) aiText += obj.chunk
              if(obj.emergency) emergencyFlag = true
              setMessages(prev=>{
                const copy = [...prev]
                for(let i=copy.length-1;i>=0;i--){
                  if(copy[i].role==='ai'){
                    copy[i] = {role:'ai', text: aiText, emergency: emergencyFlag}
                    break
                  }
                }
                return copy
              })
            }catch(e){
              // ignore malformed JSON for now
            }
          }
        }
      }
    }catch(err){
      if(err.name==='AbortError'){
        setErrorBanner('Stream cancelled')
      }else{
        console.error('Stream read error', err)
        setErrorBanner('Stream error: '+ (err.message||err))
      }
    }finally{
      setSending(false)
      controllerRef.current = null
    }
  }

  return (
    <div className="flex flex-col h-full">
      {errorBanner ? (
        <div className="bg-yellow-100 border-l-4 border-yellow-400 text-yellow-700 p-3">{errorBanner} <button className="ml-2 underline" onClick={()=>setErrorBanner('')}>Dismiss</button></div>
      ) : null}
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
        <textarea value={input} onChange={(e)=>setInput(e.target.value)} onKeyDown={(e)=>{ if(e.key==='Enter' && !e.shiftKey){ e.preventDefault(); send() } }} placeholder="Message the assistant..." className="flex-1 mr-2 p-2 border rounded resize-none" rows={2} />
        <div className="flex items-center gap-2">
          {sending ? (
            <button onClick={()=>{ if(controllerRef.current){ controllerRef.current.abort() } }} className="px-3 py-2 bg-gray-300 text-gray-800 rounded">Cancel</button>
          ) : null}
          <button onClick={send} disabled={sending} className={`px-4 py-2 ${sending? 'bg-gray-400':'bg-blue-600'} text-white rounded`}>{sending? 'Sending...' : 'Send'}</button>
        </div>
      </div>
    </div>
  )
}
