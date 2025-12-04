# Processamento de Imagens - Filtros Espaciais

Trabalho acadêmico desenvolvido para análise de filtros espaciais aplicados à redução de ruído em imagens.

## Estrutura

```
├── processamento_imagens.ipynb    # Notebook completo
├── webapp/                         # Aplicação web
│   ├── main.py                    # Backend FastAPI
│   ├── image_processor.py         # Processamento
│   └── templates/                 # Frontend
├── images/                        # Imagens de entrada
└── results/                       # Resultados gerados
```

## Uso Rápido

### Notebook Jupyter

```bash
pip install -r requirements.txt
jupyter notebook processamento_imagens.ipynb
```

### Aplicação Web

```bash
cd webapp
pip install -r requirements.txt
python start.py
```

Acesse: http://localhost:8000

## Funcionalidades

- 8 filtros espaciais (Média, Gaussiano, Mediana, Moda em 3×3 e 7×7)
- 2 tipos de ruído (Sal e Pimenta, Gaussiano)
- Métricas MSE e PSNR
- Interface web interativa
- Gráficos em tempo real
- Exportação de resultados

## Deploy (Render)

1. Adicione `Procfile`:
```
web: cd webapp && uvicorn main:app --host 0.0.0.0 --port $PORT
```

2. Configure no Render:
   - Build Command: `pip install -r webapp/requirements.txt`
   - Start Command: `cd webapp && uvicorn main:app --host 0.0.0.0 --port $PORT`

## Tecnologias

Python, FastAPI, OpenCV, NumPy, Plotly, Tailwind CSS
