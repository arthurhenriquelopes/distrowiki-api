#!/usr/bin/env python3
"""
Teste de parsing usando os arquivos HTML salvos localmente.
Valida se os seletores estão corretos antes de fazer scraping real.
"""

import re
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup


def extract_slug_from_filename(filename: str) -> str:
    """Extrai slug do nome do arquivo."""
    # "DistroWatch.com_ CachyOS.html" -> "cachyos"
    name = filename.replace('DistroWatch.com_', '').replace('.html', '').strip()
    return name.lower().replace(' ', '')


def parse_category(soup: BeautifulSoup) -> str:
    """Extrai categoria da página."""
    try:
        for li in soup.find_all('li'):
            b_tag = li.find('b')
            if b_tag and 'Categoria' in b_tag.get_text():
                categories = [a.get_text(strip=True) for a in li.find_all('a')]
                return ', '.join(categories)
    except Exception as e:
        print(f"   ⚠️ Erro ao extrair categoria: {e}")
    return None


def parse_release_date(soup: BeautifulSoup) -> str:
    """Extrai data de lançamento (formato DD/MM/YYYY)."""
    try:
        for th in soup.find_all('th'):
            if 'Data de Lançamento' in th.get_text():
                row = th.find_parent('tr')
                date_td = row.find('td', class_='Date')
                if date_td:
                    date_str = date_td.get_text(strip=True)  # "2025-11-17"
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    return date_obj.strftime('%d/%m/%Y')  # "17/11/2025"
    except Exception as e:
        print(f"   ⚠️ Erro ao extrair data: {e}")
    return None


def parse_popularity(soup: BeautifulSoup) -> dict:
    """Extrai popularidade de 4 semanas."""
    result = {'rank': None, 'hits_per_day': None}
    
    try:
        for text_node in soup.find_all(string=re.compile(r'4 semanas')):
            full_text = text_node.parent.get_text()
            match = re.search(r'4 semanas:\s*(\d+)\s*\(([0-9,]+)\)', full_text)
            if match:
                result['rank'] = int(match.group(1))
                result['hits_per_day'] = int(match.group(2).replace(',', ''))
                break
    except Exception as e:
        print(f"   ⚠️ Erro ao extrair popularidade: {e}")
    
    return result


def parse_rating(soup: BeautifulSoup) -> float:
    """Extrai rating dos visitantes."""
    try:
        # Buscar por <a> que contém "Average visitor rating"
        for a_tag in soup.find_all('a', href=lambda x: x and 'ratings' in x):
            if 'Average visitor rating' in a_tag.get_text():
                # O rating está na mesma linha: </a></b>: <b>9.2</b>/10
                # Buscar no parent (que é <b>) e depois no parent dele
                parent_b = a_tag.parent  # <b>
                if parent_b and parent_b.name == 'b':
                    # Buscar no contexto do parent do <b>
                    parent_container = parent_b.parent
                    if parent_container:
                        # Buscar o próximo <b> após o </b> do link
                        for sibling in parent_b.next_siblings:
                            if hasattr(sibling, 'name') and sibling.name == 'b':
                                # Este é o <b>9.2</b>
                                rating_text = sibling.get_text(strip=True)
                                try:
                                    return float(rating_text)
                                except ValueError:
                                    pass
                            elif isinstance(sibling, str):
                                # Pode estar no texto: ": <b>9.2</b>/10"
                                pass
    except Exception as e:
        print(f"   ⚠️ Erro ao extrair rating: {e}")
    return None


def test_html_file(html_file: Path):
    """Testa parsing de um arquivo HTML."""
    print(f"\n{'='*60}")
    print(f"📄 Testando: {html_file.name}")
    print('='*60)
    
    # Ler HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Nome
    name = None
    h1 = soup.find('h1')
    if h1:
        name = h1.get_text(strip=True)
    print(f"✅ Nome: {name}")
    
    # 2. ID/Slug
    slug = extract_slug_from_filename(html_file.name)
    print(f"✅ ID: {slug}")
    
    # 3. Categoria
    category = parse_category(soup)
    print(f"✅ Categoria: {category}")
    
    # 4. Data de Lançamento
    release_date = parse_release_date(soup)
    print(f"✅ Data de Lançamento: {release_date}")
    
    # 5. Popularidade
    popularity = parse_popularity(soup)
    print(f"✅ Popularidade (4 semanas):")
    print(f"   - Rank: {popularity['rank']}")
    print(f"   - Hits/dia: {popularity['hits_per_day']}")
    
    # 6. Rating
    rating = parse_rating(soup)
    print(f"✅ Rating: {rating}")
    
    # Resultado consolidado
    result = {
        'id': slug,
        'name': name,
        'category': category,
        'release_date': release_date,
        'popularity_rank': popularity['rank'],
        'popularity_hits': popularity['hits_per_day'],
        'rating': rating
    }
    
    return result


def main():
    """Testa parsing de todos os HTMLs salvos."""
    print("🧪 TESTE DE PARSING - Arquivos HTML Locais")
    print("="*60)
    
    # Diretório com os HTMLs
    url_dir = Path('url')
    
    if not url_dir.exists():
        print(f"❌ Diretório '{url_dir}' não encontrado!")
        return
    
    # Buscar todos os arquivos HTML
    html_files = list(url_dir.glob('*.html'))
    
    if not html_files:
        print(f"❌ Nenhum arquivo HTML encontrado em '{url_dir}'!")
        return
    
    print(f"📁 Encontrados {len(html_files)} arquivos HTML\n")
    
    # Testar cada arquivo
    all_results = []
    for html_file in html_files:
        result = test_html_file(html_file)
        all_results.append(result)
    
    # Resumo final
    print(f"\n{'='*60}")
    print("📊 RESUMO DOS TESTES")
    print('='*60)
    
    for i, result in enumerate(all_results, 1):
        print(f"\n{i}. {result['name']} ({result['id']})")
        print(f"   ✓ Categoria: {'OK' if result['category'] else '❌ FALTA'}")
        print(f"   ✓ Data: {'OK' if result['release_date'] else '❌ FALTA'}")
        print(f"   ✓ Popularidade: {'OK' if result['popularity_rank'] else '❌ FALTA'}")
        print(f"   ✓ Rating: {'OK' if result['rating'] else '❌ FALTA'}")
    
    # Salvar resultados
    import json
    output_file = Path('test_parsing_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: {output_file}")
    print("\n✅ Teste concluído!")


if __name__ == '__main__':
    main()
