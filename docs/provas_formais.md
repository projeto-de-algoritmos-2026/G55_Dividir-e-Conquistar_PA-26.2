# Provas formais do Closest Pair

Este documento analisa as duas versões de divisão e conquista implementadas em
`backend/app/algorithms/closest_pair_nlog2n.py` e
`backend/app/algorithms/closest_pair_nlogn.py`. Ambas recebem eventos já
projetados em coordenadas cartesianas `(x, y)`, em quilômetros, e minimizam a
distância euclidiana nesse plano. As rotinas compartilhadas de faixa e
empacotamento estão em `backend/app/algorithms/closest_pair_comum.py`.

## Notação e estrutura da recursão

Seja \(P\) um conjunto de \(n\) pontos projetados. A lista \(P_x\) é ordenada
lexicograficamente por \((x,y,\mathrm{id})\). Cada chamada recursiva recebe um
intervalo contíguo dessa lista e, para \(n>3\), divide-o por posição no índice
\(m=\lfloor n/2\rfloor\). A reta vertical usada na combinação é
\[
  L:\ x=\ell,\qquad
  \ell=\frac{x_{m-1}+x_m}{2}.
\]
Essa escolha divide igualmente os pontos mesmo quando há valores de \(x\)
repetidos. Os casos com no máximo três pontos são resolvidos por força bruta.

Sejam \(d_L\) e \(d_R\) as distâncias dos pares mínimos encontrados nas duas
metades, e
\[
  \delta=\min(d_L,d_R).
\]
Todo par contido inteiramente em uma metade tem distância pelo menos
\(\delta\). A faixa considerada na combinação contém os pontos que satisfazem
\(|x-\ell|<\delta\). Ordenados por \(y\), eles são comparados com no máximo os
sete pontos seguintes, interrompendo a varredura quando a diferença de
coordenada \(y\) alcança \(\delta\).

## Prova de corretude

Provamos por indução no número de pontos que a chamada retorna um par mínimo
no plano projetado. Para \(n\leq 3\), a força bruta avalia todos os pares, logo
o resultado é mínimo. Considere agora uma chamada com \(n>3\) e suponha que as
chamadas recursivas sejam corretas.

Um par globalmente mais próximo está necessariamente em um dos três casos:

1. **Ambos os pontos à esquerda de \(L\).** O par está inteiramente na
   subinstância esquerda. Pela hipótese de indução, a recursão esquerda
   encontra a menor distância nessa metade; a combinação conserva o menor
   resultado entre os dois lados.
2. **Ambos os pontos à direita de \(L\).** Analogamente, a recursão direita
   encontra o menor par da metade e seu resultado participa da escolha do
   melhor par.
3. **Um ponto em cada metade (par que cruza a divisão).** Se a distância desse
   par for menor que \(\delta\), então a diferença horizontal entre seus
   pontos é menor que \(\delta\), portanto ambos pertencem à faixa
   \(|x-\ell|<\delta\). A diferença vertical também é menor que \(\delta\).
   Pelo lema de empacotamento abaixo, na ordem por \(y\) o segundo ponto está
   entre os sete sucessores que são examinados a partir do primeiro. Assim,
   esse par é comparado. Se a distância do par cruzado for pelo menos
   \(\delta\), ele não pode melhorar o melhor par já encontrado em uma das
   metades.

Em particular, não é necessário que cada ponto de uma metade esteja
estritamente de um lado geométrico de \(L\): se os valores de \(x\) empatam
na divisão por posição, alguns pontos com \(x=\ell\) podem ficar em metades
distintas. O argumento da faixa e do empacotamento continua válido, pois
limita separadamente a ocupação em cada metade.

Esses casos cobrem todos os pares. Como a combinação conserva os vencedores
recursivos e examina todos os pares cruzados que poderiam melhorar \(\delta\),
ela devolve um par globalmente mínimo.

## Lema de empacotamento e os sete sucessores

**Lema.** Seja \(\delta\) a menor distância entre os pares mínimos das duas
metades. Para qualquer ponto \(p\) da faixa ordenada por \(y\), basta comparar
\(p\) com, no máximo, os sete pontos seguintes nessa ordem para encontrar um
par cruzado de distância menor que \(\delta\), se tal par existir.

**Prova.** Considere o retângulo vertical de largura \(2\delta\), centrado em
\(L\), e altura \(\delta\), que cobre \(p\) e todos os pontos da faixa com
coordenada \(y\) entre \(p_y\) e \(p_y+\delta\). Divida-o pela reta \(L\) em
duas partes de largura \(\delta\). Em cada metade, subdivida a região em duas
colunas de largura \(\delta/2\) e duas linhas de altura \(\delta/2\): são
quatro caixas por metade, oito ao todo.

Se \(\delta=0\), um par mínimo de uma das metades já tem distância zero e
nenhum par cruzado pode melhorá-lo; portanto, considere \(\delta>0\) a seguir.
Cada caixa tem diagonal
\[
  \sqrt{(\delta/2)^2+(\delta/2)^2}
  =\frac{\delta}{\sqrt{2}}<\delta.
\]
Se duas caixas contivessem pontos da mesma metade, a distância entre esses
dois pontos seria menor que \(\delta\), contrariando a definição de \(\delta\)
como limite inferior das distâncias entre pontos de uma mesma metade. Portanto
cada uma das oito caixas contém no máximo um ponto de sua metade e o retângulo
contém no máximo oito pontos. Essa contagem continua válida quando há empate
de \(x\) em \(L\): os pontos sobre a reta podem pertencer a qualquer uma das
metades, mas a ocupação continua sendo limitada separadamente em cada metade.

Fixado \(p\), qualquer ponto posterior a mais de sete posições está separado
dele por pelo menos oito posições no conjunto contado a partir de \(p\).
Como o retângulo contém no máximo oito pontos, incluindo \(p\), esse ponto
posterior não pode estar a menos de \(\delta\) em \(y\). Sua distância
euclidiana a \(p\) também não pode ser menor que \(\delta\). Assim, os únicos
sucessores que podem melhorar o resultado são os sete imediatamente
seguintes.

A implementação em `varrer_faixa` segue esse limite e ainda encerra a
varredura para um ponto quando \(q_y-p_y\geq\delta\). Se o melhor valor
diminui durante a varredura, a interrupção só fica mais restritiva; pares
ainda não examinados não podem recuperar uma distância inferior ao novo
limite.

## Complexidade da versão \(O(n\log^2 n)\)

Em `closest_pair_nlog2n.py`, cada chamada recursiva constrói a faixa filtrando
os pontos do subproblema e a ordena por \(y\) com mergesort. Esse passo custa
\(O(n\log n)\). A varredura da faixa custa \(O(n)\), pelo limite constante de
sete comparações por ponto. A divisão e as demais operações também não
excedem \(O(n\log n)\). Portanto, para \(n>3\),
\[
  T(n)=2T(n/2)+O(n\log n),\qquad T(n)=O(1)\text{ para }n\leq3.
\]

Pelo teorema mestre, \(a=2\), \(b=2\), logo \(n^{\log_b a}=n\), e
\(f(n)=\Theta(n\log n)=\Theta(n^{\log_b a}\log n)\). O caso 2 do teorema
mestre resulta em
\[
  T(n)=\Theta(n\log^2 n).
\]
A ordenação inicial por \(x\) também custa \(O(n\log n)\), ficando dominada
pela recursão.

## Complexidade da versão \(O(n\log n)\)

Em `closest_pair_nlogn.py`, cada chamada devolve, além do melhor par, todos
os pontos do subproblema ordenados por \(y\). Os casos-base ordenam no máximo
três pontos. Nos demais casos, `merge` intercala em tempo linear as duas
listas ordenadas por \(y\); filtrar essa lista para formar a faixa e varrê-la
também custa \(O(n)\). Assim, para \(n>3\),
\[
  T(n)=2T(n/2)+O(n),\qquad T(n)=O(1)\text{ para }n\leq3.
\]
Pelo teorema mestre, \(a=2\), \(b=2\), \(n^{\log_b a}=n\) e
\(f(n)=\Theta(n)\). O caso 2 fornece
\[
  T(n)=\Theta(n\log n).
\]
A ordenação inicial por \(x\) custa igualmente \(O(n\log n)\), portanto não
altera a ordem assintótica total. O espaço adicional das listas de merge é
linear por nível recursivo, sem alterar a complexidade de tempo demonstrada.

## Efeito da projeção e validação geodésica

As provas acima se aplicam às coordenadas \((x,y)\) projetadas e à distância
euclidiana calculada pelo algoritmo. Portanto, o algoritmo encontra o par
ótimo **no plano projetado**, não uma garantia matemática de que esse par
minimiza a distância sobre toda a superfície terrestre. O projeto usa uma
projeção azimutal equidistante centrada na região, que preserva distâncias a
partir do centro e tem distorção pequena em escala regional, mas as distâncias
entre outros pontos podem divergir das geodésicas.

Após encontrar o par no plano, o resultado calcula também sua distância
geodésica pela fórmula de Haversine. Para instâncias dentro do limite da
validação, uma busca exaustiva geodésica pode verificar se outro par é mais
próximo sobre a esfera e sinalizar uma divergência. Essa validação avalia o
efeito da projeção; ela não altera a prova de corretude planar nem transforma
o algoritmo de divisão e conquista em uma busca geodésica.
