"""
Script para crear una imagen de prueba sintética para el OCR
Crea una imagen que simula un registro de confirmación
"""

from PIL import Image, ImageDraw, ImageFont
import os

def crear_imagen_test_confirmacion():
    """Crear una imagen de prueba que simule un registro de confirmación"""
    
    # Crear imagen base
    width, height = 1200, 800
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Intentar usar una fuente del sistema
    try:
        font_title = ImageFont.truetype("arial.ttf", 24)
        font_normal = ImageFont.truetype("arial.ttf", 16)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        # Fallback a fuente por defecto
        font_title = ImageFont.load_default()
        font_normal = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Título
    draw.text((width//2 - 150, 30), "REGISTRO DE CONFIRMACIONES", 
              font=font_title, fill='black')
    
    # Línea divisoria
    draw.line([(50, 80), (width-50, 80)], fill='black', width=2)
    
    # Encabezados de columnas
    headers = [
        "NOMBRE CONFIRMANDO",
        "F. NAC",
        "PARROQUIA BAUTISMO", 
        "F. BAUT",
        "PADRES",
        "PADRINOS"
    ]
    
    x_positions = [60, 300, 380, 580, 650, 900]
    y_header = 100
    
    for i, header in enumerate(headers):
        draw.text((x_positions[i], y_header), header, font=font_small, fill='black')
    
    # Línea debajo de encabezados
    draw.line([(50, 130), (width-50, 130)], fill='black', width=1)
    
    # Datos de ejemplo (simulando registros de confirmación)
    registros = [
        [
            "JUAN CARLOS MIRANDA LOPEZ",
            "15/03/2004",
            "SAN PEDRO",
            "20/04/2004", 
            "CARLOS MIRANDA Y MARIA LOPEZ",
            "JOSE GARCIA Y CARMEN RUIZ"
        ],
        [
            "MARIA FERNANDA QUISBERT ROJAS", 
            "22/07/2003",
            "NUESTRA SEÑORA",
            "15/08/2003",
            "LUIS QUISBERT Y ANA ROJAS",
            "PEDRO MORALES Y LUCIA HERRERA"
        ],
        [
            "CARLOS EDUARDO MENDOZA SILVA",
            "08/11/2004",
            "SAN ANTONIO",
            "12/12/2004",
            "EDUARDO MENDOZA Y ROSA SILVA", 
            "MIGUEL TORRES Y SOFIA VARGAS"
        ],
        [
            "JHOSELIN ANDREA JIMENEZ CRUZ",
            "30/05/2003",
            "NUEVA PAZ",
            "25/06/2003",
            "ROBERTO JIMENEZ Y ANDREA CRUZ",
            "DANIEL ROMERO Y PATRICIA LEON"
        ]
    ]
    
    # Dibujar líneas de separación vertical
    for x in x_positions[1:]:
        draw.line([(x-5, 130), (x-5, 130 + len(registros)*40 + 20)], 
                  fill='gray', width=1)
    
    # Dibujar registros
    y_start = 150
    for i, registro in enumerate(registros):
        y_pos = y_start + i * 40
        
        # Línea horizontal de separación
        if i > 0:
            draw.line([(50, y_pos - 5), (width-50, y_pos - 5)], 
                      fill='lightgray', width=1)
        
        # Datos del registro
        for j, dato in enumerate(registro):
            x_pos = x_positions[j]
            draw.text((x_pos, y_pos), dato, font=font_small, fill='black')
    
    # Línea final
    final_y = y_start + len(registros) * 40 + 10
    draw.line([(50, final_y), (width-50, final_y)], fill='black', width=2)
    
    # Guardar imagen
    img_path = "test_registro_confirmacion.jpg"
    img.save(img_path, "JPEG", quality=85)
    
    print(f"✅ Imagen de prueba creada: {img_path}")
    print(f"📏 Dimensiones: {width}x{height}")
    print(f"📋 Registros simulados: {len(registros)}")
    
    return img_path

if __name__ == "__main__":
    crear_imagen_test_confirmacion()