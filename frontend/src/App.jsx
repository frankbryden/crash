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
import { getRandomName } from './utils/names';
import Lobby from './Lobby';
import Bidding from './Bidding';
import NumbersTable from './NumbersTable';
import FancyButton from './FancyButton';
import Error from './Error';
import useErrorQueue from './utils/useErrorQueue';
import CashoutTable from './CashoutTable';

export default function App() {
    const queryClient = useQueryClient();
    const dataFetcher = new DataFetcher();
    const navigate = useNavigate();

    const outlet = useOutlet();

    const ws = useRef(null);
    const { token, setToken } = useToken();
    const { errorQueue, addError } = useErrorQueue();
    const { email } = useTokenDecoded(token);
    const [players, setPlayers] = useState([]);
    const [points, setPoints] = useState([]);
    const [bids, setBids] = useState({});
    const [cashVaults, setCashVaults] = useState({});
    const [gameState, setGameState] = useState("");
    const [cashoutData, setCashoutData] = useState([]);
    const [countDownVal, setCountDownVal] = useState(null);

    useEffect(() => {
        if (countDownVal == null) {
            return;
        }
        if (countDownVal > 0) {
            setTimeout(() => setCountDownVal(countDownVal - 1), 95);
        }
    }, [countDownVal]);

    if (email == undefined) {
        throw new Response("Not authorized", { status: 401 });
    }

    const wsConnection = useEffect(() => {
        ws.current = new WebSocket(import.meta.env.VITE_BACKEND_WSL);
        ws.current.onopen = () => {
            console.log(`ws opened, sending ${email}`);
            ws.current.send(JSON.stringify({
                "type": "join",
                "name": getRandomName(),
            }));
        };
        ws.current.onclose = () => console.log("ws closed");
        ws.current.onmessage = (ev) => {
            let event = JSON.parse(ev.data);
            switch (event.type) {
                case "join":
                    setPlayers(event.lobby)
                    break;
                case "state":
                    setGameState(event.state);
                    if (event.state == "playing") {
                        setCountDownVal(null);
                        setPoints([]);
                        setCashoutData([]);
                    } else if (event.state == "waiting") {
                        // {"type": "state", "state": "waiting", "estimated_start": 1734394996.9588025}
                        const now = new Date();
                        const remainingTimeMs = event.estimated_start * 1000 - now;
                        // We want to countdown 100ms at a time
                        setCountDownVal(remainingTimeMs / 100);
                    }
                    break;
                case "bid":
                    setBids(event.bids);
                    setCashVaults(event.cash_vaults);
                    break;
                case "error":
                    addError(event.message);
                    break;
                case "mult":
                    if (event.mult > 0) {
                        setPoints(points => [...points, event.mult]);
                    }
                    break;
                case "cashout":
                    setCashoutData(event.cashouts);
                    break;
                default:
                    break;
            }
        };

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

    function makeBid(bidAmount) {
        if (ws == null) {
            return;
        }
        const wsCurrent = ws.current;
        wsCurrent.send(JSON.stringify({
            "type": "bid",
            "amount": parseInt(bidAmount),
        }));
    }

    function cashout() {
        if (ws == null) {
            return;
        }
        const wsCurrent = ws.current;
        wsCurrent.send(JSON.stringify({
            "type": "cashout",
        }));

    }

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
                    <h1>{gameState}</h1>
                    <h1>{Math.round(countDownVal) / 10}s</h1>
                    <div>
                        <CrashCurve points={points} />
                    </div>
                    <Lobby players={players} />
                    <NumbersTable title="Bids" keyColTitle="Player" valColTitle="Amount" mapping={bids} sorted={true} />
                    <NumbersTable title="Cash vaults" keyColTitle="Player" valColTitle="Value" mapping={cashVaults} />
                    <CashoutTable rows={cashoutData} />
                    <Bidding bidFunc={makeBid} />
                    <FancyButton name={"Cashout"} onClick={cashout} />
                    {/* Errors */}
                    {errorQueue.map((error, index) => <Error key={index} message={error} />)}
                </div >
            }
        </div >
    );
}