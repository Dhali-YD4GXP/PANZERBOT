"use client";

import React, { useRef, useState, useEffect } from "react";

interface JoystickProps {
  label: string;
  onChange: (x: number, y: number) => void;
  color?: string;
}

export default function Joystick({ label, onChange, color = "var(--primary-glow)" }: JoystickProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);

  // Batasi pemanggilan onChange menggunakan throttle/interval
  const lastSent = useRef<{ x: number; y: number }>({ x: 0, y: 0 });
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const handleStart = (clientX: number, clientY: number) => {
    setIsDragging(true);
    updatePosition(clientX, clientY);
  };

  const handleMove = (clientX: number, clientY: number) => {
    if (!isDragging) return;
    updatePosition(clientX, clientY);
  };

  const handleEnd = () => {
    setIsDragging(false);
    setPosition({ x: 0, y: 0 });
  };

  const updatePosition = (clientX: number, clientY: number) => {
    if (!containerRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const radius = rect.width / 2;

    // Hitung jarak dari pusat
    let dx = clientX - centerX;
    let dy = clientY - centerY;
    const distance = Math.sqrt(dx * dx + dy * dy);

    // Batasi pergerakan joystick knob agar tidak keluar dari ring (radius)
    if (distance > radius) {
      dx = (dx / distance) * radius;
      dy = (dy / distance) * radius;
    }

    setPosition({ x: dx, y: dy });
  };

  // Kirim data berkala jika sedang menyeret knob
  useEffect(() => {
    if (isDragging) {
      intervalRef.current = setInterval(() => {
        if (!containerRef.current) return;
        const rect = containerRef.current.getBoundingClientRect();
        const radius = rect.width / 2;

        // Normalisasi nilai antara -1.0 s.d 1.0
        // Sumbu Y dibalik karena koordinat layar Y bernilai positif ke bawah
        const normalizedX = parseFloat((position.x / radius).toFixed(2));
        const normalizedY = parseFloat((-position.y / radius).toFixed(2));

        // Hanya kirim jika ada perubahan bermakna
        if (
          Math.abs(lastSent.current.x - normalizedX) > 0.02 ||
          Math.abs(lastSent.current.y - normalizedY) > 0.02
        ) {
          lastSent.current = { x: normalizedX, y: normalizedY };
          onChange(normalizedX, normalizedY);
        }
      }, 50); // 20 Hz
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      // Kirim posisi tengah saat dilepas
      if (lastSent.current.x !== 0 || lastSent.current.y !== 0) {
        lastSent.current = { x: 0, y: 0 };
        onChange(0, 0);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isDragging, position, onChange]);

  // Touch handlers
  const onTouchStart = (e: React.TouchEvent) => {
    const touch = e.touches[0];
    handleStart(touch.clientX, touch.clientY);
  };

  const onTouchMove = (e: React.TouchEvent) => {
    const touch = e.touches[0];
    handleMove(touch.clientX, touch.clientY);
  };

  // Mouse handlers (untuk testing di web browser PC)
  const onMouseDown = (e: React.MouseEvent) => {
    handleStart(e.clientX, e.clientY);
  };

  const onMouseMove = (e: React.MouseEvent) => {
    handleMove(e.clientX, e.clientY);
  };

  useEffect(() => {
    const handleGlobalMouseUp = () => {
      if (isDragging) handleEnd();
    };

    window.addEventListener("mouseup", handleGlobalMouseUp);
    window.addEventListener("touchend", handleGlobalMouseUp);
    
    return () => {
      window.removeEventListener("mouseup", handleGlobalMouseUp);
      window.removeEventListener("touchend", handleGlobalMouseUp);
    };
  }, [isDragging]);

  return (
    <div className="joystick-wrapper">
      <span className="joystick-label">{label}</span>
      <div
        ref={containerRef}
        className="joystick-container"
        onTouchStart={onTouchStart}
        onTouchMove={onTouchMove}
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        style={{ borderColor: color, boxShadow: `0 0 15px ${color}33` }}
      >
        {/* Ring Tengah dekoratif */}
        <div className="joystick-inner-ring" />
        
        {/* Knob / Thumb joystick */}
        <div
          className="joystick-knob"
          style={{
            transform: `translate(${position.x}px, ${position.y}px)`,
            backgroundColor: color,
            boxShadow: `0 0 20px ${color}`,
          }}
        />
      </div>
    </div>
  );
}
