# Lógica de Nómina: Ajustes por Ingreso Tardío (Honduras)

## 1. Cálculo de Salario Prorrateado (Primer Mes)
Si `fecha_ingreso` > día 1 del mes:
- `sueldo_diario = sueldo_base / 30`
- `dias_trabajados = 30 - dia_ingreso` (o lógica de días reales laborados)
- `salario_mes_1 = sueldo_diario * dias_trabajados`

## 2. Proyección Fiscal ISR (Año Natural)
Para empleados que ingresan después de enero:
- **Meses a trabajar (`n`):** `12 - mes_ingreso + 1` (Ej: Ingreso en Febrero, n = 11).
- **Ingreso Anual Proyectado:** `(salario_mes_1) + (sueldo_base * (n - 1))`.
- **Deducciones Proyectadas (IVM/IHSS):** Se calculan base `n` meses trabajados.
- **Gastos Médicos:** Valor fijo anual (L 40,000.00) sin importar el mes de ingreso.

## 3. Retenciones (IHSS/Aportaciones)
- Aplicar techos vigentes sobre el salario real percibido cada mes.
- El cálculo del primer mes debe basarse obligatoriamente en el `salario_mes_1`.