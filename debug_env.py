import pathlib

env_path = pathlib.Path('D:\\mis proyectos\\.env')
print(f"Archivo existe: {env_path.exists()}")
print(f"Ruta absoluta: {env_path.absolute()}")

if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"\nContenido raw (primeros 200 caracteres):")
        print(repr(content[:200]))
        
        print(f"\nLíneas:")
        for i, line in enumerate(content.split('\n')):
            if line.strip():
                print(f"  Línea {i}: {repr(line)}")
