"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import Joystick from "./components/Joystick";
import SettingsModal from "./components/SettingsModal";
import Soundboard from "./components/Soundboard";

export default function PanzerbotHUD() {
  const [ipAddress, setIpAddress] = useState<string>("192.168.1.100");
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState<boolean>(false);
  const [latency, setLatency] = useState<number | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const lastPingTime = useRef<number>(0);

  // Muat IP Address dari localStorage pada saat startup
  useEffect(() => {
    const savedIp = localStorage.getItem("panzerbot_ip");
    if (savedIp) {
      setIpAddress(savedIp);
    } else {
      setIsSettingsOpen(true); // Buka pengaturan jika IP belum diset
    }
  }, []);

  // Hubungkan ke WebSocket Server
  const connectWebSocket = useCallback((ip: string) => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    const wsUrl = `ws://${ip}:8765`;
    console.log(`Menghubungkan ke WebSocket: ${wsUrl}`);
    
    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("WebSocket Terkoneksi!");
        setIsConnected(true);
        
        // Mulai interval ping untuk mengukur latensi
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            lastPingTime.current = Date.now();
            ws.send(JSON.stringify({ event: "ping", data: "" }));
          }
        }, 3000);
      };

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.event === "pong") {
            const diff = Date.now() - lastPingTime.current;
            setLatency(diff);
          }
        } catch {
          // Abaikan jika bukan JSON
        }
      };

      ws.onclose = () => {
        console.log("WebSocket Terputus.");
        setIsConnected(false);
        setLatency(null);
        cleanupPing();

        // Reconnect otomatis setelah 3 detik
        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket(ip);
        }, 3000);
      };

      ws.onerror = (err) => {
        console.error("WebSocket Error:", err);
        ws.close();
      };
    } catch (e) {
      console.error("Gagal menginisialisasi WebSocket:", e);
    }
  }, []);

  const cleanupPing = () => {
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }
  };

  // Mulai koneksi jika IP berubah
  useEffect(() => {
    if (ipAddress) {
      connectWebSocket(ipAddress);
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      cleanupPing();
    };
  }, [ipAddress, connectWebSocket]);

  // Fungsi kirim data ke WebSocket
  const sendEvent = useCallback((event: string, data: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ event, data }));
    }
  }, []);

  // Callback joystick pergerakan tank
  const handleTankMove = useCallback((x: number, y: number) => {
    sendEvent("tank_joystick", { x, y });
  }, [sendEvent]);

  // Callback joystick arah kamera
  const handleCameraMove = useCallback((x: number, y: number) => {
    sendEvent("camera_joystick", { x, y });
  }, [sendEvent]);

  // Callback mainkan suara soundboard
  const handlePlaySound = useCallback((soundName: string) => {
    sendEvent("soundboard", soundName);
  }, [sendEvent]);

  // Fungsi simpan pengaturan IP baru
  const handleSaveSettings = (newIp: string) => {
    setIpAddress(newIp);
    localStorage.setItem("panzerbot_ip", newIp);
  };

  return (
    <main className="hud-wrapper">
      {/* Video Feed (WebRTC) / Simulator Background */}
      <div className="video-feed-container">
        {isConnected ? (
          <iframe
            src={`http://${ipAddress}:8889/panzerbot/`}
            className="video-iframe"
            title="Panzerbot Camera Feed"
            allow="autoplay; encrypted-media"
          />
        ) : (
          <div className="video-placeholder">
            <div className="radar-grid" />
            <div className="connection-alert">
              <span className="warning-icon">⚠️</span>
              <h3>DISCONNECTED</h3>
              <p>Menunggu koneksi ke Panzerbot di ws://{ipAddress}:8765...</p>
              <button className="btn-secondary mt-2" onClick={() => setIsSettingsOpen(true)}>
                Buka Pengaturan
              </button>
            </div>
          </div>
        )}
      </div>

      {/* HUD HUD Overlay */}
      <div className="hud-overlay">
        {/* Top Status Bar */}
        <header className="hud-header glass">
          <div className="hud-left">
            <span className="brand">PANZERBOT v1.0</span>
            <div className={`status-indicator ${isConnected ? "online" : "offline"}`}>
              <span className="status-dot"></span>
              {isConnected ? "ONLINE" : "OFFLINE"}
            </div>
            {isConnected && latency !== null && (
              <span className="ping-indicator">LATENCY: {latency}ms</span>
            )}
          </div>

          <div className="hud-center">
            <div className="crosshair-indicator">
              <span className="hud-axis-marker"></span>
            </div>
          </div>

          <div className="hud-right">
            <button className="btn-settings" onClick={() => setIsSettingsOpen(true)}>
              ⚙️ SETTINGS
            </button>
          </div>
        </header>

        {/* Cockpit Overlay Grid (Futuristic HUD borders) */}
        <div className="cockpit-borders">
          <div className="border-bracket left" />
          <div className="border-bracket right" />
        </div>

        {/* Joystick Controls Container */}
        <div className="controls-layout">
          {/* Left Joystick: Tank Drive */}
          <div className="joystick-slot left-slot">
            <Joystick 
              label="TANK DRIVE" 
              onChange={handleTankMove} 
              color="#00d2ff" 
            />
          </div>

          {/* Right Joystick: Camera Pan-Tilt */}
          <div className="joystick-slot right-slot">
            <Joystick 
              label="CAMERA AIM" 
              onChange={handleCameraMove} 
              color="#ff3e3e" 
            />
          </div>
        </div>

        {/* Floating Soundboard Drawer */}
        <Soundboard onPlaySound={handlePlaySound} isConnected={isConnected} />
      </div>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        currentIp={ipAddress}
        onSave={handleSaveSettings}
      />
    </main>
  );
}
