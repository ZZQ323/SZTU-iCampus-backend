// 全局
function foo() {
    console.log('foo');
    var d = "d";
}
foo();  // 直接调用foo()
var b = "b";
var b = "b";
var b = "b";
var b = "b";
var b = "b";
var b = "b";
// let b = 1;
let a = "a";
{
    //var a;
}
{
    var c = "c";
}

if (typeof window !== 'undefined') { // 检查是否在浏览器环境中
    window.foo();   // foo
    console.log(window.a);  // undefined
    console.log(window.b);  // b
    console.log(window.c);  // c
    console.log(window.foo.d);  // undefined
    console.log(window.d);  // undefined
    // 在浏览器中运行的代码
    console.log('Running in the browser');
} else {
    // globalThis.foo();   
    // 在Node.js中运行的代码
    console.log('Running in Node.js');
}