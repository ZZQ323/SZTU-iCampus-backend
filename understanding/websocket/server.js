// 创建HTTP服务器 (用于提供HTML页面)
var app = require('http').createServer(handler);
// 导入WebSocket库
var ws = require('nodejs-websocket');
// 导入文件系统模块
var fs = require('fs');

// HTTP服务器监听80端口
app.listen(80);

// HTTP请求处理函数
function handler(req, res) {
    // 读取并返回 index.html文件  (注意：实际应改为index.html)
    fs.readFile(__dirname + '/index.html', function (err, data) {
        if (err) {
            res.writeHead(500);  // 服务器错误状态码
            return res.end('error ');  // 返回错误信息
        }
        res.writeHead(200);  // 成功状态码
        res.end(data);  // 返回文件内容
    });
}

// 创建WebSocket服务器 (监听5000端口)
var server = ws.createServer(function (conn) {
    console.log('new conneciton');  // 新连接日志
    
    // 收到客户端文本消息时触发
    conn.on("text", function (str) {
        broadcast(server, str);  // 广播消息给所有客户端
    });
    
    // 连接关闭时触发
    conn.on("close", function (code, reason) {
        console.log('connection closed');  // 连接关闭日志
    })
}).listen(5000);  // WebSocket监听5000端口

// 广播消息函数
function broadcast(server, msg) {
    // 遍历所有客户端连接
    server.connections.forEach(function (conn) {
        conn.sendText(msg);  // 发送消息给每个客户端
    })
}