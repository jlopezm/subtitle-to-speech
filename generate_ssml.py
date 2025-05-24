import pysrt
import json
import os
import codecs
import argparse


MAX_BYTES = 5000

def aplicar_alias_ssml(texto, alias_dict):
    for palabra, config in alias_dict.items():
        alias = config.get("alias", palabra)
        reemplazo = f'<sub alias="{alias}">{palabra}</sub>'
        texto = texto.replace(palabra, reemplazo)
    return texto

def srt_a_ssml(srt_path, alias_path, output_ssml_path):
    # Leer subtítulos

    with codecs.open(srt_path, "r", "utf-8-sig") as f:
        srt_content = f.read()

    subs = pysrt.from_string(srt_content, error_handling='ignore')

    # Leer configuración y alias
    with open(alias_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        config = data.get("config", {})
        alias_dict = data.get("alias", {})

    rate = config.get("rate", "100%")
    header = f"<speak>\n<prosody rate=\"{rate}\">"
    footer = "</prosody>\n</speak>"

    output_contents = []  # Lista de documentos (cada uno es lista de lines)
    current_lines = [header]

    def current_size(lines):
        contenido = "\n".join(lines + [footer])
        return len(contenido.encode("utf-8"))

    for i, sub in enumerate(subs):
        texto = sub.text.replace('\n', ' ')
        texto = aplicar_alias_ssml(texto, alias_dict)
        # Preparamos la lista de líneas a agregar: el texto y, si corresponde, la pausa
        to_add = [texto]
        if i < len(subs) - 1:
            gap_ms = subs[i + 1].start.ordinal - sub.end.ordinal
            if gap_ms > 100:
                pausa = min(gap_ms / 1000.0, 3.0)  # máximo 3s
                to_add.append(f'<break time="{pausa:.2f}s"/>')

        # Verificar si agregando estas líneas se excede el límite
        for line in to_add:
            if current_size(current_lines + [line]) > MAX_BYTES:
                # Si current_lines solo tiene el header y no se puede agregar, forzamos agregar la línea
                if len(current_lines) == 1:
                    current_lines.append(line)
                    continue
                # Finalizar documento actual y comenzar uno nuevo
                output_contents.append("\n".join(current_lines + [footer]))
                current_lines = [header, line]
            else:
                current_lines.append(line)

    # Agregar documento final si tiene contenido adicional
    if len(current_lines) > 1:
        output_contents.append("\n".join(current_lines + [footer]))

    # Borrar antiguos archivos .ssml (principal y partes) en la carpeta de salida
    output_dir = os.path.dirname(os.path.abspath(output_ssml_path))
    base_name, ext = os.path.splitext(os.path.basename(output_ssml_path))
    for file in os.listdir(output_dir):
        if file == f"{base_name}{ext}" or (file.startswith(f"{base_name}_part") and file.endswith(ext)):
            file_path = os.path.join(output_dir, file)
            os.remove(file_path)
            print(f"❌ Deleted old file: {file_path}")

    # Write SSML files
    if len(output_contents) == 1:
        with open(output_ssml_path, "w", encoding="utf-8") as f:
            f.write(output_contents[0])
        print(f"✅ SSML generated at: {output_ssml_path}")
    else:
        for idx, content in enumerate(output_contents, start=1):
            part_path = f"{base_name}_part{idx}{ext}"
            part_path = os.path.join(output_dir, part_path)
            with open(part_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ SSML generated at: {part_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generates SSML files from an SRT file and an alias file.")
    parser.add_argument("--srt_path", required=True, help="Path to the input SRT file.")
    parser.add_argument("--alias_path", required=True, help="Path to the JSON alias and configuration file.")
    parser.add_argument("--output_ssml_path", required=True, help="Path to the output SSML file.")

    args = parser.parse_args()

    srt_a_ssml(
        srt_path=args.srt_path,
        alias_path=args.alias_path,
        output_ssml_path=args.output_ssml_path
    )
