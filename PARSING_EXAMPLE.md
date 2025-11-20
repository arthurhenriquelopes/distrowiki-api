# Exemplo de Parsing do DistroWatch

Baseado nas páginas HTML salvas em `/url`:
- CachyOS.html
- MX Linux.html  
- BigLinux.html

## Estrutura HTML Identificada

### 1. Página da Distro Individual (`table.php?distribution=ubuntu`)

#### Nome da Distro
```html
<h1>BigLinux</h1>
```
**Selector BeautifulSoup**: `soup.find('h1').get_text(strip=True)`
**Resultado**: `"BigLinux"`

---

#### ID/Slug
- Extraído da URL ou do parâmetro: `table.php?distribution=biglinux`
- **ID**: `"biglinux"`

---

#### Categoria
```html
<ul>
  <li><b>Categoria:</b> <a href="...">Desktop</a>, <a href="...">Live Medium</a><br>
  </li>
</ul>
```

**Selector BeautifulSoup**:
```python
# Encontrar <li> que contém <b>Categoria:</b>
for li in soup.find_all('li'):
    b_tag = li.find('b')
    if b_tag and 'Categoria' in b_tag.get_text():
        # Extrair todos os <a> dentro desse <li>
        categories = [a.get_text(strip=True) for a in li.find_all('a')]
        # Juntar com vírgula e espaço
        category = ', '.join(categories)
```

**Resultado**: `"Desktop, Live Medium"` (string, sem colchetes)

---

#### Data de Lançamento (Última Versão)

Está na tabela "Característica" com `<th>Data de Lançamento</th>` seguido de células `<td class="Date">`:

```html
<tr>
  <th>Data de Lançamento</th>
  <td class="Date">2025-11-17</td>  <!-- Esta é a mais recente -->
  <td class="Date">2024-02-23</td>
  <td class="Date">2023-11-04</td>
  ...
</tr>
```

**Selector BeautifulSoup**:
```python
# Encontrar <th> com texto "Data de Lançamento"
for th in soup.find_all('th'):
    if 'Data de Lançamento' in th.get_text():
        # Pegar a linha (<tr>) pai
        row = th.find_parent('tr')
        # Primeira <td class="Date"> é a data mais recente
        date_td = row.find('td', class_='Date')
        if date_td:
            date_str = date_td.get_text(strip=True)  # "2025-11-17"
            # Converter para DD/MM/YYYY
            from datetime import datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            date_br = date_obj.strftime('%d/%m/%Y')  # "17/11/2025"
```

**Resultado**: `"17/11/2025"` (formato brasileiro)

---

#### Popularidade (4 semanas)

Na descrição da distro, há uma linha:
```html
<b>Popularidade (acessos por dia):</b> 
12 meses: <b>26</b> (376), 
6 meses: <b>18</b> (536), 
3 meses: <b>22</b> (538), 
4 semanas: <b>21</b> (603),  <!-- ESTE É O QUE QUEREMOS -->
1 semana: <b>14</b> (796)
```

**Selector BeautifulSoup**:
```python
import re

# Buscar texto que contenha "Popularidade (acessos por dia)"
for b_tag in soup.find_all('b'):
    if 'Popularidade (acessos por dia)' in b_tag.get_text():
        # Pegar todo o texto do parágrafo/contexto
        parent_text = b_tag.parent.get_text()
        
        # Regex para extrair "4 semanas: <b>21</b> (603)"
        match = re.search(r'4 semanas:\s*<b>(\d+)</b>\s*\((\d+(?:,\d+)?)\)', 
                         str(b_tag.parent))
        
        # OU buscar diretamente no texto:
        # "4 semanas: 21 (603)"
        match = re.search(r'4 semanas:\s*(\d+)\s*\((\d+(?:,\d+)?)\)', parent_text)
        
        if match:
            rank_4weeks = int(match.group(1))      # 21
            hpd_4weeks = int(match.group(2).replace(',', ''))  # 603
```

**Resultado**: 
- `rank`: `21` (posição no ranking de 4 semanas)
- `hits_per_day`: `603` (acessos por dia)

**IMPORTANTE**: Você pediu **popularidade de 4 semanas** (igual ao período "Last 1 month" da página de ranking).

---

#### Rating (Avaliação de Visitantes)

```html
<b>Average visitor rating</b>: <b>8.0</b>/10 from <b>332</b> review(s).
```

**Selector BeautifulSoup**:
```python
# Procurar por <b> que contém "Average visitor rating"
for b_tag in soup.find_all('b'):
    if 'Average visitor rating' in b_tag.get_text():
        # O rating está no próximo <b> tag
        parent = b_tag.parent
        # Buscar padrão: <b>8.0</b>/10
        rating_match = re.search(r'<b>(\d+\.\d+)</b>/10', str(parent))
        
        # OU no texto:
        text = parent.get_text()
        rating_match = re.search(r':\s*(\d+\.\d+)/10', text)
        
        if rating_match:
            rating = float(rating_match.group(1))  # 8.0
```

**Resultado**: `8.0` (apenas o número, sem "/10")

---

## Exemplo Completo de Parsing para BigLinux

```python
from bs4 import BeautifulSoup
import re
from datetime import datetime

# Abrir HTML
with open('url/DistroWatch.com_ BigLinux.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# 1. Nome
name = soup.find('h1').get_text(strip=True)
print(f"Nome: {name}")  # BigLinux

# 2. ID (do slug na URL ou nome normalizado)
distro_id = "biglinux"  # já temos do parâmetro da URL
print(f"ID: {distro_id}")

# 3. Categoria
category = None
for li in soup.find_all('li'):
    b_tag = li.find('b')
    if b_tag and 'Categoria' in b_tag.get_text():
        categories = [a.get_text(strip=True) for a in li.find_all('a')]
        category = ', '.join(categories)
        break
print(f"Categoria: {category}")  # Desktop, Live Medium

# 4. Data de Lançamento (mais recente)
release_date = None
for th in soup.find_all('th'):
    if 'Data de Lançamento' in th.get_text():
        row = th.find_parent('tr')
        date_td = row.find('td', class_='Date')
        if date_td:
            date_str = date_td.get_text(strip=True)  # "2025-11-17"
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            release_date = date_obj.strftime('%d/%m/%Y')  # "17/11/2025"
            break
print(f"Data de Lançamento: {release_date}")  # 17/11/2025

# 5. Popularidade (4 semanas)
popularity_rank = None
popularity_hpd = None
for text_node in soup.find_all(string=re.compile(r'4 semanas')):
    # Extrair do contexto: "4 semanas: <b>21</b> (603)"
    parent_html = str(text_node.parent)
    # Buscar no texto vizinho
    full_text = text_node.parent.get_text()
    match = re.search(r'4 semanas:\s*(\d+)\s*\(([0-9,]+)\)', full_text)
    if match:
        popularity_rank = int(match.group(1))
        popularity_hpd = int(match.group(2).replace(',', ''))
        break
print(f"Popularidade (4 semanas): Rank {popularity_rank}, {popularity_hpd} acessos/dia")
# Popularidade (4 semanas): Rank 21, 603 acessos/dia

# 6. Rating
rating = None
for text_node in soup.find_all(string=re.compile(r'Average visitor rating')):
    parent_text = text_node.parent.get_text()
    match = re.search(r':\s*(\d+\.\d+)/10', parent_text)
    if match:
        rating = float(match.group(1))
        break
print(f"Rating: {rating}")  # 9.2
```

**Saída esperada**:
```
Nome: BigLinux
ID: biglinux
Categoria: Desktop, Live Medium
Data de Lançamento: 17/11/2025
Popularidade (4 semanas): Rank 21, 603 acessos/dia
Rating: 9.2
```

---

## Observações Importantes

1. **Data no formato brasileiro**: Converter de `YYYY-MM-DD` para `DD/MM/YYYY`
2. **Popularidade de 4 semanas**: Usar o período "4 semanas" que corresponde ao ranking "Last 1 month"
3. **Rating**: Extrair apenas o número decimal (ex: `8.0`), sem o `/10`
4. **Categoria**: Pode ter múltiplas categorias separadas por vírgula
5. **Algumas distros podem não ter todos os campos**: Tratar como opcional

---

## Próximo Passo

Implementar este parsing no `distrowatch_cloudscraper.py` para:
1. Buscar lista de 230 distros da página `/popularity` (tabela "Last 1 month")
2. Para cada distro, acessar sua página individual
3. Extrair todos os 6 campos pedidos
4. Salvar em JSON com formato:

```json
{
  "id": "biglinux",
  "name": "BigLinux",
  "category": "Desktop, Live Medium",
  "release_date": "17/11/2025",
  "popularity": {
    "rank_4weeks": 21,
    "hits_per_day": 603
  },
  "rating": 9.2
}
```
