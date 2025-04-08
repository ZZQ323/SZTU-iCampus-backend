// 全局对象window
function foo() {console.log('foo');}
foo();  // 直接调用foo()

if (typeof window !== 'undefined') { // 检查是否在浏览器环境中
    window.foo();   // 通过window.foo()调用
    // 在浏览器中运行的代码
    console.log('Running in the browser');
} else {
    globalThis.foo();   // .foo()调用
    // 在Node.js中运行的代码
    console.log('Running in Node.js');
}