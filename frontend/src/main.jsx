import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'
import {
    QueryClient,
    QueryClientProvider,
} from 'react-query';
import {
    createBrowserRouter,
    RouterProvider,
} from "react-router-dom";
import { DataFetcher } from './utils/dataFetcher';
import ErrorBoundary from "./ErrorBoundary";
import Login from './auth/Login';

// Create a client
const queryClient = new QueryClient()

//Create the router
const dataFetcher = new DataFetcher();
const router = createBrowserRouter([
    {
        path: "/",
        element: <App />,
        id: "root",
        errorElement: <ErrorBoundary />,
        loader: async () => {
            // const tagDefinitions = await dataFetcher.fetchTagDefinitions();
            // return tagDefinitions;
            return {};
        },
        children: [
            {
                path: "login",
                element: <Login />
            },
        ],
    },
]);

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <QueryClientProvider client={queryClient}>
            <RouterProvider router={router} />
        </QueryClientProvider>
    </React.StrictMode>,
)
