"use strict";   //严格模式
// 变量提升 —— 只有
let a = 1;
{
    let a = 1;
    // var a = 1; error
}

var b = 1;
// let b = 1;
var b = 1;
var b = 1;
var b = 1;
console.log(b + 1 + "1" + 1);

function foo() {
    var a = 1;
    {
        var a = 1;
        {
            var a = 1;
        }
    }
}

// 模拟全局对象window
const jsdom = require('jsdom');
const { JSDOM } = jsdom;

const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>');

// 模拟浏览器的window对象
const window = dom.window;
const document = window.document;


function foo() {console.log('foo');}
foo();  // 直接调用foo()

if (typeof window !== 'undefined') { // 检查是否在浏览器环境中
    // window.foo();   // 通过window.foo()调用 error 还是不会自动挂载
    // 在浏览器中运行的代码
    console.log('Running in the browser');
} else {
    // globalThis.foo();   error
    // 顶层声明的函数并不会绑定到 globalThis（或传统 Node.js 的全局对象 global）上，而是局限在当前文件的模块作用域内
    // 在Node.js中运行的代码
    console.log('Running in Node.js');
}
