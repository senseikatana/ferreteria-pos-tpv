# Universal POS Core (@senseikatana/pos-universal)

Enterprise-grade, framework-agnostic Point of Sale (POS) and inventory management platform built with **Nuxt 4**, **Vue 3**, **Tailwind CSS**, **Prisma ORM**, **Hexagonal Architecture**, and native **InsForge PostgreSQL** DBA cloud support.

Engineered to operate seamlessly across retail, hardware stores (*ferreterías*), grocery, electronics, and general merchandise businesses.

---

## 🚀 Key Features

- **Domain-Agnostic Engine**: Designed for any retail niche with customizable product metadata, units (`unit`, `kg`, `meter`, `box`, `liter`), and barcode indexing.
- **Hardware Scanner Ready**: Low-latency barcode scanner listener with automatic input focus, rapid scan buffer capture, and keyboard shortcuts.
- **Hexagonal Architecture (Ports & Adapters)**: Strict separation of Core Domain, Application Use Cases, and Infrastructure Adapters.
- **The 6 Essential Design Patterns**:
  - **Singleton**: Thread-safe Prisma client and central Domain Event Bus.
  - **Facade**: `PosFacade` unifying inventory, sales, customer debts, and cash reconciliation.
  - **Factory**: `PaymentStrategyFactory` instantiating payment mechanisms at runtime.
  - **Observer**: Decoupled `DomainEventBus` listening for `SaleCompleted` and `LowStock` events.
  - **Strategy**: Pluggable `CashPaymentStrategy`, `CardPaymentStrategy`, and `CreditDebtPaymentStrategy`.
  - **Decorator**: `withAudit` wrapping critical database queries with execution timing and error telemetry.
- **Atomic Transactions (Zero Data Loss)**: All checkouts run within `prisma.$transaction`. Stock deduction, debt increment, and ticket issuance either commit together or roll back cleanly.
- **Multi-Role Authentication (RBAC)**: Secure `httpOnly` JWT sessions distinguishing `ADMIN` (reports, user management, audit) from `CASHIER` (sales, fiados, daily register close).
- **Accounts Receivable / Store Credit (*Fiado*)**: Real-time credit limits, customer debt balances, and audit logs for partial/total repayments (*abonos*).
- **KatanaKit CDN Integration**: Direct client-side consumption of `katanakit-js@2.14.1` through ESM CDN (`https://esm.sh/katanakit-js@2.14.1`) with safe error unwrapping and network fallbacks.
- **InsForge & PostgreSQL Ready**: Direct compatibility with InsForge DBA infrastructure and standard PostgreSQL databases.

---

## 🏛️ System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                      Presentation Layer                     │
│        Nuxt 4 (Vue 3) • Tailwind CSS • KatanaKit CDN        │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / JSON
┌──────────────────────────────▼──────────────────────────────┐
│                    Nitro API Controllers                    │
│   /api/auth  •  /api/sales  •  /api/products  •  /api/cash  │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                   POS Facade (Entry Point)                   │
│                       PosFacade.ts                          │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
┌──────────────▼──────────────┐ ┌──────────────▼──────────────┐
│    Strategies & Factories   │ │    Observers & Event Bus    │
│  - PaymentStrategyFactory   │ │  - DomainEventBus           │
│  - Cash / Card / CreditDebt │ │  - SaleCompleted / LowStock │
└──────────────┬──────────────┘ └──────────────┬──────────────┘
               │                               │
┌──────────────▼───────────────────────────────▼──────────────┐
│                Secondary Adapters (Prisma ORM)              │
│  - PrismaProductRepository   - PrismaCustomerRepository     │
│  - PrismaSaleRepository      - PrismaCashRegisterRepository │
└──────────────────────────────┬──────────────────────────────┘
                               │ TCP / Connection Pool
┌──────────────────────────────▼──────────────────────────────┐
│                  InsForge / PostgreSQL DB                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Tech Stack

| Component | Technology | Version |
|---|---|---|
| **Framework** | Nuxt 4 (Nitro Server) | `^4.5.2` |
| **Frontend** | Vue 3 + Tailwind CSS | `^3.5.13` / `^3.4.17` |
| **ORM** | Prisma ORM | `^6.19.3` |
| **Database** | InsForge / PostgreSQL | `15+` |
| **Service Toolkit** | KatanaKit JS (via CDN) | `^2.14.1` |
| **Security** | Bcrypt + JSON Web Tokens | `bcrypt@6.0.0` / `jsonwebtoken@9.0.2` |
| **Language** | TypeScript (Strict) | `^5.7.3` |

---

## 🛠️ Quick Start

### 1. Prerequisites
- **Node.js**: `v20.0.0` or higher (tested on Node `v26.8.1`).
- **Yarn**: `4.x` or **npm** `10.x+`.

### 2. Installation
```bash
# Clone the repository
git clone <repository-url>
cd pos-astro-node

# Install dependencies
yarn install
```

### 3. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Configure your InsForge or PostgreSQL connection string:
```env
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/pos_universal?schema=public"
JWT_SECRET="your-secure-jwt-production-secret"
KATANAKIT_CDN_URL="https://esm.sh/katanakit-js@2.14.1"
```

### 4. Database Setup & Seed
```bash
# Generate Prisma Client
yarn prisma:generate

# Push schema to InsForge / PostgreSQL
yarn prisma:push

# Seed initial users, products, and customers
yarn prisma:seed
```

### 5. Run Development Server
```bash
yarn dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🔑 Demo Credentials

| Role | Username | Password | Accessible Modules |
|---|---|---|---|
| **Admin** | `admin` | `admin123` | POS, Customers, Cash Register, Reports, Users, Inventory |
| **Cashier** | `vendedor` | `vendedor123` | POS, Customers (Fiado), Cash Register |

---

## 📖 Available Scripts

- `yarn dev`: Launches the Nuxt 4 development server.
- `yarn build`: Compiles the production application.
- `yarn preview`: Runs the compiled production build locally.
- `yarn prisma:generate`: Generates typed Prisma Client bindings.
- `yarn prisma:push`: Synchronizes database schema directly with InsForge/PostgreSQL.
- `yarn prisma:seed`: Populates the database with sample inventory and customers.

---

## 📄 License
MIT © senseikatana
