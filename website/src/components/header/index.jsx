import styles from './index.module.css';

const Header = () => {
  return (
      <>
      <div className={styles.stripe}/>
      <header className={styles.header}>
        <a className={styles.aerospike} href='/'><img src="/Aerospike_Logo_Space_Blue_RGB.png" alt="Aerospike logo"/></a>
      </header>
      </>
  )
}

export default Header;
