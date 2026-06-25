"use client";

import React, { useState } from "react";

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentIp: string;
  onSave: (ip: string) => void;
}

export default function SettingsModal({ isOpen, onClose, currentIp, onSave }: SettingsModalProps) {
  const [ip, setIp] = useState(currentIp);

  if (!isOpen) return null;

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(ip.trim());
    onClose();
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-content glass">
        <div className="modal-header">
          <h2>KONFIGURASI JARINGAN</h2>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>
        <form onSubmit={handleSave} className="modal-form">
          <div className="form-group">
            <label htmlFor="ip-input">IP Address Raspberry Pi</label>
            <input
              id="ip-input"
              type="text"
              value={ip}
              onChange={(e) => setIp(e.target.value)}
              placeholder="Contoh: 192.168.1.100"
              required
              className="text-input"
            />
            <small>Masukkan alamat IP Raspberry Pi yang terhubung ke jaringan yang sama.</small>
          </div>
          
          <div className="connection-info">
            <div>
              <strong>WebSocket URL:</strong>
              <code>ws://{ip || "IP_RASPI"}:8765</code>
            </div>
            <div>
              <strong>Stream Video (MediaMTX):</strong>
              <code>http://{ip || "IP_RASPI"}:8889/panzerbot</code>
            </div>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Batal
            </button>
            <button type="submit" className="btn-primary">
              Simpan & Hubungkan
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
