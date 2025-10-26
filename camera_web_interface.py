#!/usr/bin/env python3
"""
Camera Web Interface - HTML template for camera detection
"""

# HTML template for camera detection interface
CAMERA_HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShadowHunt - Camera Detection</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;600&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Exo 2', sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
            color: white; 
            overflow-x: hidden;
            min-height: 100vh;
        }
        
        .animated-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            background: radial-gradient(circle at 20% 80%, rgba(0, 255, 255, 0.1) 0%, transparent 50%),
                        radial-gradient(circle at 80% 20%, rgba(255, 0, 255, 0.1) 0%, transparent 50%);
            animation: bgPulse 8s ease-in-out infinite;
        }
        
        @keyframes bgPulse {
            0%, 100% { opacity: 0.3; transform: scale(1); }
            50% { opacity: 0.6; transform: scale(1.05); }
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px;
            position: relative;
            z-index: 1;
        }
        .header { 
            text-align: center; 
            margin-bottom: 40px;
            animation: slideDown 1s ease-out;
        }
        
        @keyframes slideDown {
            from { transform: translateY(-50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        .title { 
            font-family: 'Orbitron', monospace;
            font-size: 3.5rem; 
            font-weight: 900;
            background: linear-gradient(45deg, #00ffff, #ff00ff, #ffff00, #00ffff);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: gradientShift 3s ease-in-out infinite, glow 2s ease-in-out infinite alternate;
            margin-bottom: 20px;
            text-shadow: 0 0 30px rgba(0, 255, 255, 0.5);
        }
        
        @keyframes gradientShift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        @keyframes glow {
            from { filter: drop-shadow(0 0 20px rgba(0, 255, 255, 0.3)); }
            to { filter: drop-shadow(0 0 40px rgba(255, 0, 255, 0.5)); }
        }
        
        .camera-section { 
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            padding: 30px; 
            border-radius: 20px; 
            margin: 30px 0;
            border: 1px solid rgba(0, 255, 255, 0.2);
            animation: slideUp 1s ease-out;
        }
        
        @keyframes slideUp {
            from { transform: translateY(50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        .btn { 
            background: linear-gradient(45deg, #00ffff, #ff00ff);
            color: white;
            padding: 18px 36px;
            border: none;
            border-radius: 50px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin: 15px;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 10px 20px rgba(0, 255, 255, 0.3);
        }
        
        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s ease;
        }
        
        .btn:hover::before {
            left: 100%;
        }
        
        .btn:hover { 
            transform: translateY(-3px);
            box-shadow: 0 15px 30px rgba(255, 0, 255, 0.4);
            background: linear-gradient(45deg, #ff00ff, #00ffff);
        }
        
        .btn:disabled { 
            background: #666; 
            cursor: not-allowed;
            box-shadow: none;
            transform: none;
        }
        
        .btn.danger { 
            background: linear-gradient(45deg, #ff4444, #ff6666);
        }
        .btn.danger:hover { 
            background: linear-gradient(45deg, #cc3333, #ff4444);
        }
        
        .btn.success { 
            background: linear-gradient(45deg, #44ff44, #66ff66);
        }
        .btn.success:hover { 
            background: linear-gradient(45deg, #33cc33, #44ff44);
        }
        .camera-list { 
            margin: 30px 0; 
            display: grid;
            gap: 20px;
        }
        
        .camera-item { 
            background: linear-gradient(135deg, rgba(0, 255, 255, 0.1), rgba(255, 0, 255, 0.05));
            backdrop-filter: blur(10px);
            padding: 25px; 
            border-radius: 20px; 
            border: 2px solid rgba(0, 255, 255, 0.3);
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
        }
        
        .camera-item::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(0, 255, 255, 0.1), transparent);
            transform: rotate(45deg);
            transition: all 0.6s ease;
            opacity: 0;
        }
        
        .camera-item:hover::before {
            animation: shimmer 1.5s ease-in-out;
        }
        
        .camera-item:hover {
            background: linear-gradient(135deg, rgba(0, 255, 255, 0.2), rgba(255, 0, 255, 0.1));
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 40px rgba(0, 255, 255, 0.3);
            border-color: #ff00ff;
        }
        
        .camera-item h3 { 
            margin: 0 0 15px 0; 
            color: #00ffff;
            font-family: 'Orbitron', monospace;
            font-size: 1.3rem;
            font-weight: 700;
            text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
        }
        
        .camera-item p { 
            margin: 8px 0; 
            color: #b0b0b0;
            font-size: 0.95rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .camera-item .camera-spec {
            background: rgba(0, 0, 0, 0.3);
            padding: 8px 12px;
            border-radius: 8px;
            font-family: 'Orbitron', monospace;
            font-size: 0.85rem;
            color: #fff;
        }
        .camera-controls { 
            margin: 30px 0;
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            justify-content: center;
        }
        
        .camera-preview { 
            width: 100%; 
            height: 450px; 
            background: linear-gradient(135deg, #000, #1a1a2e);
            border: 3px solid rgba(0, 255, 255, 0.4);
            border-radius: 20px; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            color: #666; 
            font-size: 20px;
            margin: 30px 0;
            position: relative;
            overflow: hidden;
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.5);
            transition: all 0.3s ease;
        }
        
        .camera-preview::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at center, rgba(0, 255, 255, 0.1) 0%, transparent 70%);
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .camera-preview.active::before {
            opacity: 1;
        }
        
        .camera-preview img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.8);
        }
        
        .camera-preview.active { 
            background: linear-gradient(135deg, #000, #0a0a1a);
            color: #00ffff;
            border-color: #00ff00;
            box-shadow: 0 20px 40px rgba(0, 255, 0, 0.3);
        }
        
        .camera-preview.error {
            border-color: #ff4444;
            background: linear-gradient(135deg, #1a0000, #2a0000);
            color: #ff6666;
        }
        
        .status-indicator {
            position: absolute;
            top: 15px;
            right: 15px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #666;
            transition: all 0.3s ease;
        }
        
        .status-indicator.active {
            background: #00ff00;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.8);
            animation: pulse 2s ease-in-out infinite;
        }
        
        .status-indicator.error {
            background: #ff4444;
            box-shadow: 0 0 15px rgba(255, 68, 68, 0.8);
            animation: pulse 1s ease-in-out infinite;
        }
        
        .status { 
            padding: 20px; 
            border-radius: 15px; 
            margin: 25px 0; 
            font-weight: bold;
            backdrop-filter: blur(10px);
            border: 2px solid;
            animation: slideIn 0.5s ease-out;
        }
        
        .status.success { 
            background: linear-gradient(135deg, rgba(68, 255, 68, 0.2), rgba(0, 255, 0, 0.1)); 
            border-color: #44ff44;
            color: #44ff44;
            box-shadow: 0 10px 20px rgba(68, 255, 68, 0.3);
        }
        
        .status.error { 
            background: linear-gradient(135deg, rgba(255, 68, 68, 0.2), rgba(255, 0, 0, 0.1)); 
            border-color: #ff4444;
            color: #ff6666;
            box-shadow: 0 10px 20px rgba(255, 68, 68, 0.3);
        }
        
        .status.warning { 
            background: linear-gradient(135deg, rgba(255, 255, 68, 0.2), rgba(255, 255, 0, 0.1)); 
            border-color: #ffff44;
            color: #ffff88;
            box-shadow: 0 10px 20px rgba(255, 255, 68, 0.3);
        }
        
        .results { 
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(15px);
            padding: 30px; 
            border-radius: 20px; 
            margin: 30px 0;
            border: 1px solid rgba(0, 255, 255, 0.2);
            animation: slideIn 0.8s ease-out;
        }
        
        .progress { 
            display: none; 
            text-align: center; 
            margin: 30px 0;
            animation: fadeIn 0.5s ease-out;
        }
        
        .progress-bar { 
            width: 100%; 
            height: 25px; 
            background: rgba(0, 0, 0, 0.3);
            border-radius: 50px;
            overflow: hidden;
            border: 2px solid rgba(0, 255, 255, 0.3);
        }
        
        .progress-fill { 
            height: 100%; 
            background: linear-gradient(90deg, #00ffff, #ff00ff, #ffff00);
            background-size: 200% 100%;
            width: 0%; 
            transition: width 0.3s ease;
            animation: progressShine 2s ease-in-out infinite;
        }
        
        .details { 
            margin: 20px 0; 
            padding: 20px; 
            background: rgba(0, 0, 0, 0.3);
            border-radius: 15px;
            border-left: 4px solid #00ffff;
            transition: all 0.3s ease;
        }
        
        .details:hover {
            background: rgba(0, 0, 0, 0.4);
            border-left-color: #ff00ff;
            transform: translateX(10px);
        }
        .back-link { 
            display: inline-flex;
            align-items: center;
            color: #00ffff; 
            text-decoration: none; 
            margin-bottom: 30px; 
            padding: 15px 25px;
            border-radius: 50px;
            background: linear-gradient(135deg, rgba(0, 255, 255, 0.1), rgba(255, 0, 255, 0.05));
            border: 2px solid rgba(0, 255, 255, 0.3);
            transition: all 0.4s ease;
            font-weight: 600;
            font-size: 1rem;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 20px rgba(0, 255, 255, 0.2);
        }
        
        .back-link::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.6s ease;
        }
        
        .back-link:hover::before {
            left: 100%;
        }
        
        .back-link:hover { 
            background: linear-gradient(135deg, rgba(0, 255, 255, 0.2), rgba(255, 0, 255, 0.1));
            transform: translateX(-8px) translateY(-2px);
            box-shadow: 0 15px 30px rgba(0, 255, 255, 0.4);
            border-color: #ff00ff;
            color: #fff;
            text-decoration: none;
        }
        
        .back-link .back-icon {
            margin-right: 10px;
            font-size: 1.2rem;
            transition: transform 0.3s ease;
        }
        
        .back-link:hover .back-icon {
            transform: translateX(-3px);
        }
        
        .title-container {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
        }
        
        .camera-icon {
            width: 80px;
            height: 80px;
            margin-right: 20px;
            position: relative;
            animation: cameraPulse 3s ease-in-out infinite;
            filter: drop-shadow(0 0 20px rgba(0, 255, 255, 0.6));
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .camera-icon::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 60px;
            height: 45px;
            background: linear-gradient(135deg, #00ffff, #ff00ff);
            border-radius: 8px;
            border: 3px solid #fff;
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
        }
        
        .camera-icon::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 20px;
            height: 20px;
            background: #fff;
            border-radius: 50%;
            border: 2px solid #00ffff;
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.8);
        }
        
        .camera-icon:hover {
            transform: scale(1.1) rotate(5deg);
            filter: drop-shadow(0 0 30px rgba(255, 0, 255, 0.8));
        }
        
        .camera-icon:hover::before {
            background: linear-gradient(135deg, #ff00ff, #00ffff);
            box-shadow: 0 0 25px rgba(255, 0, 255, 0.7);
        }
        
        .camera-icon:hover::after {
            border-color: #ff00ff;
            box-shadow: 0 0 20px rgba(255, 0, 255, 0.9);
        }
        
        @keyframes cameraPulse {
            0%, 100% { 
                transform: scale(1);
                filter: drop-shadow(0 0 20px rgba(0, 255, 255, 0.6));
            }
            50% { 
                transform: scale(1.05);
                filter: drop-shadow(0 0 30px rgba(255, 0, 255, 0.8));
            }
        }
        .camera-preview { 
            width: 100%; 
            max-width: 640px; 
            height: 480px; 
            background: #333; 
            border: 2px solid #00ffff; 
            border-radius: 10px; 
            margin: 20px auto; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            color: #666; 
            font-size: 18px; 
        }
        .camera-preview.active { 
            background: #000; 
            color: #00ffff; 
        }
        .floating-particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
        }
        
        .particle {
            position: absolute;
            width: 4px;
            height: 4px;
            background: rgba(0, 255, 255, 0.5);
            border-radius: 50%;
            animation: float 6s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0; }
            10%, 90% { opacity: 1; }
            50% { transform: translateY(-100px) rotate(180deg); }
        }
        
        /* ID Verification Card Styles */
        .id-verification-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(15px);
            border-radius: 20px;
            padding: 40px;
            margin: 30px 0;
            border: 2px solid rgba(0, 255, 255, 0.3);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            animation: slideIn 0.8s ease-out;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .verification-header {
            display: flex;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid rgba(0, 255, 255, 0.2);
        }
        
        .verification-icon {
            font-size: 4rem;
            margin-right: 20px;
            animation: pulse 2s ease-in-out infinite;
        }
        
        .verification-icon.verified {
            color: #00ff00;
            text-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
        }
        
        .verification-icon.rejected {
            color: #ff4444;
            text-shadow: 0 0 20px rgba(255, 68, 68, 0.5);
        }
        
        .verification-title h2 {
            font-family: 'Orbitron', monospace;
            font-size: 1.8rem;
            font-weight: 700;
            color: #00ffff;
            margin-bottom: 5px;
            letter-spacing: 2px;
        }
        
        .verification-title p {
            color: #b0b0b0;
            font-size: 1rem;
            margin: 0;
        }
        
        .verification-status {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .status-badge {
            display: inline-block;
            padding: 15px 30px;
            border-radius: 50px;
            margin-bottom: 15px;
            font-family: 'Orbitron', monospace;
            font-weight: 700;
            font-size: 1.2rem;
            letter-spacing: 1px;
            animation: statusGlow 2s ease-in-out infinite alternate;
        }
        
        .verification-status.real .status-badge {
            background: linear-gradient(45deg, #00ff00, #44ff44);
            color: #000;
            border: 2px solid #00ff00;
        }
        
        .verification-status.fake .status-badge {
            background: linear-gradient(45deg, #ff4444, #ff6666);
            color: #fff;
            border: 2px solid #ff4444;
        }
        
        .confidence-score {
            margin-top: 15px;
        }
        
        .score-label {
            color: #b0b0b0;
            font-size: 0.9rem;
            margin-bottom: 5px;
        }
        
        .score-value {
            font-family: 'Orbitron', monospace;
            font-size: 2.5rem;
            font-weight: 900;
            color: #00ffff;
            text-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
        }
        
        .verification-details {
            margin-bottom: 30px;
        }
        
        .detail-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .detail-row:last-child {
            border-bottom: none;
        }
        
        .detail-label {
            color: #b0b0b0;
            font-weight: 600;
            font-size: 0.9rem;
        }
        
        .detail-value {
            color: #fff;
            font-weight: 400;
            font-size: 0.9rem;
        }
        
        .verification-summary {
            margin-bottom: 30px;
        }
        
        .summary-title {
            font-family: 'Orbitron', monospace;
            font-size: 1.2rem;
            font-weight: 700;
            color: #00ffff;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .summary-item {
            margin-bottom: 15px;
        }
        
        .summary-label {
            color: #b0b0b0;
            font-size: 0.9rem;
            margin-bottom: 8px;
            display: block;
        }
        
        .summary-bar {
            position: relative;
            height: 25px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 15px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .summary-fill {
            height: 100%;
            border-radius: 15px;
            transition: width 1s ease-out;
            position: relative;
        }
        
        .summary-fill.real {
            background: linear-gradient(90deg, #00ff00, #44ff44);
        }
        
        .summary-fill.fake {
            background: linear-gradient(90deg, #ff4444, #ff6666);
        }
        
        .summary-percentage {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            color: #fff;
            font-weight: 700;
            font-size: 0.8rem;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
        }
        
        .verification-footer {
            text-align: center;
            padding-top: 20px;
            border-top: 2px solid rgba(0, 255, 255, 0.2);
        }
        
        .footer-text {
            color: #b0b0b0;
            font-size: 1rem;
            line-height: 1.5;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="animated-bg"></div>
    
    <div class="floating-particles" id="particles"></div>
    
    <div class="container">
        <a href="/" class="back-link">
            <span class="back-icon">←</span>
            Back to ShadowHunt
        </a>
        
        <div class="header">
            <div class="title-container">
                <div class="camera-icon"></div>
                <h1 class="title">Camera Detection</h1>
            </div>
            <p>Detect fake/virtual cameras and verify camera authenticity</p>
        </div>
        
        <div class="camera-section">
            <h2>Laptop Camera</h2>
            <div style="display: flex; gap: 15px; margin-bottom: 20px; flex-wrap: wrap;">
                <button class="btn" onclick="loadCameras()">🔍 Detect Camera</button>
                <button class="btn" onclick="refreshCameras()">🔄 Refresh</button>
                <button class="btn" onclick="checkCameraPermissions()">🔐 Check Permissions</button>
                <button class="btn" onclick="showCameraTroubleshooting()">❓ Troubleshooting</button>
            </div>
            <div id="cameraList" class="camera-list"></div>
        </div>
        
        <div class="camera-section">
            <h2>Camera Control</h2>
            <div id="cameraControl" style="display: none;">
                <button class="btn success" id="startBtn" onclick="startCameraStream()">▶️ Start Stream</button>
                <button class="btn danger" id="stopBtn" onclick="stopCameraStream()" disabled>⏹️ Stop Stream</button>
                <button class="btn" id="analyzeBtn" onclick="analyzeCamera()" disabled>🔍 Analyze Camera</button>
            </div>
            <div id="selectedCameraInfo"></div>
            
            <div class="camera-preview" id="cameraPreview">
                <div class="status-indicator" id="statusIndicator"></div>
                <div style="text-align: center;">
                    <div style="font-size: 3rem; margin-bottom: 20px; opacity: 0.5;">📷</div>
                    <div>Camera feed will appear here</div>
                    <div style="font-size: 0.9rem; margin-top: 10px; opacity: 0.7;">Start streaming your laptop camera</div>
                </div>
            </div>
        </div>
        
        <div class="progress" id="progressContainer">
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <p id="progressText">Analyzing camera...</p>
        </div>
        
        <div id="statusContainer"></div>
        <div id="resultsContainer"></div>
    </div>

    <script>
        let availableCameras = [];
        let selectedCameraIndex = 0;
        let isStreaming = false;
        
        // Create floating particles
        function createParticles() {
            const particlesContainer = document.getElementById('particles');
            const particleCount = 30;
            
            for (let i = 0; i < particleCount; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.top = Math.random() * 100 + '%';
                particle.style.animationDelay = Math.random() * 6 + 's';
                particle.style.animationDuration = (Math.random() * 3 + 3) + 's';
                particlesContainer.appendChild(particle);
            }
        }
        
        // Initialize particles on page load
        window.addEventListener('load', createParticles);
        
        async function loadCameras() {
            const cameraList = document.getElementById('cameraList');
            const cameraControl = document.getElementById('cameraControl');
            const statusContainer = document.getElementById('statusContainer');
            
            statusContainer.innerHTML = '<div class="status warning">Scanning for cameras...</div>';
            
            try {
                const response = await fetch('/api/cameras');
                const result = await response.json();
                
                if (result.error) {
                    statusContainer.innerHTML = `<div class="status error">Error: ${result.error}</div>`;
                    return;
                }
                
                availableCameras = result;
                cameraList.innerHTML = '';
                
                if (availableCameras.length === 0) {
                    cameraList.innerHTML = '<div class="status warning">No cameras found. Please connect a camera and try again.</div>';
                } else {
                    const camera = availableCameras[0];
                    const cameraDiv = document.createElement('div');
                    cameraDiv.className = 'camera-item';
                    cameraDiv.innerHTML = `
                        <h3>${camera.name}</h3>
                        <p><strong>Type:</strong> ${camera.type || 'Unknown Camera'}</p>
                        <p><strong>Index:</strong> ${camera.index}</p>
                        <p><strong>Resolution:</strong> ${camera.width}x${camera.height}</p>
                        <p><strong>FPS:</strong> ${camera.fps}</p>
                        <p><strong>Backend:</strong> ${camera.backend_type || camera.backend || 'Unknown'}</p>
                        <p><strong>Reliability:</strong> ${camera.reliability ? (camera.reliability * 100).toFixed(0) + '%' : 'Unknown'}</p>
                        <div style="display: flex; gap: 10px; margin-top: 15px;">
                            <button class="btn" onclick="selectCamera(${camera.index})">Use Laptop Camera</button>
                            <button class="btn" onclick="testCamera(${camera.index})">Test Camera</button>
                        </div>`;
                    cameraList.appendChild(cameraDiv);
                    cameraControl.style.display = 'block';

                    // Auto-select the preferred camera for a one-click start
                    selectCamera(camera.index);
                }
                
                statusContainer.innerHTML = `<div class="status success">Found ${availableCameras.length} camera(s)</div>`;
                
            } catch (error) {
                statusContainer.innerHTML = `<div class="status error">Failed to load cameras: ${error.message}</div>`;
            }
        }
        
        function selectCamera(cameraIndex) {
            selectedCameraIndex = cameraIndex;
            const camera = availableCameras.find(c => c.index === cameraIndex);
            
            if (camera) {
                document.getElementById('selectedCameraInfo').innerHTML = `
                    <div class="status success">
                        <strong>Selected Camera:</strong> ${camera.name} (${camera.width}x${camera.height})
                    </div>
                `;
                
                // Enable start button
                document.getElementById('startBtn').disabled = false;
                
                // Start showing camera preview
                startCameraPreview(cameraIndex);
            }
        }
        
        function startCameraPreview(cameraIndex) {
            const preview = document.getElementById('cameraPreview');
            preview.innerHTML = 'Loading camera feed...';
            preview.className = 'camera-preview active';
            
            let feedInterval;
            
            // Update camera feed every 200ms
            const updateFeed = async () => {
                if (selectedCameraIndex === cameraIndex) {
                    try {
                        const response = await fetch(`/api/camera-feed/${cameraIndex}`);
                        const result = await response.json();
                        
                        if (result.success && result.frame) {
                            preview.innerHTML = `<img src="${result.frame}" style="max-width: 100%; max-height: 100%; object-fit: contain;" />`;
                        } else if (result.error) {
                            preview.innerHTML = `Camera Error: ${result.error}`;
                        } else {
                            preview.innerHTML = 'Waiting for camera...';
                        }
                    } catch (error) {
                        preview.innerHTML = 'Camera feed error: ' + error.message;
                    }
                }
            };
            
            // Start the feed update loop
            feedInterval = setInterval(updateFeed, 200);
            
            // Store interval ID for cleanup
            window.cameraFeedInterval = feedInterval;
            
            // Initial update
            updateFeed();
        }
        
        function stopCameraPreview() {
            if (window.cameraFeedInterval) {
                clearInterval(window.cameraFeedInterval);
                window.cameraFeedInterval = null;
            }
            
            const preview = document.getElementById('cameraPreview');
            preview.innerHTML = 'Camera preview stopped';
            preview.className = 'camera-preview';
        }
        
        async function startCameraStream() {
            if (selectedCameraIndex === null) {
                showStatus('Please select a camera first', 'error');
                return;
            }
            
            const statusContainer = document.getElementById('statusContainer');
            statusContainer.innerHTML = '<div class="status warning">Starting camera stream...</div>';
            
            try {
                const response = await fetch(`/api/start-stream/${selectedCameraIndex ?? 0}`, {
                    method: 'POST'
                });
                let result;
                try {
                    result = await response.json();
                } catch (e) {
                    const txt = await response.text();
                    throw new Error(txt || 'Unexpected server response');
                }
                
                if (response.ok && result && result.success) {
                    isStreaming = true;
                    document.getElementById('startBtn').disabled = true;
                    document.getElementById('stopBtn').disabled = false;
                    document.getElementById('analyzeBtn').disabled = false;
                    
                    statusContainer.innerHTML = '<div class="status success">Camera stream started successfully!</div>';
                } else {
                    const msg = (result && result.error) ? result.error : 'Unknown error';
                    statusContainer.innerHTML = `<div class="status error">Failed to start stream: ${msg}</div>`;
                }
                
            } catch (error) {
                statusContainer.innerHTML = `<div class="status error">Error starting stream: ${error.message}</div>`;
            }
        }
        
        async function stopCameraStream() {
            const statusContainer = document.getElementById('statusContainer');
            statusContainer.innerHTML = '<div class="status warning">Stopping camera stream...</div>';
            
            // Stop camera preview
            stopCameraPreview();
            
            try {
                const response = await fetch('/api/stop-stream', {
                    method: 'POST'
                });
                let result;
                try {
                    result = await response.json();
                } catch (e) {
                    const txt = await response.text();
                    result = { success: false, error: txt || 'Unexpected server response' };
                }
                
                if (result.success) {
                    isStreaming = false;
                    document.getElementById('startBtn').disabled = false;
                    document.getElementById('stopBtn').disabled = true;
                    document.getElementById('analyzeBtn').disabled = true;
                    
                    statusContainer.innerHTML = '<div class="status success">Camera stream stopped</div>';
                } else {
                    statusContainer.innerHTML = `<div class="status error">Failed to stop stream: ${result.error}</div>`;
                }
                
            } catch (error) {
                statusContainer.innerHTML = `<div class="status error">Error stopping stream: ${error.message}</div>`;
            }
        }
        
        async function analyzeCamera() {
            if (!isStreaming) {
                showStatus('Please start camera stream first', 'error');
                return;
            }
            
            const progressContainer = document.getElementById('progressContainer');
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            const resultsContainer = document.getElementById('resultsContainer');
            
            // Show progress
            progressContainer.style.display = 'block';
            resultsContainer.innerHTML = '';
            
            // Simulate progress
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += Math.random() * 10;
                if (progress > 85) progress = 85;
                progressFill.style.width = progress + '%';
            }, 200);
            
            try {
                const response = await fetch('/api/analyze-camera', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        camera_index: selectedCameraIndex ?? 0,
                        duration: 3
                    })
                });
                
                clearInterval(progressInterval);
                progressFill.style.width = '100%';
                progressText.textContent = 'Analysis complete!';
                
                setTimeout(async () => {
                    let result;
                    try {
                        result = await response.json();
                    } catch (e) {
                        const txt = await response.text();
                        result = { error: txt || 'Unexpected server response' };
                    }
                    
                    if (result.error) {
                        showStatus(`Analysis failed: ${result.error}`, 'error');
                    } else {
                        displayAnalysisResults(result);
                    }
                    
                    progressContainer.style.display = 'none';
                }, 500);
                
            } catch (error) {
                clearInterval(progressInterval);
                progressContainer.style.display = 'none';
                showStatus(`Analysis failed: ${error.message}`, 'error');
            }
        }
        
        function displayAnalysisResults(results) {
            const resultsContainer = document.getElementById('resultsContainer');
            const summary = results.analysis_summary;
            
            const isReal = !summary.is_fake_camera;
            const authenticityScore = Math.round(summary.avg_authenticity_score * 100);
            const fakeScore = Math.round(summary.fake_percentage);
            
            // Clear ID Verification Style Display for Camera
            let html = `
                <div class="id-verification-card">
                    <div class="verification-header">
                        <div class="verification-icon ${isReal ? 'verified' : 'rejected'}">
                            ${isReal ? '✅' : '❌'}
                        </div>
                        <div class="verification-title">
                            <h2>CAMERA VERIFICATION</h2>
                            <p>Hardware Authenticity Check</p>
                        </div>
                    </div>
                    
                    <div class="verification-status ${isReal ? 'real' : 'fake'}">
                        <div class="status-badge">
                            <span class="status-text">${isReal ? 'GENUINE CAMERA' : 'FAKE CAMERA DETECTED'}</span>
                        </div>
                        <div class="confidence-score">
                            <div class="score-label">Authenticity Score</div>
                            <div class="score-value">${authenticityScore}%</div>
                        </div>
                    </div>
                    
                    <div class="verification-details">
                        <div class="detail-row">
                            <span class="detail-label">Analysis Duration:</span>
                            <span class="detail-value">${summary.duration_seconds} seconds</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Frames Analyzed:</span>
                            <span class="detail-value">${summary.total_frames}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Detection Methods:</span>
                            <span class="detail-value">7 Advanced Algorithms</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Timestamp:</span>
                            <span class="detail-value">${new Date().toLocaleString()}</span>
                        </div>
                    </div>
                    
                    <div class="verification-summary">
                        <div class="summary-title">Analysis Summary</div>
                        <div class="summary-content">
                            <div class="summary-item">
                                <span class="summary-label">Authenticity Score:</span>
                                <div class="summary-bar">
                                    <div class="summary-fill real" style="width: ${authenticityScore}%"></div>
                                    <span class="summary-percentage">${authenticityScore}%</span>
                                </div>
                            </div>
                            <div class="summary-item">
                                <span class="summary-label">Fake Indicators:</span>
                                <div class="summary-bar">
                                    <div class="summary-fill fake" style="width: ${fakeScore}%"></div>
                                    <span class="summary-percentage">${fakeScore}%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="verification-footer">
                        <div class="footer-text">
                            ${isReal ? 
                                '✅ This camera appears to be genuine hardware and safe for use.' : 
                                '⚠️ This camera has been identified as potentially fake or virtual.'
                            }
                        </div>
                        <div style="margin-top: 15px; font-size: 0.9rem; color: #888;">
                            ${results.recommendation}
                        </div>
                    </div>
                </div>
            `;
            
            resultsContainer.innerHTML = html;
        }
        
        function showStatus(message, type = 'warning') {
            const statusContainer = document.getElementById('statusContainer');
            statusContainer.innerHTML = `<div class="status ${type}">${message}</div>`;
        }
        
        async function refreshCameras() {
            const statusContainer = document.getElementById('statusContainer');
            statusContainer.innerHTML = '<div class="status warning">Refreshing camera list...</div>';
            
            try {
                const response = await fetch('/api/refresh-cameras', {
                    method: 'POST'
                });
                const result = await response.json();
                
                if (result.error) {
                    statusContainer.innerHTML = `<div class="status error">Error: ${result.error}</div>`;
                    return;
                }
                
                availableCameras = result.cameras;
                const cameraList = document.getElementById('cameraList');
                cameraList.innerHTML = '';
                
                if (availableCameras.length === 0) {
                    cameraList.innerHTML = '<div class="status warning">No cameras found. Please check troubleshooting tips below.</div>';
                } else {
                    availableCameras.forEach((camera, index) => {
                        const cameraDiv = document.createElement('div');
                        cameraDiv.className = 'camera-item';
                        cameraDiv.innerHTML = `
                            <h3>${camera.name}</h3>
                            <p><strong>Type:</strong> ${camera.type || 'Unknown Camera'}</p>
                            <p><strong>Index:</strong> ${camera.index}</p>
                            <p><strong>Resolution:</strong> ${camera.width}x${camera.height}</p>
                            <p><strong>FPS:</strong> ${camera.fps}</p>
                            <p><strong>Backend:</strong> ${camera.backend_type || camera.backend || 'Unknown'}</p>
                            <p><strong>Reliability:</strong> ${camera.reliability ? (camera.reliability * 100).toFixed(0) + '%' : 'Unknown'}</p>
                            <div style="display: flex; gap: 10px; margin-top: 15px;">
                                <button class="btn" onclick="selectCamera(${camera.index})">Select Camera</button>
                                <button class="btn" onclick="testCamera(${camera.index})">Test Camera</button>
                            </div>
                        `;
                        cameraList.appendChild(cameraDiv);
                    });
                }
                
                statusContainer.innerHTML = `<div class="status success">Found ${availableCameras.length} camera(s) after refresh</div>`;
                
            } catch (error) {
                statusContainer.innerHTML = `<div class="status error">Failed to refresh cameras: ${error.message}</div>`;
            }
        }
        
        async function testCamera(cameraIndex) {
            const statusContainer = document.getElementById('statusContainer');
            statusContainer.innerHTML = '<div class="status warning">🔄 Testing camera access... Please wait...</div>';
            
            try {
                // Test camera feed endpoint
                const response = await fetch(`/api/camera-feed/${cameraIndex}`);
                let result;
                try {
                    result = await response.json();
                } catch (e) {
                    const txt = await response.text();
                    result = { error: txt || 'Unexpected server response' };
                }
                
                if (result.success) {
                    const cameraType = result.camera_type || 'Unknown';
                    const frameShape = result.frame_shape ? `${result.frame_shape[1]}x${result.frame_shape[0]}` : 'Unknown';
                    
                    statusContainer.innerHTML = `
                        <div class="status success">
                            <h3>✅ Camera ${cameraIndex} Test Successful!</h3>
                            <div style="text-align: left; margin: 15px 0;">
                                <p><strong>Camera Type:</strong> ${cameraType}</p>
                                <p><strong>Frame Size:</strong> ${frameShape}</p>
                                <p><strong>Status:</strong> Working correctly</p>
                            </div>
                            <p style="color: #00ff00; font-weight: bold;">🎉 Your camera is ready to use!</p>
                        </div>
                    `;
                } else {
                    statusContainer.innerHTML = `
                        <div class="status error">
                            <h3>❌ Camera ${cameraIndex} Test Failed</h3>
                            <p><strong>Error:</strong> ${result.error}</p>
                            <div style="margin-top: 15px;">
                                <p><strong>Common Solutions:</strong></p>
                                <ul style="text-align: left; margin: 10px 0;">
                                    <li>Make sure no other applications are using the camera</li>
                                    <li>Check camera permissions in Windows Settings</li>
                                    <li>Try running the application as administrator</li>
                                    <li>Restart your computer</li>
                                </ul>
                            </div>
                        </div>
                    `;
                }
            } catch (error) {
                statusContainer.innerHTML = `
                    <div class="status error">
                        <h3>❌ Camera ${cameraIndex} Test Failed</h3>
                        <p><strong>Network Error:</strong> ${error.message}</p>
                        <p>Please check your connection and try again.</p>
                    </div>
                `;
            }
        }
        
        async function checkCameraPermissions() {
            const statusContainer = document.getElementById('statusContainer');
            statusContainer.innerHTML = '<div class="status warning">Checking camera permissions and system status...</div>';
            
            try {
                const response = await fetch('/api/camera-permissions');
                const result = await response.json();
                
                if (result.error) {
                    statusContainer.innerHTML = `<div class="status error">❌ Error checking permissions: ${result.error}</div>`;
                    return;
                }
                
                const systemInfo = result.system_info;
                const basicAccess = result.basic_camera_access ? '✅ Available' : '❌ Not Available';
                const laptopCameras = result.laptop_cameras || 0;
                const externalCameras = result.external_cameras || 0;
                
                statusContainer.innerHTML = `
                    <div class="status success">
                        <h3>🔐 Camera Permissions & System Status</h3>
                        <div style="text-align: left; margin: 15px 0;">
                            <p><strong>Operating System:</strong> ${systemInfo.os} ${systemInfo.os_version}</p>
                            <p><strong>Python Version:</strong> ${systemInfo.python_version}</p>
                            <p><strong>OpenCV Version:</strong> ${systemInfo.opencv_version}</p>
                            <p><strong>Basic Camera Access:</strong> ${basicAccess}</p>
                            <p><strong>Laptop Cameras Found:</strong> ${laptopCameras}</p>
                            <p><strong>External Cameras Found:</strong> ${externalCameras}</p>
                        </div>
                        <div style="margin-top: 15px;">
                            ${result.basic_camera_access ? 
                                '<p style="color: #00ff00;">✅ Camera access is working properly!</p>' : 
                                '<p style="color: #ff4444;">❌ Camera access issues detected. Check troubleshooting guide.</p>'
                            }
                        </div>
                    </div>
                `;
            } catch (error) {
                statusContainer.innerHTML = `<div class="status error">❌ Failed to check permissions: ${error.message}</div>`;
            }
        }
        
        function showCameraTroubleshooting() {
            const statusContainer = document.getElementById('statusContainer');
            statusContainer.innerHTML = `
                <div class="status warning">
                    <h3>Camera Troubleshooting Guide</h3>
                    <ul style="text-align: left; margin: 15px 0;">
                        <li><strong>No cameras detected:</strong>
                            <ul>
                                <li>Make sure your camera is connected and not being used by another application</li>
                                <li>Check camera permissions in your system settings</li>
                                <li>Try running the application as administrator (Windows)</li>
                                <li>Restart your camera or unplug/replug USB cameras</li>
                                <li>Close other applications that might be using the camera (Zoom, Skype, etc.)</li>
                            </ul>
                        </li>
                        <li><strong>Camera not working:</strong>
                            <ul>
                                <li>Try refreshing the camera list</li>
                                <li>Select a different camera if multiple are available</li>
                                <li>Check if your camera drivers are up to date</li>
                                <li>Try restarting the application</li>
                            </ul>
                        </li>
                        <li><strong>Poor image quality:</strong>
                            <ul>
                                <li>Ensure good lighting conditions</li>
                                <li>Clean your camera lens</li>
                                <li>Check camera focus settings</li>
                            </ul>
                        </li>
                    </ul>
                    <button class="btn" onclick="refreshCameras()" style="margin-top: 15px;">Try Refreshing Cameras</button>
                </div>
            `;
        }
        
        // Load cameras on page load
        window.addEventListener('load', () => {
            loadCameras();
        });
    </script>
</body>
</html>
'''

