import { useLoaderData, useOutlet, useNavigate, json } from 'react-router-dom';
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
import Error from './Error';
import useErrorQueue from './utils/useErrorQueue';
import CashoutTable from './CashoutTable';
import { GameStates } from './utils/constants';
import CashValuesTable from './CashValuesTable';
import Cashout from './Cashout';

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
    const [cashoutData, setCashoutData] = useState({ currentRound: {}, previousRound: {} });
    const [giftData, setGiftData] = useState({ active: false, nextAvailableGift: new Date() });
    const [countDownVal, setCountDownVal] = useState(null);

    useEffect(() => {
        if (countDownVal == null) {
            return;
        }
        if (countDownVal.remainingTime > 0) {
            setTimeout(() => {
                const now = new Date();
                const remainingTimeMs = countDownVal.estimatedStart - now;
                if (remainingTimeMs > 0) {
                    setCountDownVal({
                        estimatedStart: countDownVal.estimatedStart,
                        // We want to countdown 100ms at a time
                        remainingTime: remainingTimeMs / 100,
                    });
                }
                // 95ms timeout cause we tend to get late scheduled
                // The remaining time doesn't get offset since we're still recomputing each time
            }, 95);
        }
    }, [countDownVal]);

    if (email == undefined) {
        throw new Response("Not authorized", { status: 401 });
    }

    let myCash = -1;
    if (Object.keys(cashVaults).length > 0) {
        myCash = cashVaults[email];
    }

    let myBid = null;
    if (email in bids) {
        myBid = bids[email];
    }

    let myCashout = null;
    if (email in cashoutData.currentRound) {
        myCashout = cashoutData.currentRound[email];
    }

    useEffect(() => {
        ws.current = new WebSocket(import.meta.env.VITE_BACKEND_WSL);
        ws.current.onopen = () => {
            console.log(`ws opened, sending ${email}`);
            ws.current.send(JSON.stringify({
                "type": "join",
                "name": email,
            }));
        };
        ws.current.onclose = () => console.log("ws closed");
        ws.current.onmessage = (ev) => {
            let event = JSON.parse(ev.data);
            switch (event.type) {
                case "join":
                    setPlayers(event.lobby);
                    setCashVaults(event.cash_vaults);
                    setGameState(event.state);
                    break;
                case "leave":
                    setPlayers(event.lobby);
                    setCashVaults(event.cash_vaults);
                    break;
                case "gift":
                    setGiftData({
                        nextAvailableGift: new Date(event.next_available_gift*1000),
                    });
                    setCashVaults((prev) => ({
                        ...prev,
                        [email]: event.cash,
                    }))
                    break;
                case "state":
                    setGameState(event.state);
                    if (event.state == "playing") {
                        setCountDownVal(null);
                        setPoints([]);
                    } else if (event.state == "waiting") {
                        setCountDownVal({
                            estimatedStart: event.estimated_start * 1000,
                            // We want to countdown 100ms at a time (and there's 100 of those in 10s)
                            remainingTime: 100
                        });
                        setCashoutData((prev) => (
                            {
                                currentRound: {},
                                previousRound: prev.currentRound,
                            })
                        );
                    } else if (event.state == "crashed") {
                        setBids({});
                        setCashVaults(event.cash_vaults);
                    }
                    break;
                case "bid":
                    setBids(event.bids);
                    setCashVaults(event.cash_vaults);
                    setCashoutData((prev) => ({
                        ...prev,
                        currentRound: event.cashouts,
                    }));
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
                    if (event.target == email) {
                        setGameState(GameStates.CASHED_OUT);
                    }
                    setCashoutData((prev) => ({
                        ...prev,
                        currentRound: event.cashouts,
                    }));
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

    function claimGift() {
        if (ws == null) {
            return;
        }
        const wsCurrent = ws.current;
        wsCurrent.send(JSON.stringify({
            "type": "gift",
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
        <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col">
            <Navbar leftLinks={leftLinks} rightLinks={rightLinks} giftData={giftData} claimGift={claimGift} />
            {outlet ||
                <div className="flex flex-col md:flex-row gap-4 p-4 w-full">
                    {/* Left Panel */}
                    <div className="flex-row w-1/5">
                        <p className="text-amber-600 font-bold text-lg">Balance: <span className="animate-pulse">{myCash}</span></p>
                        {(gameState == GameStates.PLAYING || gameState == GameStates.CASHED_OUT) &&
                            <Cashout bidAmount={myBid} hasCashedOut={gameState == GameStates.CASHED_OUT && myCashout != null} cashOutObj={myCashout} cashoutCallback={cashout} />
                        }
                        {gameState == GameStates.WAITING &&
                            <Bidding bidFunc={makeBid} bid={myBid} />
                        }
                    </div>
                    {/* Center Panel */}
                    <div className="flex-1">
                        <CrashCurve points={points} countdown={countDownVal} />
                    </div>

                    {/* Right Panel */}
                    <div className="flex flex-col grow space-y-4 min-w-96">
                        <Lobby players={players} />
                        <CashValuesTable title="Cash vaults" mapping={cashVaults} sorted={true} />
                        <CashoutTable title="Current round" rows={cashoutData.currentRound} active={true} />
                        {Object.keys(cashoutData.previousRound).length > 0 &&
                            <CashoutTable title="Previous round" rows={cashoutData.previousRound} active={false} />
                        }
                    </div>

                    {/* Errors */}
                    {errorQueue.map((error, index) => <Error key={index} message={error} />)}
                </div>
            }
        </div >
    );
}