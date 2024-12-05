import { useLoaderData, useOutlet, useNavigate } from 'react-router-dom';
import {
    useQueryClient,
} from 'react-query';
import { DataFetcher } from './utils/dataFetcher';
import useToken from './auth/useToken';
import useTokenDecoded from './auth/useTokenDecoded';
import './App.css';
import 'markdown-it-latex/dist/index.css'
import Login from './auth/Login';
import Navbar from './Navbar';
import CrashCurve from './CrashCurve';
import { useEffect, useState, useRef } from 'react';

export default function App() {
    const queryClient = useQueryClient();
    const dataFetcher = new DataFetcher();
    const navigate = useNavigate();

    const outlet = useOutlet();

    const ws = useRef(null);
    const { token, setToken } = useToken();
    const { email } = useTokenDecoded(token);

    if (email == undefined) {
        throw new Response("Not authorized", { status: 401 });
    }

    const wsConnection = useEffect(() => {
        ws.current = new WebSocket(import.meta.env.VITE_BACKEND_WSL);
        ws.current.onopen = () => {
            console.log(`ws opened, sending ${email}`);
            ws.current.send(JSON.stringify({
                "type": "join",
                "name": email,
            }));
        };
        ws.current.onclose = () => console.log("ws closed");
        ws.current.onmessage = (ev) => console.log(ev);

        const wsCurrent = ws.current;

        return () => {
            wsCurrent.close();
        };
    }, []);
    const leftLinks = [
        {
            name: "Home",
            onClick: () => window.location.href = "/"
        },
    ];

    const rightLinks = [
        {
            name: "Logout",
            onClick: () => {
                setToken(null);
                navigate("/login");
            }
        }
    ];

    return (
        <div className="min-h-screen">
            <Navbar leftLinks={leftLinks} rightLinks={rightLinks} />
            {outlet ||
                <div>
                    {/* <div className="flex flex-col items-center justify-center py-32">
                        <div className="p-4 text-center">
                            <img src={`/smart_owl.gif`} alt="Smart Owl" className="w-64 h-64" />
                        </div>
                    </div> */}
                    <div>
                        <CrashCurve />
                    </div>
                </div >
            }
        </div >
    );
}