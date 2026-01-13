package cn.edu.sztui.base.domain.model.proxy.client;

import lombok.extern.slf4j.Slf4j;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.config.Registry;
import org.apache.http.config.RegistryBuilder;
import org.apache.http.conn.socket.ConnectionSocketFactory;
import org.apache.http.conn.socket.PlainConnectionSocketFactory;
import org.apache.http.conn.ssl.NoopHostnameVerifier;
import org.apache.http.conn.ssl.SSLConnectionSocketFactory;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.impl.conn.PoolingHttpClientConnectionManager;
import org.springframework.stereotype.Component;
import javax.net.ssl.*;
import java.security.KeyManagementException;
import java.security.NoSuchAlgorithmException;
import java.security.cert.X509Certificate;
import java.util.Arrays;
import java.util.List;

@Slf4j
@Component
public class HttpClientFactory {

    private static final int TIMEOUT_SECONDS = 30;
    private static final int MAX_REDIRECTS = 15;

    /**
     * 创建默认客户端（启用重定向）
     */
    public CloseableHttpClient createDefaultClient() throws Exception {
        SSLConnectionSocketFactory sslSocketFactory = new SSLConnectionSocketFactory(
                createTrustAllSSLContext(),
                NoopHostnameVerifier.INSTANCE
        );

        Registry<ConnectionSocketFactory> socketFactoryRegistry =
                RegistryBuilder.<ConnectionSocketFactory>create()
                        .register("https", sslSocketFactory)
                        .register("http", PlainConnectionSocketFactory.getSocketFactory())
                        .build();

        PoolingHttpClientConnectionManager connectionManager =
                new PoolingHttpClientConnectionManager(socketFactoryRegistry);
        connectionManager.setMaxTotal(100);
        connectionManager.setDefaultMaxPerRoute(20);

        RequestConfig config = RequestConfig.custom()
                .setConnectTimeout(TIMEOUT_SECONDS * 1000)
                .setSocketTimeout(TIMEOUT_SECONDS * 1000)
                .setConnectionRequestTimeout(TIMEOUT_SECONDS * 1000)
                .setRedirectsEnabled(true)
                .setMaxRedirects(MAX_REDIRECTS)
                .setCircularRedirectsAllowed(false)
                .build();

        return HttpClients.custom()
                .setDefaultRequestConfig(config)
                .setConnectionManager(connectionManager)
                .disableCookieManagement()
                .build();
    }

    /**
     * 创建禁用重定向的客户端
     */
    public CloseableHttpClient createNoRedirectClient() throws Exception {
        // 1. 创建信任所有证书的 SSLContext
        SSLContext sslContext = createTrustAllSSLContext();

        // 2. 创建 SSL Socket Factory（不验证主机名）
        SSLConnectionSocketFactory sslSocketFactory = new SSLConnectionSocketFactory(
                sslContext,
                NoopHostnameVerifier.INSTANCE
        );
        // 3. 创建连接管理器
        Registry<ConnectionSocketFactory> socketFactoryRegistry =
                RegistryBuilder.<ConnectionSocketFactory>create()
                        .register("https", sslSocketFactory)
                        .register("http", PlainConnectionSocketFactory.getSocketFactory())
                        .build();

        PoolingHttpClientConnectionManager connectionManager =
                new PoolingHttpClientConnectionManager(socketFactoryRegistry);
        connectionManager.setMaxTotal(100);
        connectionManager.setDefaultMaxPerRoute(20);

        // 4. 创建请求配置（禁用重定向）
        RequestConfig requestConfig = RequestConfig.custom()
                .setConnectTimeout(TIMEOUT_SECONDS * 1000)
                .setSocketTimeout(TIMEOUT_SECONDS * 1000)
                .setConnectionRequestTimeout(TIMEOUT_SECONDS * 1000)
                .setRedirectsEnabled(false)
                .build();
        // 5. 创建客户端
        return HttpClients.custom()
                .setDefaultRequestConfig(requestConfig)
                .setConnectionManager(connectionManager)
                .disableCookieManagement()
                .build();
    }

    /**
     * 创建带学校域名验证的客户端
     */
    public CloseableHttpClient createSchoolTrustedClient() throws Exception {
        SSLContext sslContext = createTrustAllSSLContext();

        // 使用自定义的学校域名验证器
        SSLConnectionSocketFactory sslSocketFactory = new SSLConnectionSocketFactory(
                sslContext,
                new SchoolHostnameVerifier()
        );

        Registry<ConnectionSocketFactory> socketFactoryRegistry =
                RegistryBuilder.<ConnectionSocketFactory>create()
                        .register("https", sslSocketFactory)
                        .register("http", PlainConnectionSocketFactory.getSocketFactory())
                        .build();

        PoolingHttpClientConnectionManager connectionManager =
                new PoolingHttpClientConnectionManager(socketFactoryRegistry);
        connectionManager.setMaxTotal(100);
        connectionManager.setDefaultMaxPerRoute(20);

        RequestConfig requestConfig = RequestConfig.custom()
                .setConnectTimeout(TIMEOUT_SECONDS * 1000)
                .setSocketTimeout(TIMEOUT_SECONDS * 1000)
                .setConnectionRequestTimeout(TIMEOUT_SECONDS * 1000)
                .setRedirectsEnabled(false)
                .build();

        return HttpClients.custom()
                .setDefaultRequestConfig(requestConfig)
                .setConnectionManager(connectionManager)
                .disableCookieManagement()
                .build();
    }

    /**
     * 创建信任所有证书的 SSLContext
     */
    private SSLContext createTrustAllSSLContext() throws NoSuchAlgorithmException, KeyManagementException {
        TrustManager[] trustAllCerts = new TrustManager[]{
                new X509TrustManager() {
                    @Override
                    public X509Certificate[] getAcceptedIssuers() {
                        return new X509Certificate[0];
                    }

                    @Override
                    public void checkClientTrusted(X509Certificate[] certs, String authType) {
                        // 信任所有客户端证书
                    }

                    @Override
                    public void checkServerTrusted(X509Certificate[] certs, String authType) {
                        // 信任所有服务器证书
                    }
                }
        };

        SSLContext sslContext = SSLContext.getInstance("TLS");
        sslContext.init(null, trustAllCerts, new java.security.SecureRandom());
        return sslContext;
    }

    /**
     * 自定义学校域名验证器
     * 只信任学校相关的域名
     */
    private static class SchoolHostnameVerifier implements HostnameVerifier {
        private static final List<String> ALLOWED_DOMAINS = Arrays.asList(
                "sztu.edu.cn",
                "webvpn.sztu.edu.cn",
                "auth.sztu.edu.cn"
                // 添加其他信任的学校域名
        );

        @Override
        public boolean verify(String hostname, SSLSession session) {
            if (hostname == null) {
                log.warn("主机名为空，拒绝连接");
                return false;
            }

            boolean allowed = isHostAllowed(hostname);
            if (!allowed) {
                log.warn("主机名不被信任: {}", hostname);
            }
            return allowed;
        }

        private boolean isHostAllowed(String hostname) {
            for (String domain : ALLOWED_DOMAINS) {
                if (hostname.equals(domain) || hostname.endsWith("." + domain)) {
                    return true;
                }
            }
            return false;
        }
    }
}