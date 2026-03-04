# SSL 证书配置说明

## ✅ 已完成的配置

### 1. 生成自签名 SSL 证书

已为开发环境生成自签名 SSL 证书：
- 证书位置: `nginx/ssl/fullchain.pem`
- 私钥位置: `nginx/ssl/privkey.pem`
- 有效期: 365 天
- 证书信息: CN=localhost

### 2. Nginx 配置

Nginx 已配置为支持 HTTPS：
- HTTP 端口: 8080 (http://localhost:8080)
- HTTPS 端口: 8443 (https://localhost:8443)
- 自动 HTTP 到 HTTPS 重定向已启用

### 3. 当前服务状态

所有服务正常运行：
- ✅ Frontend: http://localhost:3000
- ✅ Backend: http://localhost:8000
- ✅ Nginx HTTP: http://localhost:8080
- ✅ Nginx HTTPS: https://localhost:8443
- ✅ PostgreSQL: localhost:5432
- ✅ Neo4j: localhost:7474 (Browser), localhost:7687 (Bolt)
- ✅ Redis: localhost:6379
- ✅ PgAdmin: http://localhost:5050

## 访问应用

### 开发环境（推荐）
直接访问服务，无需通过 Nginx：
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/v1

### 通过 Nginx（生产模式）
通过反向代理访问：
- HTTP: http://localhost:8080
- HTTPS: https://localhost:8443 （会显示证书警告，这是正常的）

## 浏览器证书警告

由于使用自签名证书，浏览器会显示安全警告。这在开发环境中是正常的。

### 如何继续访问：

**Chrome/Edge:**
1. 点击 "高级"
2. 点击 "继续前往 localhost (不安全)"

**Firefox:**
1. 点击 "高级"
2. 点击 "接受风险并继续"

## 生产环境配置

### 方案 1: Let's Encrypt (推荐)

使用 Certbot 获取免费的受信任 SSL 证书：

```bash
# 安装 Certbot
docker run -it --rm \
  -v "${PWD}/nginx/ssl:/etc/letsencrypt" \
  certbot/certbot certonly \
  --standalone \
  --email your-email@example.com \
  --agree-tos \
  -d your-domain.com

# 更新 nginx.conf 中的域名
# 将 your-domain.com 替换为实际域名
```

### 方案 2: 购买商业证书

1. 从证书颁发机构购买 SSL 证书
2. 将证书文件放置在 `nginx/ssl/` 目录
3. 更新 `nginx/nginx.conf` 中的证书路径

## 证书更新

### 自签名证书（开发环境）

证书有效期为 365 天，到期后重新生成：

```bash
docker run --rm -v "${PWD}/nginx/ssl:/certs" alpine/openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /certs/privkey.pem -out /certs/fullchain.pem -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

docker restart ai_review_nginx
```

### Let's Encrypt 证书（生产环境）

设置自动更新：

```bash
# 添加到 crontab
0 0 * * * docker run --rm -v "${PWD}/nginx/ssl:/etc/letsencrypt" certbot/certbot renew && docker restart ai_review_nginx
```

## 故障排除

### Nginx 无法启动

检查证书文件是否存在：
```bash
ls -la nginx/ssl/
```

查看 Nginx 日志：
```bash
docker logs ai_review_nginx
```

### 证书权限问题

确保证书文件有正确的权限：
```bash
chmod 644 nginx/ssl/fullchain.pem
chmod 600 nginx/ssl/privkey.pem
```

### 重启 Nginx

```bash
docker restart ai_review_nginx
```

## 安全建议

1. **开发环境**: 使用自签名证书即可
2. **生产环境**: 必须使用受信任的 SSL 证书（Let's Encrypt 或商业证书）
3. **私钥保护**: 确保 `privkey.pem` 文件权限为 600，不要提交到版本控制
4. **定期更新**: 在证书到期前更新证书
5. **强制 HTTPS**: 在生产环境中启用 HSTS 头（已在配置中启用）

## 相关文件

- `nginx/nginx.conf` - Nginx 主配置文件
- `nginx/ssl/fullchain.pem` - SSL 证书
- `nginx/ssl/privkey.pem` - SSL 私钥
- `docker-compose.yml` - Docker Compose 配置
- `.gitignore` - 确保私钥不被提交

## 注意事项

⚠️ **重要**: `nginx/ssl/privkey.pem` 已添加到 `.gitignore`，不会被提交到版本控制。
✅ 证书文件已通过 Docker volume 正确挂载到 Nginx 容器。
✅ HTTP/2 配置已更新为新的语法格式。
