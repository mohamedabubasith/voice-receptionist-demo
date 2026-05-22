import { useState, useCallback } from 'react'
import {
  LiveKitRoom,
  RoomAudioRenderer,
  useVoiceAssistant,
  useRoomContext,
  BarVisualizer,
} from '@livekit/components-react'
import { SignJWT } from 'jose'
import styles from './App.module.css'

const LIVEKIT_URL          = import.meta.env.VITE_LIVEKIT_URL as string
const API_KEY              = import.meta.env.VITE_LIVEKIT_API_KEY as string
const API_SECRET           = import.meta.env.VITE_LIVEKIT_API_SECRET as string

declare global { interface Window { __CONFIG__?: { RECEPTIONIST_NAME?: string; CLINIC_NAME?: string } } }
const RECEPTIONIST_NAME    = window.__CONFIG__?.RECEPTIONIST_NAME || (import.meta.env.VITE_RECEPTIONIST_NAME as string) || 'Priya'
const CLINIC_NAME          = window.__CONFIG__?.CLINIC_NAME || (import.meta.env.VITE_CLINIC_NAME as string) || 'Demo Clinic'

type Language = 'en' | 'ta'

async function generateToken(language: Language): Promise<{ token: string; room: string }> {
  const room = `dental-clinic-${Date.now()}`
  const secret = new TextEncoder().encode(API_SECRET)
  const now = Math.floor(Date.now() / 1000)
  const token = await new SignJWT({
    iss: API_KEY,
    sub: `user-${Date.now()}`,
    iat: now,
    exp: now + 3600,
    name: 'Test User',
    metadata: JSON.stringify({ language }),
    video: { roomJoin: true, room, canPublish: true, canSubscribe: true },
  })
    .setProtectedHeader({ alg: 'HS256' })
    .sign(secret)
  return { token, room }
}

type AgentState = 'disconnected' | 'connecting' | 'pre-connect-buffering' | 'failed' | 'listening' | 'thinking' | 'speaking'

const STATUS_LABELS: Partial<Record<AgentState, string>> = {
  'pre-connect-buffering': 'Connecting…',
  connecting: 'Connecting…',
  listening: 'Listening',
  thinking: 'Thinking…',
  speaking: 'Speaking',
  failed: 'Connection failed',
}

export default function App() {
  const [session, setSession] = useState<{ token: string; room: string } | null>(null)
  const [loading, setLoading] = useState(false)
  const [language, setLanguage] = useState<Language>('en')

  const startCall = useCallback(async () => {
    setLoading(true)
    try {
      setSession(await generateToken(language))
    } finally {
      setLoading(false)
    }
  }, [language])

  const endCall = useCallback(() => setSession(null), [])

  if (!session) {
    return (
      <div className={styles.screen}>
        <div className={styles.card}>
          <div className={styles.avatar}>P</div>
          <h1 className={styles.name}>{RECEPTIONIST_NAME}</h1>
          <p className={styles.subtitle}>{CLINIC_NAME} · AI Receptionist</p>
          <div className={styles.langToggle}>
            <button
              className={`${styles.langBtn} ${language === 'en' ? styles.langActive : ''}`}
              onClick={() => setLanguage('en')}
            >English</button>
            <button
              className={`${styles.langBtn} ${language === 'ta' ? styles.langActive : ''}`}
              onClick={() => setLanguage('ta')}
            >தமிழ்</button>
          </div>
          <button className={`${styles.btn} ${styles.startBtn}`} onClick={startCall} disabled={loading}>
            {loading ? 'Connecting…' : language === 'ta' ? 'அழைப்பை தொடங்கு' : 'Start Call'}
          </button>
        </div>
      </div>
    )
  }

  return (
    <LiveKitRoom
      token={session.token}
      serverUrl={LIVEKIT_URL}
      audio={true}
      video={false}
      onDisconnected={endCall}
    >
      <RoomAudioRenderer />
      <CallInterface onEnd={endCall} />
    </LiveKitRoom>
  )
}

function CallInterface({ onEnd }: { onEnd: () => void }) {
  const { state, audioTrack } = useVoiceAssistant()
  const room = useRoomContext()
  const activeState = ['listening', 'thinking', 'speaking'].includes(state) ? state : ''

  const handleEnd = useCallback(async () => {
    await room.disconnect()
    onEnd()
  }, [room, onEnd])

  return (
    <div className={styles.screen}>
      <div className={styles.card}>
        <div className={`${styles.avatar} ${activeState ? styles[activeState] : ''}`}>P</div>
        <h1 className={styles.name}>{RECEPTIONIST_NAME}</h1>
        <p className={styles.status}>{STATUS_LABELS[state as AgentState] ?? state}</p>
        <BarVisualizer state={state} track={audioTrack} barCount={9} className={styles.visualizer} />
        <button className={`${styles.btn} ${styles.endBtn}`} onClick={handleEnd}>End Call</button>
      </div>
    </div>
  )
}
