import styles from './index.module.css';
import { useAuth } from '../hooks/useAuth';
import SignIn from '../components/signIn';
import Header from '../components/header';
import Conversation from '../components/conversation';

const App = () => {
  const { auth, roles } = useAuth();

  return (
      auth !== null && 
      <div className={styles.app}>
        {auth ?
        <>
          <Header />
          {/*roles.includes("admin") ? <Conversation /> : <div className={styles.content}><h2>Sorry...</h2><p>This tool is currently being shown live. Please check back later for renewed access.</p></div>*/}
          <Conversation />
        </>
        :
        <SignIn />}
      </div>
  )
}

export default App
