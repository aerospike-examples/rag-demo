import styles from './index.module.css';
import Header from '../components/header';
import Conversation from '../components/conversation';

const App = () => {
  return (
      <div className={styles.app}>
          <Header />
          <Conversation />
      </div>
  )
}

export default App
