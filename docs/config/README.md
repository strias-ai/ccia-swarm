# Configuración local segura

Este repositorio se puede clonar sin credenciales incluidas. Copia `.env.template` a `.env`, completa solo los servicios que vayas a utilizar y nunca subas el archivo resultante.

| Variable | Uso |
| --- | --- |
| `GITHUB_TOKEN` | Automatizaciones de GitHub opcionales. |
| `ISSUEHUNT_TOKEN` | Consultas autenticadas a IssueHunt, si proceden. |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` | Integración de Stripe. Usa claves de prueba durante desarrollo. |
| `KRAKEN_API_KEY`, `KRAKEN_API_SECRET` | Integración opcional de Kraken. |
| `SOLANA_WALLET_PRIVATE_KEY` | Solo en un almacén local seguro; nunca en Git. |
| `TURSO_URL`, `TURSO_TOKEN` | Sincronización opcional con Turso. |
| `USER_IBAN_SEPA` | Dato financiero local opcional; nunca público. |

Revoca y rota cualquier valor que haya llegado a un repositorio público, incluso si el archivo se elimina después.
