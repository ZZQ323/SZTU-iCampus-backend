# SZTU-iCampus 登录验证流程完整文档

## 📋 概述

本文档详细说明了SZTU-iCampus微信小程序的登录验证机制，包括token管理、openid处理、权限验证等核心流程。

## 🎯 登录方式支持

### 1. 微信一键登录 ⭐️ 
- **核心机制**：微信code → openid → 用户绑定检查 → JWT Token
- **数据存储**：`persons.wechat_openid`, `persons.wechat_session_key`
- **用户体验**：一键登录，无需记住密码

### 2. 账号密码登录
- **核心机制**：学号/工号 + 密码 → 数据库验证 → JWT Token  
- **安全措施**：SHA-256+盐值哈希、登录次数限制
- **适用场景**：传统认证方式，不依赖微信平台

### 3. 体验模式
- **核心机制**：临时身份 → 受限权限Token
- **功能限制**：仅能访问公开功能
- **使用场景**：无需注册的功能体验

---

## 🔐 微信登录详细流程

### 时序图
```
小程序 ----wx.login()----> 微信服务器
小程序 <---返回code------ 微信服务器
小程序 ----code--------> Backend胶水层
Backend ----code------> 微信API
Backend <--openid------ 微信API  
Backend ----查询openid--> Data-Service
Backend <--用户信息---- Data-Service
Backend ----JWT Token-> 小程序
小程序 ----本地存储----> LocalStorage
```

### 关键代码实现

#### 前端：获取微信code
```javascript
// miniprogram/pages/login/login.js
async onWechatLogin() {
  // 🔑 步骤1：获取微信临时凭证
  const loginRes = await new Promise((resolve, reject) => {
    wx.login({
      success: resolve,
      fail: reject
    })
  })
  
  const wechatCode = loginRes.code // 5分钟有效期
  
  // 🔍 步骤2：检查绑定状态
  const checkRes = await this.checkWechatBinding(wechatCode)
  
  if (checkRes.is_bound) {
    // 已绑定 → 直接登录
    await this.loginWithWechatCode(wechatCode)
  } else {
    // 未绑定 → 显示绑定界面
    this.setData({ wechatLoginStep: 'bind' })
  }
}
```

#### 后端：微信认证处理
```python
# backend/app/api/v1/endpoints/auth.py
@router.post("/wechat/login")
async def wechat_login(request: WeChatLoginRequest):
    """微信登录处理"""
    # 🔑 code换取openid
    wechat_info = await wechat_client.get_session_info(request.code)
    openid = wechat_info.get("openid")
    
    # 🔍 查询绑定用户
    user_data = await http_client.get_person_by_openid(openid)
    
    # 🎟️ 生成JWT Token
    token = create_access_token(
        data={
            "sub": user_data["person_id"],
            "person_type": user_data["person_type"],
            "login_method": "wechat"
        }
    )
    
    return {
        "access_token": token,
        "user": user_data
    }
```

---

## 🎫 JWT Token管理机制

### Token结构设计
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "P2025063441",        // 用户ID
    "person_type": "student",    // 用户类型  
    "login_method": "wechat",    // 登录方式
    "iat": 1703980800,          // 签发时间
    "exp": 1704067200           // 过期时间(7天)
  },
  "signature": "..."
}
```

### Token生成代码
```python
# backend/app/core/security.py
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None):
    """创建JWT访问令牌"""
    to_encode = data.copy()
    
    # ⏰ 设置7天过期时间
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    # 🔐 HS256算法签名
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    """验证JWT令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token已过期")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token无效")
```

### 前端Token使用
```javascript
// miniprogram/utils/api.js  
static async request(url, options = {}) {
  const token = wx.getStorageSync('token')
  
  // 🎫 添加Authorization头
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  }
  
  return wx.request({
    url: `${BASE_URL}${url}`,
    header: headers,
    ...options,
    success: (response) => {
      // 🔄 处理Token过期
      if (response.statusCode === 401) {
        this.handleTokenExpired()
      }
    }
  })
}

// Token过期处理
static handleTokenExpired() {
  wx.removeStorageSync('token')
  wx.removeStorageSync('userInfo')
  wx.navigateTo({ url: '/pages/login/login' })
}
```

---

## 💾 用户状态存储管理

### 本地存储结构
```javascript
// LocalStorage存储内容
{
  "token": "eyJhbGciOiJIUzI1NiIs...",  // JWT访问令牌
  "userInfo": {                        // 用户信息缓存
    "person_id": "P2025063441",
    "name": "张三",  
    "person_type": "student",
    "student_id": "202100000001",
    "college_name": "计算机学院",
    "major_name": "软件工程",
    "wechat_bound": true
  }
}
```

### 全局状态管理
```javascript
// miniprogram/app.js
App({
  globalData: {
    userInfo: null,                    // 全局用户信息
    baseURL: 'http://localhost:8000'   // API基础地址
  },
  
  onLaunch() {
    // 🚀 应用启动时恢复登录状态
    this.restoreLoginState()
  },
  
  restoreLoginState() {
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')
    
    if (token && userInfo) {
      // 📋 恢复到全局状态
      this.globalData.userInfo = userInfo
      
      // 🔍 验证token有效性(可选)
      this.validateTokenIfNeeded(token)
    }
  }
})
```

---

## 🔒 权限验证系统

### 权限矩阵设计
```python
# backend/app/api/deps.py
def get_user_permissions(person_type: str) -> Dict[str, list]:
    """角色权限矩阵"""
    return {
        "student": {
            "read": ["own_data", "own_schedule", "own_grades", "public_announcements"],
            "write": ["own_profile", "course_evaluation"],
            "share": ["schedule", "contact_info"]
        },
        "teacher": {
            "read": ["own_data", "student_grades", "course_schedules"],
            "write": ["student_grades", "course_content", "announcements"],
            "share": ["course_materials", "grades"]
        },
        "admin": {
            "read": ["*"],    # 全部读权限
            "write": ["*"],   # 全部写权限
            "share": ["*"]    # 全部分享权限
        }
    }
```

### 依赖注入认证
```python
# backend/app/api/deps.py
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> Dict[str, Any]:
    """获取当前认证用户"""
    
    # 🔐 验证JWT Token
    payload = security.verify_token(credentials.credentials)
    user_id = payload.get("sub")
    
    # 🔍 查询最新用户信息
    user_data = await http_client.get_person_by_id(user_id)
    if not user_data:
        raise HTTPException(status_code=401, detail="用户不存在")
    
    # 🚫 检查账户状态
    if user_data.get("account_locked"):
        raise HTTPException(status_code=423, detail="账户已被锁定")
    
    # 📋 构建用户对象
    return {
        "person_id": user_data["person_id"],
        "person_type": user_data["person_type"],
        "permissions": get_user_permissions(user_data["person_type"]),
        # ... 其他字段
    }

# 可选认证(支持公开访问)
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security_scheme)
) -> Optional[Dict[str, Any]]:
    """可选用户认证 - 不抛出错误"""
    if not credentials:
        return None
    try:
        return await get_current_user(credentials)
    except:
        return None  # 认证失败返回None而非抛出异常
```

### API权限控制示例
```python
# 公开接口
@router.get("/announcements")
async def get_announcements(
    current_user: Optional[Dict] = Depends(get_optional_user)
):
    """公告列表 - 支持公开访问"""
    # current_user可能为None
    
# 需要认证的接口  
@router.get("/grades")
async def get_grades(current_user: Dict = Depends(get_current_user)):
    """成绩查询 - 需要登录"""
    # current_user保证存在

# 需要管理员权限
@router.post("/announcements") 
async def create_announcement(current_user: Dict = Depends(require_admin)):
    """创建公告 - 需要管理员权限"""
    # current_user保证是管理员
```

---

## 🏃‍♂️ 登录状态保持机制

### 应用启动检查
```javascript
// miniprogram/pages/login/login.js
onLoad() {
  this.checkExistingLogin()
}

checkExistingLogin() {
  const token = wx.getStorageSync('token')
  const userInfo = wx.getStorageSync('userInfo')
  
  if (token && userInfo) {
    // 💬 提示已登录
    wx.showModal({
      title: '已登录',
      content: `您已登录为 ${userInfo.name}，是否重新登录？`,
      success: (res) => {
        if (!res.confirm) {
          wx.navigateBack() // 返回上一页
        }
      }
    })
  }
}
```

### 自动登录保持
```javascript
// 页面需要登录时的处理
function requireLogin(callback) {
  const token = wx.getStorageSync('token')
  
  if (token && !isTokenExpired(token)) {
    // Token有效，继续操作
    callback()
  } else {
    // Token无效，跳转登录
    wx.showModal({
      title: '需要登录',
      content: '请先登录后使用此功能',
      success: (res) => {
        if (res.confirm) {
          wx.navigateTo({ url: '/pages/login/login' })
        }
      }
    })
  }
}

// Token过期检查
function isTokenExpired(token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.exp < Date.now() / 1000
  } catch {
    return true
  }
}
```

---

## 🚪 退出登录流程

### 前端退出处理
```javascript
// 用户主动退出
function logout() {
  wx.showModal({
    title: '确认退出',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        performLogout()
      }
    }
  })
}

function performLogout() {
  // 🗑️ 清除本地存储
  wx.removeStorageSync('token')
  wx.removeStorageSync('userInfo')
  
  // 🔄 清除全局状态
  const app = getApp()
  app.globalData.userInfo = null
  
  // 🏠 跳转登录页
  wx.reLaunch({ url: '/pages/login/login' })
  
  wx.showToast({ title: '已退出登录', icon: 'success' })
}
```

### 后端退出接口
```python
@router.post("/logout")
async def logout(current_user: Dict = Depends(get_current_user)):
    """用户登出"""
    # JWT无状态特性：服务端无需特殊处理
    # 客户端删除token即可实现登出
    
    # 📊 可选：记录登出日志
    await log_user_activity(current_user["person_id"], "logout")
    
    return {"message": "登出成功"}
```

---

## 🔐 安全机制保障

### 1. 密码安全
```python
# backend/app/core/security.py
def hash_password(password: str) -> Tuple[str, str]:
    """密码哈希处理"""
    # 🧂 生成16字节随机盐值
    salt = secrets.token_hex(16)
    
    # 🔐 SHA-256 + 盐值哈希
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    
    return password_hash, salt

def verify_password(plain_password: str, stored_hash: str, salt: str) -> bool:
    """密码验证"""
    computed_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
    return computed_hash == stored_hash
```

### 2. 登录保护
```python
# 登录次数限制
def validate_login_attempts(attempts: int, locked: bool) -> bool:
    if locked:
        raise HTTPException(status_code=423, detail="账户已锁定")
    if attempts >= 5:
        raise HTTPException(status_code=429, detail="尝试次数过多")
    return True
```

### 3. 数据传输安全
- **HTTPS加密**：生产环境强制HTTPS传输
- **Token安全**：JWT签名防篡改，合理过期时间
- **敏感数据**：密码等敏感信息通过POST请求体传输

### 4. 本地存储安全
```javascript
// 安全存储管理
class SecureStorage {
  static setToken(token) {
    // 可选：对token进行客户端加密
    wx.setStorageSync('token', token)
  }
  
  static getToken() {
    const token = wx.getStorageSync('token')
    // 验证token格式和过期时间
    return this.validateToken(token) ? token : null
  }
  
  static clearAll() {
    wx.removeStorageSync('token')
    wx.removeStorageSync('userInfo')
  }
}
```

---

## 📊 核心数据流

### 登录数据流
```
1. 用户操作 → 微信code/账号密码
2. 前端请求 → Backend认证API
3. Backend验证 → Data-Service查询
4. 生成Token → JWT签名
5. 返回前端 → 本地存储
6. API请求 → Bearer Token认证
7. Token验证 → 用户信息获取
8. 权限检查 → 业务逻辑执行
```

### 关键存储位置
- **前端存储**：`wx.getStorageSync('token')`, `app.globalData.userInfo`
- **数据库存储**：`persons.wechat_openid`, `persons.password_hash`
- **JWT Payload**：用户ID、角色、登录方式、过期时间

---

## 🎯 总结

### 技术特点
1. **🔄 多方式登录**：微信、密码、体验模式并存
2. **🎫 JWT无状态**：分布式友好，无服务端会话
3. **🏗️ 分层架构**：前端→胶水层→数据服务，职责清晰
4. **🔒 安全可靠**：多层安全机制，权限细粒度控制
5. **📱 用户友好**：自动登录保持，优雅错误处理

### 关键文件
- **前端核心**：`login.js`, `api.js`, `app.js`  
- **后端核心**：`auth.py`, `deps.py`, `security.py`
- **数据结构**：`persons`表，微信绑定字段

这套登录验证系统在保证安全性的同时，提供了良好的用户体验，完全适配微信小程序的使用场景和校园管理需求。 