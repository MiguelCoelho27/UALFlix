# UALFlix – Frontend

Interface web para o sistema de streaming distribuído **UALFlix**, desenvolvido com:

- [Next.js 14](https://nextjs.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [shadcn/ui](https://ui.shadcn.com/)
- Typescript

---

## ⚙️ Funcionalidades implementadas

- 📥 Adicionar vídeos (título + URL)
- 🎞️ Listagem de vídeos com player integrado
- 💅 Interface moderna com componentes estilizados (`card`, `input`, `button`)
- 🔄 Comunicação direta com os microserviços:
  - `catalog-service` (porta 5000)
  - `admin-service` (porta 5004)

---

## ▶️ Iniciar localmente

```bash
# Instalar dependências
npm install

# Correr aplicação
npm run dev
```

Acede a: [http://localhost:3000](http://localhost:3000)

---

## 📝 Notas

- O projeto usa o **App Router** (`/app`).
- Todos os componentes UI foram gerados com `shadcn/ui` com o estilo `New York` e cor base `Zinc`.
- Os endpoints estão configurados para `localhost`. Para produção via Docker Swarm, os domínios de serviço deverão ser ajustados (ex: `http://catalog-service:5000`).

---

## 📁 Estrutura relevante

```
frontend/
├── app/
│   ├── page.tsx          # Página principal
│   └── globals.css       # Estilos base
├── components/ui/        # Componentes UI com shadcn
├── lib/utils.ts          # Função auxiliar `cn`
├── public/
├── next.config.js
└── tsconfig.json
```
