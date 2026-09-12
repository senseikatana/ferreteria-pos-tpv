import { PrismaClient } from '@prisma/client'
import bcrypt from 'bcrypt'

const prisma = new PrismaClient()

async function main() {
  console.log('Seeding POS database...')

  // 1. Seed Users
  const adminPasswordHash = await bcrypt.hash('admin123', 10)
  const cashierPasswordHash = await bcrypt.hash('vendedor123', 10)

  const admin = await prisma.user.upsert({
    where: { username: 'admin' },
    update: {},
    create: {
      fullName: 'System Administrator',
      username: 'admin',
      passwordHash: adminPasswordHash,
      role: 'ADMIN',
      isActive: true,
    },
  })

  const cashier = await prisma.user.upsert({
    where: { username: 'vendedor' },
    update: {},
    create: {
      fullName: 'Head Cashier',
      username: 'vendedor',
      passwordHash: cashierPasswordHash,
      role: 'CASHIER',
      isActive: true,
    },
  })

  console.log(`Users seeded: ${admin.username}, ${cashier.username}`)

  // 2. Seed Products (Agnostic Catalog with sample retail/hardware data)
  const products = [
    { barcode: '7501234560012', name: 'Phillips Screw 1/4 x 1"', category: 'Fasteners', salePrice: 0.15, costPrice: 0.07, stock: 500, unit: 'unit' },
    { barcode: '7501234560029', name: 'Phillips Screw 1/4 x 2"', category: 'Fasteners', salePrice: 0.20, costPrice: 0.10, stock: 400, unit: 'unit' },
    { barcode: '7501234560036', name: 'Hex Nut 1/4"', category: 'Fasteners', salePrice: 0.10, costPrice: 0.04, stock: 600, unit: 'unit' },
    { barcode: '7501234560043', name: 'Standard 2" Nails (kg)', category: 'Fasteners', salePrice: 1.80, costPrice: 1.10, stock: 50, unit: 'kg' },
    { barcode: '7501234560050', name: 'Heavy Duty 3" Nails (kg)', category: 'Fasteners', salePrice: 1.95, costPrice: 1.20, stock: 45, unit: 'kg' },
    { barcode: '7501234560067', name: 'Measuring Tape 5m Pro', category: 'Tools', salePrice: 4.50, costPrice: 2.80, stock: 25, unit: 'unit' },
    { barcode: '7501234560074', name: 'Claw Hammer 16oz Fiberglass', category: 'Tools', salePrice: 9.90, costPrice: 6.20, stock: 15, unit: 'unit' },
    { barcode: '7501234560081', name: 'Phillips Screwdriver #2 x 4"', category: 'Tools', salePrice: 3.25, costPrice: 1.90, stock: 30, unit: 'unit' },
    { barcode: '7501234560098', name: 'Slotted Screwdriver 1/4 x 4"', category: 'Tools', salePrice: 3.25, costPrice: 1.90, stock: 30, unit: 'unit' },
    { barcode: '7501234560104', name: 'Solid Brass Padlock 40mm', category: 'Security', salePrice: 6.75, costPrice: 4.10, stock: 20, unit: 'unit' },
    { barcode: '7501234560111', name: 'Galvanized Wire 16 Gauge (kg)', category: 'General', salePrice: 2.30, costPrice: 1.50, stock: 40, unit: 'kg' },
    { barcode: '7501234560128', name: 'Clear Silicone Sealant 280ml', category: 'Sealants', salePrice: 3.80, costPrice: 2.20, stock: 35, unit: 'unit' },
    { barcode: '7501234560135', name: 'Electrical Tape Black 20m', category: 'Electrical', salePrice: 1.20, costPrice: 0.60, stock: 60, unit: 'unit' },
    { barcode: '7501234560142', name: 'LED Bulb 9W Cool Daylight', category: 'Electrical', salePrice: 2.90, costPrice: 1.70, stock: 50, unit: 'unit' },
    { barcode: '7501234560159', name: 'Split Cowhide Work Gloves', category: 'Safety', salePrice: 5.50, costPrice: 3.10, stock: 20, unit: 'pair' },
    { barcode: '7501234560166', name: 'Anti-Rust Primer Paint 1/4 Gal', category: 'Paint', salePrice: 8.90, costPrice: 5.60, stock: 18, unit: 'unit' },
    { barcode: '7501234560173', name: 'Flat Paint Brush 2"', category: 'Paint', salePrice: 2.10, costPrice: 1.10, stock: 40, unit: 'unit' },
    { barcode: '7501234560180', name: 'Adjustable Wrench 8"', category: 'Tools', salePrice: 7.40, costPrice: 4.50, stock: 12, unit: 'unit' },
    { barcode: '7501234560197', name: 'PTFE Thread Seal Tape', category: 'Plumbing', salePrice: 0.80, costPrice: 0.35, stock: 70, unit: 'unit' },
    { barcode: '7501234560203', name: 'PVC Pipe 1/2" Schedule 40 (m)', category: 'Plumbing', salePrice: 1.50, costPrice: 0.90, stock: 100, unit: 'meter' },
  ]

  for (const item of products) {
    await prisma.product.upsert({
      where: { barcode: item.barcode },
      update: {},
      create: item,
    })
  }

  console.log(`Seeded ${products.length} products.`)

  // 3. Seed Customers
  const customers = [
    { name: 'Constructora Los Andes S.A.', phone: '+1 555-0101', address: 'Industrial Park Block B', creditLimit: 1500.0, currentDebt: 345.50 },
    { name: 'Ramiro Gomez Contractor', phone: '+1 555-0102', address: '42 Maple Street', creditLimit: 500.0, currentDebt: 75.00 },
    { name: 'Metro Hardware Reseller', phone: '+1 555-0103', address: 'Commercial Ave 105', creditLimit: 2000.0, currentDebt: 0.0 },
    { name: 'Maria Fernanda Lopez', phone: '+1 555-0104', address: 'Spring Gardens #12', creditLimit: 250.0, currentDebt: 45.20 },
    { name: 'Thunder Auto Repair Shop', phone: '+1 555-0105', address: 'Highway 9 North Km 4', creditLimit: 800.0, currentDebt: 120.00 },
  ]

  for (const customer of customers) {
    const existing = await prisma.customer.findFirst({ where: { name: customer.name } })
    if (!existing) {
      await prisma.customer.create({ data: customer })
    }
  }

  console.log(`Seeded ${customers.length} customers with credit balances.`)
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })
