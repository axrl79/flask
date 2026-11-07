import os
import pymupdf

def create_sample_industrial_manual(output_path: str = "sample_manual_ga37.pdf") -> str:
    """Crea un documento PDF técnico real con especificaciones, tablas y códigos de error."""
    doc = pymupdf.open()

    # Página 1: Introducción y Procedimiento de Arranque
    page1 = doc.new_page()
    text1 = """MANUAL TÉCNICO DE OPERACIÓN Y MANTENIMIENTO
COMPRESOR DE TORNILLO ROTATIVO INDUSTRIAL MODELO GA-37

1. PROCEDIMIENTO DE ARRANQUE SEGURO
Antes de poner en marcha el compresor GA-37, asegúrese de cumplir con los siguientes pasos obligatorios:
Paso 1: Verifique el nivel de aceite en la mirilla del depósito separador. El nivel debe estar entre las marcas MIN y MAX.
Paso 2: Compruebe que la válvula de salida de aire comprimido esté completamente abierta.
Paso 3: Conecte el interruptor principal de alimentación eléctrica (400V trifásico, 50 Hz).
Paso 4: Pulse el botón de arranque (I) en el panel de control Elektronikon.
Paso 5: El motor arrancará en configuración estrella-triángulo y pasará automáticamente al estado de carga tras 10 segundos.
ADVERTENCIA: Nunca intente retirar el tapón de llenado de aceite mientras el compresor esté presurizado."""
    page1.insert_text((50, 60), text1, fontsize=11)

    # Página 2: Especificaciones Técnicas y Torques
    page2 = doc.new_page()
    text2 = """2. ESPECIFICACIONES TÉCNICAS Y PAR DE APRIETE (TORQUE)

Valores nominales de operación del compresor GA-37:
- Presión máxima de trabajo efectiva: 10.5 bar (152 psi).
- Caudal de aire libre suministrado (FAD): 5.8 m3/min a 10 bar.
- Potencia nominal del motor principal: 37 kW (50 HP).
- Capacidad del cárter de aceite: 13.5 litros.
- Tipo de lubricante recomendado: Aceite sintético Roto-Inject Fluid HD.
- Nivel de presión sonora: 68 dB(A) según norma ISO 2151.

ESPECIFICACIÓN DE TORQUES DE MONTAJE:
- Pernos de brida del elemento compresor (M12): 85 Nm.
- Tornillos de tapa de válvula de admisión (M10): 45 Nm.
- Tapón de purga de aceite del depósito (G 1/2 pulgada): 35 Nm.
- Sensores de temperatura y presión (rosca NPT 1/4): 20 Nm."""
    page2.insert_text((50, 60), text2, fontsize=11)

    # Página 3: Diagnóstico y Códigos de Error
    page3 = doc.new_page()
    text3 = """3. GUÍA DE RESOLUCIÓN DE PROBLEMAS Y CÓDIGOS DE FALLA

El controlador Elektronikon registra alarmas y paradas de emergencia mediante códigos alfanuméricos:

Código E-101: Alta temperatura en elemento compresor.
Causa: Enfriador de aceite obstruido por suciedad o bajo nivel de refrigerante.
Solución: Limpiar el radiador con aire a presión y reponer Roto-Inject Fluid hasta el nivel MAX.

Código E-205: Baja presión de lubricación.
Causa: Filtro de aceite saturado o bomba de aceite defectuosa.
Solución: Reemplazar el cartucho del filtro de aceite (referencia 1622-0871-00) inmediatamente.

Código E-314: Sobrecarga del motor eléctrico principal.
Causa: Caída de tensión en la red eléctrica o rodamientos desgastados.
Solución: Medir voltaje entre fases (debe ser 400V +/- 10%) y comprobar giro manual del tornillo."""
    page3.insert_text((50, 60), text3, fontsize=11)

    # Página 4: Mantenimiento Periódico
    page4 = doc.new_page()
    text4 = """4. PROGRAMA DE MANTENIMIENTO PREVENTIVO
Intervalos de servicio recomendados para operación industrial continua:
- Cada 500 horas de servicio: Limpieza del filtro de aire y comprobación de fugas neumáticas.
- Cada 2000 horas de servicio: Reemplazo del filtro de aire y sustitución del filtro de aceite.
- Cada 4000 horas o 1 año: Cambio completo de aceite sintético y reemplazo del cartucho separador de aceite.
- Cada 8000 horas o 2 años: Inspección completa del elemento compresor y sustitución de juntas de válvulas."""
    page4.insert_text((50, 60), text4, fontsize=11)

    doc.save(output_path)
    doc.close()
    return output_path

if __name__ == "__main__":
    path = create_sample_industrial_manual()
    print("Manual PDF generado exitosamente en:", path)
