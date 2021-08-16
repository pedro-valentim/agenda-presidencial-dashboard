# Dashboard: agenda-presidencial

Visualização da agenda presidencial com Streamlit

## Descrição

Utilizando os dados encontrados em [sjcdigital/data-etl](https://github.com/sjcdigital/data-etl/tree/main/agenda-presidente).

Link direto: https://raw.githubusercontent.com/sjcdigital/data-etl/main/agenda-presidente/bolsonaro/report.json

## Instalação e uso

Pode ser utilizado o Pipenv pra construir o ambiente com os requisitos `streamlit` e `pandas`. Saiba mais: https://pipenv.pypa.io/en/latest/
Com o pipenv já instalado, siga os passos:

1. Execute o shell no ambiente:

```
    python3 -m pipenv shell
```

2. Execute o dashboard Streamlit:

```
    streamlit run app.py
```

3. Acesse a URL gerada (porta `:8501` por padrão).
