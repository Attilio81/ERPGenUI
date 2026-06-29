const nf = new Intl.NumberFormat("it-IT", { maximumFractionDigits: 0 });
const nf2 = new Intl.NumberFormat("it-IT", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const eur = new Intl.NumberFormat("it-IT", { style: "currency", currency: "EUR" });

export const num = (v: number | null | undefined) => nf.format(Number(v ?? 0));
export const num2 = (v: number | null | undefined) => nf2.format(Number(v ?? 0));
export const euro = (v: number | null | undefined) => eur.format(Number(v ?? 0));

export const dataIt = (iso: string | null | undefined) => {
  if (!iso) return "—";
  const d = new Date(iso);
  return isNaN(d.getTime()) ? String(iso) : d.toLocaleDateString("it-IT");
};
