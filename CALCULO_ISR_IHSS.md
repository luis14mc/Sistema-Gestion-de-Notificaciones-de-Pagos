# Calculo de ISR e IHSS - Sistema de Pagos CNI

**Consejo Nacional de Inversiones - Honduras**  
Documentacion tecnica de los algoritmos de calculo  
Version 2.1.0 - Febrero 2026

---

## Indice

1. [Calculo del ISR (Impuesto Sobre la Renta)](#calculo-del-isr-impuesto-sobre-la-renta)
2. [Calculo del IHSS (Instituto Hondureno de Seguridad Social)](#calculo-del-ihss-instituto-hondureno-de-seguridad-social)
3. [Ejemplos practicos](#ejemplos-practicos)
4. [Configuracion y personalizacion](#configuracion-y-personalizacion)

---

## Calculo del ISR (Impuesto Sobre la Renta)

### Concepto

El ISR en Honduras se calcula en dos etapas:

1. **Deducciones**: Se restan del ingreso anual los gastos medicos y el deducible IVM (aportacion al regimen de Invalidez, Vejez y Muerte).
2. **Renta Neta Gravable**: Es el resultado de restar las deducciones al ingreso anual.
3. **Tabla Progresiva Anual**: Se aplica la tabla de tramos sobre la Renta Neta Gravable (en montos anuales).
4. **ISR Mensual**: El impuesto anual se divide entre los meses trabajados para obtener la retencion mensual.

### Deducciones Configurables

| Parametro | Descripcion | Valor por defecto |
|-----------|-------------|:-----------------:|
| **Gastos Medicos** | Deduccion fija anual (L.) | 40,000.00 |
| **Deducible IVM** | Monto fijo mensual que se multiplica x 12 (L.) | 297.58 |

### Formula Completa

```
Deducciones_Anual = Gastos_Medicos + (Deducible_IVM × 12)
Ingreso_Anual = Salario_Mensual × 12  (o × meses_trabajados si es parcial)
Renta_Neta_Gravable = max(0, Ingreso_Anual - Deducciones_Anual)
ISR_Anual = aplicar tabla progresiva sobre Renta_Neta_Gravable
ISR_Mensual = ISR_Anual / 12
```

### Tabla Progresiva Oficial 2026 (Referencia SH) - Renta Neta Gravable Anual

| Tasa | Desde (L./anual) | Hasta (L./anual) | Salario Mensual |
|:----:|-----------------:|-----------------:|----------------:|
| Exentos | 0.01 | 228,324.32 | 0.01 - 22,360.36 |
| 15% | 228,324.33 | 348,154.10 | 22,360.37 - 32,346.18 |
| 20% | 348,154.11 | 809,660.75 | 32,346.19 - 70,805.06 |
| 25% | 809,660.76 | en adelante | 70,805.07 en adelante |

### Algoritmo de la Tabla Progresiva

Para cada tramo, en orden ascendente por `desde_anual`:

1. **Si** la renta neta gravable es menor que el limite inferior del tramo (`desde`), **terminar**.
2. **Calcular** la porcion gravable en ese tramo:
   ```
   gravable = min(renta_neta_gravable, hasta) - desde + 0.01
   ```
3. **Si** `gravable > 0`, sumar al ISR anual:
   ```
   isr_anual += gravable * (tasa / 100)
   ```
4. **Repetir** para el siguiente tramo.
5. **Retornar** `ISR_anual / 12` redondeado a 2 decimales (ISR mensual).

### Ejemplo Numerico - Salario L. 26,400/mes (Ingreso Anual L. 316,800)

**Paso 1 - Deducciones**:
```
Deducciones = 40,000 + (297.58 × 12) = 40,000 + 3,570.96 = L. 43,570.96
```

**Paso 2 - Renta Neta Gravable**:
```
Renta_Neta_Gravable = 316,800 - 43,570.96 = L. 273,229.04
```

**Paso 3 - Aplicar tabla progresiva anual**:

| Tramo | Tasa | Desde | Hasta | Porcion gravable | Impuesto tramo |
|-------|:----:|------:|------:|-----------------:|---------------:|
| 1     | 0%   | 0.12  | 268,324.32 | 268,324.32 | L. 0.00 |
| 2     | 15%  | 268,324.44 | 388,154.16 | 4,904.60 | L. 735.69 |
| **Total ISR Anual** | | | | | **L. 735.69** |

**Paso 4 - ISR Mensual**:
```
ISR_Mensual = 735.69 / 12 = L. 61.31
```

### Empleados que ingresan a mitad de ano o mitad de mes

**Salario del primer mes (prorrateado por dias):**
- Si el empleado no ingresa el dia 1: `sueldo_dias = Salario_Base / 30`
- `Sueldo_mes_primero = sueldo_dias × cantidad_dias` (dias desde fecha ingreso hasta fin de mes)

**ISR:**
- **meses_trabajados** = 12 - mes_ingreso + 1 (ej: ingreso en febrero = 11 meses)
- **Ingreso_Anual** = Sueldo_primer_mes_prorrateado + (Salario_Mensual × (meses_trabajados - 1))
- **Deducciones** = (Gastos_Medicos × meses/12) + (Deducible_IVM × meses_trabajados)
- **ISR_Mensual** = ISR_Anual / meses_trabajados

**IHSS:** Se calcula sobre el salario efectivo del periodo (prorrateado en primer mes).

La fecha de ingreso se configura en el formulario del empleado. Al generar boletas, el sistema aplica automaticamente el prorrateo cuando corresponde.  


## Calculo del IHSS (Instituto Hondureno de Seguridad Social)

### Concepto

El IHSS (aportacion del empleado) se calcula sobre un **salario base** que no puede superar un **techo de cotizacion**. Se aplican las tasas de Enfermedad y Maternidad (EM) e Invalidez, Vejez y Muerte (IVM).

### Parametros configurables

| Parametro | Descripcion | Valor por defecto |
|-----------|-------------|:-----------------:|
| **Tasa EM** | Enfermedad y Maternidad - aporte del empleado | 2.5% |
| **Tasa IVM** | Invalidez, Vejez y Muerte - aporte del empleado | 2.5% |
| **Techo de Cotizacion** | Salario maximo sobre el cual se calcula (L./mensual) | L. 12,000.00 |

### Formula

```
Salario Base = min(Salario Real, Techo de Cotizacion)
IHSS Total = Salario Base × (Tasa EM + Tasa IVM) / 100
```

**En palabras**: Se toma el menor entre el salario del empleado y el techo. Sobre ese monto se aplica la suma de las tasas EM e IVM.

### Algoritmo

1. Obtener `tasa_em`, `tasa_ivm` y `techo` de la configuracion del sistema.
2. Calcular:
   ```
   salario_base = min(salario, techo)
   tasa_total = tasa_em + tasa_ivm
   ihss_total = salario_base * tasa_total / 100.0
   ```
3. Retornar el resultado redondeado a 2 decimales.

### Ejemplo Numerico - Salario L. 30,000 (techo L. 12,000, EM 2.5%, IVM 2.5%)

```
Salario Base = min(30,000, 12,000) = L. 12,000
IHSS = 12,000 × (2.5 + 2.5) / 100 = L. 600.00
```

### Ejemplo Numerico - Salario L. 8,000 (techo L. 12,000)

```
Salario Base = min(8,000, 12,000) = L. 8,000
IHSS = 8,000 × 5% = L. 400.00
```

### Comportamiento

- **Salario menor al techo**: Se calcula sobre el salario real. A mayor salario, mayor IHSS.
- **Salario mayor o igual al techo**: Se calcula sobre el techo. El IHSS se mantiene constante aunque el salario suba.

---

## Ejemplos practicos

### Caso 1: Empleado con salario L. 25,000

**ISR**:
- Tramo 0%: 22,360.36 × 0% = 0
- Tramo 15%: (25,000 - 22,360.37 + 0.01) = 2,639.64 × 15% = 395.95
- **ISR total: L. 395.95**

**IHSS** (techo 12,000, EM 2.5% + IVM 2.5% = 5%):
- Salario base = 12,000
- IHSS = 12,000 × 5% = **L. 600.00**

**Salario neto** (sin otra deduccion):
- L. 25,000 - 395.95 - 600.00 = **L. 24,004.05**

---

### Caso 2: Empleado con salario L. 50,000

**ISR**:
- Tramo 0%: 22,360.36 × 0% = 0
- Tramo 15%: 9,985.82 × 15% = 1,497.87
- Tramo 20%: (50,000 - 32,346.19 + 0.01) = 17,653.82 × 20% = 3,530.76
- **ISR total: L. 5,028.63**

**IHSS**:
- Salario base = 12,000
- IHSS = **L. 600.00**

**Salario neto** (sin otra deduccion):
- L. 50,000 - 5,028.63 - 600.00 = **L. 44,371.37**

---

### Caso 3: Empleado con salario L. 10,000 (menor al techo IHSS)

**ISR**:
- Tramo 0%: 10,000 (todo el salario en tramo exento)
- **ISR total: L. 0.00**

**IHSS**:
- Salario base = 10,000 (salario real menor al techo)
- IHSS = 10,000 × 5% = **L. 500.00**

**Salario neto**:
- L. 10,000 - 0 - 500.00 = **L. 9,500.00**

---

## Configuracion y personalizacion

### Tabla ISR

La tabla de tramos se puede modificar en **Configuracion > Tabla Progresiva ISR**:

- **Agregar tramo**: Boton "+ Agregar Tramo"
- **Editar tramo**: Icono de lapiz en cada fila
- **Eliminar tramo**: Icono de papelera
- **Guardar**: Boton "Guardar Tabla ISR"
- **Recalcular**: Despues de guardar, usar "Recalcular Todos los Empleados" para actualizar el ISR de todos los empleados existentes

### Configuracion IHSS

La configuracion IHSS se modifica en **Configuracion > IHSS**:

- **Tasa EM**: Porcentaje de Enfermedad y Maternidad
- **Tasa IVM**: Porcentaje de Invalidez, Vejez y Muerte
- **Techo de Cotizacion**: Monto maximo en Lempiras (salario sobre el cual se calcula)
- **Guardar**: Boton "Guardar Configuracion IHSS"
- **Recalcular**: Despues de guardar, usar "Recalcular IHSS de Todos los Empleados"

### API de calculo

Para probar el calculo desde fuera del sistema:

```bash
# Calcular ISR para un salario
curl "http://localhost:5000/api/calcular_isr?salario=25000"

# Respuesta: {"isr": 395.95}
```

---

## Referencias

- **Codigo fuente**: `server.py` - funciones `_calcular_isr()` y `_calcular_ihss()`
- **Tablas de base de datos**: `isr_tramos`, `ihss_config`
- **Manual tecnico**: `MANUAL_TECNICO.md` - seccion "Logica de Negocio"

---

**Desarrollado por**: Ing. Luis Martinez - luismartinez.94mc@gmail.com  
**Consejo Nacional de Inversiones - Honduras**
