// UMD (Universal Module Definition)
(function (f) { 
  if (typeof exports === "object" && typeof module !== "undefined") {
    module.exports = f() 
  } else if (typeof define === "function" && define.amd) { 
    define([], f)
  } else { 
    var g; 
    if (typeof window !== "undefined") {
      g = window 
    } else if (typeof global !== "undefined") { 
      g = global 
    } else if (typeof self !== "undefined") { 
      g = self 
    } else { 
      g = this 
    } 
    g.Promise = f() 
  } 
})
(function () {
  // 模块引导器
  var define, module, exports; 
  return (function e(t, n, r) {
    function s(o, u) { 
      if (!n[o]) { 
        if (!t[o]) { 
          var a = typeof require == "function" && require; 
          if (!u && a) return a(o, !0); 
          if (i) return i(o, !0); 
          var f = new Error("Cannot find module '" + o + "'"); 
          throw f.code = "MODULE_NOT_FOUND", f 
        } 
        var l = n[o] = { exports: {} }; 
        t[o][0].call(l.exports, function (e) {
          var n = t[o][1][e]; return s(n ? n : e) 
        }, l, l.exports, e, t, n, r) 
      } 
      return n[o].exports 
    } 
    var i = typeof require == "function" && require; 
    for (var o = 0; o < r.length; o++)s(r[o]); return s })
  ({
    1: [function (_dereq_, module, exports) {
      (function (global) {
        'use strict';
        var Mutation = global.MutationObserver || global.WebKitMutationObserver;
        // 这是 MutationObserver 的函数对象
        // 当前运行环境（浏览器、Node-JS-DOM shim 等）里能够拿到的 MutationObserver 构造函数；
        // 如果是早期 WebKit 内核则取 WebKitMutationObserver。
        var scheduleDrain;
        // 这段代码的真正目的——造一个“最快的微任务调度器”
        {
          // 作者想要一个跨环境的 nextTick()：
            // 优先用 MutationObserver（最快、与 Promise 同优先级）；
            // 其次退而求其次用 MessageChannel；
            // 再次用 <script>.onreadystatechange；
            // 最差才降到 setTimeout(fn, 0)（宏任务，事件循环下一轮才跑）。
          if (Mutation) {
            var called = 0;
            var observer = new Mutation(nextTick);
            // 每次 scheduleDrain() 被调用，element.data 会在 0 - 1 之间翻转；
            // 这正好触发 MutationObserver 的回调 nextTick
            var element = global.document.createTextNode('');
            observer.observe(element, {
              characterData: true
              // 只关心 该文本节点内容的变化
            });
            //  故意去改动 Text 节点的数据，从而触发一次 “characterData mutation”
            scheduleDrain = function () {
              element.data = (called = ++called % 2);
            };
          } else if (!global.setImmediate && typeof global.MessageChannel !== 'undefined') {
            var channel = new global.MessageChannel();
            channel.port1.onmessage = nextTick;
            scheduleDrain = function () {
              channel.port2.postMessage(0);
            };
          } else if ('document' in global && 'onreadystatechange' in global.document.createElement('script')) {
            scheduleDrain = function () {

              // Create a <script> element; its readystatechange event will be fired asynchronously once it is inserted
              // into the document. Do so, thus queuing up the task. Remember to clean up once it's been called.
              var scriptEl = global.document.createElement('script');
              scriptEl.onreadystatechange = function () {
                nextTick();

                scriptEl.onreadystatechange = null;
                scriptEl.parentNode.removeChild(scriptEl);
                scriptEl = null;
              };
              global.document.documentElement.appendChild(scriptEl);
            };
          } else {
            scheduleDrain = function () {
              setTimeout(nextTick, 0);
            };
          }
        }

        // 是否在清空队列
        var draining;
        // 任务队列
        var queue = [];
        //named nextTick for less confusing stack traces
        /**
          * @description 
          * @param 
          * @return 
          * @author zzq323 2025/06/18
          */
        function nextTick() {
          draining = true;
          var i, oldQueue;
          var len = queue.length;
          while (len) {
            oldQueue = queue;
            queue = [];
            i = -1;
            while (++i < len) {
              oldQueue[i]();
            }
            len = queue.length;
          }
          draining = false;
        }
        // 导出模块
          // 把 immediate 函数公开给其他模块。
          // 别的模块 const nextTick = require('./immediate'); 
        module.exports = immediate;
        /**
          * @description 第一个推入的时候，立即触发 nextTick
          * @param 
          * @return 
          * @author zzq323 2025/06/18
          */
        function immediate(task) {
          // 刚刚拿到一个task的时候
          if (queue.push(task) === 1 && !draining) {
            scheduleDrain();
          }
        }

      }).call(this, typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})
    }, {}], 
    2: [function (_dereq_, module, exports) {
      'use strict';
      var immediate = _dereq_(1);

      /* istanbul ignore next */
      function INTERNAL() { }

      var handlers = {};

      var REJECTED = ['REJECTED'];
      var FULFILLED = ['FULFILLED'];
      var PENDING = ['PENDING'];

      module.exports = Promise;

      function Promise(resolver) {
        if (typeof resolver !== 'function') {
          throw new TypeError('resolver must be a function');
        }
        this.state = PENDING;
        // 这里的 queue 不同于上面的 queue
        this.queue = [];
        this.outcome = void 0;
        // 内部调用不进入
        if (resolver !== INTERNAL) {
          safelyResolveThenable(this, resolver);
        }
      }

      Promise.prototype["finally"] = function (callback) {
        if (typeof callback !== 'function') {
          return this;
        }
        var p = this.constructor;
        return this.then(resolve, reject);

        function resolve(value) {
          function yes() {
            return value;
          }
          return p.resolve(callback()).then(yes);
        }
        function reject(reason) {
          function no() {
            throw reason;
          }
          return p.resolve(callback()).then(no);
        }
      };
      Promise.prototype["catch"] = function (onRejected) {
        return this.then(null, onRejected);
      };
      /**
        * @description 当你直接调用then的时候进入
        * @param 
        * @return 
        * @author zzq323 2025/06/18
        */
      Promise.prototype.then = function (onFulfilled, onRejected) {
        // 如果传入的不是函数，且状态是不确定的，直接返回调用的那个人？
        if (typeof onFulfilled !== 'function' && this.state === FULFILLED ||
          typeof onRejected !== 'function' && this.state === REJECTED) {
          return this;
        }
        // 内部调用走流程
        var promise = new this.constructor(INTERNAL);
        // 所以这里展示了promise的核心逻辑
        // 如果你永远不调用 handlers.resolve(self, value) 
        // 那么所有后续 .then() / .catch() / await 都等不到结果，代码就像卡住了一样
        // 这就是 promise 做出的承诺：你必须做完了，才有下一步
        if (this.state !== PENDING) {
          // 注意，这里写的是this的state，而不是新new出来的
          // then可以直接执行
          var resolver = this.state === FULFILLED ? onFulfilled : onRejected;
          unwrap(promise, resolver, this.outcome);
        } else {
          // 如果前面的 promise、then 需要等待的话
          this.queue.push(new QueueItem(promise, onFulfilled, onRejected));
        }
        // 返回这个包装了新then的promise
        return promise;
      };
      /**
        * @description 如果需要等待的话，你会被推入此地
        * 
        * onFulfilled、onRejected实际上并没有单独的函数
        * 不过就好像是then的if-else一样，如果你顺利，就调用onFulfilled；否则调用 onRejected 处理异常
        * @return 
        * @author zzq323 2025/06/18
        */
      function QueueItem(promise, onFulfilled, onRejected) {
        // 包装了待执行 then 的 promise
        this.promise = promise;
        if (typeof onFulfilled === 'function') {
          this.onFulfilled = onFulfilled;
          this.callFulfilled = this.otherCallFulfilled; // ← 只在有onFulfilled方法时
        }
        if (typeof onRejected === 'function') {
          this.onRejected = onRejected;
          this.callRejected = this.otherCallRejected; // ← 只在有onRejected方法时
        }
      }
      /**
        * @description 默认成功分支；当 then() 没有 成功回调
        * @return 
        * @author zzq323 2025/06/18
        */
      QueueItem.prototype.callFulfilled = function (value) {
        handlers.resolve(this.promise, value);
      };
      /**
        * @description 当 then() 有 成功回调
        * @return 
        * @author zzq323 2025/06/18
        */
      QueueItem.prototype.otherCallFulfilled = function (value) {
        unwrap(this.promise, this.onFulfilled, value);
      };
      /**
        * @description 默认失败分支；当 then() 没有 失败回调
        * @return 
        * @author zzq323 2025/06/18
        */
      QueueItem.prototype.callRejected = function (value) {
        handlers.reject(this.promise, value);
      };
      /**
        * @description 当 then() 有 失败回调
        * @return 
        * @author zzq323 2025/06/18
        */
      QueueItem.prototype.otherCallRejected = function (value) {
        unwrap(this.promise, this.onRejected, value);
      };

      /**
        * @description 使用 immediate 注册。immediate 和 tryCatch 类似，只是不允许返回 promise
        * 
        * 
        * @return 
        * @author zzq323 2025/06/18
        */
      function unwrap(promise, func, value) {
        immediate(function () {
          var returnValue;
          try {
            returnValue = func(value);
          } catch (e) {
            return handlers.reject(promise, e);
          }
          // ✅ 可以向 resolve(value) 里传入一个 Promise/thenable
          // ✅ 也可以在 .then(onFulfilled) 的回调里 返回一个 Promise/thenable
          // ⛔️ 唯一不行的是：把「同一个 Promise 实例」既传进去又返回出来——那会造成自引用
          if (returnValue === promise) {
            handlers.reject(promise, new TypeError('Cannot resolve promise with itself'));
          } else {
            handlers.resolve(promise, returnValue);
          }
        });
      }

      /**
        * @description 结束一切的函数，修正promise的函数；
        * 
        * value可能会有所不同，如果可以继续处理的话，那么value会继续被处理
        * @return 
        * @author zzq323 2025/06/18
        */
      handlers.resolve = function (self, value) {
        // 传入代表着 “成功” 的参数，去找这个参数有没有 then
        var result = tryCatch(getThen, value);
        if (result.status === 'error') {
          return handlers.reject(self, result.value);
        }
        // 啊，原来是可以继续then的
        // 此时应该是个函数
        var thenable = result.value;
        if (thenable) {
          // then起来
          safelyResolveThenable(self, thenable);
        } else {
          // 成功标志
          self.state = FULFILLED;
          self.outcome = value;
          // 如果这个then的执行姗姗来迟 —— 其他东西都执行完了才 tm 轮到
          // 顺序执行因为较慢success积累的所有then
          var i = -1;
          var len = self.queue.length;
          while (++i < len) {
            self.queue[i].callFulfilled(value);
          }
        }
        return self;
      };
      /**
        * @description 
        * @param 
        * @return 
        * @author zzq323 2025/06/18
        */
      handlers.reject = function (self, error) {
        self.state = REJECTED;
        self.outcome = error;
        var i = -1;
        var len = self.queue.length;
        while (++i < len) {
          self.queue[i].callRejected(error);
        }
        return self;
      };

      /**
        * @description 判断：你resolve的参数是可以then的吗？
        * @return undefined or 经常传入 promise 的回调函数
        * @author zzq323 2025/06/18
        */
      function getThen(obj) {
        // Make sure we only access the accessor once as required by the spec
        // 只读取一次 .then，避免多次触发 getter 带来副作用 ？
        var then = obj && obj.then;
        if (obj && (typeof obj === 'object' || typeof obj === 'function') && typeof then === 'function') {
          // 非空且obj是函数or对象 且 then 是函数
          return function applyThen() {
            // 返回一个包装器，让你那个有then的类去then去
            then.apply(obj, arguments);
          };
        }
        // 否则返回 undefined
      }
      /**
        * @description 带 this 入 try 执行函数
        * @param 
        * @return 
        * @author zzq323 2025/06/18
        */
      function safelyResolveThenable(self, thenable) {
        // Either fulfill, reject or reject with error
        var called = false;
        // resolver 参数2
        function onError(value) {
          if (called) {
            return;
          }
          called = true;
          handlers.reject(self, value);
        }
        // resolver 参数1
        function onSuccess(value) {
          if (called) {
            return;
          }
          called = true;
          handlers.resolve(self, value);
        }
        // 执行函数
        function tryToUnwrap() {
          thenable(onSuccess, onError);
        }
        // try内执行结果，是个对象
        var result = tryCatch(tryToUnwrap);
        if (result.status === 'error') {
          onError(result.value);
        }
      }

      /**
        * @description try内执行函数，返回执行结果；要么报错，要么返回执行结果的值
        * @param
        * @author zzq323 2025/06/18
        */
      function tryCatch(func, value) {
        // 输出{
        //     value: any;
        //     status: string;
        // }
        var out = {};
        try {
          out.value = func(value);
          out.status = 'success';
        } catch (e) {
          out.status = 'error';
          out.value = e;
        }
        return out;
      }

      Promise.resolve = resolve;
      function resolve(value) {
        if (value instanceof this) {
          return value;
        }
        return handlers.resolve(new this(INTERNAL), value);
      }

      Promise.reject = reject;
      function reject(reason) {
        var promise = new this(INTERNAL);
        return handlers.reject(promise, reason);
      }

      Promise.all = all;
      function all(iterable) {
        var self = this;
        if (Object.prototype.toString.call(iterable) !== '[object Array]') {
          return this.reject(new TypeError('must be an array'));
        }

        var len = iterable.length;
        var called = false;
        if (!len) {
          return this.resolve([]);
        }

        var values = new Array(len);
        var resolved = 0;
        var i = -1;
        var promise = new this(INTERNAL);

        while (++i < len) {
          allResolver(iterable[i], i);
        }
        return promise;
        function allResolver(value, i) {
          self.resolve(value).then(resolveFromAll, function (error) {
            if (!called) {
              called = true;
              handlers.reject(promise, error);
            }
          });
          function resolveFromAll(outValue) {
            values[i] = outValue;
            if (++resolved === len && !called) {
              called = true;
              handlers.resolve(promise, values);
            }
          }
        }
      }

      Promise.race = race;
      function race(iterable) {
        var self = this;
        if (Object.prototype.toString.call(iterable) !== '[object Array]') {
          return this.reject(new TypeError('must be an array'));
        }

        var len = iterable.length;
        var called = false;
        if (!len) {
          return this.resolve([]);
        }

        var i = -1;
        var promise = new this(INTERNAL);

        while (++i < len) {
          resolver(iterable[i]);
        }
        return promise;
        function resolver(value) {
          self.resolve(value).then(function (response) {
            if (!called) {
              called = true;
              handlers.resolve(promise, response);
            }
          }, function (error) {
            if (!called) {
              called = true;
              handlers.reject(promise, error);
            }
          });
        }
      }

    }, { "1": 1 }]
  }, {}, [2]
  )(2)
});
