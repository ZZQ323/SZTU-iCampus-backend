package cn.edu.sztui.common.util.jwt;

import cn.binarywang.wx.miniapp.bean.WxMaJscode2SessionResult;
import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import jakarta.annotation.PostConstruct;
import lombok.Data;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;
import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

/**
 * JWT 配置和工具类
 */
@Data
@Component
@ConfigurationProperties(prefix = "jwt.wxmini")
public class JwtConfig {

    private static final Logger log = LoggerFactory.getLogger(JwtConfig.class);

    /**
     * 密钥字符串（从配置文件读取）
     */
    private String secret;

    /**
     * 过期时间（秒）
     */
    private Long expire;

    /**
     * token 前缀
     */
    private String tokenPrefix;

    /**
     * 请求头名称
     */
    private String header;

    /**
     * 签名密钥
     */
    private SecretKey secretKey;

    /**
     * 初始化密钥
     */
    @PostConstruct
    public void init() {
        // 使用 HMAC-SHA256 算法，密钥至少需要 256 位
        this.secretKey = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
    }

    /**
     * 生成 Token
     *
     * @param  session    用户的会话信息
     * @return JWT token
     */
    public String generateToken(WxMaJscode2SessionResult session) {
        return generateToken(session, expire);
    }

    /**
     * 生成 Token（指定过期时间）
     *
     * @param  session    用户的会话信息
     * @param expireSeconds 过期时间（秒）
     * @return JWT token
     */
    public String generateToken(WxMaJscode2SessionResult session, long expireSeconds) {
        Date now = new Date();
        Date expireDate = new Date(now.getTime() + expireSeconds * 1000);
        // 可以在 claims 中放入更多信息
        Map<String, Object> claims = new HashMap<>();
        claims.put("openid", session.getOpenid());
        claims.put("unionid", session.getUnionid());
        claims.put("sessionkey", session.getSessionKey());

        return Jwts.builder()
                .setClaims(claims)
                .setSubject( session.getUnionid() )              // 主题（用户标识）
                .setIssuedAt(now)                               // 签发时间
                .setExpiration(expireDate)                      // 过期时间
                .signWith(secretKey, SignatureAlgorithm.HS256)  // 签名算法和密钥
                .compact();
    }

    /**
     * 解析 Token
     *
     * @param token JWT token
     * @return Claims
     * @throws JwtException 解析失败时抛出异常
     */
    public Claims parseToken(String token) {
        // 移除 Bearer 前缀
        if (token != null && token.startsWith(tokenPrefix)) {
            token = token.substring(tokenPrefix.length()).trim();
        }
        return Jwts.parserBuilder()
                .setSigningKey(secretKey)
                .build()
                .parseClaimsJws(token)
                .getBody();
    }

    /**
     * 验证 Token 是否有效
     *
     * @param token JWT token
     * @return 验证结果
     */
    public TokenValidationResult validateToken(String token) {
        try {
            Claims claims = parseToken(token);
            return TokenValidationResult.success(claims);
        } catch (ExpiredJwtException e) {
            log.warn("Token 已过期: {}", e.getMessage());
            return TokenValidationResult.expired();
        } catch (SignatureException e) {
            log.warn("Token 签名无效: {}", e.getMessage());
            return TokenValidationResult.invalid("签名无效");
        } catch (MalformedJwtException e) {
            log.warn("Token 格式错误: {}", e.getMessage());
            return TokenValidationResult.invalid("格式错误");
        } catch (Exception e) {
            log.warn("Token 验证失败: {}", e.getMessage());
            return TokenValidationResult.invalid("验证失败");
        }
    }

    /**
     * 从 Token 中获取 unionid（不验证是否过期）
     */
    public String getOpenidFromToken(String token) {
        try {
            // 移除 Bearer 前缀
            if (token != null && token.startsWith(tokenPrefix))
                token = token.substring(tokenPrefix.length()).trim();
            // 即使过期也能解析出 claims
            Claims claims = Jwts.parserBuilder()
                    .setSigningKey(secretKey)
                    .build()
                    .parseClaimsJws(token)
                    .getBody();
            return claims.getSubject();
        } catch (ExpiredJwtException e) {
            // 过期的 token 也能获取 openid
            return e.getClaims().getSubject();
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * 判断 Token 是否即将过期（剩余时间小于指定时间）
     *
     * @param token       JWT token
     * @param minSeconds  最小剩余时间（秒）
     * @return 是否即将过期
     */
    public boolean isTokenExpiringSoon(String token, long minSeconds) {
        try {
            Claims claims = parseToken(token);
            Date expiration = claims.getExpiration();
            long remainingTime = expiration.getTime() - System.currentTimeMillis();
            return remainingTime < minSeconds * 1000;
        } catch (Exception e) {
            return true;
        }
    }

    /**
     * Token 验证结果
     */
    public static class TokenValidationResult {
        private boolean valid;
        private boolean expired;
        private String message;
        private Claims claims;

        public static TokenValidationResult success(Claims claims) {
            TokenValidationResult result = new TokenValidationResult();
            result.valid = true;
            result.expired = false;
            result.claims = claims;
            return result;
        }

        public static TokenValidationResult expired() {
            TokenValidationResult result = new TokenValidationResult();
            result.valid = false;
            result.expired = true;
            result.message = "Token已过期";
            return result;
        }

        public static TokenValidationResult invalid(String message) {
            TokenValidationResult result = new TokenValidationResult();
            result.valid = false;
            result.expired = false;
            result.message = message;
            return result;
        }

        // Getter
        public boolean isValid() { return valid; }
        public boolean isExpired() { return expired; }
        public String getMessage() { return message; }
        public Claims getClaims() { return claims; }
    }
}
