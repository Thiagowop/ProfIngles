#!/usr/bin/env python3
"""
Script para testar todos os arquivos main*.py
Verifica sintaxe, imports e funcionalidade básica
"""

import os
import sys
import importlib.util
import traceback
from pathlib import Path

def test_python_syntax(file_path):
    """Testa se o arquivo tem sintaxe Python válida"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        compile(code, file_path, 'exec')
        return True, "✅ Sintaxe válida"
    except SyntaxError as e:
        return False, f"❌ Erro de sintaxe: {e}"
    except Exception as e:
        return False, f"❌ Erro ao ler arquivo: {e}"

def test_imports(file_path):
    """Testa se os imports do arquivo funcionam"""
    try:
        # Extrair imports do arquivo
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        imports = []
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                if not line.startswith('#'):
                    imports.append(line)
        
        # Testar cada import
        failed_imports = []
        for import_line in imports:
            try:
                exec(import_line)
            except ImportError as e:
                failed_imports.append(f"{import_line} -> {e}")
            except Exception as e:
                failed_imports.append(f"{import_line} -> {e}")
        
        if failed_imports:
            return False, f"❌ Imports falharam:\n" + "\n".join(failed_imports)
        else:
            return True, f"✅ Todos os {len(imports)} imports funcionam"
            
    except Exception as e:
        return False, f"❌ Erro ao testar imports: {e}"

def check_fastapi_structure(file_path):
    """Verifica se o arquivo tem estrutura FastAPI válida"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        has_fastapi = 'FastAPI' in content
        has_app = 'app = FastAPI' in content or 'app=FastAPI' in content
        has_uvicorn = 'uvicorn' in content
        has_routes = '@app.' in content
        
        score = sum([has_fastapi, has_app, has_uvicorn, has_routes])
        
        details = []
        details.append(f"FastAPI import: {'✅' if has_fastapi else '❌'}")
        details.append(f"App instance: {'✅' if has_app else '❌'}")
        details.append(f"Uvicorn present: {'✅' if has_uvicorn else '❌'}")
        details.append(f"Routes defined: {'✅' if has_routes else '❌'}")
        
        return score, details
        
    except Exception as e:
        return 0, [f"❌ Erro ao analisar: {e}"]

def test_main_file(file_path):
    """Testa um arquivo main específico"""
    print(f"\n{'='*60}")
    print(f"🧪 TESTANDO: {file_path.name}")
    print(f"{'='*60}")
    
    # Teste 1: Sintaxe
    syntax_ok, syntax_msg = test_python_syntax(file_path)
    print(f"📝 Sintaxe: {syntax_msg}")
    
    if not syntax_ok:
        print("❌ FALHOU - Sintaxe inválida")
        return False
    
    # Teste 2: Imports
    imports_ok, imports_msg = test_imports(file_path)
    print(f"📦 Imports: {imports_msg}")
    
    # Teste 3: Estrutura FastAPI
    fastapi_score, fastapi_details = check_fastapi_structure(file_path)
    print(f"🚀 FastAPI Score: {fastapi_score}/4")
    for detail in fastapi_details:
        print(f"   {detail}")
    
    # Teste 4: Tamanho do arquivo (seguindo WORKSPACE_RULES)
    file_size = file_path.stat().st_size
    line_count = len(file_path.read_text(encoding='utf-8').splitlines())
    print(f"📏 Tamanho: {file_size} bytes, {line_count} linhas")
    
    if line_count > 500:
        print(f"⚠️  AVISO: Arquivo tem {line_count} linhas (>500, viola WORKSPACE_RULES)")
    
    # Determinar se o arquivo parece funcional
    is_functional = syntax_ok and imports_ok and fastapi_score >= 3
    
    print(f"🎯 RESULTADO: {'✅ FUNCIONAL' if is_functional else '❌ PROBLEMÁTICO'}")
    
    return is_functional

def main():
    """Função principal"""
    print("🔍 TESTE DE TODOS OS ARQUIVOS MAIN")
    print("=" * 60)
    
    backend_dir = Path(__file__).parent
    main_files = list(backend_dir.glob("main*.py"))
    
    if not main_files:
        print("❌ Nenhum arquivo main*.py encontrado!")
        return
    
    print(f"📂 Encontrados {len(main_files)} arquivos main:")
    for file in main_files:
        print(f"   - {file.name}")
    
    # Testar cada arquivo
    functional_files = []
    problematic_files = []
    
    for main_file in main_files:
        if main_file.name == "test_all_mains.py":  # Pular este próprio arquivo
            continue
            
        try:
            is_functional = test_main_file(main_file)
            if is_functional:
                functional_files.append(main_file.name)
            else:
                problematic_files.append(main_file.name)
        except Exception as e:
            print(f"❌ ERRO CRÍTICO testando {main_file.name}: {e}")
            problematic_files.append(main_file.name)
    
    # Relatório final
    print(f"\n{'='*60}")
    print("📊 RELATÓRIO FINAL")
    print(f"{'='*60}")
    
    print(f"✅ FUNCIONAIS ({len(functional_files)}):")
    for file in functional_files:
        print(f"   - {file}")
    
    print(f"\n❌ PROBLEMÁTICOS ({len(problematic_files)}):")
    for file in problematic_files:
        print(f"   - {file}")
    
    if functional_files:
        print(f"\n🎯 RECOMENDAÇÃO: Use {functional_files[0]} para iniciar o backend")
    else:
        print(f"\n⚠️  PROBLEMA: Nenhum arquivo main funcional encontrado!")
        print("   Verifique dependências e imports em cada arquivo")

if __name__ == "__main__":
    main()
