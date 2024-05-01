import styles from './index.module.css';
import { useAuth } from '../hooks/useAuth';
import SignIn from '../components/signIn';
import Header from '../components/header';
import Conversation from '../components/conversation';

const App = () => {
  const { auth } = useAuth();

  return (
      <div className={styles.app}>
        {auth ?
        <>
          <Header />
          <Conversation />
        </>
        :
        <SignIn />}
      </div>
  )
}

export default App
