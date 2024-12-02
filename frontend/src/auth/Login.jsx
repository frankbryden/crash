import React from 'react';
import { Navigate } from "react-router-dom";
import { initializeApp } from "firebase/app";
import useToken from './useToken';

import { getAuth, signInWithPopup, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: "crash-3b3e6.firebaseapp.com",
    projectId: "crash-3b3e6",
    storageBucket: "crash-3b3e6.firebasestorage.app",
    messagingSenderId: "544522710595",
    appId: "1:544522710595:web:9143a114c25f83e320eef6",
    measurementId: "G-6M70K3YB18"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

export default function Login() {

    const { token, setToken } = useToken();
    const auth = getAuth();

    async function launchAuth() {
        console.log("Launch auth");
        const userCred = await signInWithPopup(auth, new GoogleAuthProvider());
        console.log(userCred.user.accessToken);
        setToken(userCred.user.accessToken);
    }

    return (
        <div>
            {token ?
                <Navigate to="/" replace={true} />
                :
                <div>
                    <h1>Please login</h1> <br />
                    <button onClick={launchAuth}>Login with Firebase</button>
                </div>
            }
        </div>
    )
}
