import { BrowserRouter, Outlet, Route, Routes } from 'react-router'
import Cabecalho from './components/Cabecalho'
import Mapa from './pages/Mapa'
import PassoAPasso from './pages/PassoAPasso'
import Comparativo from './pages/Comparativo'

function Layout() {
  return (
    <div className="flex h-full flex-col">
      <Cabecalho />
      <div className="min-h-0 flex-1">
        <Outlet />
      </div>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Mapa />} />
          <Route path="/passo-a-passo" element={<PassoAPasso />} />
          <Route path="/comparativo" element={<Comparativo />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
