import requests, time, os, re, webbrowser, csv, json
from pathlib import Path
from html.parser import HTMLParser
import html as html_lib

UA = {"User-Agent": "TuNombre (tu.email@ejemplo.com)"}  # ← ¡pon tu email real!
BASE = "https://data.sec.gov"  # para endpoints de API tipo /submissions
SEC_FILES = "https://www.sec.gov"  # para recursos bajo /files y /Archives

def get_cik_from_ticker(ticker: str) -> str:
    """
    Devuelve el CIK de 10 dígitos como string a partir de un ticker.
    Intenta primero company_tickers.json (SEC /files) y cae a include/ticker.txt.
    """
    t = ticker.upper()
    # 1) Intento con JSON estructurado
    json_url = f"{SEC_FILES}/files/company_tickers.json"
    try:
        r = requests.get(json_url, headers=UA)
        r.raise_for_status()
        data = r.json()
        # Puede venir como dict de índices o como lista
        rows = data.values() if isinstance(data, dict) else data
        for row in rows:
            if row.get("ticker", "").upper() == t:
                return f"{int(row['cik_str']):010d}"
    except requests.HTTPError:
        pass
    except Exception:
        pass

    # 2) Fallback: mapa de texto ticker -> cik bajo /include/ticker.txt
    txt_url = f"{SEC_FILES}/include/ticker.txt"
    r2 = requests.get(txt_url, headers=UA)
    r2.raise_for_status()
    for line in r2.text.splitlines():
        if "|" in line:
            tick, cik = line.split("|", 1)
            if tick.upper() == t:
                return f"{int(cik):010d}"

    raise ValueError(f"Ticker no encontrado: {ticker}")

def get_company_submissions(cik_10: str) -> dict:
    """
    Descarga el JSON de submissions de una empresa.
    """
    url = f"{BASE}/submissions/CIK{cik_10}.json"
    r = requests.get(url, headers=UA)
    r.raise_for_status()
    return r.json()

def list_recent_filings(submissions: dict, form_types=("10-K","10-Q","8-K"), limit=20):
    """
    Devuelve una lista de dicts con las presentaciones recientes filtradas por tipo.
    """
    recent = submissions["filings"]["recent"]
    out = []
    for i, form in enumerate(recent["form"]):
        if form in form_types:
            out.append({
                "form": form,
                "accession": recent["accessionNumber"][i],  # con guiones
                "filing_date": recent["filingDate"][i],
                "primary_doc": recent["primaryDocument"][i],
            })
        if len(out) >= limit:
            break
    return out

def accession_to_path_bits(cik_10: str, accession_with_dashes: str):
    """
    Convierte accession '0000320193-24-000123' → ('320193','000032019324000123')
    y CIK sin ceros a la izquierda para rutas.
    """
    cik_no_zeros = str(int(cik_10))
    acc_nodash = accession_with_dashes.replace("-", "")
    return cik_no_zeros, acc_nodash

def build_filing_urls(cik_10: str, accession_with_dashes: str, primary_doc: str):
    """
    Construye URLs útiles para un filing concreto.
    - index.json (lista todos los archivos del expediente)
    - documento principal (html, htm, txt, etc.)
    """
    cik_no_zeros, acc_nodash = accession_to_path_bits(cik_10, accession_with_dashes)
    base = f"https://www.sec.gov/Archives/edgar/data/{cik_no_zeros}/{acc_nodash}"
    return {
        "index_json": f"{base}/index.json",
        "primary_doc": f"{base}/{primary_doc}",
        "folder": base
    }

def download_file(url: str, dest_path: Path, delay=0.2):
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, headers=UA, stream=True)
    r.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1<<14):
            if chunk:
                f.write(chunk)
    time.sleep(delay)  # sé amable con el rate limit

def download_entire_filing(cik_10: str, accession_with_dashes: str, out_dir="filings", include_exhibits=True):
    """
    Descarga todo el expediente (primary + exhibits) apoyándose en index.json.
    """
    urls = build_filing_urls(cik_10, accession_with_dashes, primary_doc="")
    idx = requests.get(urls["index_json"], headers=UA)
    idx.raise_for_status()
    index_json = idx.json()
    files = index_json.get("directory", {}).get("item", [])
    base_http = urls["folder"]

    base_dir = Path(out_dir) / accession_with_dashes
    downloaded = []
    for f in files:
        name = f["name"]
        # Si no quieres exhibits, descarga solo los *.htm(l)/*.txt principales:
        if not include_exhibits and not re.search(r"\.(htm|html|txt)$", name, re.I):
            continue
        url = f"{base_http}/{name}"
        dest = base_dir / name
        download_file(url, dest)
        downloaded.append(str(dest))
    return downloaded


def _print_recent_filings(filings):
    if not filings:
        print("No se encontraron filings recientes para los tipos solicitados.")
        return
    print("\nFilings recientes:")
    for idx, f in enumerate(filings, start=1):
        print(f"  [{idx}] {f['form']}  | fecha: {f['filing_date']} | accession: {f['accession']} | doc: {f['primary_doc']}")


def _choose_preferred_view_file(base_dir: Path, accession: str, primary_doc: str) -> Path:
    """
    Heurística para elegir el mejor archivo HTML para visualizar el filing localmente.
    Prioriza:
      1) primary_doc si es "grande" (no un frameset minúsculo)
      2) {accession}-index-headers.html
      3) {accession}-index.html
      4) R1.htm
      5) El más grande entre R*.htm
      6) El .htm/.html más grande que no parezca exhibit
    """
    def file_size(p: Path) -> int:
        try:
            return p.stat().st_size
        except Exception:
            return 0

    # 1) primary_doc si es significativo
    p_primary = base_dir / primary_doc
    if p_primary.exists() and file_size(p_primary) > 2048:
        return p_primary

    # 2) index-headers
    p_headers = base_dir / f"{accession}-index-headers.html"
    if p_headers.exists():
        return p_headers

    # 3) index simple
    p_index = base_dir / f"{accession}-index.html"
    if p_index.exists():
        return p_index

    # 4) R1.htm
    p_r1 = base_dir / "R1.htm"
    if p_r1.exists():
        return p_r1

    # 5) mayor entre R*.htm
    r_candidates = [p for p in base_dir.glob("R*.htm*")]
    if r_candidates:
        r_candidates.sort(key=file_size, reverse=True)
        return r_candidates[0]

    # 6) mayor .htm/.html no exhibit
    def is_exhibit_name(name: str) -> bool:
        lower = name.lower()
        return lower.startswith("ex") or "exhibit" in lower or "xex" in lower

    html_candidates = [p for p in base_dir.glob("*.htm*") if not is_exhibit_name(p.name)]
    if html_candidates:
        html_candidates.sort(key=file_size, reverse=True)
        return html_candidates[0]

    # fallback final: primary o nada
    return p_primary if p_primary.exists() else base_dir


class _SimpleTableParser(HTMLParser):
    """
    Parser HTML muy simple para extraer tablas en forma de listas de filas.
    Ignora colspan/rowspan y tablas anidadas se manejan por profundidad.
    """
    def __init__(self):
        super().__init__()
        self.tables = []
        self._in_table_depth = 0
        self._current_table = None
        self._current_row = None
        self._in_cell = False
        self._cell_buffer = []

    def handle_starttag(self, tag, attrs):
        t = tag.lower()
        if t == "table":
            if self._in_table_depth == 0:
                self._current_table = []
            self._in_table_depth += 1
        elif self._in_table_depth > 0 and t == "tr":
            self._current_row = []
        elif self._in_table_depth > 0 and t in ("td", "th"):
            self._in_cell = True
            self._cell_buffer = []

    def handle_endtag(self, tag):
        t = tag.lower()
        if t == "table":
            if self._in_table_depth > 0:
                self._in_table_depth -= 1
                if self._in_table_depth == 0 and self._current_table is not None:
                    self.tables.append(self._current_table)
                    self._current_table = None
        elif self._in_table_depth > 0 and t in ("td", "th"):
            if self._in_cell:
                text = self._clean_text("".join(self._cell_buffer))
                if self._current_row is not None:
                    self._current_row.append(text)
            self._in_cell = False
            self._cell_buffer = []
        elif self._in_table_depth > 0 and t == "tr":
            if self._current_row is not None and self._current_table is not None:
                self._current_table.append(self._current_row)
            self._current_row = None

    def handle_data(self, data):
        if self._in_table_depth > 0 and self._in_cell:
            self._cell_buffer.append(data)

    @staticmethod
    def _clean_text(s: str) -> str:
        s = re.sub(r"\s+", " ", s or "")
        return s.strip()


def extract_tables_from_html(html_path: Path, out_dir: Path, min_columns: int = 2, max_tables: int = 200):
    """
    Extrae tablas sencillas desde un HTML y guarda:
      - CSV por tabla: {stem}_table_{i}.csv
      - Un JSON con todas las tablas: {stem}_tables.json
    Devuelve lista de rutas CSV generadas y la ruta del JSON.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    html_text = html_path.read_text(errors="ignore")
    parser = _SimpleTableParser()
    parser.feed(html_text)
    tables = []
    for t in parser.tables:
        # filtra tablas vacías o con pocas columnas
        widest = max((len(r) for r in t if isinstance(r, list)), default=0)
        if widest >= min_columns:
            tables.append(t)
        if len(tables) >= max_tables:
            break

    csv_paths = []
    stem = html_path.stem
    for i, table in enumerate(tables, start=1):
        csv_path = out_dir / f"{stem}_table_{i}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for row in table:
                writer.writerow(row)
        csv_paths.append(str(csv_path))

    json_path = out_dir / f"{stem}_tables.json"
    try:
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump({"source": str(html_path), "tables": tables}, jf, ensure_ascii=False)
    except Exception:
        json_path = None

    return csv_paths, (str(json_path) if json_path else None), len(tables)


def get_company_facts(cik_10: str) -> dict:
    """
    Descarga Company Facts (XBRL) para la empresa: /api/xbrl/companyfacts/CIK{cik}.json
    """
    url = f"{BASE}/api/xbrl/companyfacts/CIK{cik_10}.json"
    r = requests.get(url, headers=UA)
    r.raise_for_status()
    return r.json()


def _series_from_fact(fact_obj: dict, preferred_units=("USD", "shares")) -> dict:
    """
    Convierte un objeto de concepto en un dict {end_date -> (val, filed)}
    priorizando unidades preferred_units y tomando el último por fecha de 'filed'.
    """
    units = fact_obj.get("units", {})
    for unit in preferred_units:
        if unit in units:
            series = {}
            for obs in units[unit]:
                end = obs.get("end") or obs.get("instant") or obs.get("filed")
                if not end:
                    continue
                val = obs.get("val")
                filed = obs.get("filed") or ""
                # Conserva el más reciente filed para la misma fecha
                prev = series.get(end)
                if prev is None or (filed and filed > prev[1]):
                    series[end] = (val, filed)
            return series
    return {}


def export_statements_from_company_facts(facts: dict, out_dir: Path) -> dict:
    """
    Construye CSVs para Income Statement (IS), Balance Sheet (BS) y Cash Flows (CF)
    usando un subconjunto de conceptos US-GAAP comunes. Incluye todas las fechas disponibles.
    Devuelve rutas de archivos generados por estado.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    usgaap = (facts.get("facts", {}).get("us-gaap", {}) or facts.get("facts", {}))

    statements = {
        "IS": [
            "Revenues",
            "SalesRevenueNet",
            "CostOfRevenue",
            "GrossProfit",
            "OperatingExpenses",
            "ResearchAndDevelopmentExpense",
            "SellingGeneralAndAdministrativeExpense",
            "OperatingIncomeLoss",
            "InterestExpense",
            "IncomeTaxExpenseBenefit",
            "NetIncomeLoss",
        ],
        "BS": [
            "Assets",
            "AssetsCurrent",
            "Liabilities",
            "LiabilitiesCurrent",
            "StockholdersEquity",
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
            "RetainedEarningsAccumulatedDeficit",
            "CashAndCashEquivalentsAtCarryingValue",
            "InventoryNet",
            "CommonStockSharesOutstanding",
        ],
        "CF": [
            "NetCashProvidedByUsedInOperatingActivities",
            "NetCashProvidedByUsedInInvestingActivities",
            "NetCashProvidedByUsedInFinancingActivities",
            "PaymentsToAcquirePropertyPlantAndEquipment",
            "DepreciationDepletionAndAmortization",
            "PaymentsForRepurchaseOfCommonStock",
            "ProceedsFromIssuanceOfLongTermDebt",
            "RepaymentsOfLongTermDebt",
            "PaymentsOfDividends",
        ],
    }

    generated = {}
    for stmt, concepts in statements.items():
        # Construir series por concepto
        concept_to_series = {}
        all_dates = set()
        for cname in concepts:
            fact_obj = usgaap.get(cname)
            if not fact_obj:
                continue
            series = _series_from_fact(fact_obj, preferred_units=("USD", "shares"))
            if not series:
                continue
            concept_to_series[cname] = series
            all_dates.update(series.keys())

        if not all_dates:
            continue

        dates_sorted = sorted(all_dates)
        csv_path = out_dir / f"{stmt}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            header = ["Date"] + concepts
            writer.writerow(header)
            for d in dates_sorted:
                row = [d]
                for cname in concepts:
                    val = concept_to_series.get(cname, {}).get(d, ("", ""))[0]
                    row.append(val)
                writer.writerow(row)
        generated[stmt] = str(csv_path)

    # Guarda también el JSON crudo para referencia
    raw_path = out_dir / "company_facts.json"
    try:
        with open(raw_path, "w", encoding="utf-8") as jf:
            json.dump(facts, jf, ensure_ascii=False)
        generated["RAW_JSON"] = str(raw_path)
    except Exception:
        pass

    return generated


def extract_text_items_to_md(html_path: Path, out_dir: Path) -> dict:
    """
    Extrae bloques de texto por Items (Item 1, 1A, 2, 7, 7A, etc.) y los guarda en .md.
    Usa heurística basada en encabezados "ITEM X" en el texto plano.
    Devuelve mapa {item_id -> ruta_md} y un índice.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    raw = html_path.read_text(errors="ignore")
    # Normaliza saltos y quita scripts/estilos por encima
    raw = re.sub(r"<script[\s\S]*?</script>", " ", raw, flags=re.I)
    raw = re.sub(r"<style[\s\S]*?</style>", " ", raw, flags=re.I)
    # Preserva saltos en etiquetas de bloque comunes
    raw = re.sub(r"<(br|/p|/div|/tr|/h\d)>", "\n", raw, flags=re.I)
    # Quita el resto de etiquetas
    text = re.sub(r"<[^>]+>", " ", raw)
    text = html_lib.unescape(text)
    # Normaliza espacios
    text = re.sub(r"\r\n|\r", "\n", text)
    text = re.sub(r"\u00a0", " ", text)
    text = re.sub(r"[\t ]+", " ", text)
    # Colapsa múltiples saltos
    text = re.sub(r"\n{2,}", "\n\n", text)

    # Detecta encabezados tipo ITEM 1, ITEM 1A, etc. al inicio de línea
    pattern = re.compile(r"(?im)^\s*item\s+(\d+[a-z]?)\.?\s*(.*)$")
    matches = list(pattern.finditer(text))
    if not matches:
        return {}

    sections = {}
    for i, m in enumerate(matches):
        item_id = m.group(1).upper()
        title_rest = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        # Limpia contenido extra
        content = re.sub(r"\n{3,}", "\n\n", content)

        filename = f"Item_{item_id}.md"
        md_path = out_dir / filename
        with open(md_path, "w", encoding="utf-8") as mf:
            header = f"## Item {item_id} {title_rest}".strip()
            mf.write(header + "\n\n")
            mf.write(content + "\n")
        sections[item_id] = str(md_path)

    # Índice
    index_path = out_dir / "sections_index.md"
    with open(index_path, "w", encoding="utf-8") as idx:
        idx.write("## Items extraídos\n\n")
        for k in sorted(sections.keys()):
            idx.write(f"- Item {k}: {Path(sections[k]).name}\n")
    sections["INDEX"] = str(index_path)

    return sections


def main():
    try:
        ticker = input("Ingresa el ticker (ej. AAPL): ").strip()
        if not ticker:
            print("Ticker vacío. Saliendo.")
            return

        cik_10 = get_cik_from_ticker(ticker)
        print(f"CIK (10 dígitos) para {ticker.upper()}: {cik_10}")

        submissions = get_company_submissions(cik_10)
        filings = list_recent_filings(submissions)
        if not filings:
            print("No hay filings que coincidan con los tipos por defecto (10-K, 10-Q, 8-K).")
            return

        _print_recent_filings(filings)

        while True:
            sel = input(f"\nElige un número [1-{len(filings)}] (ENTER=1): ").strip()
            if sel == "":
                choice = 1
            else:
                if not sel.isdigit():
                    print("Entrada no válida; escribe un número.")
                    continue
                choice = int(sel)
            if 1 <= choice <= len(filings):
                break
            print("Fuera de rango. Intenta de nuevo.")

        selected = filings[choice - 1]
        urls = build_filing_urls(cik_10, selected["accession"], selected["primary_doc"])

        print("\nFiling seleccionado:")
        print(f"- Ticker: {ticker.upper()}")
        print(f"- CIK: {cik_10}")
        print(f"- Form: {selected['form']}")
        print(f"- Fecha de presentación: {selected['filing_date']}")
        print(f"- Accession: {selected['accession']}")
        print(f"- Documento principal: {urls['primary_doc']}")
        print(f"- Index JSON: {urls['index_json']}")
        print(f"- Carpeta del expediente: {urls['folder']}")

        while True:
            dl = input("\n¿Deseas descargar el expediente completo? (s/N): ").strip().lower()
            if dl in ("", "s", "n"):
                break
            print("Responde 's' o 'n'.")
        if dl == "s":
            while True:
                inc = input("¿Incluir exhibits/anexos? (s/N): ").strip().lower()
                if inc in ("", "s", "n"):
                    break
                print("Responde 's' o 'n'.")
            include_exhibits = (inc == "s")
            try:
                print("Descargando... esto puede tardar unos minutos según el tamaño.")
                files = download_entire_filing(cik_10, selected["accession"], out_dir="filings", include_exhibits=include_exhibits)
                print(f"Descarga completa. Archivos: {len(files)}")
                try:
                    primary_path = Path("filings") / selected["accession"] / selected["primary_doc"]
                    base_dir = Path("filings") / selected["accession"]
                    recommended = _choose_preferred_view_file(base_dir, selected["accession"], selected["primary_doc"])
                    if recommended and recommended.exists() and recommended.is_file():
                        print(f"Documento recomendado para visualizar: {recommended}")
                    # Fallback útil: archivo de texto completo de la submission
                    txt_bundle = base_dir / f"{selected['accession']}.txt"
                    if txt_bundle.exists():
                        print(f"Archivo completo de la submission (raw .txt): {txt_bundle}")
                    # Ofrecer abrir en navegador
                    try:
                        open_ans = input("\n¿Abrir el documento recomendado en el navegador? (s/N): ").strip().lower()
                        if open_ans == "s" and recommended and recommended.exists():
                            webbrowser.open(recommended.resolve().as_uri())
                    except Exception:
                        pass
                    # Ofrecer extracción de tablas
                    try:
                        ext_ans = input("¿Extraer tablas a CSV/JSON desde el documento recomendado? (s/N): ").strip().lower()
                        if ext_ans == "s" and recommended and recommended.exists() and recommended.is_file():
                            out_tables_dir = base_dir / "tables"
                            csv_list, json_file, n_tables = extract_tables_from_html(recommended, out_tables_dir)
                            print(f"Tablas extraídas: {n_tables}")
                            if json_file:
                                print(f"JSON con todas las tablas: {json_file}")
                            if csv_list:
                                print(f"Ejemplo CSV: {csv_list[0]}")
                    except Exception as e:
                        print(f"No se pudieron extraer tablas: {e}")
                    # Ofrecer extracción de secciones de texto a .md
                    try:
                        md_ans = input("¿Extraer secciones de texto (Items) a .md? (s/N): ").strip().lower()
                        if md_ans == "s" and recommended and recommended.exists() and recommended.is_file():
                            md_dir = base_dir / "sections"
                            sections = extract_text_items_to_md(recommended, md_dir)
                            if sections:
                                print("Secciones de texto extraídas:")
                                for k, v in sections.items():
                                    print(f"- {k}: {v}")
                            else:
                                print("No se detectaron encabezados de Items para extraer.")
                    except Exception as e:
                        print(f"No se pudieron extraer secciones de texto: {e}")
                    # Ofrecer exportación de estados desde Company Facts
                    try:
                        facts_ans = input("\n¿Exportar estados financieros (IS/BS/CF) desde Company Facts (XBRL)? (s/N): ").strip().lower()
                        if facts_ans == "s":
                            facts = get_company_facts(cik_10)
                            facts_out = base_dir / "facts"
                            results = export_statements_from_company_facts(facts, facts_out)
                            print("Archivos generados desde Company Facts:")
                            for k, v in results.items():
                                print(f"- {k}: {v}")
                    except Exception as e:
                        print(f"No se pudieron exportar estados: {e}")
                except Exception:
                    pass
                if files:
                    print(f"Primer archivo descargado (referencia): {files[0]}")
            except Exception as e:
                print(f"Hubo un problema al descargar: {e}")

    except requests.HTTPError as http_err:
        print(f"Error HTTP al consultar la SEC: {http_err}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
