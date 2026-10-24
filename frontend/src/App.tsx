import { BrowserRouter, Route, Routes } from 'react-router'
import Inicio from './pages/Inicio'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Inicio />} />
      </Routes>
    </BrowserRouter>
  )
}
