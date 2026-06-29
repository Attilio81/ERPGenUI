"use client";

import { AgentState } from "@/lib/state";
import { euro, num } from "@/lib/format";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

// Rampa mono: dal segnale arancio all'inchiostro — la posizione = il rango.
const SIGNAL = { r: 0xd6, g: 0x48, b: 0x1b };
const INK = { r: 0x6a, g: 0x35, b: 0x14 };
const shade = (i: number, n: number) => {
  const t = n <= 1 ? 0 : i / (n - 1);
  const c = (a: number, b: number) => Math.round(a + (b - a) * t);
  return `rgb(${c(SIGNAL.r, INK.r)}, ${c(SIGNAL.g, INK.g)}, ${c(SIGNAL.b, INK.b)})`;
};

export function GraficoVendite({ state }: { state: AgentState }) {
  const dati = state.chart_dati ?? [];
  const isValore = (state.chart_spec?.["misura"] ?? "valore") === "valore";
  const fmt = (v: number) => (isValore ? euro(v) : num(v));

  return (
    <div className="panel">
      <div className="panel-head">
        <div>
          <h2>{state.chart_titolo || "Grafico vendite"}</h2>
          <p className="muted">{dati.length} voci</p>
        </div>
      </div>

      {dati.length ? (
        <div className="chart-wrap">
          <ResponsiveContainer width="100%" height={Math.max(320, dati.length * 34)}>
            <BarChart data={dati} layout="vertical" margin={{ left: 12, right: 32, top: 8, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e5e7eb" />
              <XAxis type="number" tickFormatter={(v) => fmt(Number(v))} tick={{ fontSize: 11 }} />
              <YAxis
                type="category"
                dataKey="etichetta"
                width={220}
                tick={{ fontSize: 11 }}
                interval={0}
              />
              <Tooltip formatter={(v) => fmt(Number(v))} cursor={{ fill: "#f1f5f9" }} />
              <Bar dataKey="valore" radius={[0, 1, 1, 0]}>
                {dati.map((_, i) => (
                  <Cell key={i} fill={shade(i, dati.length)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="empty">Nessun dato per il grafico.</div>
      )}
    </div>
  );
}
