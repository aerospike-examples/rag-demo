import React from 'react';
import styles from './index.module.css';
import { Google } from '../logos';
import { useAuth } from '../../hooks/useAuth';

const SignIn = () => {
    const { login } = useAuth();
    return (
        <div className={styles.login}>
            <img src="/Aerospike_Logo_Space_Blue_RGB.png" alt="Aerospike logo"/>
            <div className={styles.signIn} onClick={login}><Google /><span>Sign in</span></div>
        </div>
    )
}
export default SignIn;