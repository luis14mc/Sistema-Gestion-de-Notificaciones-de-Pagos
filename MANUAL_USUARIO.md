# 📖 Manual de Usuario - Sistema de Pagos CNI

**Consejo Nacional de Inversiones - Honduras**  
Guía Completa para Usuarios  
Versión 2.0 - Febrero 2026

---

## 📑 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Inicio de la Aplicación](#inicio-de-la-aplicación)
3. [Interfaz Principal](#interfaz-principal)
4. [Gestión de Personal](#gestión-de-personal)
5. [Configuración del Sistema](#configuración-del-sistema)
6. [Generación de Boletas](#generación-de-boletas)
7. [Histórico de Pagos](#histórico-de-pagos)
8. [Resolución de Problemas](#resolución-de-problemas)

---

## 🎯 Introducción

Bienvenido al **Sistema de Pagos** del Consejo Nacional de Inversiones de Honduras.

### ¿Qué puedes hacer con este sistema?

✅ Gestionar información de empleados  
✅ Calcular automáticamente ISR e IHSS  
✅ Generar boletas de pago en PDF  
✅ Enviar boletas por correo electrónico  
✅ Consultar histórico de pagos  
✅ Exportar reportes de auditoría  

### Requisitos del Sistema

- **Sistema Operativo**: Windows 10/11, Linux o macOS
- **Pantalla**: Resolución mínima 1280x720
- **Conexión a Internet**: Necesaria para envío de correos

---

## 🚀 Inicio de la Aplicación

### Método 1: Ejecutable (Windows)

1. Hacer doble clic en `Sistema_Pagos_CNI.exe`
2. La aplicación se abrirá en una ventana
3. Esperar a que cargue la interfaz (2-3 segundos)

### Método 2: Python (Todos los sistemas)

1. Abrir terminal/consola
2. Navegar a la carpeta del programa:
   ```bash
   cd ruta/a/app_rrhh_cni
   ```
3. Ejecutar:
   ```bash
   python app.py
   ```

### Primera Vez

Al iniciar por primera vez, el sistema:
- ✓ Crea la base de datos automáticamente
- ✓ Configura valores predeterminados
- ✓ Prepara las carpetas necesarias

---

## 🖥️ Interfaz Principal

### Componentes de la Pantalla

```
┌─────────────────────────────────────────────────────┐
│  [Logo]  Sistema de Pagos                    👤     │
│          Consejo Nacional de Inversiones            │
├──────────┬──────────────────────────────────────────┤
│          │                                          │
│  📋 Menu │        Área de Trabajo                   │
│          │                                          │
│ Personal │  Aquí se muestra el contenido           │
│ Boleta   │  de cada sección                         │
│ Histórico│                                          │
│ Config   │                                          │
│          │                                          │
├──────────┴──────────────────────────────────────────┤
│  v2.0 Web                                     CNI   │
└─────────────────────────────────────────────────────┘
```

### Barra Lateral (Menú)

El menú lateral te permite navegar entre secciones:

- **📋 Personal**: Gestión de empleados
- **📄 Boleta de Pago**: Generar boletas
- **🕐 Histórico de Pagos**: Consultar registros
- **⚙️ Configuración**: Ajustes del sistema

**Nota**: La sección activa se resalta con un **borde cyan** a la izquierda.

---

## 👥 Gestión de Personal

### Ver Lista de Empleados

1. Clic en **"Personal"** en el menú lateral
2. Se mostrará la tabla con todos los empleados
3. Puedes ver:
   - Código de empleado (CNI###)
   - Nombre completo
   - Cargo
   - Salario mensual
   - IHSS (calculado automáticamente)
   - ISR (calculado automáticamente)
   - Correo institucional

### Buscar Empleado

1. En la parte superior, usa el campo **"Buscar empleado..."**
2. Escribe el nombre o código
3. La lista se filtrará automáticamente

### Agregar Nuevo Empleado

1. Clic en botón **"+ Nuevo Empleado"** (arriba a la derecha)
2. Completar el formulario:

   **Campos obligatorios** (marcados con *):
   - **Nombre Completo**: Ej. "Juan Carlos Pérez"
   - **Cargo**: Ej. "Analista Financiero"
   - **Salario Mensual**: Ej. 25000.00
   - **Correo Institucional**: Ej. "juan.perez@cni.hn"

   **Campos automáticos** (no editable):
   - **Código de Empleado**: Se genera automáticamente (CNI001, CNI002, etc.)
   - **IHSS**: Se calcula al ingresar el salario
   - **ISR**: Se calcula al ingresar el salario

   **Campos opcionales**:
   - **Otra Deducción**: Cantidad adicional a descontar
   - **Observación**: Descripción de la deducción adicional

3. **Importante**: Al escribir el salario, verás cómo se calculan automáticamente:
   - **IHSS** (fondo verde): Basado en tasas EM + IVM
   - **ISR** (fondo turquesa): Según tabla progresiva

4. Clic en **"Guardar Empleado"**
5. Confirmación: "Empleado guardado correctamente"

### Editar Empleado

1. En la tabla, clic en el ícono **✏️ (lápiz)** del empleado
2. Modificar los campos necesarios
3. **Nota**: El código de empleado NO se puede cambiar
4. Clic en **"Guardar Empleado"**

### Eliminar Empleado

1. En la tabla, clic en el ícono **🗑️ (basura)**
2. Aparecerá confirmación: **"¿Estás seguro?"**
3. Confirmar para eliminar permanentemente

**⚠️ ADVERTENCIA**: Esta acción no se puede deshacer.

---

## ⚙️ Configuración del Sistema

### Acceder a Configuración

1. Clic en **"Configuración"** en el menú lateral
2. Verás tres secciones:
   - Tabla Progresiva ISR 2026
   - Configuración IHSS 2026
   - Configuración SMTP

---

### 📊 Configurar Tabla ISR

La tabla de ISR determina cuánto impuesto se descuenta según el salario.

#### Ver Tabla Actual

La tabla muestra los tramos:
- **Tasa %**: Porcentaje a aplicar
- **Desde (Mensual)**: Salario mínimo del tramo
- **Hasta (Mensual)**: Salario máximo del tramo
- **Descripción**: Ej. "Exentos", "15%", etc.

#### Modificar un Tramo

1. Clic en el ícono **✏️ (editar)** del tramo
2. Aparecerá un diálogo con:
   - Tasa (%)
   - Desde Mensual (L.)
   - Hasta Mensual (L.)
   - Descripción
3. Modificar valores
4. Clic en **"Guardar"**

#### Agregar Nuevo Tramo

1. Clic en **"+ Agregar Tramo"**
2. Completar datos del nuevo tramo
3. Clic en **"Agregar"**
4. Los tramos se ordenan automáticamente

#### Eliminar Tramo

1. Clic en el ícono **🗑️ (eliminar)**
2. El tramo se elimina inmediatamente

#### Guardar Cambios

**IMPORTANTE**: Después de modificar la tabla:

1. Clic en **"Guardar Tabla ISR"**
2. Confirmación: "Tabla ISR Guardada"
3. Opcionalmente, clic en **"Recalcular Todos los Empleados"**
   - Esto actualiza el ISR de todos los empleados existentes
   - Recomendado si cambiaste los tramos

#### Probar Cálculo

Usa la calculadora de prueba:
1. Ingresa un salario de ejemplo
2. Ve el ISR calculado instantáneamente
3. Verifica que los tramos funcionen correctamente

---

### 🏥 Configurar IHSS

El IHSS (Instituto Hondureño de Seguridad Social) se calcula con tres parámetros:

#### Tasas del Empleado

1. **Tasa EM** (Enfermedad y Maternidad): Normalmente 2.5%
2. **Tasa IVM** (Invalidez, Vejez y Muerte): Normalmente 2.5%
3. **Techo de Cotización Mensual**: Máximo salario para cálculo (ej. L. 12,000)

#### Fórmula de Cálculo

```
Salario Base = Mínimo(Salario Real, Techo de Cotización)
IHSS Total = Salario Base × (Tasa EM + Tasa IVM)
```

#### Ejemplo Práctico

Si un empleado gana **L. 30,000** y el techo es **L. 12,000**:
- Salario Base = L. 12,000 (se aplica el techo)
- IHSS = 12,000 × (2.5% + 2.5%) = L. 600.00

#### Modificar Configuración

1. Cambiar los valores en los campos:
   - **Tasa EM** (%)
   - **Tasa IVM** (%)
   - **Techo** (Lempiras)

2. Usa la **calculadora de ejemplo**:
   - Ingresa un salario de prueba
   - Ve el IHSS calculado
   - Verifica que sea correcto

3. Clic en **"Guardar Configuración IHSS"**

4. **Recomendado**: Clic en **"Recalcular IHSS de Todos los Empleados"**
   - Actualiza el IHSS de todos los empleados
   - Usa la nueva configuración

---

### 📧 Configurar Correo (SMTP)

Para enviar boletas por email, necesitas configurar Office 365.

#### Información Requerida

Necesitarás:
- ✉️ **Usuario**: Tu correo @cni.hn con licencia Office 365
- 🔑 **Contraseña**: Contraseña del correo
- 📛 **Nombre para mostrar**: Ej. "Recursos Humanos CNI"

#### Configuración Paso a Paso

1. **Host SMTP**: Dejar `smtp.office365.com`
2. **Puerto**: Dejar `587`
3. **Username**: Ingresar correo completo
   ```
   Ejemplo: rrhh@cni.hn
   ```
4. **Password**: Ingresar contraseña del correo
5. **Emisor**: Dejar "Servicios Online"
6. **Remitente para mostrar**: Tu nombre o departamento
   ```
   Ejemplo: Recursos Humanos CNI
   ```

7. Clic en **"Guardar Configuración SMTP"**

#### Verificar Configuración

Para probar que funciona:
1. Genera una boleta de prueba
2. Selecciona modo **"Enviar Email"**
3. Si llega el correo, la configuración es correcta

#### Solución de Problemas SMTP

**Error: "Autenticación fallida"**
- ✓ Verificar usuario y contraseña
- ✓ Asegurar que la cuenta tenga licencia Office 365
- ✓ Verificar que no tenga autenticación de dos factores

**Error: "No se pudo conectar al servidor"**
- ✓ Verificar conexión a internet
- ✓ Verificar que puerto 587 no esté bloqueado
- ✓ Contactar a Ing. Luis Martínez si persiste

---

## 📄 Generación de Boletas

### Acceder a Boletas

1. Clic en **"Boleta de Pago"** en el menú lateral

### Generar Boleta Individual

#### Paso 1: Seleccionar Empleado

1. En el campo **"Empleado"**, clic en el desplegable
2. Buscar y seleccionar el empleado
3. La información del empleado se cargará automáticamente

#### Paso 2: Establecer Período

1. **Desde**: Fecha de inicio del período (DD/MM/AAAA)
   ```
   Ejemplo: 01/02/2026
   ```
2. **Hasta**: Fecha de fin del período (DD/MM/AAAA)
   ```
   Ejemplo: 28/02/2026
   ```

#### Paso 3: Generar Vista Previa

1. Clic en **"👁 Vista Previa"**
2. Aparecerá la boleta simulada a la derecha:
   - Información del empleado
   - Salario mensual (en verde)
   - Deducciones (IHSS, ISR, Otro)
   - Total de deducciones (en rojo)
   - **Salario Neto** (destacado en grande)

3. Revisar que todo esté correcto

#### Paso 4: Generar Boleta

Tienes 3 opciones:

**Opción 1: Solo PDF**
- Genera el PDF
- Lo guarda en: `reportes_pagos_RRHH/AAAA/MM/`
- No envía correo

**Opción 2: Solo Email**
- Envía el correo con la boleta
- No guarda PDF localmente

**Opción 3: PDF + Email** (Recomendado)
- Genera el PDF
- Lo guarda localmente
- Lo envía por correo adjunto

**Seleccionar opción y confirmar**:
1. Aparecerá diálogo de confirmación
2. Mostrar período y modo seleccionado
3. Clic en **"Generar"**

#### Resultado

- ✅ Éxito: "Boleta generada correctamente"
- 📁 Ubicación del PDF (si aplica)
- ✉️ "Email enviado" (si aplica)

---

### Generar Boletas Masivas

Para generar boletas de **todos los empleados** a la vez:

#### Paso 1: Botón Generar Todos

1. En la parte superior derecha, clic en **"Generar Todos"**
2. Aparecerá un formulario

#### Paso 2: Configurar Generación

1. **Fecha Desde**: Inicio del período (ej. 01/02/2026)
2. **Fecha Hasta**: Fin del período (ej. 28/02/2026)
3. **Modo**: Seleccionar
   - Solo PDF
   - Solo Email
   - PDF + Email

#### Paso 3: Confirmar

1. Clic en **"Generar"**
2. El sistema mostrará:
   - **Progreso**: "Generando boletas..."
   - Indicador de carga animado

#### Paso 4: Revisar Resultados

Al terminar, verás un resumen:

```
✅ Boletas Generadas

Exitosos: 45
Fallidos: 2
Total: 47

--- Detalles ---
❌ Pedro García: No tiene correo institucional
❌ Ana Martínez: Error al enviar email
```

**Casos de error comunes**:
- Empleado sin correo institucional
- SMTP mal configurado
- Sin conexión a internet (para emails)

---

## 📚 Histórico de Pagos

### Acceder al Histórico

1. Clic en **"Histórico de Pagos"** en el menú lateral

### Estadísticas Generales

En la parte superior verás 3 tarjetas:

1. **Total Empleados**: Cantidad de empleados activos
2. **Total Boletas**: Boletas generadas en el sistema
3. **Monto Total**: Suma de todos los salarios netos pagados

### Filtrar Registros

Puedes filtrar el histórico:

1. **Por Empleado**: Buscar por nombre o código
2. **Por Fecha Desde**: Seleccionar fecha inicio
3. **Por Fecha Hasta**: Seleccionar fecha fin
4. Clic en **"Filtrar"** o presionar Enter

**Limpiar filtros**: Clic en "🗑️ Limpiar" o dejar campos vacíos

### Tabla de Registros

La tabla muestra:
- **Fecha**: Cuándo se generó
- **Empleado**: Código y nombre
- **Cargo**: Puesto del empleado
- **Período**: Fechas del pago
- **Salario**: Salario mensual
- **IHSS**: Deducción IHSS
- **ISR**: Deducción ISR
- **Otro**: Otra deducción
- **Deducciones**: Total descontado
- **Neto**: Salario final
- **Tipo**: PDF, Email o Ambos

### Exportar Reporte de Auditoría

Para generar un reporte completo:

1. Aplicar filtros si deseas (opcional)
2. Clic en **"Exportar Reporte"**
3. El sistema generará un PDF con:
   - Tabla completa de registros
   - Totales y subtotales
   - Fecha de generación
   - Logo institucional

4. El archivo se guarda en:
   ```
   reportes_pagos_RRHH/auditoria/Auditoria_AAAAMMDD_HHMMSS.pdf
   ```

5. Confirmación: "Reporte exportado correctamente"

### Ordenar Tabla

- Clic en los **encabezados de columna** para ordenar
- Primer clic: Ascendente (↑)
- Segundo clic: Descendente (↓)

---

## 🔧 Resolución de Problemas

### La aplicación no inicia

**Síntoma**: Al hacer doble clic, no pasa nada

**Soluciones**:
1. Verificar que Python esté instalado
2. Abrir terminal y ejecutar manualmente:
   ```bash
   python app.py
   ```
3. Ver errores en consola
4. Verificar que todas las dependencias estén instaladas:
   ```bash
   pip install -r requirements.txt
   ```

---

### No se guardan los cambios

**Síntoma**: Los datos no se guardan al cerrar

**Soluciones**:
1. Verificar permisos de escritura en la carpeta
2. Verificar que `rrhh_cni.db` no esté en uso por otro programa
3. Cerrar la aplicación correctamente (no forzar cierre)

---

### Error al generar PDF

**Síntoma**: "Error al generar PDF"

**Soluciones**:
1. Verificar que la carpeta `reportes_pagos_RRHH` exista
2. Verificar permisos de escritura
3. Cerrar cualquier PDF abierto del sistema
4. Verificar espacio en disco

---

### Error al enviar email

**Síntoma**: "No se pudo enviar el correo"

**Causas comunes**:

1. **SMTP no configurado**
   - Ir a Configuración → SMTP
   - Completar todos los campos
   - Guardar configuración

2. **Empleado sin correo**
   - Verificar que el empleado tenga correo institucional
   - Editar empleado y agregar correo

3. **Contraseña incorrecta**
   - Verificar usuario y contraseña SMTP
   - Debe ser una cuenta Office 365 válida

4. **Sin conexión a internet**
   - Verificar conexión
   - Probar abrir un navegador

5. **Puerto bloqueado**
   - Contactar a TI
   - El puerto 587 debe estar abierto

---

### ISR o IHSS mal calculados

**Síntoma**: Los montos no coinciden con lo esperado

**Soluciones**:

1. **Verificar tabla ISR**
   - Ir a Configuración → Tabla ISR
   - Revisar que los tramos sean correctos
   - Usar calculadora de prueba

2. **Verificar configuración IHSS**
   - Ir a Configuración → IHSS
   - Revisar tasas EM e IVM
   - Verificar techo de cotización
   - Usar calculadora de ejemplo

3. **Recalcular**
   - Después de modificar configuraciones
   - Usar botones "Recalcular Todos"
   - Esto actualiza todos los empleados

---

### La interfaz se ve mal

**Síntoma**: Colores, tamaños o disposición incorrectos

**Soluciones**:
1. Refrescar con **Ctrl + Shift + R** (Windows/Linux) o **Cmd + Shift + R** (Mac)
2. Limpiar caché del navegador/ventana
3. Verificar resolución de pantalla (mínimo 1280x720)
4. Actualizar navegador embebido (pywebview)

---

### Base de datos corrupta

**Síntoma**: Errores al acceder a datos

**Solución - Restaurar backup**:

1. Cerrar aplicación
2. Buscar archivo `rrhh_cni.db`
3. Si tienes backup, reemplazar:
   ```bash
   cp rrhh_cni_backup.db rrhh_cni.db
   ```
4. Si no hay backup, contactar a Ing. Luis Martínez

**Prevención**:
- Hacer backups periódicos de `rrhh_cni.db`
- Usar herramientas de backup automático

---

## 📋 Buenas Prácticas

### ✅ Recomendaciones

1. **Backups regulares**
   - Respaldar `rrhh_cni.db` semanalmente
   - Guardar en ubicación segura

2. **Verificar antes de enviar**
   - Siempre generar vista previa
   - Revisar datos antes de confirmar

3. **Actualizar configuraciones**
   - Revisar tabla ISR anualmente
   - Actualizar tasas IHSS según legislación

4. **Organización de archivos**
   - Los PDFs se organizan automáticamente por año/mes
   - No mover ni renombrar archivos generados

5. **Uso del histórico**
   - Consultar periódicamente
   - Exportar reportes de auditoría mensuales

---

## 📞 Soporte y Ayuda

### Contacto del Desarrollador

Para dudas técnicas sobre el sistema:

- **Nombre**: Ing. Luis Martínez
- **Rol**: Software Developer
- **Email**: luismartinez.94mc@gmail.com

### Contacto CNI (Soporte Interno)

Para soporte operativo dentro del CNI:

- **Departamento**: Oficial de TI
- **Email**: amartinez@cni.hn
- **Organización**: Consejo Nacional de Inversiones

### Información a proporcionar

Al reportar un problema, incluir:
1. Versión del sistema (v2.0)
2. Sistema operativo
3. Descripción del problema
4. Pasos para reproducir
5. Capturas de pantalla (si aplica)

### Canales de Soporte

- **Problemas técnicos/bugs**: Contactar a Ing. Luis Martínez (luismartinez.94mc@gmail.com)
- **Configuración/uso diario**: Contactar a Oficial de TI CNI (amartinez@cni.hn)
- **Urgencias**: Contactar a ambos

---

## 📝 Glosario

- **ISR**: Impuesto Sobre la Renta
- **IHSS**: Instituto Hondureño de Seguridad Social
- **EM**: Enfermedad y Maternidad
- **IVM**: Invalidez, Vejez y Muerte
- **SMTP**: Protocolo de envío de correos
- **PDF**: Formato de documento portable
- **CNI**: Consejo Nacional de Inversiones

---

## ✨ Consejos Finales

1. **Familiarízate con la interfaz** explorando cada sección
2. **Practica con datos de prueba** antes de usar datos reales
3. **Mantén actualizada** la configuración según cambios legales
4. **Consulta este manual** ante cualquier duda
5. **Reporta problemas** a Ing. Luis Martínez para mejorar el sistema

---

**¡Gracias por usar el Sistema de Pagos CNI!**

---

**Última actualización**: Febrero 2026  
**Versión del Manual**: 2.0  
**Desarrollado por**: Ing. Luis Martínez - Software Developer
