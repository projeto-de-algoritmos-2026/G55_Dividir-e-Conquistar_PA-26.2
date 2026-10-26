interface Props {
  texto: string
}

export default function Carregando({ texto }: Props) {
  return (
    <span className="inline-flex items-center gap-2 text-sm text-tinta-suave" role="status">
      <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-grade border-t-epicentro motion-reduce:animate-none" />
      {texto}
    </span>
  )
}
