import styles from './index.module.css';
import { Gemma } from '../logos';

const Header = () => {
  return (
      <>
      <div className={styles.stripe}/>
      <header className={styles.header}>
        <a className={styles.aerospike} href='/'><img src="/Aerospike_Logo_Space_Blue_RGB.png" alt="Aerospike logo"/></a>
        <div className={styles.gemma}><Gemma className={styles.logos}/></div>
      </header>
      </>
  )
}

export default Header;
