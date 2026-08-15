import React, { useState, useEffect } from 'react';
import { Settings2, X, Save, RotateCcw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export const defaultSystemPrompt = "You are an expert Enterprise AI Assistant. You have access to a semantic search database of the user's uploaded documents. When answering questions related to the user's data, base your answers strictly on the provided document excerpts. However, you may also engage in normal conversation, answer general knowledge questions, and refer back to your conversational history. Keep your answers concise, professional, and helpful.";
export const defaultTemperature = 0.2;

export function SettingsModal({ isOpen, onClose }: Props) {
  const [systemPrompt, setSystemPrompt] = useState(defaultSystemPrompt);
  const [temperature, setTemperature] = useState(defaultTemperature);
  const [isSaved, setIsSaved] = useState(false);

  useEffect(() => {
    if (isOpen) {
      const storedPrompt = localStorage.getItem('systemPrompt');
      const storedTemp = localStorage.getItem('temperature');
      
      if (storedPrompt) setSystemPrompt(storedPrompt);
      if (storedTemp) setTemperature(parseFloat(storedTemp));
      
      setIsSaved(false);
    }
  }, [isOpen]);

  const handleSave = () => {
    localStorage.setItem('systemPrompt', systemPrompt);
    localStorage.setItem('temperature', temperature.toString());
    setIsSaved(true);
    setTimeout(() => {
      onClose();
    }, 1000);
  };

  const handleReset = () => {
    setSystemPrompt(defaultSystemPrompt);
    setTemperature(defaultTemperature);
    localStorage.removeItem('systemPrompt');
    localStorage.removeItem('temperature');
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="modal-overlay">
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="modal-content glass-panel" 
          style={{ maxWidth: '600px', width: '90%' }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', margin: 0, fontSize: '1.25rem' }}>
              <Settings2 size={24} color="var(--accent-primary)" />
              Advanced AI Settings
            </h2>
            <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}>
              <X size={20} />
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                System Prompt
              </label>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                Define the AI's core instructions and personality.
              </p>
              <textarea
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                style={{
                  width: '100%',
                  height: '150px',
                  background: 'rgba(0,0,0,0.2)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  color: 'var(--text-primary)',
                  padding: '1rem',
                  fontFamily: 'var(--font-sans)',
                  resize: 'vertical'
                }}
              />
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '0.5rem' }}>
                <label style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                  Temperature: {temperature.toFixed(2)}
                </label>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                Controls creativity. 0.0 is focused and deterministic, 1.0 is highly creative.
              </p>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                style={{ width: '100%', cursor: 'pointer' }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                <span>Precise (0.0)</span>
                <span>Creative (1.0)</span>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '2rem', paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
            <button
              onClick={handleReset}
              style={{
                display: 'flex', alignItems: 'center', gap: '0.5rem',
                background: 'none', border: '1px solid rgba(255,255,255,0.1)',
                color: 'var(--text-secondary)', padding: '0.5rem 1rem', borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              <RotateCcw size={16} /> Reset to Default
            </button>

            <button
              onClick={handleSave}
              className="btn-primary"
              style={{ width: 'auto', marginBottom: 0, padding: '0.5rem 1.5rem' }}
            >
              <Save size={16} />
              {isSaved ? 'Saved!' : 'Save Changes'}
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
