import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";

export default function Nav() {
    const location = useLocation();
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const onScroll = () => setScrolled(window.scrollY > 20);
        window.addEventListener("scroll", onScroll, { passive: true });
        return () => window.removeEventListener("scroll", onScroll);
    }, []);

    return (
        <nav className={`nav ${scrolled ? "scrolled" : ""}`}>
            <div className="nav-inner">
                <Link to="/" className="nav-logo">
                    <svg viewBox="0 0 24 24" fill="none" stroke="url(#grad)" strokeWidth="2.5" strokeLinecap="round">
                        <defs>
                            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stopColor="#06b6d4" />
                                <stop offset="100%" stopColor="#d946ef" />
                            </linearGradient>
                        </defs>
                        <circle cx="12" cy="12" r="3" />
                        <path d="M12 2v4m0 12v4M2 12h4m12 0h4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83" />
                    </svg>
                    Antigravity
                </Link>
                <ul className="nav-links">
                    <li><Link to="/" className={location.pathname === "/" ? "active" : ""}>Home</Link></li>
                    <li><Link to="/catalog" className={location.pathname === "/catalog" ? "active" : ""}>Simulations</Link></li>
                    <li><a href="https://github.com" target="_blank" rel="noopener">GitHub</a></li>
                </ul>
            </div>
        </nav>
    );
}
