<div align="center">

# ✨ Purpurine Smart Lamp ✨
### *PWA para controle de lâmpada via MQTT (WebSocket)*

![Versão](https://img.shields.io/badge/vers%C3%A3o-1.0-blue)
![PWA](https://img.shields.io/badge/PWA-standalone-5A7A8A)
![MQTT](https://img.shields.io/badge/MQTT-mqtt.js-7A5A9A)
![Status](https://img.shields.io/badge/status-prot%C3%B3tipo-yellow)

</div>

---

## 📋 Índice
- [Documentação](#-documentação)
- [Aplicativo (PWA)](#-aplicativo-pwa)
- [Sobre o Projeto](#-sobre-o-projeto)
- [Características](#-características)
- [Hardware (Dispositivo IoT)](#-hardware-dispositivo-iot)
- [Firmware (ESP32 / Wokwi)](#-firmware-esp32--wokwi)
- [Arquitetura do Software](#-arquitetura-do-software)
- [Modos de Operação](#-modos-de-operação)
- [Interface e Navegação](#-interface-e-navegação)
- [Instalação e Execução](#-instalação-e-execução)
- [Comunicação MQTT](#-comunicação-mqtt)
- [Troubleshooting](#-troubleshooting)
- [Créditos](#-créditos)

---

## 📚 Documentação

Este repositório contém uma aplicação Web (PWA) simples e portátil para controle de uma lâmpada inteligente através de **MQTT via WebSocket**.

Arquivos principais:
- `index.html` — interface, lógica do controle e conexão MQTT.
- `manifest.json` — manifesto PWA (nome, cores, ícone).
- `sw.js` — Service Worker (cache básico para funcionamento offline do shell).

---

## 📱 Aplicativo (PWA)

O app roda direto no navegador e pode ser instalado como aplicativo (modo *standalone*):
- Funciona em Android/Chrome, Windows/Edge e navegadores compatíveis com PWA.
- Possui **tema claro/escuro**, **pop-up de instruções** e **pop-up de acessibilidade**.
- Exibe **status online/off** do MQTT e **luminosidade do sensor** em tempo real.

---

## 🎯 Sobre o Projeto

A **Purpurine Smart Lamp** é uma interface de controle para uma lâmpada IoT. Ela publica comandos no broker MQTT e escuta um tópico de sensor para atualizar a interface.

O objetivo é oferecer uma experiência agradável e acessível para:
- trocar **modos** de iluminação
- escolher **cor personalizada (RGB)**
- ajustar **brilho (0–100%)**
- acompanhar a **luminosidade do ambiente** (sensor)

<div align="center">

```mermaid
graph LR
	A[Navegador / PWA\nindex.html + mqtt.js] -->|MQTT over WebSocket\nsetMode / setRGB / setBrightness| B[(Broker MQTT)]
	C[Dispositivo IoT\ncontrolador da lâmpada] -->|Publica sensor| B
	B -->|/TEF/lamp001/attrs/l\n(luminosidade %)| A
	B -->|/TEF/lamp001/cmd\n(comandos)| C
```

</div>

---

## ✨ Características

| Recurso | Descrição |
|--------|-----------|
| 🎮 **6 modos** | Automático, Relaxar, Foco, Personalizado, Balada, Alívio Sensorial |
| 🎨 **Cor personalizada (RGB)** | Envia `setRGB|r,g,b` a partir do seletor de cor |
| 🔆 **Controle de brilho** | Slider 0–100% com envio de `setBrightness|N` |
| 📡 **Status MQTT** | Badge `online/off` conforme conexão com o broker |
| 💡 **Sensor de luminosidade** | Leitura em tempo real do tópico do sensor (0–100%) |
| 🌗 **Tema claro/escuro** | Preferência persistida no `localStorage` |
| 🧩 **PWA** | Manifesto + Service Worker para cache básico |

---

## 🛠️ Hardware (Dispositivo IoT)

Este repositório é **a camada de interface (front-end)**. Do lado do hardware/firmware você precisa de um dispositivo que:

- Conecte ao mesmo broker MQTT.
- **Assine** o tópico de comandos.
- **Publique** a luminosidade do sensor.

Requisitos mínimos sugeridos:
- Microcontrolador com Wi‑Fi (ex.: ESP32 / ESP8266 / outro com stack MQTT).
- Atuador de iluminação (LED RGB, fita RGB, lâmpada com driver, etc.).
- Sensor de luminosidade (ex.: LDR + divisor resistivo), convertido para escala 0–100.

---

## 🔌 Firmware (ESP32 / Wokwi)

O firmware (simulado no Wokwi) implementa a lógica da lâmpada e dos sensores, consumindo os comandos que a PWA publica e reportando a luminosidade.

### Componentes/sensores usados

| Item | Função | Observação |
|------|--------|-----------|
| LED RGB | Iluminação (R/G/B) | PWM para cor e brilho |
| LDR | Luminosidade ambiente | Leitura analógica e mapeamento para 0–100 |
| HC-SR04 | Presença/proximidade | Presença mantém a lâmpada ativa no modo Automático |
| Microfone (ADC) | Detecção de palmas | 3 palmas alterna liga/desliga |
| Botão | Liga/desliga | Debounce de ~200ms |

### Pinagem (conforme o código do Wokwi)

| Sinal | Pino |
|------:|:----:|
| R | 25 |
| G | 26 |
| B | 27 |
| LDR (ADC) | 34 |
| Ultrassom TRIG | 5 |
| Ultrassom ECHO | 18 |
| Microfone (ADC) | 32 |
| Botão | 4 |

### Broker e rede (atenção)

No código do Wokwi/ESP32 existe uma configuração de broker **MQTT TCP** (porta 1883) e Wi‑Fi (SSID/senha). Por segurança:
- não publique SSID/senha reais em repositórios públicos
- use placeholders e/ou variáveis de ambiente quando possível

Além disso, observe que:
- a PWA está configurada para **MQTT via WebSocket** (`BROKER_URL` no `index.html`)
- o ESP32 está configurado para **MQTT TCP** (`default_BROKER_MQTT` no firmware)

Para o sistema funcionar ponta-a-ponta, ambos precisam apontar para o **mesmo broker lógico** (um broker que ofereça TCP 1883 e/ou uma ponte WebSocket 9001/8083/… para o mesmo backend).

---

---

## 🏗️ Arquitetura do Software

### Conexão MQTT

Parâmetros usados no `index.html`:
- Broker: `ws://54.198.188.2:9001`
- Tópico de comandos: `/TEF/lamp001/cmd`
- Tópico do sensor: `/TEF/lamp001/attrs/l`

O app usa `mqtt.js` e:
- tenta reconectar a cada ~3s (`reconnectPeriod: 3000`)
- ao conectar, faz subscribe no tópico do sensor
- reenvia estado atual (modo, cor e brilho) após ~500ms

### Cache (Service Worker)

O `sw.js` faz cache do *app shell*:
- `./`
- `./index.html`

Isso ajuda a abrir o app mesmo com conectividade limitada, mas **não garante** operação completa sem internet (a conexão ao broker ainda depende de rede).

---

## 🎮 Modos de Operação

Os botões da interface enviam um modo numérico (`setMode|N`). A lógica de cada modo é implementada no **dispositivo IoT** (firmware).

| Modo | Código | Ícone | Observação |
|:----:|:-----:|:-----:|-----------|
| Automático | 1 | 🤖 | Comportamento automático definido no firmware |
| Relaxar | 2 | 🌙 | Ambiente suave |
| Foco | 3 | 🎯 | Iluminação para concentração |
| Personalizado | 4 | 🎨 | Seleção de cor (RGB) + brilho |
| Balada | 5 | 🪩 | Efeitos / transições definidos no firmware |
| Alívio Sensorial | 6 | 💆 | Perfil confortável / baixa estimulação |

Nota: ao escolher uma cor no seletor, o app força o modo **Personalizado (4)** automaticamente.

---

## 🖥️ Interface e Navegação

### Componentes principais

- **Cartão “Modos de operação”**: seleciona um modo e destaca o botão ativo.
- **Cartão “Cor personalizada”**: mostra HEX/RGB e envia a cor ao dispositivo.
- **Cartão “Intensidade da luz”**: slider com feedback numérico e ícone por faixa.
- **Cartão “Luminosidade do sensor”**: valor percentual e barra de progresso.

### Ações no topo (fixas)

- 🌙/☀️ Alterna tema (salvo em `localStorage` como `purpurine-theme`).
- ℹ️ Mostra “Sobre acessibilidade”.
- 📖 Mostra “Instruções de uso”.

---

## 🔧 Instalação e Execução

### 1) Pré-requisitos

- Um navegador moderno (Chrome/Edge/Firefox).
- Servir os arquivos via **servidor local** (evite abrir por `file://` para não limitar recursos do PWA/Service Worker).

### 2) Rodando localmente

Opção B — VS Code Live Server:
- Instale a extensão “Live Server”
- Clique em “Go Live” e abra no navegador

### 3) Ajustando broker/tópicos

Se você precisar apontar para outro broker ou mudar o ID do dispositivo, edite no `index.html`:

```js
const BROKER_URL = "ws://54.198.188.2:9001";
const TOPIC_CMD = "/TEF/lamp001/cmd";
const TOPIC_SENSOR = "/TEF/lamp001/attrs/l";
```

---

## 📡 Comunicação MQTT

### Tópicos

| Tipo | Tópico | Direção |
|------|--------|---------|
| Comandos | `/TEF/lamp001/cmd` | PWA ➜ Dispositivo |
| Sensor (luminosidade) | `/TEF/lamp001/attrs/l` | Dispositivo ➜ PWA |

No firmware (Wokwi/ESP32), também é publicado:
- `/TEF/lamp001/attrs` com payload no formato `l|<valor>`

### Payloads (strings)

| Ação | Payload | Exemplo |
|------|--------|---------|
| Definir modo | `setMode|N` | `setMode|4` |
| Definir cor RGB | `setRGB|r,g,b` | `setRGB|212,200,222` |
| Definir brilho | `setBrightness|N` | `setBrightness|80` |

### Sensor de luminosidade

O app espera receber no tópico do sensor (`/TEF/lamp001/attrs/l`) um valor interpretável como inteiro (0–100). No firmware, esse valor é publicado a cada ~3s.

Ele é exibido como:
- número (ex.: `45`)
- barra de progresso (largura em %)

---

## 🔍 Troubleshooting

<details>
<summary>📡 Status fica sempre “off”</summary>

- Verifique se o broker `ws://54.198.188.2:9001` está acessível.
- Confira firewall/rede.
- Abra o console do navegador (F12) para ver logs de conexão.
</details>

<details>
<summary>🔒 Página em HTTPS e broker em WS (conteúdo misto)</summary>

Se você hospedar a página em `https://`, o navegador pode bloquear `ws://` (inseguro). Soluções:
- rode localmente em `http://localhost` (localhost é contexto seguro para PWA, mas evita mixed content com WS), ou
- mude o broker para `wss://...` (WebSocket seguro), ou
- hospede a página em `http://` em um ambiente controlado.
</details>

<details>
<summary>🧠 Alterei arquivos e não atualiza (cache do Service Worker)</summary>

- Faça hard refresh (Ctrl+F5).
- Ou abra DevTools → Application → Service Workers → “Unregister” e recarregue.
- O `sw.js` atual cacheia `./` e `./index.html`.
</details>

<details>
<summary>🖼️ Ícone do PWA não aparece</summary>

O `manifest.json` referencia `icon.png`. Garanta que o arquivo exista no root do projeto ou atualize o manifesto.
</details>

<details>
<summary>🔤 Fontes não carregam</summary>

Se as fontes Google não carregarem, verifique a URL do `<link>` no `index.html` e se há conectividade.
</details>

---

## 👥 Créditos

<div align="center">

### Glitter Computer & CO. — Purpurine

| Membros |
|--------|
| **Ana Lara Dellacorte Simões** |
| **Eláine Gomes Moreira** |
| **Joyce da Costa Peres** |
| **Rayssa Alves André** |

</div>

---

<div align="center">

**✨ Desenvolvido para automação e conforto ✨**

[⬆ Voltar ao topo](#-índice)

</div>