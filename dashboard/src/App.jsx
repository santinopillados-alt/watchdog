import { useState, useEffect } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const API = "http://127.0.0.1:8000";

export default function App() {
  const [metricas, setMetricas] = useState([]);
  const [alertas, setAlertas] = useState([]);
  const [status, setStatus] = useState(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      const [m, a, s] = await Promise.all([
        fetch(`${API}/metricas`).then(r => r.json()),
        fetch(`${API}/alertas`).then(r => r.json()),
        fetch(`${API}/status`).then(r => r.json()),
      ]);
      setMetricas(m.slice(-30));
      setAlertas(a.slice(-5));
      setStatus(s);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ background: "#0a0a0f", minHeight: "100vh", padding: "32px", fontFamily: "monospace", color: "#e2e8f0" }}>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8 }}>⬡ Watchdog</h1>
      <p style={{ color: "#475569", marginBottom: 32 }}>Real-time system observability</p>

      {status && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 32 }}>
          {[
            { label: "CPU", value: `${status.cpu_actual}%`, color: status.cpu_actual > 80 ? "#ef4444" : "#22c55e" },
            { label: "Memory", value: `${status.memoria_actual}%`, color: status.memoria_actual > 90 ? "#ef4444" : "#22c55e" },
            { label: "Measurements", value: status.total_mediciones },
            { label: "Status", value: status.estado, color: status.estado === "CRITICO" ? "#ef4444" : "#22c55e" },
          ].map((item, i) => (
            <div key={i} style={{ background: "#0f1117", border: "1px solid #1e293b", borderRadius: 8, padding: "16px" }}>
              <div style={{ fontSize: 11, color: "#475569", marginBottom: 4 }}>{item.label}</div>
              <div style={{ fontSize: 22, fontWeight: 700, color: item.color || "#e2e8f0" }}>{item.value}</div>
            </div>
          ))}
        </div>
      )}

      <div style={{ background: "#0f1117", border: "1px solid #1e293b", borderRadius: 8, padding: 20, marginBottom: 24 }}>
        <div style={{ fontSize: 12, color: "#475569", marginBottom: 16 }}>CPU % — last 30 seconds</div>
        <ResponsiveContainer width="100%" height={180}>
          <LineChart data={metricas}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="hora" tick={{ fontSize: 10, fill: "#475569" }} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: "#475569" }} />
            <Tooltip contentStyle={{ background: "#0f1117", border: "1px solid #1e293b" }} />
            <Line type="monotone" dataKey="cpu" stroke="#3b82f6" dot={false} strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div style={{ background: "#0f1117", border: "1px solid #1e293b", borderRadius: 8, padding: 20, marginBottom: 24 }}>
        <div style={{ fontSize: 12, color: "#475569", marginBottom: 16 }}>Memory % — last 30 seconds</div>
        <ResponsiveContainer width="100%" height={180}>
          <LineChart data={metricas}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="hora" tick={{ fontSize: 10, fill: "#475569" }} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: "#475569" }} />
            <Tooltip contentStyle={{ background: "#0f1117", border: "1px solid #1e293b" }} />
            <Line type="monotone" dataKey="memoria" stroke="#8b5cf6" dot={false} strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {alertas.length > 0 && (
        <div style={{ background: "#0f1117", border: "1px solid #ef444440", borderRadius: 8, padding: 20 }}>
          <div style={{ fontSize: 12, color: "#ef4444", marginBottom: 12 }}>⚠ Active Alerts</div>
          {alertas.map((a, i) => (
            <div key={i} style={{ padding: "8px 12px", background: "#ef444410", borderRadius: 4, marginBottom: 6, fontSize: 13, color: "#fca5a5" }}>
              {a.hora} — {a.mensaje}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}