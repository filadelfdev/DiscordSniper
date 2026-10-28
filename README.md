<div align="center">

```ansi
   ██████╗  ██████╗ ██╗  ██╗██╗   ██╗███╗   ██╗████████╗[0m
  ██╔═══██╗██╔════╝ ██║  ██║██║   ██║████╗  ██║╚══██╔══╝[0m
 ██║   ██║██║  ███╗███████║██║   ██║██╔██╗ ██║   ██║   [0m
  ██║   ██║██║   ██║██╔══██║██║   ██║██║╚██╗██║   ██║   [0m
 ╚██████╔╝╚██████╔╝██║  ██║╚██████╔╝██║ ╚████║   ██║   [0m
  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   [0m
```

<br>

![Python](https://img.shields.io/badge/Python-3.10%2B-blueviolet?style=for-the-badge&logo=python&logoColor=white&labelColor=0a0a0a)
![Workers](https://img.shields.io/badge/Workers-5000-9400D3?style=for-the-badge&labelColor=0a0a0a)
![TLS](https://img.shields.io/badge/TLS-JA3_Spoof-8A2BE2?style=for-the-badge&labelColor=0a0a0a)
![Platforms](https://img.shields.io/badge/Platforms-6-6A0DAD?style=for-the-badge&labelColor=0a0a0a)

<sub>by <strong>hz x ima1</strong> · discord: <strong>beijariamos</strong></sub>

<br>

[🇧🇷 Português](#-português) · [🇺🇸 English](#-english)

</div>

---

## 🇧🇷 Português

### 🎯 Plataformas

| Plataforma | Verificação | Auto-claim |
|---|---|---|
| <img src="https://cdn.simpleicons.org/discord/5865F2" width="16"/> Discord | API POMELO unique-username | ✅ token de usuário |
| <img src="https://cdn.simpleicons.org/roblox/ffffff" width="16"/> Roblox | Endpoint de validação de auth | ✅ cookie |
| <img src="https://cdn.simpleicons.org/tiktok/ffffff" width="16"/> TikTok | Probe de perfil | ❌ |
| <img src="https://cdn.simpleicons.org/instagram/E4405F" width="16"/> Instagram | Web profile API | ❌ |
| <img src="https://cdn.simpleicons.org/youtube/FF0000" width="16"/> YouTube | Probe de handle | ❌ |
| <img src="https://cdn.simpleicons.org/minecraft/62B47A" width="16"/> Minecraft | API Mojang | ✅ bearer token |

### ⚡ Funcionalidades

- **até 5.000 workers simultâneos** — snapshot de proxy lock-free, fila assíncrona de stdout, sem overhead de JSON/base64 no caminho quente
- **spoof de fingerprint TLS** via `tls_client` — rotação JA3 entre perfis Chrome, Firefox, Safari, Opera
- **pool de proxies inteligente** — rotação por request, cooldown em rate-limit sem matar o proxy, contador de falhas, verificação ao vivo contra cada plataforma
- **15 geradores de username** — só letras, leet, palíndromos, vogal-heavy, sufixo numérico, caos total e mais
- **auto-claim instantâneo** — Discord PATCH, Roblox CSRF claim, Minecraft PUT, dispara no momento do hit
- **notificações via webhook + bot** — embeds ricos, ping de cargo/usuário, totalmente configurável
- **modo wordlist** — traga sua própria lista `.txt` e sniped
- **controles de teclado** — `N` pausa/retoma, `Ctrl+C` para limpo
- **config persistente** — `oghunt_config.json` e `oghunt_proxies.json`

### 📦 Requisitos

```bash
Python 3.10+
pip install requests colorama urllib3 tls_client
```

> `tls_client` é opcional — sem ele usa adaptador SSL customizado de alta concorrência.

### 🚀 Como usar

```bash
python OGHunt.py
```

| Opção | Descrição |
|---|---|
| `[1] Gerar Nomes` | cria batch com padrão e tamanho escolhidos |
| `[2] Checar Nomes` | sniped batch gerado ou carregado |
| `[3] Gerar + Checar` | gera e sniped no mesmo fluxo |
| `[4] Checar Wordlist` | carrega qualquer `.txt` e sniped |

### 🌐 Setup de Proxies

```
ip:port
ip:port:user:pass
http://user:pass@ip:port
```

### 🔑 Tokens / Cookies

| Plataforma | O que você precisa | Onde configurar |
|---|---|---|
| Discord | token(s) de usuário | Gerenciador de Tokens |
| Roblox | cookie `.ROBLOSECURITY` | Config → Roblox Claim |
| Minecraft | bearer token | Config → Minecraft Claim |

### 💬 Quer um build em outra linguagem?

Go, Rust, C#, Node, qualquer uma — me chama no Discord: **`ima1`**

---

## 🇺🇸 English

### 🎯 Platforms

| Platform | Check method | Auto-claim |
|---|---|---|
| <img src="https://cdn.simpleicons.org/discord/5865F2" width="16"/> Discord | POMELO unique-username API | ✅ user token |
| <img src="https://cdn.simpleicons.org/roblox/ffffff" width="16"/> Roblox | Auth validation endpoint | ✅ cookie |
| <img src="https://cdn.simpleicons.org/tiktok/ffffff" width="16"/> TikTok | Profile page probe | ❌ |
| <img src="https://cdn.simpleicons.org/instagram/E4405F" width="16"/> Instagram | Web profile API | ❌ |
| <img src="https://cdn.simpleicons.org/youtube/FF0000" width="16"/> YouTube | Handle probe | ❌ |
| <img src="https://cdn.simpleicons.org/minecraft/62B47A" width="16"/> Minecraft | Mojang profile API | ✅ bearer token |

### ⚡ Features

- **up to 5,000 concurrent workers** — lock-free proxy snapshot, async stdout queue, zero hot-path JSON/base64 overhead
- **TLS fingerprint spoofing** via `tls_client` — JA3 rotation across Chrome, Firefox, Safari, Opera profiles
- **smart proxy pool** — per-request rotation, rate-limit cooldowns without killing the proxy, fail counter, live verification against each platform
- **15 username generators** — letters only, leet, palindromes, vowel-heavy, digit suffix, chaos mix and more
- **instant auto-claim** — Discord PATCH, Roblox CSRF claim, Minecraft PUT, fires the moment a hit lands
- **webhook + bot notifications** — rich embeds, role/user pings, fully configurable
- **wordlist mode** — bring your own `.txt` list and snipe it
- **keyboard controls** — `N` pause/resume, `Ctrl+C` clean stop
- **persistent config** — `oghunt_config.json` and `oghunt_proxies.json`

### 📦 Requirements

```bash
Python 3.10+
pip install requests colorama urllib3 tls_client
```

> `tls_client` is optional — falls back to a high-concurrency custom SSL cipher adapter.

### 🚀 Usage

```bash
python OGHunt.py
```

| Option | Description |
|---|---|
| `[1] Generate Names` | create a batch with chosen pattern and length |
| `[2] Check Names` | snipe a previously generated or loaded batch |
| `[3] Gen + Check` | generate then immediately snipe |
| `[4] Wordlist Check` | load any `.txt` wordlist and snipe it |

### 🌐 Proxy Setup

```
ip:port
ip:port:user:pass
http://user:pass@ip:port
```

### 🔑 Token / Cookie Setup

| Platform | What you need | Where to set it |
|---|---|---|
| Discord | user token(s) | Token Manager |
| Roblox | `.ROBLOSECURITY` cookie | Config → Roblox Claim |
| Minecraft | bearer token | Config → Minecraft Claim |

### 💬 Want a build in another language?

Go, Rust, C#, Node, whatever — hit me up on Discord: **`ima1`**

---

<div align="center">
<sub>by <strong>hz x uyp</strong> · discord: <strong>beijariamos</strong></sub>
</div>
