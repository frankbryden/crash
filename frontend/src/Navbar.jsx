import useToken from "./auth/useToken";
import useTokenDecoded from "./auth/useTokenDecoded";
import { host } from "./utils/constants";
import { useState } from "react";
import { ChevronDownIcon } from '@heroicons/react/24/solid';
import Gift from "./Gift";

/**
 * Navbar placed top of the page with links and an icon.
 * @param {leftLinks} array List of objects with the schema { name, onclickClbk } placed 
 *                          on the left side of the navbar
 * @param {rightLinks} array List of objects with the schema { name, onclickClbk } placed
 *                          on the right side of the navbar
 * @returns A navbar rendering the links.
 */
export default function Navbar({ leftLinks, rightLinks, giftData, claimGift }) {
    const { token } = useToken();
    const { picture } = useTokenDecoded(token);
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);

    const toggleDropdown = () => {
        setIsDropdownOpen(!isDropdownOpen);
    };

    return (
        <nav className="bg-gradient-to-r from-blue-500 to-purple-500 shadow-lg relative z-50">
            <div className="flex items-center justify-between p-4">
                <div className="flex items-center space-x-3">
                    <a href="#">
                        <img src={`/smart_owl.gif`} alt="Logo" className="h-10 w-10 object-cover rounded-full" />
                    </a>
                    <ul className="flex space-x-4">
                        {leftLinks.map((leftLink) => (
                            <li key={leftLink.name} className="relative">
                                {leftLink.name === "How it works" ? (
                                    <>
                                        <a
                                            className="text-white font-semibold hover:text-yellow-200 transition-colors duration-200 cursor-pointer flex items-center"
                                            onClick={toggleDropdown}>
                                            {leftLink.name}
                                            <ChevronDownIcon className="h-5 w-5 ml-1" />

                                        </a>
                                        <div className={`absolute left-0 mt-2 w-48 bg-white rounded-md shadow-lg z-50 ${isDropdownOpen ? 'block' : 'hidden'}`}>
                                            <a href="#" className="block px-4 py-2 text-gray-800 hover:bg-gray-200">Feature 1</a>
                                            <a href="#" className="block px-4 py-2 text-gray-800 hover:bg-gray-200">Feature 2</a>
                                            <a href="#" className="block px-4 py-2 text-gray-800 hover:bg-gray-200">Feature 3</a>
                                        </div>
                                    </>
                                ) : (
                                    <a
                                        onClick={leftLink.onClick}
                                        className="text-white font-semibold hover:text-yellow-200 transition-colors duration-200"
                                        href="#">
                                        {leftLink.name}
                                    </a>
                                )}
                            </li>
                        ))}
                    </ul>
                </div>
                <div className="flex items-center space-x-4 ml-auto">
                    <ul className="flex space-x-4">
                        {rightLinks.map((rightLink) => (
                            <li key={rightLink.name}>
                                <a
                                    onClick={rightLink.onClick}
                                    className="text-white font-semibold hover:text-yellow-200 transition-colors duration-200"
                                    href="#">
                                    {rightLink.name}
                                </a>
                            </li>
                        ))}
                    </ul>
                    <Gift isActive={giftData.active} nextAvailableGift={giftData.nextAvailableGift} claimGift={claimGift} />
                    <a href="#">
                        <img
                            src={picture}
                            alt="User Avatar"
                            className="h-10 w-10 object-cover rounded-full border-2 border-white" />
                    </a>
                </div>
            </div>
        </nav>
    );
};
