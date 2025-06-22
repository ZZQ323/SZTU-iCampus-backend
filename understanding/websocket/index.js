// 获取DOM元素
var oUl = document.getElementById('content');       // 消息列表容器
var oConnect = document.getElementById('connect');  // 连接按钮
var oSend = document.getElementById('send');        // 发送按钮
var oInput = document.getElementById('message');    // 消息输入框

var ws = null;  // WebSocket连接对象

// 连接按钮点击事件
oConnect.onclick = function () {
    // 创建WebSocket连接 (连接到本地5000端口)
    ws = new WebSocket('ws://localhost:5000');
    // 连接建立时触发
    ws.onopen = function () {
        oUl.innerHTML += "<li>客户端已连接</li>";  
        // 添加连接成功提示
    }
    // 收到服务器消息时触发
    ws.onmessage = function (evt) {
        oUl.innerHTML += "<li>" + evt.data + "</li>";  
        // 显示接收的消息
    }
    // 连接关闭时触发
    ws.onclose = function () {
        oUl.innerHTML += "<li>客户端已断开连接</li>";  
        // 添加断开连接提示
    };
    // 发生错误时触发
    ws.onerror = function (evt) {
        oUl.innerHTML += "<li>" + evt.data + "</li>";  
        // 显示错误信息
    };
};

// 发送按钮点击事件
oSend.onclick = function () {
    if (ws) {
        ws.send(oInput.value);  // 发送输入框中的内容
    }
}