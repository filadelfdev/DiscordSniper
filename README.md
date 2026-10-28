<div align="center">

<strong>High-velocity multi-platform username sniper — up to 5,000 concurrent workers, TLS fingerprint spoofing, proxy rotation and auto-claim.</strong>

<br><br>

[🇧🇷 Português](#português) · [🇺🇸 English](#english)

</div>

---

<h2 id="português">🇧🇷 Português</h2>

<h3>Plataformas suportadas</h3>

| Plataforma | Método de verificação | Auto-claim |
|---|---|---|
| Discord | API POMELO unique-username | ✅ (token de usuário) |
| Roblox | Endpoint de validação de auth | ✅ (cookie) |
| TikTok | Probe de perfil | ❌ |
| Instagram | Web profile API | ❌ |
| YouTube | Probe de handle | ❌ |
| Minecraft | API de perfil Mojang | ✅ (bearer token) |

<h3>Funcionalidades</h3>

- Até **5.000 workers simultâneos** — snapshot de proxy lock-free, fila assíncrona de stdout, sem overhead de JSON/base64 no caminho quente
- **Spoof de fingerprint TLS** via `tls_client` — rotação JA3 entre perfis Chrome, Firefox, Safari, Opera
- **Pool de proxies inteligente** — rotação por request, cooldown em rate-limit sem matar o proxy, contador de falhas, verificação ao vivo contra cada plataforma antes de snipear
- **15 geradores de username** — só letras, leet, palíndromos, vogal-heavy, sufixo numérico, caos total e mais
- **Auto-claim** dispara no momento que o hit é detectado — Discord PATCH, Roblox CSRF claim, Minecraft PUT
- **Notificações via Webhook + Bot** — embeds ricos, ping de cargo/usuário, totalmente configurável
- **Modo Wordlist** — traga sua própria lista e sniped
- **Controles de teclado** — `N` para pausar/retomar durante a sessão, `Ctrl+C` para parar
- **Config persistente** — tudo salvo em `oghunt_config.json`, proxies em `oghunt_proxies.json`

<h3>Requisitos</h3>

```
Python 3.10+
pip install requests colorama urllib3 tls_client
```

`tls_client` é opcional mas recomendado — se não instalado, cai no adaptador SSL customizado.

<h3>Como usar</h3>

```bash
python OGHunt.py
```

No dashboard, escolha a plataforma, configure proxies e tokens, depois escolha um dos quatro fluxos:

1. **Gerar nomes** — cria um batch com padrão e tamanho escolhidos
2. **Checar nomes** — sniped um batch gerado ou carregado
3. **Gerar + checar** — gera e sniped no mesmo fluxo
4. **Checar wordlist** — carrega qualquer `.txt` e sniped

<h3>Setup de proxies</h3>

Jogue seus proxies no `oghunt_proxies.json` em qualquer um desses formatos:

```
ip:port
ip:port:user:pass
http://user:pass@ip:port
```

Ou cole direto pelo Gerenciador de Proxies dentro da ferramenta. Sempre verifique contra a plataforma alvo antes da sessão.

<h3>Setup de tokens / cookies</h3>

| Plataforma | O que você precisa | Onde configurar |
|---|---|---|
| Discord | Token(s) de usuário | Gerenciador de Tokens → Adicionar |
| Roblox | Cookie `.ROBLOSECURITY` | Config → Roblox Claim |
| Minecraft | Bearer token | Config → Minecraft Claim |

<h3>Quer um build em outra linguagem?</h3>

Se quiser seu próprio sniper em outra linguagem — Go, Rust, C#, Node, qualquer uma — me chama no Discord:

**`ima1`**

---

<h2 id="english">🇺🇸 English</h2>

<h3>Supported platforms</h3>

| Platform | Check method | Auto-claim |
|---|---|---|
| Discord | POMELO unique-username API | ✅ (user token) |
| Roblox | Auth validation endpoint | ✅ (cookie) |
| TikTok | Profile page probe | ❌ |
| Instagram | Web profile API | ❌ |
| YouTube | Handle probe | ❌ |
| Minecraft | Mojang profile API | ✅ (bearer token) |

<h3>Features</h3>

- Up to **5,000 concurrent workers** — lock-free proxy snapshot, async stdout queue, zero hot-path JSON/base64 overhead
- **TLS fingerprint spoofing** via `tls_client` — JA3 rotation across Chrome, Firefox, Safari, Opera profiles
- **Smart proxy pool** — per-request rotation, rate-limit cooldowns without killing the proxy, fail counter, live verification against each platform before sniping
- **15 username generators** — letters only, leet, palindromes, vowel-heavy, digit suffix, chaos mix and more
- **Auto-claim** fires the moment a hit lands — Discord PATCH, Roblox CSRF claim, Minecraft PUT
- **Webhook + Bot notifications** — rich embeds, role/user pings, fully configurable
- **Wordlist mode** — bring your own list and snipe it
- **Keyboard controls** — `N` to pause/resume mid-session, `Ctrl+C` to stop
- **Persistent config** — all settings saved to `oghunt_config.json`, proxies to `oghunt_proxies.json`

<h3>Requirements</h3>

```
Python 3.10+
pip install requests colorama urllib3 tls_client
```

`tls_client` is optional but recommended — falls back to a custom SSL cipher adapter if not installed.

<h3>Usage</h3>

```bash
python OGHunt.py
```

From the dashboard, pick your platform, configure proxies and tokens, then choose one of the four workflows:

1. **Generate Names** — create a username batch with a chosen pattern and length
2. **Check Names** — snipe a previously generated or loaded batch
3. **Gen + Check** — generate then immediately snipe in one flow
4. **Wordlist Check** — load any `.txt` wordlist and snipe it

<h3>Proxy setup</h3>

Drop your proxies into `oghunt_proxies.json` in any of these formats:

```
ip:port
ip:port:user:pass
http://user:pass@ip:port
```

Or paste them directly from the Proxy Manager inside the tool. Always verify against the target platform before a session.

<h3>Token / cookie setup</h3>

| Platform | What you need | Where to set it |
|---|---|---|
| Discord | User token(s) | Token Manager → Add |
| Roblox | `.ROBLOSECURITY` cookie | Config → Roblox Claim |
| Minecraft | Bearer token | Config → Minecraft Claim |

<h3>Want a build in another language?</h3>

If you want your own sniper built in a different language — Go, Rust, C#, Node, whatever — hit me up on Discord:

**`ima1`**

---

<div align="center">
<sub>by hz x uyp · discord: beijariamos</sub>
</div>
