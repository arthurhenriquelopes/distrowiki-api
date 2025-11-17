# Testes do DistroWiki

Scripts de teste para validação do sistema.

## Scripts Disponíveis

- **test_api.py**: Testes completos da API REST
- **test_cachyos.py**: Teste específico do CachyOS (scraping completo)
- **test_distrowatch.py**: Teste de scraping básico do DistroWatch
- **test_ranking.py**: Teste da busca do ranking "Last 1 month"
- **test_complete_system.py**: Teste end-to-end do sistema completo

## Executar Testes

```powershell
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Executar um teste específico
python tests\test_cachyos.py

# Executar teste do ranking
python tests\test_ranking.py
```

## Nota

Esses testes fazem scraping real do DistroWatch.com. 
Use com moderação para respeitar o servidor deles.
