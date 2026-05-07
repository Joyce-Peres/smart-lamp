import requests
import json
import webbrowser
import os
from datetime import datetime, timedelta

# ── Configuração da API ────────────────────────────────────────────────────────

BASE_URL = "http://54.82.9.4:8666/STH/v1/contextEntities/type/Lamp/id/urn:ngsi-ld:Lamp:001/attributes/luminosity"
HEADERS = {
    'fiware-service': 'smart',
    'fiware-servicepath': '/'
}

def obter_dados(lastN=100):
    url = f"{BASE_URL}?lastN={lastN}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data['contextResponses'][0]['contextElement']['attributes'][0]['values']
    except Exception as e:
        print(f"Erro ao obter dados: {e}")
    return []

def filtrar_ultimo_minuto(dados):
    agora = datetime.utcnow()
    limite = agora - timedelta(minutes=1)
    filtrados = []
    for entry in dados:
        try:
            t = datetime.strptime(entry['recvTime'][:19], "%Y-%m-%dT%H:%M:%S")
            if t >= limite:
                filtrados.append(entry)
        except:
            pass
    return filtrados

def filtrar_ultimos_n_minutos(dados, minutos=5):
    agora = datetime.utcnow()
    limite = agora - timedelta(minutes=minutos)
    filtrados = []
    for entry in dados:
        try:
            t = datetime.strptime(entry['recvTime'][:19], "%Y-%m-%dT%H:%M:%S")
            if t >= limite:
                filtrados.append(entry)
        except:
            pass
    return filtrados

def formatar_para_js(dados):
    """Transforma lista de dicts em JSON serializável."""
    resultado = []
    for entry in dados:
        try:
            resultado.append({
                "recvTime": entry['recvTime'],
                "attrValue": float(entry['attrValue'])
            })
        except:
            pass
    return resultado

# ── Geração do HTML ────────────────────────────────────────────────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Monitor de Luminosidade</title>
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Nunito+Sans:wght@400;600&display=swap" rel="stylesheet"/>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.0.1/dist/chartjs-plugin-annotation.min.js"></script>
<style>
  :root {
    --bg:        #f3eeff;
    --surface:   #ffffffdd;
    --title:     #3b1f6e;
    --line:      #5c2fa8;
    --accent:    #7c3aed;
    --mean:      #c4b5fd;
    --mean-lbl:  #4c1d95;
    --border:    #ddd6fe;
    --text:      #2e1065;
    --subtext:   #6d28d9;
    --shadow:    0 4px 24px #7c3aed22;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'Nunito', sans-serif;
    background: var(--bg);
    min-height: 100vh;
    padding: 2rem 1.5rem 3rem;
    color: var(--text);
  }

  /* subtle radial glow in the background */
  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background: radial-gradient(ellipse 70% 50% at 50% 0%, #c4b5fd44 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
  }

  .wrapper { position: relative; z-index: 1; max-width: 1100px; margin: 0 auto; }

  header {
    text-align: center;
    margin-bottom: 2.5rem;
  }
  header h1 {
    font-size: 2rem;
    font-weight: 800;
    color: var(--title);
    letter-spacing: -0.5px;
  }
  header p {
    margin-top: .4rem;
    font-family: 'Nunito Sans', sans-serif;
    color: var(--subtext);
    font-size: .95rem;
  }

  .badge {
    display: inline-block;
    margin-top: .8rem;
    background: var(--line);
    color: #fff;
    font-size: .75rem;
    font-weight: 700;
    padding: .25rem .75rem;
    border-radius: 999px;
    letter-spacing: .5px;
  }

  .grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.75rem;
  }

  .card {
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: 18px;
    padding: 1.5rem 1.75rem 1.75rem;
    box-shadow: var(--shadow);
    backdrop-filter: blur(6px);
  }

  .card-header {
    display: flex;
    align-items: baseline;
    gap: .75rem;
    margin-bottom: 1.25rem;
    flex-wrap: wrap;
  }
  .card-header h2 {
    font-size: 1.1rem;
    font-weight: 800;
    color: var(--title);
  }
  .card-header .chip {
    font-size: .72rem;
    font-weight: 700;
    color: var(--accent);
    background: #ede9fe;
    border-radius: 999px;
    padding: .18rem .6rem;
  }
  .stat {
    font-family: 'Nunito Sans', sans-serif;
    font-size: .82rem;
    color: var(--subtext);
    margin-left: auto;
  }
  .stat span {
    font-weight: 700;
    color: var(--mean-lbl);
  }

  .chart-wrap { position: relative; height: 260px; }

  /* empty state */
  .empty {
    height: 260px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--subtext);
    font-size: .9rem;
    opacity: .6;
  }

  footer {
    text-align: center;
    margin-top: 2.5rem;
    font-size: .8rem;
    color: #a78bfa99;
    font-family: 'Nunito Sans', sans-serif;
  }
</style>
</head>
<body>
<div class="wrapper">

  <header>
    <h1>💡 Monitor de Luminosidade</h1>
    <p>Lâmpada <strong>urn:ngsi-ld:Lamp:002</strong></p>
    <span class="badge" id="ts">carregando…</span>
  </header>

  <div class="grid">

    <!-- Gráfico 1 — Todo o período -->
    <div class="card">
      <div class="card-header">
        <h2>Todo o Período</h2>
        <span class="chip">histórico completo</span>
        <span class="stat" id="stat-all">média: <span>–</span></span>
      </div>
      <div class="chart-wrap" id="wrap-all">
        <canvas id="chart-all"></canvas>
      </div>
    </div>

    <!-- Gráfico 2 — Último minuto -->
    <div class="card">
      <div class="card-header">
        <h2>Último Minuto</h2>
        <span class="chip">tempo real</span>
        <span class="stat" id="stat-1m">média: <span>–</span></span>
      </div>
      <div class="chart-wrap" id="wrap-1m">
        <canvas id="chart-1m"></canvas>
      </div>
    </div>

    <!-- Gráfico 3 — Últimos 5 minutos -->
    <div class="card">
      <div class="card-header">
        <h2>Últimos 5 Minutos</h2>
        <span class="chip">janela deslizante</span>
        <span class="stat" id="stat-5m">média: <span>–</span></span>
      </div>
      <div class="chart-wrap" id="wrap-5m">
        <canvas id="chart-5m"></canvas>
      </div>
    </div>

  </div>

  <footer>Atualizado automaticamente a cada 30 s · fiware-service: smart</footer>
</div>

<script>
// ── Dados injetados pelo Python ───────────────────────────────────────────────
const ALL_DATA  = __ALL_DATA__;
const DATA_1M   = __DATA_1M__;
const DATA_5M   = __DATA_5M__;

// ── Helpers ───────────────────────────────────────────────────────────────────
function formatTime(iso) {
  // Trata timestamps UTC (pode ter 'Z' ou não)
  const s = iso.endsWith('Z') ? iso : iso + 'Z';
  const d = new Date(s);
  if (isNaN(d)) return iso.slice(11,19); // fallback: HH:MM:SS
  return d.toLocaleString('pt-BR', {
    day: '2-digit', month: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
    timeZone: 'America/Sao_Paulo'
  });
}

function media(arr) {
  if (!arr.length) return null;
  return arr.reduce((a, b) => a + b, 0) / arr.length;
}

// ── Paleta ────────────────────────────────────────────────────────────────────
const LINE_COLOR   = '#5c2fa8';
const FILL_COLOR   = '#7c3aed18';
const MARKER_COLOR = '#5c2fa8';
const MEAN_COLOR   = '#9333ea';
const MEAN_BG      = '#f5f3ff';

// ── Fábrica de gráficos ───────────────────────────────────────────────────────
function buildChart(canvasId, wrapId, data, statId) {
  const wrap = document.getElementById(wrapId);

  if (!data || data.length === 0) {
    const canvas = document.getElementById(canvasId);
    canvas.style.display = 'none';
    const empty = document.createElement('div');
    empty.className = 'empty';
    empty.textContent = 'Sem dados nesse intervalo de tempo.';
    wrap.appendChild(empty);
    return;
  }

  const labels = data.map(d => formatTime(d.recvTime));
  const values = data.map(d => d.attrValue);
  const avg    = media(values);

  // Atualiza stat
  const statEl = document.querySelector(`#${statId} span`);
  if (statEl) statEl.textContent = avg !== null ? avg.toFixed(1) : '–';

  // Reduz labels no eixo X se muitos pontos
  const maxLabels = 10;
  const step = Math.ceil(labels.length / maxLabels);
  const sparseLabels = labels.map((l, i) => (i % step === 0 ? l : ''));

  new Chart(document.getElementById(canvasId), {
    type: 'line',
    data: {
      labels: sparseLabels,
      datasets: [{
        label: 'Luminosidade',
        data: values,
        borderColor: LINE_COLOR,
        backgroundColor: FILL_COLOR,
        pointBackgroundColor: MARKER_COLOR,
        pointBorderColor: '#fff',
        pointBorderWidth: 1.5,
        pointRadius: values.length > 40 ? 2 : 5,
        pointHoverRadius: 7,
        borderWidth: 2.5,
        tension: 0.35,
        fill: true,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#3b1f6e',
          titleColor: '#e9d5ff',
          bodyColor: '#fff',
          titleFont: { family: 'Nunito', weight: '700' },
          bodyFont: { family: 'Nunito Sans' },
          padding: 10,
          callbacks: {
            title: (items) => labels[items[0].dataIndex],  // tooltip mostra label completo
            label: (item) => ` Luminosidade: ${item.raw.toFixed(1)}`
          }
        },
        annotation: avg !== null ? {
          annotations: {
            meanLine: {
              type: 'line',
              yMin: avg,
              yMax: avg,
              borderColor: MEAN_COLOR,
              borderWidth: 2,
              borderDash: [6, 4],
              label: {
                display: true,
                content: `Média: ${avg.toFixed(1)}`,
                position: 'end',
                backgroundColor: MEAN_COLOR,
                color: '#fff',
                font: { family: 'Nunito', weight: '700', size: 12 },
                padding: { x: 8, y: 4 },
                borderRadius: 6,
              }
            }
          }
        } : {}
      },
      scales: {
        x: {
          grid: { color: '#ede9fe88' },
          ticks: {
            color: '#6d28d9',
            font: { family: 'Nunito', weight: '700', size: 11 },
            maxRotation: 40,
            minRotation: 20,
          }
        },
        y: {
          grid: { color: '#ede9fe88' },
          ticks: {
            color: '#6d28d9',
            font: { family: 'Nunito', weight: '700', size: 11 },
          },
          title: {
            display: true,
            text: 'Luminosidade',
            color: '#3b1f6e',
            font: { family: 'Nunito', weight: '800', size: 12 }
          }
        }
      }
    }
  });
}

// ── Inicialização ─────────────────────────────────────────────────────────────
document.getElementById('ts').textContent =
  'Atualizado em ' + new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' });

buildChart('chart-all', 'wrap-all', ALL_DATA,  'stat-all');
buildChart('chart-1m',  'wrap-1m',  DATA_1M,   'stat-1m');
buildChart('chart-5m',  'wrap-5m',  DATA_5M,   'stat-5m');
</script>
</body>
</html>
"""

# ── Main ───────────────────────────────────────────────────────────────────────

def gerar_dashboard():
    print("Buscando dados da API…")
    todos = obter_dados(lastN=100)

    if not todos:
        print("⚠️  Nenhum dado retornado. Verifique a conexão com a API.")

    dados_1m = filtrar_ultimo_minuto(todos)
    dados_5m = filtrar_ultimos_n_minutos(todos, minutos=5)

    html = HTML_TEMPLATE \
        .replace("__ALL_DATA__", json.dumps(formatar_para_js(todos))) \
        .replace("__DATA_1M__",  json.dumps(formatar_para_js(dados_1m))) \
        .replace("__DATA_5M__",  json.dumps(formatar_para_js(dados_5m)))

    caminho = os.path.abspath("dashboard_luminosidade.html")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Dashboard gerado: {caminho}")
    webbrowser.open(f"file://{caminho}")

if __name__ == "__main__":
    gerar_dashboard()
