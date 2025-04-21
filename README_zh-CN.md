# sms-forward Webhook 服务端

一个简单的 Python Flask webhook 服务端，用于接收来自 SmsForwarder 等应用的短信转发消息，将其存储在 SQLite 数据库中，并提供一个带有身份认证和前端解密功能的 Web 界面来查看接收到的消息。

`Thanks Gemini 2.5 pro.`

## 功能特性

*   接收包含短信或通知数据的 webhook 请求（POST, GET, PUT, PATCH）。
*   将接收到的消息存储在本地 SQLite 数据库 (`sms_webhook.db`) 中。
*   提供一个 Web 界面 (`/`) 用于查看历史消息。
*   Web 界面受用户名/密码会话认证保护。
*   在 Web 界面上显示的消息在存储时是加密的，并在浏览器中使用用户提供的密钥进行解密。
*   支持使用可配置的密钥对传入的 webhook 请求进行签名验证。

## 环境要求

*   Python 3.8+ (已在 3.13.2 上测试)
*   Flask
*   Flask-Session (虽然使用了基本的 session，但 Flask 内置的 session 需要一个 secret key)
*   `cryptography` 库用于 AES 和 HMAC
*   `requests` (如果您计划添加出站转发功能，目前尚未实现)

## 安装

1.  克隆仓库：
    ```bash
    git clone https://github.com/a2102107/sms-forward-webhook-server.git
    cd sms-webhook
    ```
2.  使用 pip 安装依赖：
    ```bash
    pip install Flask cryptography
    ```
    *(注意：使用了 Flask 内置的 session，需要一个 secret key。对于当前实现，`Flask-Session` 不是必需的，但对于更高级的 session 管理可能有用。)*

## 配置

编辑 `config.py` 文件来配置您的服务端：

*   `DATABASE_PATH`: SQLite 数据库文件路径 (默认: `sms_webhook.db`)。
*   `SECRET_KEY`: 用于验证传入 webhook 签名的密钥 (与 SmsForwarder 中的 `secret` 设置匹配)。设置为 `None` 可禁用签名验证。
*   `WEBHOOK_PATH`: 服务端监听传入 webhook 的 URL 路径 (默认: `/webhook`)。
*   `FLASK_SECRET_KEY`: Flask session 的密钥。**请将其更改为一个随机的、强密钥。**
*   `WEB_USERNAME`: Web 界面登录用户名 (默认: `admin`)。**在生产环境中请更改此项。**
*   `WEB_PASSWORD`: Web 界面登录密码 (默认: `password`)。**在生产环境中请将其更改为一个强密码。**
*   `BASE_DECRYPTION_STRING`: 用于派生消息加密/解密所需的 AES 和 HMAC 密钥的基础字符串。**请将其更改为一个安全的、唯一的字符串。** 这个字符串将是您在 Web 界面中输入的“解密密钥”。

## 运行服务端

运行 `app.py` 文件：

```bash
py app.py
```

服务端将默认启动并监听 `http://0.0.0.0:5000/`。

## 使用说明

### Webhook 端点

配置您的短信转发应用（如 SmsForwarder）向 `http://您的服务器IP:5000/webhook`（或您在 `WEBHOOK_PATH` 中配置的路径）发送 POST, GET, PUT 或 PATCH 请求。有关请求格式和签名验证的详细信息，请参阅 SmsForwarder 的 wiki。

### Web 界面

1.  打开您的 Web 浏览器，访问 `http://您的服务器IP:5000/`。
2.  您将被重定向到登录页面。输入在 `config.py` 中配置的 `WEB_USERNAME` 和 `WEB_PASSWORD`。
3.  登录后，您将看到消息页面。消息最初将显示为加密状态。
4.  在“解密密钥”输入框中输入您在 `config.py` 中配置的 `BASE_DECRYPTION_STRING`，然后点击“解密消息”。
5.  如果密钥正确，消息将被解密并显示。密钥将存储在您浏览器的 `sessionStorage` 中，以便在同一会话中后续页面加载时自动解密。

## 安全注意事项

*   **前端解密（HTTP 的折衷方案）：** 在浏览器中解密消息是作为使用 HTTP（而非推荐的 HTTPS）时的一种折衷方案实现的。这意味着解密逻辑和密钥派生方法暴露在前端 JavaScript 代码中。虽然 `BASE_DECRYPTION_STRING` 本身不直接在 JS 中，但从它派生 AES/HMAC 密钥的方法是暴露的。在不受信任的环境中，**不建议将此方法用于敏感数据**。
*   **更改默认凭据和密钥：** 在部署到生产环境之前，务必更改 `config.py` 中的默认 `FLASK_SECRET_KEY`、`WEB_USERNAME`、`WEB_PASSWORD` 和 `BASE_DECRYPTION_STRING`。
*   **HTTPS：** 对于生产环境使用，强烈建议将此服务端部署在反向代理（如 Nginx 或 Caddy）后面，并使用 HTTPS 来加密客户端和服务端之间的通信。HTTPS 提供传输过程中的加密，保护登录凭据和加密的消息数据免遭窃听。

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。