# Manual de Usuario - Sistema de Pagos CNI

**Consejo Nacional de Inversiones - Honduras**  
Guia Completa para Usuarios  
Version 2.1.0 - Febrero 2026

---

## Tabla de Contenidos

1. [Descripcion General del Sistema](#descripcion-general-del-sistema)
2. [Resumen de Funcionalidades](#resumen-de-funcionalidades)
3. [Inicio de la Aplicacion](#inicio-de-la-aplicacion)
4. [Interfaz Principal](#interfaz-principal)
5. [Modulo 1: Gestion de Personal](#modulo-1-gestion-de-personal)
6. [Modulo 2: Boleta de Pago](#modulo-2-boleta-de-pago)
7. [Modulo 3: Historico de Pagos](#modulo-3-historico-de-pagos)
8. [Modulo 4: Configuracion del Sistema](#modulo-4-configuracion-del-sistema)
9. [Resolucion de Problemas](#resolucion-de-problemas)
10. [Buenas Practicas](#buenas-practicas)
11. [Glosario](#glosario)
12. [Soporte y Contacto](#soporte-y-contacto)

---

## Descripcion General del Sistema

El **Sistema de Pagos CNI** es una aplicacion desarrollada para el Consejo Nacional de Inversiones de Honduras que centraliza y automatiza los procesos de gestion de nomina del departamento de Recursos Humanos.

El sistema permite administrar la informacion de los empleados, calcular automaticamente las deducciones legales (ISR e IHSS), generar boletas de pago en formato PDF con identidad institucional, enviar dichas boletas por correo electronico y mantener un historico completo de todos los pagos realizados con capacidad de auditoria.

### Arquitectura de la Aplicacion

La aplicacion funciona como un sistema web local que se ejecuta en el equipo del usuario. Al iniciarla, se levanta un servidor interno y la interfaz se presenta en el navegador o en una ventana de escritorio nativa. Toda la informacion se almacena localmente en una base de datos SQLite, lo que garantiza privacidad y no requiere conexion a internet para operar (la conexion solo es necesaria para el envio de correos electronicos).

### Requisitos del Sistema

| Requisito | Especificacion |
|-----------|---------------|
| Sistema Operativo | Windows 10/11 (ejecutable .exe) o cualquier SO con Python 3.8+ |
| Pantalla | Resolucion minima 1280x720 |
| Espacio en disco | 100 MB para la aplicacion + espacio para reportes PDF |
| Conexion a Internet | Solo necesaria para el envio de correos electronicos |
| Navegador | Edge, Chrome, Firefox o cualquier navegador moderno (modo navegador) |

---

## Resumen de Funcionalidades

A continuacion se presenta un panorama completo de lo que ofrece cada modulo del sistema. En las secciones posteriores se explica cada funcionalidad paso a paso.

### Modulo 1 - Gestion de Personal

Este modulo es el punto de partida del sistema. Aqui se registran, consultan, modifican y eliminan los empleados del Consejo Nacional de Inversiones.

**Funcionalidades principales:**

- **Registro de empleados**: Crear nuevos registros con nombre, cargo, salario mensual, correo institucional y deducciones opcionales.
- **Codigo automatico**: Cada empleado recibe un codigo unico con formato `CNI001`, `CNI002`, etc., generado automaticamente y no editable.
- **Calculo automatico de ISR**: Al ingresar el salario, el sistema calcula en tiempo real el Impuesto Sobre la Renta aplicando la tabla progresiva configurada. El campo no es editable manualmente.
- **Calculo automatico de IHSS**: Igualmente, se calcula la cotizacion al Instituto Hondureno de Seguridad Social considerando las tasas de Enfermedad y Maternidad (EM) e Invalidez, Vejez y Muerte (IVM), respetando el techo de cotizacion. Tampoco es editable manualmente.
- **Deducciones adicionales**: Campo opcional para registrar cualquier otro descuento (prestamos, adelantos, etc.) con su respectiva observacion.
- **Busqueda y filtrado**: Campo de busqueda rapida por nombre o codigo sobre la tabla de empleados.
- **Edicion y eliminacion**: Modificar datos de un empleado existente o eliminarlo del sistema con confirmacion de seguridad.

### Modulo 2 - Boleta de Pago

Este modulo permite generar las boletas de pago individuales o masivas para todos los empleados. Es el nucleo operativo del sistema.

**Funcionalidades principales:**

- **Seleccion de empleado**: Desplegable con todos los empleados registrados.
- **Selector de mes**: Se escoge unicamente el mes de pago. El sistema calcula automaticamente el periodo correspondiente: del dia 20 del mes anterior al dia 20 del mes seleccionado (por ejemplo, seleccionar "Febrero 2026" genera el periodo 20/01/2026 al 20/02/2026).
- **Vista previa**: Antes de generar, se puede visualizar un resumen completo de la boleta con todos los montos calculados (salario, deducciones, neto).
- **Generacion en PDF**: Crea un documento PDF profesional con el logo del CNI, colores institucionales (azul #233981, cyan #2AAAD6, verde #1BAE64), desglose de ingresos y deducciones, y barra destacada de salario neto.
- **Envio por correo electronico**: Envia la boleta al correo institucional del empleado como cuerpo HTML con diseño corporativo limpio (fondo blanco, compatible con modo oscuro de clientes de correo) y el PDF adjunto.
- **Tres modos de generacion**: Solo PDF, Solo Email, o PDF + Email (recomendado).
- **Generacion masiva ("Generar Todos")**: Un solo clic genera las boletas de todos los empleados registrados, mostrando al finalizar un reporte detallado con exitos, fallos y motivos de error.

### Modulo 3 - Historico de Pagos

Este modulo ofrece una vista completa de todas las boletas que han sido generadas en el sistema, sirviendo como registro de auditoria y consulta.

**Funcionalidades principales:**

- **Tarjetas de estadisticas**: En la parte superior se muestran tres indicadores resumidos: total de registros, monto neto total pagado y total de deducciones aplicadas.
- **Filtros de busqueda**: Filtrar por nombre/codigo de empleado y por rango de fechas con selectores de calendario. El sistema valida que la fecha final no sea menor a la inicial.
- **Tabla simplificada**: Muestra Fecha, Codigo, Empleado, Cargo, Tipo y un boton de accion. Los registros se ordenan automaticamente del mas reciente al mas antiguo.
- **Detalle en modal**: Al hacer clic en "Ver", se abre una ventana superpuesta con el desglose financiero completo de esa boleta (salario, cada deduccion, total deducciones, salario neto y ruta del PDF).
- **Paginacion**: La tabla muestra 10 registros por pagina con navegacion (Primera, Anterior, Siguiente, Ultima) e indicador de pagina actual.
- **Exportar reporte de auditoria**: Genera un PDF profesional con el logo CNI y colores institucionales que incluye la tabla completa de todos los registros historicos.

### Modulo 4 - Configuracion del Sistema

Este modulo permite ajustar los parametros que rigen los calculos automaticos y la comunicacion por correo.

**Funcionalidades principales:**

- **Tabla progresiva de ISR**: Configurar los tramos del Impuesto Sobre la Renta con sus rangos de salario y tasas porcentuales. Permite agregar, editar y eliminar tramos. Incluye una calculadora de prueba para verificar los calculos y un boton para recalcular el ISR de todos los empleados existentes.
- **Configuracion de IHSS**: Definir la tasa de Enfermedad y Maternidad (EM), la tasa de Invalidez, Vejez y Muerte (IVM) y el techo de cotizacion mensual. Incluye calculadora de ejemplo y boton para recalcular el IHSS de todos los empleados.
- **Configuracion SMTP (correo)**: Parametros del servidor de correo Office 365 para el envio de boletas: host, puerto, usuario, contrasena y nombre de remitente.

### Caracteristicas Transversales

Ademas de los modulos, el sistema cuenta con:

- **Identidad institucional**: Logo del CNI y paleta de colores institucionales en toda la interfaz, PDFs y correos electronicos.
- **Interfaz moderna**: Diseno responsivo con Tailwind CSS, menu lateral con indicador de seccion activa y alertas interactivas con SweetAlert2.
- **Validacion de datos**: Verificacion automatica de campos obligatorios, formatos de fecha y coherencia de rangos.
- **Organizacion automatica de archivos**: Los PDF se guardan en carpetas organizadas por anio y mes dentro de `reportes_pagos_RRHH/`.

---

## Inicio de la Aplicacion

### Metodo 1: Ejecutable de Windows (Recomendado para usuarios finales)

1. Localizar el archivo `SistemaPagosCNI.exe` en la carpeta de instalacion
2. Hacer doble clic para ejecutar
3. La aplicacion abrira automaticamente el navegador por defecto con la interfaz del sistema
4. Esperar 2-3 segundos a que cargue completamente

**Nota**: En la consola que aparece se mostrara la direccion local (ej. `http://127.0.0.1:XXXXX`). No cerrar esa ventana de consola mientras se usa la aplicacion.

### Metodo 2: Ejecucion con Python (Desarrollo o Linux/macOS)

1. Abrir una terminal o consola de comandos
2. Navegar a la carpeta del proyecto:
   ```bash
   cd ruta/a/app_rrhh_cni
   ```
3. Ejecutar:
   ```bash
   python app.py
   ```
4. Si se desea solo el modo web sin ventana de escritorio:
   ```bash
   python server.py
   ```
   Luego abrir `http://localhost:5000` en el navegador.

### Primera Ejecucion

Al iniciar por primera vez, el sistema automaticamente:
- Crea la base de datos `rrhh_cni.db` con todas las tablas necesarias
- Establece valores por defecto para ISR, IHSS y SMTP
- Crea la carpeta `reportes_pagos_RRHH/` para almacenar los PDFs

No se requiere ninguna configuracion inicial para comenzar a usar el sistema.

---

## Interfaz Principal

### Estructura de la Pantalla

La interfaz se divide en tres zonas:

```
+---------------------------------------------------------+
|  [Logo CNI]  Sistema de Pagos                           |
|              Consejo Nacional de Inversiones             |
+------------+--------------------------------------------+
|            |                                            |
|  MENU      |          AREA DE TRABAJO                   |
|  LATERAL   |                                            |
|            |  Aqui se muestra el contenido              |
| > Personal |  de la seccion seleccionada                |
|   Boleta   |                                            |
|   Historico|                                            |
|   Config   |                                            |
|            |                                            |
+------------+--------------------------------------------+
|  v2.1.0 Web              Consejo Nacional de Inversiones|
+---------------------------------------------------------+
```

### Menu Lateral

El menu de la izquierda permite navegar entre los cuatro modulos del sistema:

| Opcion | Descripcion |
|--------|-------------|
| **Personal** | Gestion de empleados (agregar, editar, eliminar, buscar) |
| **Boleta de Pago** | Generar boletas individuales o masivas |
| **Historico de Pagos** | Consultar registros pasados y exportar auditorias |
| **Configuracion** | Ajustar ISR, IHSS y correo SMTP |

La seccion activa se distingue por un **borde cyan a la izquierda** y un fondo mas claro.

---

## Modulo 1: Gestion de Personal

### Vista General

Al acceder a esta seccion se muestra la tabla de todos los empleados registrados con sus datos principales y un campo de busqueda en la parte superior.

### 1.1 Ver Lista de Empleados

1. Hacer clic en **"Personal"** en el menu lateral
2. La tabla muestra las siguientes columnas:
   - **Codigo**: Identificador unico del empleado (CNI001, CNI002, ...)
   - **Nombre**: Nombre completo
   - **Cargo**: Puesto dentro de la organizacion
   - **Salario**: Salario mensual bruto en Lempiras
   - **IHSS**: Deduccion calculada automaticamente
   - **ISR**: Impuesto calculado automaticamente
   - **Correo**: Correo institucional del empleado
   - **Acciones**: Botones para editar y eliminar

### 1.2 Buscar un Empleado

1. Ubicar el campo **"Buscar empleado..."** en la parte superior de la tabla
2. Escribir el nombre o codigo del empleado
3. La tabla se filtra automaticamente en tiempo real conforme se escribe

### 1.3 Agregar un Nuevo Empleado

1. Hacer clic en el boton **"+ Nuevo Empleado"** ubicado arriba a la derecha
2. Se despliega el formulario de registro con los siguientes campos:

**Campos que se llenan manualmente:**

| Campo | Obligatorio | Ejemplo |
|-------|:-----------:|---------|
| Nombre Completo | Si | Juan Carlos Perez Lopez |
| Cargo | Si | Analista Financiero |
| Salario Mensual (L.) | Si | 25000.00 |
| Correo Institucional | Si | juan.perez@cni.hn |
| Otra Deduccion (L.) | No | 500.00 |
| Observacion de deduccion | No | Prestamo personal |

**Campos automaticos (no editables):**

| Campo | Como se calcula |
|-------|----------------|
| Codigo de Empleado | Generado secuencialmente: CNI001, CNI002, CNI003... |
| IHSS | Segun tasas EM + IVM y techo de cotizacion configurados |
| ISR | Segun tabla progresiva de tramos configurada |

3. Al escribir el salario mensual, observar como los campos de IHSS e ISR se actualizan automaticamente:
   - **IHSS** aparece con fondo verde
   - **ISR** aparece con fondo turquesa

4. Hacer clic en **"Guardar Empleado"**
5. Aparecera un mensaje de confirmacion: "Empleado guardado correctamente"
6. El nuevo empleado se mostrara en la tabla

### 1.4 Editar un Empleado Existente

1. En la tabla de empleados, localizar al empleado que se desea modificar
2. Hacer clic en el icono de **lapiz** (columna Acciones)
3. El formulario se llena con los datos actuales del empleado
4. Modificar los campos necesarios
5. **Nota importante**: El codigo de empleado (CNI###) no se puede cambiar
6. Si se modifica el salario, el IHSS e ISR se recalculan automaticamente
7. Hacer clic en **"Guardar Empleado"** para confirmar los cambios

### 1.5 Eliminar un Empleado

1. En la tabla, hacer clic en el icono de **papelera** del empleado
2. Aparece un dialogo de confirmacion: "¿Estas seguro de eliminar a [nombre]?"
3. Hacer clic en **"Confirmar"** para proceder o **"Cancelar"** para abortar

**Advertencia**: La eliminacion es permanente y no se puede deshacer. Los registros historicos de boletas generadas previamente para ese empleado se conservan.

---

## Modulo 2: Boleta de Pago

### Vista General

Este modulo permite generar boletas de pago para un empleado especifico o para todos los empleados de manera masiva. La boleta incluye el desglose completo de ingresos, deducciones y salario neto.

### 2.1 Generar Boleta Individual

#### Paso 1 - Seleccionar Empleado

1. Hacer clic en **"Boleta de Pago"** en el menu lateral
2. En el campo **"Empleado"**, hacer clic en el desplegable
3. Seleccionar el empleado deseado de la lista
4. Los datos del empleado se cargan automaticamente

#### Paso 2 - Seleccionar el Mes de Pago

1. En el campo **"Mes de Pago"**, hacer clic para abrir el selector de meses
2. Seleccionar el mes y anio correspondientes al periodo de pago

El sistema calcula automaticamente el periodo:
- **Fecha inicio**: Dia 20 del mes anterior al seleccionado
- **Fecha fin**: Dia 20 del mes seleccionado

Ejemplo: Si se selecciona **Febrero 2026**, el periodo sera **20/01/2026 al 20/02/2026**.

3. El periodo calculado se muestra en una barra informativa con el texto: "Periodo: 20/01/2026 al 20/02/2026"

#### Paso 3 - Generar Vista Previa

1. Hacer clic en el boton **"Vista Previa"**
2. Debajo del formulario aparecera la simulacion de la boleta con:
   - **Datos del empleado**: Codigo, nombre, cargo, correo institucional y periodo
   - **Ingreso**: Salario mensual (resaltado en verde)
   - **Deducciones**: IHSS, ISR y Otra deduccion si existe (resaltados en rojo)
   - **Total Deducciones**: Suma de todas las deducciones
   - **Salario Neto**: Monto final a recibir, destacado en una barra azul CNI prominente
3. Revisar que todos los datos y montos sean correctos antes de continuar

#### Paso 4 - Seleccionar Modo y Generar

Se presentan tres botones con las opciones de generacion:

| Modo | Que hace | Cuando usarlo |
|------|----------|---------------|
| **Solo PDF** | Genera el archivo PDF y lo guarda en disco | Cuando no se necesita enviar correo |
| **Solo Email** | Envia la boleta por correo al empleado | Cuando no se necesita guardar PDF local |
| **PDF + Email** | Genera el PDF, lo guarda y lo envia por correo | **Recomendado** para operacion normal |

1. Hacer clic en el boton del modo deseado
2. Aparecera un dialogo de confirmacion mostrando el empleado, el periodo y el modo
3. Hacer clic en **"Generar"** para confirmar

#### Resultado

- **Exito**: Mensaje "Boleta generada correctamente" con la ruta del PDF (si aplica) y confirmacion de envio de correo (si aplica)
- **Error**: Mensaje descriptivo indicando el motivo del fallo

**Ubicacion de los PDFs generados:**
```
reportes_pagos_RRHH/
  2026/
    01/
      Boleta_CNI001_20-12_20-01.pdf
    02/
      Boleta_CNI001_20-01_20-02.pdf
```

### 2.2 Generar Boletas Masivas (Generar Todos)

Esta funcion permite generar las boletas de **todos los empleados registrados** en una sola operacion.

#### Paso 1 - Iniciar Generacion Masiva

1. Estando en la seccion **"Boleta de Pago"**, hacer clic en el boton **"Generar Todos"** ubicado en la parte superior derecha
2. Aparecera un dialogo de configuracion

#### Paso 2 - Configurar

1. **Mes de Pago**: Seleccionar el mes correspondiente. El periodo del 20 al 20 se calcula automaticamente.
2. **Modo de generacion**: Elegir entre Solo PDF, Solo Email o PDF + Email

#### Paso 3 - Confirmar y Esperar

1. Hacer clic en **"Generar"**
2. El sistema muestra un indicador de progreso animado: "Generando boletas..."
3. Esperar a que el proceso termine (el tiempo depende de la cantidad de empleados y el modo seleccionado)

#### Paso 4 - Revisar el Reporte de Resultados

Al finalizar, aparece un resumen detallado:

```
Boletas Generadas

Exitosos: 45
Fallidos: 2
Total: 47

--- Detalles de errores ---
Pedro Garcia: No tiene correo institucional
Ana Martinez: Error al enviar email
```

**Causas comunes de fallo en generacion masiva:**
- Empleado sin correo institucional registrado (para modos con Email)
- Configuracion SMTP incorrecta o incompleta
- Sin conexion a internet (para modos con Email)

### 2.3 Formato del PDF Generado

Los PDFs de boleta de pago se generan con las siguientes caracteristicas:

- **Encabezado**: Fondo azul CNI (#233981) con logo institucional y linea decorativa cyan (#2AAAD6)
- **Titulo**: "BOLETA DE PAGO" con subtitulo "Consejo Nacional de Inversiones - Honduras, C.A."
- **Datos del empleado**: Codigo, nombre, cargo, correo y periodo de pago
- **Seccion de Ingresos**: Con encabezado verde CNI (#1BAE64) mostrando el salario mensual
- **Seccion de Deducciones**: Con encabezado rojo mostrando IHSS, ISR y otra deduccion (si aplica)
- **Salario Neto**: Barra prominente en azul CNI con texto blanco
- **Pie de pagina**: Fecha de generacion, numero de pagina y version del sistema

### 2.4 Formato del Correo Electronico

Los correos de boleta se envian con:

- **Diseno**: Tabla HTML limpia y corporativa, compatible con todos los clientes de correo
- **Fondo**: Blanco, con `color-scheme: light only` para evitar alteraciones en modo oscuro
- **Colores**: Solo azul CNI (#233981), blanco, gris oscuro y rojo para deducciones
- **Contenido**: Saludo personalizado, tabla de conceptos con montos y salario neto destacado
- **Adjunto**: El PDF de la boleta (si se genero en modo PDF + Email)

---

## Modulo 3: Historico de Pagos

### Vista General

Este modulo funciona como el registro y bitacora de todas las boletas generadas. Permite consultar, filtrar, revisar el detalle de cada boleta y exportar reportes de auditoria.

### 3.1 Tarjetas de Estadisticas

En la parte superior de la seccion se muestran tres tarjetas con indicadores resumidos:

| Tarjeta | Que muestra |
|---------|-------------|
| **Registros** | Cantidad total de boletas generadas en el sistema |
| **Monto Neto** | Suma de todos los salarios netos pagados (L.) |
| **Deducciones** | Suma total de todas las deducciones aplicadas (L.) |

Estos valores se actualizan automaticamente al aplicar filtros.

### 3.2 Filtrar Registros

Para buscar registros especificos:

1. **Por empleado**: Escribir el nombre o codigo en el campo de texto "Buscar empleado"
2. **Por fecha desde**: Hacer clic en el selector de calendario e indicar la fecha de inicio
3. **Por fecha hasta**: Hacer clic en el selector de calendario e indicar la fecha final
4. Hacer clic en **"Buscar"** para aplicar los filtros

**Validacion de fechas**: Si se selecciona una fecha "Hasta" anterior a la fecha "Desde", el sistema ajusta automaticamente la fecha final y muestra una advertencia.

Para quitar todos los filtros: hacer clic en **"Limpiar"**.

### 3.3 Tabla de Registros

La tabla muestra los registros de forma simplificada con las siguientes columnas:

| Columna | Contenido |
|---------|-----------|
| **Fecha** | Fecha y hora en que se genero la boleta |
| **Codigo** | Codigo del empleado (CNI###) |
| **Empleado** | Nombre completo |
| **Cargo** | Puesto del empleado |
| **Tipo** | Modo de generacion: PDF, Email o PDF+Email |
| **Acciones** | Boton "Ver" para abrir el detalle completo |

**Ordenamiento**: Los registros se muestran siempre del mas reciente al mas antiguo.

### 3.4 Ver Detalle de una Boleta

1. Localizar el registro deseado en la tabla
2. Hacer clic en el boton **"Ver"** de la columna Acciones
3. Se abre una ventana modal (superpuesta) con la informacion completa:

**Seccion de datos generales:**
- Codigo del empleado
- Nombre completo
- Cargo
- Fecha de generacion
- Tipo de generacion
- Periodo de pago

**Seccion de desglose financiero:**
- Salario Mensual (en verde)
- IHSS (en rojo)
- ISR (en rojo)
- Otra deduccion y su observacion (en rojo, si existe)
- Total Deducciones
- **Salario Neto** (destacado en azul CNI)

**Ruta del PDF**: Si se genero PDF, se muestra la ubicacion del archivo

4. Para cerrar el detalle: hacer clic en la **X** de la esquina superior derecha, o hacer clic fuera de la ventana modal

### 3.5 Paginacion

La tabla muestra un maximo de 10 registros por pagina. En la parte inferior se encuentran los controles de navegacion:

| Control | Funcion |
|---------|---------|
| **Primera** | Ir a la primera pagina |
| **Anterior** | Retroceder una pagina |
| **Indicador** | Muestra "Pagina X / Y" |
| **Siguiente** | Avanzar una pagina |
| **Ultima** | Ir a la ultima pagina |

Tambien se muestra un texto informativo: "Mostrando X-Y de Z registros".

Los botones se deshabilitan automaticamente cuando no aplican (por ejemplo, "Anterior" en la primera pagina).

### 3.6 Exportar Reporte de Auditoria

1. Hacer clic en el boton **"Exportar Auditoria"** ubicado en la parte superior derecha de la seccion
2. El sistema genera un archivo PDF profesional que incluye:
   - Encabezado con logo CNI y fondo azul institucional
   - Linea decorativa cyan
   - Titulo "REPORTE DE AUDITORIA"
   - Subtitulo "Consejo Nacional de Inversiones"
   - Tabla completa con todos los registros (encabezados en azul CNI, filas alternas en gris claro)
   - Pie con total de registros, fecha de generacion y version del sistema

3. El archivo se guarda automaticamente en:
   ```
   reportes_pagos_RRHH/_auditorias/Auditoria_AAAAMMDD_HHMMSS.pdf
   ```

4. Aparece un mensaje de confirmacion con la ruta del archivo generado

---

## Modulo 4: Configuracion del Sistema

### Vista General

La seccion de configuracion permite ajustar tres aspectos fundamentales del sistema: la tabla de calculo del ISR, los parametros del IHSS y la configuracion del servidor de correo electronico.

### 4.1 Tabla Progresiva de ISR

El Impuesto Sobre la Renta se calcula aplicando porcentajes progresivos segun tramos de salario. Esta seccion permite configurar dichos tramos.

#### Ver la Tabla Actual

La tabla muestra cada tramo con:
- **Tasa (%)**: Porcentaje de impuesto a aplicar
- **Desde Mensual (L.)**: Limite inferior del tramo
- **Hasta Mensual (L.)**: Limite superior del tramo
- **Descripcion**: Texto identificativo (ej. "Exentos", "15%", "20%")

#### Modificar un Tramo Existente

1. Hacer clic en el icono de **lapiz** del tramo a modificar
2. En el dialogo emergente, ajustar los valores:
   - Tasa (%)
   - Desde Mensual (L.)
   - Hasta Mensual (L.)
   - Descripcion
3. Hacer clic en **"Guardar"**

#### Agregar un Nuevo Tramo

1. Hacer clic en **"+ Agregar Tramo"**
2. Completar los datos del nuevo tramo
3. Hacer clic en **"Agregar"**
4. Los tramos se reordenan automaticamente por monto

#### Eliminar un Tramo

1. Hacer clic en el icono de **papelera** del tramo
2. El tramo se elimina de la tabla inmediatamente

#### Guardar la Tabla

1. Despues de realizar todos los cambios, hacer clic en **"Guardar Tabla ISR"**
2. Aparecera confirmacion: "Tabla ISR Guardada"

#### Recalcular ISR de Todos los Empleados

Despues de modificar la tabla, es recomendable recalcular el ISR de todos los empleados existentes:

1. Hacer clic en **"Recalcular Todos los Empleados"**
2. El sistema actualizara el campo ISR de cada empleado segun la nueva tabla
3. Se muestra un resumen de los empleados actualizados

#### Calculadora de Prueba

En la parte inferior de esta seccion hay una calculadora para verificar los calculos:
1. Ingresar un salario de ejemplo
2. El ISR calculado se muestra instantaneamente
3. Util para validar que los tramos esten configurados correctamente

### 4.2 Configuracion de IHSS

El IHSS (Instituto Hondureno de Seguridad Social) se calcula con tres parametros configurables.

#### Parametros

| Parametro | Descripcion | Valor tipico |
|-----------|-------------|:------------:|
| **Tasa EM (%)** | Enfermedad y Maternidad - aporte del empleado | 2.5% |
| **Tasa IVM (%)** | Invalidez, Vejez y Muerte - aporte del empleado | 2.5% |
| **Techo de Cotizacion (L.)** | Salario maximo sobre el cual se calcula | 12,000.00 |

#### Formula de Calculo

```
Salario Base = Minimo(Salario Real del Empleado, Techo de Cotizacion)
IHSS Total = Salario Base x (Tasa EM + Tasa IVM) / 100
```

**Ejemplo**: Empleado con salario de L. 30,000 y techo de L. 12,000:
- Salario Base = min(30,000, 12,000) = L. 12,000
- IHSS = 12,000 x (2.5% + 2.5%) = 12,000 x 5% = **L. 600.00**

#### Modificar la Configuracion

1. Ajustar los valores de Tasa EM, Tasa IVM y/o Techo
2. Usar la **calculadora de ejemplo** para verificar: ingresar un salario y ver el IHSS resultante
3. Hacer clic en **"Guardar Configuracion IHSS"**

#### Recalcular IHSS de Todos los Empleados

1. Hacer clic en **"Recalcular IHSS de Todos los Empleados"**
2. Se actualiza el campo IHSS de cada empleado con la nueva configuracion
3. Se muestra un resumen de los empleados actualizados

### 4.3 Configuracion de Correo Electronico (SMTP)

Para poder enviar boletas por correo, se debe configurar una cuenta de Office 365.

#### Campos de Configuracion

| Campo | Valor | Notas |
|-------|-------|-------|
| **Host SMTP** | smtp.office365.com | No modificar |
| **Puerto** | 587 | No modificar |
| **Username** | correo@cni.hn | Cuenta con licencia Office 365 |
| **Password** | (contrasena) | Contrasena de la cuenta |
| **Emisor** | Servicios Online | Nombre tecnico del emisor |
| **Remitente** | Recursos Humanos CNI | Nombre que vera el destinatario |

#### Configurar Paso a Paso

1. Completar el campo **Username** con la direccion de correo completa
2. Ingresar la **contrasena** de dicha cuenta
3. Opcionalmente, personalizar el nombre del **Remitente**
4. Hacer clic en **"Guardar Configuracion SMTP"**

#### Verificar que Funcione

1. Ir a **Boleta de Pago**
2. Seleccionar un empleado de prueba que tenga correo
3. Generar una boleta en modo **Solo Email**
4. Verificar que el correo llegue a la bandeja de entrada del empleado

#### Problemas Comunes

| Error | Causa probable | Solucion |
|-------|---------------|----------|
| "Autenticacion fallida" | Usuario o contrasena incorrectos | Verificar credenciales |
| "Autenticacion fallida" | Cuenta sin licencia Office 365 | Solicitar licencia al area de TI |
| "Autenticacion fallida" | Autenticacion de dos factores activa | Desactivar 2FA o usar contrasena de aplicacion |
| "No se pudo conectar" | Sin conexion a internet | Verificar conectividad de red |
| "No se pudo conectar" | Puerto 587 bloqueado por firewall | Contactar al area de TI |

---

## Resolucion de Problemas

### La aplicacion no inicia

**Sintoma**: Al hacer doble clic en el ejecutable, no pasa nada o se cierra inmediatamente.

**Soluciones**:
1. Ejecutar desde la linea de comandos para ver errores:
   ```cmd
   cd ruta\a\SistemaPagosCNI
   SistemaPagosCNI.exe
   ```
2. Verificar que no haya otra instancia ejecutandose (revisar Administrador de Tareas)
3. Si se usa el modo Python, verificar que Python y las dependencias esten instalados:
   ```bash
   pip install -r requirements.txt
   ```

### No se guardan los cambios

**Sintoma**: Los datos ingresados desaparecen al cerrar la aplicacion.

**Soluciones**:
1. Verificar que se haya hecho clic en "Guardar" (los cambios no se guardan automaticamente)
2. Verificar permisos de escritura en la carpeta de la aplicacion
3. Verificar que el archivo `rrhh_cni.db` no este abierto por otro programa
4. No forzar el cierre de la aplicacion (usar el boton X normal)

### Error al generar PDF

**Sintoma**: Mensaje "Error al generar PDF" al intentar crear una boleta.

**Soluciones**:
1. Verificar que la carpeta `reportes_pagos_RRHH/` exista junto al ejecutable
2. Verificar que haya espacio disponible en disco
3. Cerrar cualquier PDF del sistema que este abierto en otro programa
4. Verificar que la carpeta `img/` con `logo_cni.png` este presente

### Error al enviar correo electronico

**Sintoma**: Mensaje "No se pudo enviar el correo" al generar con modo Email.

**Soluciones**:
1. Verificar que la configuracion SMTP este completa (Configuracion > SMTP)
2. Verificar que el empleado tenga correo institucional registrado
3. Verificar la conexion a internet
4. Verificar que las credenciales SMTP sean correctas
5. Si el puerto 587 esta bloqueado, contactar al area de TI

### ISR o IHSS calculados incorrectamente

**Sintoma**: Los montos de ISR o IHSS no coinciden con los valores esperados.

**Soluciones**:
1. Ir a **Configuracion** y verificar la tabla de ISR (tramos y tasas)
2. Verificar la configuracion de IHSS (tasas EM, IVM y techo)
3. Usar las calculadoras de prueba en cada seccion para validar
4. Despues de corregir, usar **"Recalcular Todos los Empleados"** para actualizar los valores existentes

### La interfaz se ve mal o desordenada

**Sintoma**: Elementos desalineados, colores incorrectos o texto cortado.

**Soluciones**:
1. Refrescar la pagina con **Ctrl + Shift + R**
2. Verificar que la resolucion de pantalla sea al menos 1280x720
3. Si se usa en modo navegador, probar con Edge o Chrome actualizados

### Base de datos corrupta

**Sintoma**: Errores al acceder a cualquier seccion del sistema.

**Solucion**:
1. Cerrar la aplicacion completamente
2. Localizar el archivo `rrhh_cni.db`
3. Si se tiene un respaldo, reemplazar el archivo:
   ```bash
   cp rrhh_cni_backup.db rrhh_cni.db
   ```
4. Si no hay respaldo, eliminar `rrhh_cni.db` y reiniciar la aplicacion (se creara una base nueva vacia)
5. Contactar a Ing. Luis Martinez si el problema persiste

---

## Buenas Practicas

### Respaldos

- Realizar copias de seguridad del archivo `rrhh_cni.db` al menos una vez por semana
- Guardar los respaldos en una ubicacion diferente (USB, nube, servidor de archivos)
- Antes de modificar la tabla ISR o IHSS, respaldar la base de datos

### Operacion Diaria

- Siempre generar **Vista Previa** antes de emitir una boleta definitiva
- Usar el modo **PDF + Email** para tener respaldo local y notificar al empleado simultaneamente
- Verificar la configuracion SMTP al inicio de cada periodo de pago

### Configuracion

- Revisar y actualizar la tabla ISR al inicio de cada anio fiscal segun la legislacion vigente
- Actualizar las tasas y techo de IHSS cuando el Instituto emita nuevas disposiciones
- Despues de cualquier cambio en ISR o IHSS, ejecutar **"Recalcular Todos los Empleados"**

### Auditoria

- Exportar el reporte de auditoria mensualmente como respaldo en PDF
- Consultar el historico periodicamente para validar que los registros sean correctos
- Conservar los PDFs generados como comprobantes oficiales

---

## Glosario

| Termino | Significado |
|---------|-------------|
| **CNI** | Consejo Nacional de Inversiones |
| **ISR** | Impuesto Sobre la Renta |
| **IHSS** | Instituto Hondureno de Seguridad Social |
| **EM** | Enfermedad y Maternidad (regimen del IHSS) |
| **IVM** | Invalidez, Vejez y Muerte (regimen del IHSS) |
| **SMTP** | Simple Mail Transfer Protocol - protocolo para envio de correos |
| **PDF** | Portable Document Format - formato de documento portable |
| **Techo de Cotizacion** | Monto maximo de salario sobre el cual se calculan las cotizaciones al IHSS |
| **Tabla Progresiva** | Sistema de tramos donde cada rango de ingreso tiene una tasa diferente |
| **Boleta de Pago** | Documento que detalla los ingresos y deducciones de un empleado en un periodo |
| **Salario Neto** | Monto que recibe el empleado despues de aplicar todas las deducciones |

---

## Soporte y Contacto

### Desarrollador del Sistema

Para dudas tecnicas, errores o solicitudes de mejora:

- **Nombre**: Ing. Luis Martinez
- **Rol**: Software Developer
- **Email**: luismartinez.94mc@gmail.com

### Soporte Interno CNI

Para soporte operativo, acceso a cuentas y configuracion de red:

- **Area**: Oficial de TI
- **Email**: amartinez@cni.hn
- **Organizacion**: Consejo Nacional de Inversiones

### Al Reportar un Problema

Incluir la siguiente informacion para una resolucion mas rapida:

1. Version del sistema (visible en la esquina inferior izquierda de la interfaz)
2. Sistema operativo utilizado
3. Descripcion clara del problema
4. Pasos exactos para reproducirlo
5. Capturas de pantalla si es posible
6. Mensaje de error completo (si aparece alguno)

### Canales de Soporte

| Tipo de consulta | Contactar a |
|-----------------|-------------|
| Errores tecnicos o bugs | Ing. Luis Martinez (luismartinez.94mc@gmail.com) |
| Configuracion y uso diario | Oficial de TI CNI (amartinez@cni.hn) |
| Urgencias | Ambos contactos |

---

**Ultima actualizacion**: 16 de Febrero 2026  
**Version del Sistema**: 2.1.0  
**Version del Manual**: 2.1  
**Estado**: Produccion  
**Desarrollado por**: Ing. Luis Martinez - Software Developer  
**Consejo Nacional de Inversiones - Honduras**
