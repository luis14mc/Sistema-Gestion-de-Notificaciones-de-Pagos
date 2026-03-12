## Ajustes.
    - Cuando hay un nuevo empleado y es su primer el salario base va a depender de su fecha de ingreso por ejemplo si su salario es de L. 26,400 y ese mes ingreso el 10 entonces ese primer mes se recalcula internamente su sueldo como:
        sueldo_dias = (sueldo_base)/30
        Sueldo_mes_primero = sueldo_dias* cantidad_dias ( viene por fecha ingreso)
    
    - El ISR por ejemplo se calcula tambien entonces con esta limitante si en el primer mes de ingreso no ingresa el primer dia su sueldo del primer mes dbe reflejarse en el calculo asi. por ejemplo en el caso que ingrese en el mes de Febrero entonces su calculo seria:
        
        - **meses_trabajados** = 12 - mes_ingreso (ej: ingreso en febrero = 11 meses)
        - **Ingreso_Anual** = Salario_Mensual × meses_trabajados (tomando en cuenta que el salario del primer mes esta sujeto a fecha de ingreso como lo explico arriba)
        - lo mismo para el resto de calculos. con la condicion especial el IVM en el ISR debe ser calculado en base a los meses_trabajados es decir las deduciones son base meses trabajados con la salvedad del dato fijo gastos_medicos que es fijo anual / año natural.

    - IHSS. es el mismo caso porque debe ser en base a los meses trabajados siempre tomando en cuenta el apgo especial del primer mes cuando aplique.
    