const numero = new Intl.NumberFormat('pt-BR')
const dataHora = new Intl.DateTimeFormat('pt-BR', {
  dateStyle: 'short',
  timeStyle: 'medium',
  timeZone: 'UTC',
})

export function formatarNumero(valor: number, casas = 0): string {
  return valor.toLocaleString('pt-BR', {
    minimumFractionDigits: casas,
    maximumFractionDigits: casas,
  })
}

export function formatarInteiro(valor: number): string {
  return numero.format(Math.round(valor))
}

/** Abaixo de 1 km mostra em metros; zero indica epicentros coincidentes. */
export function formatarDistancia(km: number): string {
  if (km === 0) return '0 m'
  if (km < 0.01) return `${formatarNumero(km * 1000, 1)} m`
  if (km < 1) return `${formatarInteiro(km * 1000)} m`
  return `${formatarNumero(km, 2)} km`
}

export function formatarData(iso: string): string {
  return `${dataHora.format(new Date(iso))} UTC`
}

export function formatarIntervalo(isoA: string, isoB: string): string {
  const horas = Math.abs(new Date(isoB).getTime() - new Date(isoA).getTime()) / 3_600_000
  if (horas < 1) return `${formatarInteiro(horas * 60)} min`
  if (horas < 48) return `${formatarNumero(horas, 1)} h`
  const dias = horas / 24
  if (dias < 365) return `${formatarInteiro(dias)} dias`
  return `${formatarNumero(dias / 365.25, 1)} anos`
}

export function formatarTempo(ms: number): string {
  return ms < 10 ? `${formatarNumero(ms, 1)} ms` : `${formatarInteiro(ms)} ms`
}

/** Raio do marcador em px: cresce com a magnitude. */
export function raioPorMagnitude(magnitude: number): number {
  return Math.max(2, (magnitude - 1.5) * 2)
}
