import requests
import json
import webbrowser
import os
from datetime import datetime, timedelta

# ═══════════════════════════════════════════════════════════════
#  CONFIGURAÇÃO - AJUSTADO COM O SEU IP E ID CORRETOS
# ═══════════════════════════════════════════════════════════════
CONFIG = {
    "base_url":    "http://54.82.9.4:8666",        # Seu IP da AWS
    "entity_type": "Lamp",
    "entity_id":   "urn:ngsi-ld:Lamp:001",         # ID 001 conforme seu Wokwi
    "attribute":   "luminosity",
    "lastN":       100,
    "service":     "smart",                        # Header fiware-service
    "service_path": "/"                            # Header fiware-servicepath
}

# ═══════════════════════════════════════════════════════════════
#  BUSCA DE DADOS COM HEADERS OBRIGATÓRIOS
# ═══════════════════════════════════════════════════════════════
def obter_dados():
    url = (
        f"{CONFIG['base_url']}/STH/v1/contextEntities"
        f"/type/{CONFIG['entity_type']}"
        f"/id/{CONFIG['entity_id']}"
        f"/attributes/{CONFIG['attribute']}"
        f"?lastN={CONFIG['lastN']}"
    )
    
    # Estes headers evitam o erro 400
    headers = {
        "fiware-service":     CONFIG["service"],
        "fiware-servicepath": CONFIG["service_path"]
    }
    
    print(f"Buscando dados em: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        # Se der erro 400 ou 404, o raise_for_status vai avisar
        response.raise_for_status() 
        
        data = response.json()
        
        # Extração do caminho específico do STH-Comet
        valores = data["contextResponses"][0]["contextElement"]["attributes"][0]["values"]
        print(f"✅ {len(valores)} registros recebidos.")
        return valores

    except requests.exceptions.HTTPError as e:
        if response.status_code == 400:
            print("❌ Erro 400: O servidor exigiu os Headers (smart/ /). Verifique o CONFIG.")
        else:
            print(f"❌ Erro HTTP: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
    return []

# ═══════════════════════════════════════════════════════════════
#  FILTROS E NORMALIZAÇÃO
# ═══════════════════════════════════════════════════════════════
def filtrar_ultimos(dados, minutos):
    corte = datetime.utcnow() - timedelta(minutes=minutos)
    resultado = []
    for entry in dados:
        try:
            # Converte recvTime para objeto datetime para comparar
            t = datetime.strptime(entry["recvTime"][:19], "%Y-%m-%dT%H:%M:%S")
            if t >= corte:
                resultado.append(entry)
        except:
            pass
    return resultado

def normalizar(dados):
    resultado = []
    for entry in dados:
        try:
            resultado.append({
                "recvTime":  entry["recvTime"],
                "attrValue": float(entry["attrValue"])
            })
        except:
            pass
    return resultado

# ═══════════════════════════════════════════════════════════════
#  TEMPLATE HTML (Visual Tech-Glam)
# ═══════════════════════════════════════════════════════════════
HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"/><title>Monitor de Luminosidade</title>
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;800&display=swap" rel="stylesheet"/>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.0.1/dist/chartjs-plugin-annotation.min.js"></script>
<style>
  :root { --bg: #f3eeff; --title: #3b1f6e; --accent: #7c3aed; }
  body { font-family: 'Nunito', sans-serif; background: var(--bg); padding: 2rem; color: #2e1065; }
  .wrapper { max-width: 1000px; margin: 0 auto; }
  header { text-align: center; margin-bottom: 2rem; }
  .card { background: white; border-radius: 15px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 4px 15px rgba(124,58,237,0.1); }
  .chart-wrap { height: 250px; position: relative; }
  .info-pill { background: #ede9fe; color: var(--accent); padding: 0.4rem 1rem; border-radius: 20px; font-weight: 700; font-size: 0.8rem; margin: 0 5px; }
</style>
</head>
<body>
<div class="wrapper">
  <header>
    <h1>💡 Monitor de Luminosidade</h1>
    <p>Entidade: <strong>{{ENTITY_ID}}</strong></p>
    <div style="margin-top:15px">
        <span class="info-pill">📦 {{TOTAL}} registros</span>
        <span class="info-pill">🕐 1 min: {{COUNT_1M}}</span>
        <span class="info-pill">🕔 5 min: {{COUNT_5M}}</span>
    </div>
  </header>

  <div class="card">
    <h3>Histórico Geral (Últimos 100)</h3>
    <div class="chart-wrap"><canvas id="chart-all"></canvas></div>
  </div>
  <div class="card">
    <h3>Último Minuto</h3>
    <div class="chart-wrap"><canvas id="chart-1m"></canvas></div>
  </div>
</div>

<script>
const ALL_DATA = {{ALL_DATA}};
const DATA_1M  = {{DATA_1M}};

function buildChart(id, data) {
  if(!data.length) return;
  const ctx = document.getElementById(id).getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.map(d => d.recvTime.slice(11,19)),
      datasets: [{
        label: 'Luminosidade',
        data: data.map(d => d.attrValue),
        borderColor: '#7c3aed',
        backgroundColor: 'rgba(124,58,237,0.1)',
        fill: true,
        tension: 0.3
      }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });
}
buildChart('chart-all', ALL_DATA);
buildChart('chart-1m', DATA_1M);
</script>
</body>
</html>"""

# ═══════════════════════════════════════════════════════════════
#  EXECUÇÃO
# ═══════════════════════════════════════════════════════════════
def gerar_dashboard(dados_all):
    dados_1m = filtrar_ultimos(dados_all, 1)
    dados_5m = filtrar_ultimos(dados_all, 5)
    
    html_final = HTML \
        .replace("{{ALL_DATA}}",   json.dumps(normalizar(dados_all))) \
        .replace("{{DATA_1M}}",    json.dumps(normalizar(dados_1m))) \
        .replace("{{DATA_5M}}",    json.dumps(normalizar(dados_5m))) \
        .replace("{{ENTITY_ID}}",  CONFIG["entity_id"]) \
        .replace("{{TOTAL}}",      str(len(dados_all))) \
        .replace("{{COUNT_1M}}",   str(len(dados_1m))) \
        .replace("{{COUNT_5M}}",   str(len(dados_5m)))

    caminho = os.path.abspath("dashboard_luminosidade.html")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html_final)
    
    print(f"✅ Dashboard gerado com sucesso!")
    webbrowser.open(f"file://{caminho}")

if __name__ == "__main__":
    dados = obter_dados()
    if dados:
        gerar_dashboard(dados)
    else:
        print("⚠️  A API não retornou dados. Certifique-se de que o Wokwi está rodando e enviando LDR.")