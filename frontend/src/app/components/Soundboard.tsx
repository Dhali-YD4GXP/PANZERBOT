"use client";

import React, { useState } from "react";

interface SoundboardProps {
  onPlaySound: (soundName: string) => void;
  isConnected: boolean;
}

interface SoundItem {
  id: string;
  name: string;
  emoji: string;
  color: string;
}

const SOUNDS: SoundItem[] = [
  { id: "boom", name: "Boom", emoji: "💥", color: "#ff3e3e" },
  { id: "fart", name: "Fart", emoji: "💨", color: "#a88b56" },
  { id: "get_out", name: "Get Out", emoji: "🚪", color: "#ff8c00" },
  { id: "giga_chad", name: "Giga Chad", emoji: "🗿", color: "#00d2ff" },
  { id: "goofy", name: "Goofy", emoji: "🤪", color: "#ffd700" },
  { id: "king_baldwin", name: "Baldwin", emoji: "👑", color: "#d1b3c4" },
  { id: "metal_pipe", name: "Metal Pipe", emoji: "🔔", color: "#c0c0c0" },
  { id: "oi_oi_oi", name: "Oi Oi Oi", emoji: "🗣️", color: "#a855f7" },
  { id: "outro", name: "Outro", emoji: "🎵", color: "#ec4899" },
  { id: "rizz", name: "Rizz", emoji: "😏", color: "#10b981" },
  { id: "uwu", name: "UwU", emoji: "🥺", color: "#ff69b4" }
];

export default function Soundboard({ onPlaySound, isConnected }: SoundboardProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className={`soundboard-wrapper glass ${isOpen ? "open" : ""}`}>
      {/* Toggle Button */}
      <button 
        className="soundboard-toggle" 
        onClick={() => setIsOpen(!isOpen)}
        style={{
          boxShadow: isOpen ? "none" : "0 -5px 15px rgba(0, 210, 255, 0.2)"
        }}
      >
        <span className="soundboard-toggle-icon">{isOpen ? "⬇️" : "🔊"}</span>
        <span className="soundboard-toggle-text">SOUNDBOARD</span>
      </button>

      {/* Sound Buttons Grid */}
      <div className="soundboard-content">
        <div className="soundboard-grid">
          {SOUNDS.map((sound) => (
            <button
              key={sound.id}
              onClick={() => onPlaySound(sound.id)}
              disabled={!isConnected}
              className="sound-btn"
              style={{
                borderColor: sound.color,
                "--hover-color": sound.color,
              } as React.CSSProperties}
            >
              <span className="sound-emoji">{sound.emoji}</span>
              <span className="sound-name">{sound.name}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
