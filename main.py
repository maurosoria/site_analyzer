import asyncio
import json
import logging
import os
import re
import argparse
import urllib.parse
from lib.logging_utils import highlight, init_logging
from lib.scan_result import ScanResults
from lib.site_analyzer import get_url_content, load_keywords, load_scripts
from playwright.async_api import async_playwright


from lib.extractors import (
    extract_emails_from_js,
    extract_urls_from_js,
    extract_endpoints,
    extract_keywords_from_js,
)


async def main():
    parser = argparse.ArgumentParser(description='Process a URL and extract information.')
    parser.add_argument('-u', '--url', required=True, help='URL to navigate')
    parser.add_argument('-d', '--dir', default='./js', help='Directory containing JS scripts')
    parser.add_argument('-k', '--keywords', default='./db/keywords.txt', help='File containing keywords to search for')
    parser.add_argument('--debug', action='store_true', help='Activar modo DEBUG para logging detallado')
    args = parser.parse_args()

    # Inicializar logging según el parámetro --debug
    init_logging(args.debug)

    scan_results = ScanResults()
    js_injects = await load_scripts(args.dir)
    # Cargamos keywords desde el archivo; se usarán en el extractor.
    _ = load_keywords(args.keywords)  # No se asigna, ya que re-check en el scan

    async with async_playwright() as p:
        #browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        # Alternativamente, usar:
        browser = await p.chromium.launch(headless=True)
        content, assets = await get_url_content(browser, args.url, scan_results, js_injects)

    highlight("Resumen final de resultados", level="FINAL")
    logging.info("Emails encontrados: %s", list(scan_results.emails))
    logging.info("URLs encontradas: %s", list(scan_results.urls))
    logging.info("Endpoints encontrados: %s", list(scan_results.endpoints))
    logging.info("Keywords encontradas: %s", list(scan_results.keywords))
    logging.info("SourceMap matches: %s", list(scan_results.sourcemap_matches))
    logging.info("JS Paths encontrados: %s", list(scan_results.js_paths))

if __name__ == '__main__':
    asyncio.run(main())
