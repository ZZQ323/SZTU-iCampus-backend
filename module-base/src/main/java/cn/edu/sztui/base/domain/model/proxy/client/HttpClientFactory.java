package cn.edu.sztui.base.domain.model.proxy.client;

import lombok.extern.slf4j.Slf4j;
import org.apache.hc.client5.http.config.RequestConfig;
import org.apache.hc.client5.http.impl.classic.*;
import org.apache.hc.client5.http.impl.io.PoolingHttpClientConnectionManagerBuilder;
import org.apache.hc.client5.http.ssl.SSLConnectionSocketFactoryBuilder;
import org.apache.hc.core5.ssl.SSLContextBuilder;
import org.springframework.stereotype.Component;
import javax.net.ssl.*;
import java.util.concurrent.TimeUnit;

@Slf4j
@Component
public class HttpClientFactory {

    private static final int TIMEOUT_SECONDS = 30;
    private static final int MAX_REDIRECTS = 15;

    public CloseableHttpClient createDefaultClient() throws Exception {
        RequestConfig config = RequestConfig.custom()
                .setConnectTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
                .setResponseTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
                .setRedirectsEnabled(true)
                .setMaxRedirects(MAX_REDIRECTS)
                .setCircularRedirectsAllowed(false)
                .build();

        return HttpClients.custom()
                .setDefaultRequestConfig(config)
                .disableCookieManagement()
                .build();
    }

    public CloseableHttpClient createNoRedirectClient() throws Exception {
        SSLContext sslContext = createTrustAllSSLContext();
        HostnameVerifier hostnameVerifier = createSchoolHostnameVerifier();

        RequestConfig config = RequestConfig.custom()
                .setConnectTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
                .setResponseTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
                .setRedirectsEnabled(false)
                .build();

        return HttpClients.custom()
                .setDefaultRequestConfig(config)
                .setConnectionManager(PoolingHttpClientConnectionManagerBuilder.create()
                        .setSSLSocketFactory(SSLConnectionSocketFactoryBuilder.create()
                                .setSslContext(sslContext)
                                .setHostnameVerifier(hostnameVerifier)
                                .build())
                        .build())
                .disableCookieManagement()
                .build();
    }

    private SSLContext createTrustAllSSLContext() throws Exception {
        return SSLContextBuilder.create()
                .loadTrustMaterial(null, (chain, authType) -> true)
                .build();
    }

    private HostnameVerifier createSchoolHostnameVerifier() {
        return (hostname, session) -> {
            if (hostname.endsWith("webvpn.sztu.edu.cn") || hostname.endsWith("sztu.edu.cn")) {
                return true;
            }
            return HttpsURLConnection.getDefaultHostnameVerifier().verify(hostname, session);
        };
    }
}
