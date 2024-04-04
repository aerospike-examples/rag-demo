import { useEffect, useRef, useState } from 'react';
import styles from './index.module.css';
import Format from '../components/format';
import { Gemma } from '../components/logos';

function App() {
  const [prompt, setPrompt] = useState("");
  const [conversation, setConversation] = useState(null);
  const [waiting, setWaiting] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const prmtRef = useRef();
  const convRef = useRef();

  useEffect(() => {
    convRef.current?.scrollIntoView({ behavior: "smooth"});
  }, [conversation])
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if(!prompt) return;
    let body = new FormData();
    body.append("text", prompt);
    setStreaming(true);
    setConversation(prev => prev === null ? `**${prompt.trim()}**\n\n` : `${prev}**${prompt.trim()}**\n\n`);
    setPrompt("");

    fetch("/rest/v1/chat/", {
      method: "POST",
      credentials: "include",
      body
    })
    .then(async (response) => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        while (true) {
          const { done, value } = await reader.read();
          if(done) {
            setConversation(prev => `${prev}\n\n<hr />\n\n`);
            setStreaming(false);
            setTimeout(() => prmtRef.current.focus(), 100);
            return
          }
          else {
            let text = decoder.decode(value, {stream: true});
            if(text === "\nGenerating a response...\n\n") setWaiting(true);
            else setWaiting(false);

            setConversation(prev => prev + text);
          }
        }
    })
  }

  return (
      <>
      <div className={styles.stripe}/>
      <div className={styles.app}>
        <header className={styles.header}>
          <a href='/'><img src='https://developer-hub.s3.us-west-1.amazonaws.com/email-signature/logo_1707930697719.png' alt="Aerospike logo" /></a>
          <div className={styles.gemma}><Gemma className={styles.logos}/></div>
        </header>
        <div className={styles.container}>
          {conversation &&
          <div className={styles.conversation}>
            <Format>{conversation}</Format>
            {waiting && <div className={styles.waiting}/>}
            <div ref={convRef} />
          </div>}
          <form onSubmit={handleSubmit} className={styles.form}>
            <label>
              <input ref={prmtRef} type="text" value={prompt} onChange={(e) => setPrompt(e.currentTarget.value)} className={styles.prompt} disabled={waiting || streaming} placeholder='Ask a question...' />
            </label>
            <button type="submit">&#9166;</button>
          </form>
        </div>
      </div>
      </>
  )
}

export default App
