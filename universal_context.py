# /// script
# dependencies = [
#    "streamlit",
#    "streamlit-tree-select",
#    "pathspec"
# ]
# ///

import streamlit as st
import os
import pathspec
from pathlib import Path
from typing import List, Dict, Set, Tuple
import math
import json


CONFIG_FILE = Path(".context_config.json")

try:
    from streamlit_tree_select import tree_select
except ImportError:
    st.error("Falta la librería: `streamlit-tree-select`. Por favor, ejecuta `uv sync` o `pip install streamlit-tree-select`.")
    st.stop()  # <--- Esto evita que el script siga y de el NameError

# ==========================================
# 0. UI COMPACTA Y CORRECCIÓN DE COLORES
# ==========================================
st.set_page_config(page_title="Universal Context", page_icon="🏗️", layout="wide")

st.markdown("""
<style>
    /* 1. FUENTE */
    html, body, [class*="css"], div {
        font-family: 'Consolas', 'Menlo', monospace !important;
        font-size: 12px;
    }
    
    label { font-size: 1rem !important; }
    button, input  { font-size: 0.92rem !important; }
     .stCheckbox, p  { font-size: 0.8rem !important; }
    
    /* 2. TÍTULOS */
    h1 { font-size: 1.2rem !important; margin: 0 !important; padding: 0 !important; color: #58a6ff; }
    h2, h3 { font-size: 1rem !important; font-weight: bold; }
    
    /* 3. INPUTS */
    .stTextInput input, .stTextArea textarea {
        background-color: #6e6e6e !important; 
        color: #e3e9f7!important;
        border: 1px solid #30363d !important;
        border-radius: 2px !important;
    }
    
    /* 4. ARBOL DE ARCHIVOS */
    .stTreeSelect {
        background-color: #0d1117 !important;
        border: 1px solid #30363d !important;
        padding: 2px 5px !important;
    }
    
    /* 5. AJUSTES DE ESPACIO */
    .block-container { margin-top: 2rem; max-width: 99% !important; }
    div[data-testid="stVerticalBlock"] { gap: 0.75rem; }
    .stButton button { padding: 0px 10px; height: 30px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. LÓGICA (MOTORES)
# ==========================================

class ContextEngine:
    def __init__(self, root: str, ignores: str):
        self.root = Path(root)
        # Construir pathspec
        pats = [".git/", "node_modules/", "__pycache__/", "dist/", "build/", ".env", ".venv"]
        pats.extend([x.strip() for x in ignores.split(',') if x.strip()])
        
        git = self.root / ".gitignore"
        if git.exists():
            with open(git, "r") as f: pats.extend(f.readlines())
            
        self.spec = pathspec.PathSpec.from_lines("gitwildmatch", pats)

    def is_ignored(self, p: Path) -> bool:
        try:
            rel = str(p.relative_to(self.root)).replace("\\", "/")
            
            # WHITELIST: Forzar visibilidad de carpetas de compilación
            whitelist = ["target", "generated", "build", "generated-sources"]
            # Si es la carpeta exacta o está dentro de una de ellas, NO ignorar
            if rel in whitelist or any(rel.startswith(f"{w}/") for w in whitelist):
                return False
                
            if p.is_dir(): rel += "/"
            return self.spec.match_file(rel)
        except: return True

    def scan(self, search: str, exts: Set[str]) -> List[Dict]:
        return self._rec_scan(self.root, search.lower(), exts)

    def _rec_scan(self, path: Path, search: str, exts: Set[str]) -> List[Dict]:
        nodes = []
        try:
            items = sorted(list(path.iterdir()), key=lambda x: (not x.is_dir(), x.name.lower()))
            
            for item in items:
                if self.is_ignored(item): continue
                
                rel = str(item.relative_to(self.root))
                
                if item.is_dir():
                    children = self._rec_scan(item, search, exts)
                    if children or (search and search in item.name.lower()):
                        nodes.append({"label": item.name, "value": rel, "children": children})
                else:
                    suffix = item.suffix.lower()
                    if "NO_EXT" not in exts and not suffix: continue
                    if suffix and suffix not in exts: continue
                    
                    if search and search not in item.name.lower(): continue
                    
                    ico = "📄"
                    if suffix == ".py": ico = "🐍"
                    elif suffix in [".js", ".ts", ".tsx"]: ico = "🟨"
                    elif suffix == ".md": ico = "📝"
                    elif suffix in [".java", ".kt", ".class"]: ico = "☕"
                    elif suffix == ".xml": ico = "📜"
                    elif suffix in [".json", ".yml", ".yaml"]: ico = "⚙️"
                    
                    nodes.append({"label": f"{ico} {item.name}", "value": rel})
        except: pass
        return nodes

def load_last_path():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f).get("last_path", os.getcwd())
        except: pass
    return os.getcwd()

def save_last_path(path):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"last_path": str(path)}, f)
    except: pass
    
def compact_tree(nodes: List[Dict]) -> List[Dict]:
    for node in nodes:
        if "children" in node and len(node["children"]) == 1:
            child = node["children"][0]
            if "children" in child:
                node["label"] = f"{node['label']} / {child['label']}"
                node["value"] = child["value"]
                node["children"] = child["children"]
                compact_tree([node])
        if "children" in node:
            compact_tree(node["children"])
    return nodes

def clean_code(text: str, mode: str) -> str:
    if mode == "Full": return text
    lines = []
    for line in text.splitlines():
        s = line.strip()
        if not s: continue
        if s.startswith(('#', '//')) and not s.startswith('#!'): continue
        if mode == "Smart":
            if s.startswith(('import ', 'from ', 'package ', 'console.', 'print(')): continue
        lines.append(line)
    return "\n".join(lines)

def get_all_leaves(nodes):
    leaves = []
    for n in nodes:
        if "children" in n: leaves.extend(get_all_leaves(n["children"]))
        else: leaves.append(n["value"])
    return leaves

def get_smart_category(file_path: str) -> str:
    # Normalizamos a minúsculas y reemplazamos backslashes por slashes
    p = file_path.lower().replace("\\", "/")
    name = os.path.basename(p)
    
    # 1. CÓDIGO AUTOGENERADO (Prioridad Alta)
    # Detecta carpetas target, build o paquetes 'generated' de OpenAPI
    if any(x in p for x in ["target/", "build/", "generated-sources", "generated", "openapi"]): 
        return "🤖 GENERATED / OPENAPI"

    # 2. DOCUMENTACIÓN
    if any(x in p for x in ["read", "doc", "license", "changelog", ".md"]): 
        return "📚 DOCS"

    # 3. CONFIGURACIÓN
    if any(x in p for x in ["config", ".env", "docker", ".json", ".xml", ".yml", ".yaml", "pom.xml", "build.gradle"]): 
        return "🛠️ CONFIG & INFRA"

    # 4. TESTS
    if any(x in p for x in ["test", "spec", "__tests__", "junit", "mock"]): 
        return "🧪 TESTS"

    # 5. BACKEND - CAPA DE API/CONTROLADORES
    if any(x in p for x in ["controller", "api", "resource", "route", "handler", "endpoint"]): 
        return "🔌 API LAYER"

    # 6. BACKEND - MODELOS DE DATOS (DTOs, Entities)
    if any(x in p for x in ["model", "dto", "entity", "schema", "interface", "type", "domain", "enum"]): 
        return "📐 MODELS & DATA"

    # 7. BACKEND - LÓGICA DE NEGOCIO
    if any(x in p for x in ["service", "logic", "usecase", "impl", "business"]): 
        return "⚙️ BUSINESS LOGIC"

    # 8. UTILIDADES
    if any(x in p for x in ["util", "helper", "common", "shared", "exception", "mapper"]): 
        return "🧱 SHARED / UTILS"
    
    # 9. FRONTEND (Si aplica)
    if any(x in p for x in ["ui", "component", "view", "page", "css", "html", "react", "angular", "vue"]): 
        return "🎨 FRONTEND"

    return "📦 CORE / OTROS"

# ==========================================
# 2. INTERFAZ (LAYOUT)
# ==========================================
def main():
    # --- 1. CONFIGURACIÓN INICIAL UNIFICADA ---
    default_path = load_last_path()

    c1, c2, c3 = st.columns([5, 2, 1])
    
    # Input Principal
    repo = c1.text_input("Repo Path", value=default_path, label_visibility="collapsed")
    search = c2.text_input("Search", placeholder="Filtrar...", label_visibility="collapsed")
    reload = c3.button("🔄", use_container_width=True)
    
    # Guardar ruta automáticamente si cambia y es válida
    if os.path.exists(repo) and repo != default_path:
        save_last_path(repo)

    if not os.path.exists(repo):
        st.error("Ruta inválida")
        return

    # --- 2. SIDEBAR ---
    with st.sidebar:
        st.markdown("## ⚙️ Config")
        
        # Extensiones
        exts_str = st.text_input("Extensiones (separar por comas)", value=".java, .md, .txt, .py, .js, .ts, .kt, .json, .xml, .yaml")
        allow_no_ext = st.checkbox("Incluir sin extensión", value=True)
        
        valid_exts = set()
        for e in exts_str.split(','):
            e = e.strip().lower()
            if e: valid_exts.add(e if e.startswith('.') else f".{e}")
        if allow_no_ext: valid_exts.add("NO_EXT")

        st.divider()
        ignores = st.text_area("🚫 Ignorar (Patrones)", value="test/, configuration/, config/, logs/, *.lock", height=60)
        st.divider()
        use_docs = st.checkbox("📑 Incluir Documentación")
        docs_path = st.text_input("🗂️ Ruta Docs", value=os.path.join(repo, "docs"), disabled=not use_docs)
        st.divider()
        mode = st.radio("🛁 Limpieza", ["Full", "Light", "Smart"], index=2)

    # --- 3. PROCESAMIENTO DEL ÁRBOL ---
    engine = ContextEngine(repo, ignores)
    raw_nodes = engine.scan(search, valid_exts)
    tree_data = compact_tree(raw_nodes)

    if not tree_data:
        st.warning("No se encontraron archivos con los filtros actuales.")
        selected = {"checked": []}
    else:
        col_all, col_none, _ = st.columns([1, 1, 4])
        if col_all.button("✅ Todo"):
            st.session_state["chk"] = get_all_leaves(tree_data)
            st.rerun()
        if col_none.button("🗑️ Nada"):
            st.session_state["chk"] = []
            st.rerun()
                
        selected = tree_select(tree_data, 
                               checked=st.session_state.get("chk", []), 
                               expanded=st.session_state.get("exp", []),
                               only_leaf_checkboxes=True,
                               key=f"tree_{search}_{len(valid_exts)}")
        
        st.session_state["chk"] = selected["checked"]

    # --- 4. GENERACIÓN DE CONTEXTO ---
    if selected["checked"]:
        st.divider()
        buffer = [f"# CONTEXT: {Path(repo).name}\n"]
        
        # Docs
        if use_docs and os.path.exists(docs_path):
            buffer.append("\n## 📚 DOCUMENTACIÓN\n")
            p_doc = Path(docs_path)
            if p_doc.is_file(): files_d = [p_doc]
            else: files_d = list(p_doc.glob("**/*.md")) + list(p_doc.glob("**/*.txt"))
            
            for d in files_d:
                try: buffer.append(f"### {d.name}\n{d.read_text(encoding='utf-8', errors='ignore')}\n---")
                except: pass

        # Agrupación y Código
        grouped_files = {}
        for rel in selected["checked"]:
            cat = get_smart_category(rel)
            if cat not in grouped_files: grouped_files[cat] = []
            grouped_files[cat].append(rel)

        sorted_cats = sorted(grouped_files.keys())

        for cat in sorted_cats:
            buffer.append(f"\n## === {cat} ===\n")
            for f in grouped_files[cat]:
                path = Path(repo) / f
                if path.is_file():
                    try:
                        raw = path.read_text(encoding='utf-8', errors='ignore')
                        clean = clean_code(raw, mode)
                        buffer.append(f"### File: {f}\n```\n{clean}\n```\n")
                    except: pass
        
        # --- 5. ESTADÍSTICAS Y DESCARGA ---
        final_text = "\n".join(buffer)
        
        char_count = len(final_text)
        est_tokens = math.ceil(char_count / 4)
        
        c_info, c_token, c_down = st.columns([2, 2, 2])
        c_info.success(f"📂 Archivos: {len(selected['checked'])}")
        
        if est_tokens < 8000: token_color = "green"
        elif est_tokens < 100000: token_color = "orange"
        else: token_color = "red"
        
        c_token.markdown(f"🧮 Tokens: **:{token_color}[~{est_tokens}]**")
        c_down.download_button("💾 DESCARGAR", final_text, "context.md", use_container_width=True, type="primary")

if __name__ == "__main__":
    main()