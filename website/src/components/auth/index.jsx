import React, { createContext, useEffect, useState } from 'react';
import Modal from '../modal/index.jsx';
import GoTrue from 'gotrue-js';
import { useModal } from '../../hooks/useModal';

export const AuthContext = createContext(null);

const AuthProvider = ({children}) => {
    const { modalProps, ref, openModal } = useModal();
    const [auth, setAuth] = useState(null);
    const [user, setUser] = useState(null);

    const goAuth = new GoTrue({
		APIUrl: 'https://vector-rag-aerospike.netlify.app/.netlify/identity',
		audience: '',
		setCookie: true,
	});

    const startLogin = () => {
        const url = goAuth.loginExternalUrl('google');
		window.location.href = url;
    }
    
    const handleSaved = () => {
        let saved = goAuth.currentUser();
		if(!saved){
            setAuth(false);
            return
        };
		
        goAuth.createUser(saved.token)
		.then((user) => {
			setUser(user);
			setAuth(true);
		}).catch(() => {
			saved.logout()
			.then(() => {
				setUser(null);
				setAuth(false);
			})
		})
    }

    const completeLogin = () => {
        let hash = window.location.hash ? window.location.hash.split('#')[1] : null;
		if(!hash) {
            handleSaved();
            return;
        }
		
        window.location.hash = '';
		if(hash.includes('bearer')){
			let token = {};
			hash = hash.split('&');
            for(let item of hash){
                let kv = item.split('=');
                let key = kv[0];
                let value = kv[1];
                token[key] = value;
            }
			goAuth.createUser(token, true).then(user => {
				if(user){
					setUser(user);
					setAuth(true);
				}
			})
		}
		else if(hash.includes('error')){
			openModal();
            setAuth(false);
		}
        else{
            handleSaved();
        }
    }

    useEffect(() => {
        completeLogin();
    }, []);

    const userAuth = {
        auth,
        user,
        roles: user ? user.app_metadata.roles : [],
        login: startLogin,
        logout: () => user.logout().then(() => {
                    setAuth(false);
                    setUser(null);
                })
    }

    return (
        <AuthContext.Provider value={userAuth}>
            {children}
			{modalProps.open && 
            <Modal {...modalProps} ref={ref}>
				<div>
					<h2>Error!</h2>
					<p>Access is only available to emails within the Aerospike domain.</p><p>Ensure you are using your <b>name@aerospike.com</b> email to sign in.</p>
				</div>
			</Modal>}
        </AuthContext.Provider>
    )
}

export default AuthProvider;