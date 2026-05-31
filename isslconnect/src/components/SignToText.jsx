import React, { useRef, useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import './SignToText.css';

// Memoized so skeleton updates don't re-render video
const SkeletonPanel = React.memo(({ skeleton }) => (
    <div className="panel-box">
        <h3>✋ Hand Skeleton</h3>
        {skeleton
            ? <img src={`data:image/png;base64,${skeleton}`} alt="skeleton"
                style={{ width: 400, height: 400, borderRadius: 12, border: '3px solid #FF959C', display: 'block' }} />
            : <div style={{ width: 400, height: 400, borderRadius: 12, border: '3px solid #FF959C', background: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#ccc', fontSize: 18 }}>
                Show your hand
              </div>
        }
    </div>
));

// Stable video component - never re-renders
const CameraVideo = React.memo(React.forwardRef((props, ref) => (
    <video ref={ref} autoPlay playsInline muted
        style={{ width: 480, height: 480, borderRadius: 12, border: '3px solid #FF959C', display: 'block' }} />
)));

const SignToText = () => {
    const navigate = useNavigate();
    const videoRef = useRef(null);
    const streamRef = useRef(null);
    const predTimerRef = useRef(null);
    const runningRef = useRef(false);
    const sendingRef = useRef(false);

    const [isRunning, setIsRunning] = useState(false);
    const [currentChar, setCurrentChar] = useState('');
    const [sentence, setSentence] = useState(' ');
    const [suggestions, setSuggestions] = useState(['', '', '', '']);
    const [skeleton, setSkeleton] = useState(null);
    const [status, setStatus] = useState('');

    const sendFrame = useCallback(async () => {
        if (sendingRef.current || !runningRef.current) return;
        const video = videoRef.current;
        if (!video || video.readyState < 2) return;
        sendingRef.current = true;
        try {
            const c = document.createElement('canvas');
            c.width = 320; c.height = 320;
            c.getContext('2d').drawImage(video, 0, 0, 320, 320);
            const blob = await new Promise(r => c.toBlob(r, 'image/jpeg', 0.6));
            if (!blob) return;
            const fd = new FormData();
            fd.append('frame', blob, 'frame.jpg');
            const res = await fetch('http://localhost:3002/api/process_frame', { method: 'POST', body: fd });
            if (res.ok) {
                const data = await res.json();
                if (data.character !== undefined) setCurrentChar(String(data.character));
                if (data.sentence !== undefined) setSentence(data.sentence);
                if (data.suggestions) setSuggestions(data.suggestions);
                if (data.skeleton) setSkeleton(data.skeleton);
            }
        } catch (e) {}
        finally { sendingRef.current = false; }
    }, []);

    const startCamera = useCallback(async () => {
        try {
            setStatus('Starting...');
            const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 480, height: 480 } });
            streamRef.current = stream;
            videoRef.current.srcObject = stream;
            await videoRef.current.play();
            runningRef.current = true;
            setIsRunning(true);
            setStatus('');
            const loop = () => {
                if (!runningRef.current) return;
                sendFrame();
                predTimerRef.current = setTimeout(loop, 100);
            };
            predTimerRef.current = setTimeout(loop, 100);
        } catch (e) { setStatus('❌ ' + e.message); }
    }, [sendFrame]);

    const stopCamera = useCallback(() => {
        runningRef.current = false;
        clearTimeout(predTimerRef.current);
        streamRef.current?.getTracks().forEach(t => t.stop());
        streamRef.current = null;
        if (videoRef.current) videoRef.current.srcObject = null;
        setIsRunning(false);
        setCurrentChar(''); setSentence(' ');
        setSuggestions(['', '', '', '']); setSkeleton(null);
    }, []);

    useEffect(() => () => stopCamera(), [stopCamera]);
    const handleLogout = () => { localStorage.removeItem('token'); navigate('/'); };

    return (
        <div className="sign-to-text-page">
            <div className="sign-text-animated-bg"></div>
            <nav className="sign-text-navbar navbar-visible">
                <div className="nav-brand">ISL Connect</div>
                <div className="nav-links">
                    <a href="/text-to-sign">Text to Sign</a>
                    <a href="/sign-to-text" className="active">Sign to Text</a>
                    <a href="/about">About</a>
                    <button onClick={handleLogout} className="logout-btn"><span>🚪</span><span>Logout</span></button>
                </div>
            </nav>

            <div className="sign-text-content">
                <div className="sign-text-header">
                    <h1>🤟 Sign Language to Text</h1>
                    <p>Real-time sign detection in your browser</p>
                </div>

                {!isRunning && (
                    <div className="launch-section">
                        <div className="launch-card">
                            <div className="launch-icon">🚀</div>
                            <h2>Start Sign Detection</h2>
                            <p>Click below to open camera and start detecting signs</p>
                            <button className="launch-btn" onClick={startCamera}>
                                <span>🎥</span><span>Launch Application</span>
                            </button>
                            {status && <div className="launch-status error">{status}</div>}
                        </div>
                    </div>
                )}

                {/* Detection container - always in DOM, video ref never changes */}
                <div className="detection-container" style={{ display: isRunning ? 'block' : 'none' }}>
                    <div className="detection-panels">
                        <div className="panel-box">
                            <h3>📹 Camera Feed</h3>
                            <CameraVideo ref={videoRef} />
                        </div>
                        <SkeletonPanel skeleton={skeleton} />
                    </div>

                    <div className="output-section">
                        <div className="char-box">
                            <span className="char-label">Character:</span>
                            <span className="char-value">{currentChar}</span>
                        </div>
                        <div className="sentence-box">
                            <span className="sentence-label">Sentence:</span>
                            <span className="sentence-value">{sentence}</span>
                        </div>
                    </div>

                    <div className="suggestions-section">
                        <span className="suggestions-label">💡 Suggestions:</span>
                        <div className="suggestions-btns">
                            {suggestions.map((w, i) => w && (
                                <button key={i} className="suggestion-btn"
                                    onClick={() => setSentence(p => p.substring(0, p.lastIndexOf(' ') + 1) + w.toUpperCase())}>
                                    {w}
                                </button>
                            ))}
                        </div>
                    </div>

                    <button className="stop-btn" onClick={stopCamera}>⏹ Stop Camera</button>
                </div>
            </div>
        </div>
    );
};

export default SignToText;
