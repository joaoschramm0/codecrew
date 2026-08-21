# CodeCrew Design System

O front usa um sistema visual pequeno, definido em `src/design-system.css`. Novas telas devem reutilizar os tokens existentes antes de criar novos valores.

## Tipografia

- Inter: textos, campos e mensagens.
- DM Sans: títulos, marca, destaques e ações.
- Títulos usam peso entre 600 e 700. Textos usam o peso padrão da Inter.

## Layout

- Escala de espaçamento: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64 e 80px.
- Container `wide`: 1344px para headers, onboarding e workspace.
- Container `content`: 1120px para loading, stories e conteúdo focado.
- Gutter lateral responsivo: `--page-gutter`.

## Componentes

- Controles comuns têm 48px; ações principais e campos têm 56px.
- Botões principais usam `--color-primary` e raio de 12px.
- Painéis usam raio de 16px; superfícies de destaque usam 24px.
- Ícones de apoio ficam em caixas de 40px.
- Verde representa ação e progresso; ciano representa informação e foco.
- Não usar badges ou barras decorativas. Barras ficam reservadas para progresso funcional.
- Conteúdo longo, como desafios, usa largura máxima de 880px e line-height amplo para leitura.

## Movimento

- Transições rápidas usam `--transition-fast`.
- Entradas usam `--ease-out` e deslocamentos curtos.
- Toda animação respeita `prefers-reduced-motion`.

## Responsividade

- Até 980px, grids de duas colunas passam para uma coluna quando necessário.
- Até 720px, o gutter cai para 16px e a navegação lateral vira navegação horizontal.
