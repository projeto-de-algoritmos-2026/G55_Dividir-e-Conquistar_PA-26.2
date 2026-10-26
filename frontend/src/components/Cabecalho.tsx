import { NavLink } from 'react-router'

const ITENS = [
  { para: '/', rotulo: 'Mapa' },
  { para: '/passo-a-passo', rotulo: 'Passo a Passo' },
  { para: '/comparativo', rotulo: 'Comparativo' },
]

/** Traço de sismograma usado como marca: calmo, um abalo, calmo de novo. */
function Sismograma() {
  return (
    <svg viewBox="0 0 64 20" className="h-5 w-16" aria-hidden="true">
      <polyline
        points="0,10 18,10 21,8 23,13 26,3 29,17 32,5 35,14 38,8 41,11 44,10 64,10"
        fill="none"
        stroke="var(--color-registro)"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  )
}

export default function Cabecalho() {
  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-grade bg-papel px-5">
      <div className="flex items-center gap-3">
        <Sismograma />
        <span className="titulo text-xl font-bold tracking-tight">SismoPar</span>
        <span className="hidden text-sm text-tinta-suave md:inline">
          os dois terremotos mais próximos de uma região
        </span>
      </div>
      <nav className="flex gap-1">
        {ITENS.map((item) => (
          <NavLink
            key={item.para}
            to={item.para}
            end
            className={({ isActive }) =>
              `rounded px-3 py-1.5 text-sm font-medium ${
                isActive ? 'bg-tinta text-papel' : 'text-tinta-suave hover:bg-papel-escuro'
              }`
            }
          >
            {item.rotulo}
          </NavLink>
        ))}
      </nav>
    </header>
  )
}
