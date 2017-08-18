
/* 为低版本ie作准备 */
//ie没有console
if (! window.console) {
    window.console = {
        log: function() {},
        info: function() {},
        error: function () {},
        warn: function () {},
        debug: function () {}
    };
}

//没有trim方法，用于去除头尾空格
if (! String.prototype.trim) {
    String.prototype.trim = function() {
        return this.replace(/^\s+|\s+$/g, '');
    };
}

//没有toDateTime方法
if (! Number.prototype.toDateTime) {
    var replaces = {
        'yyyy': function(dt) {
            return dt.getFullYear().toString();
        },
        'yy': function(dt) {
            return (dt.getFullYear() % 100).toString();
        },
        'MM': function(dt) {
            var m = dt.getMonth() + 1;
            return m < 10 ? '0' + m : m.toString();
        },
        'M': function(dt) {
            var m = dt.getMonth() + 1;
            return m.toString();
        },
        'dd': function(dt) {
            var d = dt.getDate();
            return d < 10 ? '0' + d : d.toString();
        },
        'd': function(dt) {
            var d = dt.getDate();
            return d.toString();
        },
        'hh': function(dt) {
            var h = dt.getHours();
            return h < 10 ? '0' + h : h.toString();
        },
        'h': function(dt) {
            var h = dt.getHours();
            return h.toString();
        },
        'mm': function(dt) {
            var m = dt.getMinutes();
            return m < 10 ? '0' + m : m.toString();
        },
        'm': function(dt) {
            var m = dt.getMinutes();
            return m.toString();
        },
        'ss': function(dt) {
            var s = dt.getSeconds();
            return s < 10 ? '0' + s : s.toString();
        },
        's': function(dt) {
            var s = dt.getSeconds();
            return s.toString();
        },
        'a': function(dt) {
            var h = dt.getHours();
            return h < 12 ? 'AM' : 'PM';
        }
    };
    var token = /([a-zA-Z]+)/;
    Number.prototype.toDateTime = function(format) {
        var fmt = format || 'yyyy-MM-dd hh:mm:ss'
        var dt = new Date(this * 1000);
        var arr = fmt.split(token);
        for (var i=0; i<arr.length; i++) {
            var s = arr[i];
            if (s && s in replaces) {
                arr[i] = replaces[s](dt);
            }
        }
        return arr.join('');
    };
}


/*-------------------------------------- 表单提交 --------------------------------------*/
/* 传递JSON */
//接受type,dataType,successs,error,url;
//如果type是'GET',url = url+'?'+data
//如果type是'POST',还需传入data以及contentType
//要区别好链接期间(没有链接成功)返回的错误 与 链接后成功输送数据到后台，后台因数据不准确而返回的错误
function _httpJSON (method,url,data,callback){
    var opt = {
        type:method,
        dataType:'json',
        success:function(r){
            if (r && r.error) {
                return callback(r);//利用JavaScript函数参数可以不全
            }
            return callback(null,r);
        },
        error:function(XMLHttpResquest,textstatus){
            return callback({'error':'http_bad_response','data': '' + XMLHttpResquest.status,'message': '网络好像出问题了 (HTTP ' + XMLHttpResquest.status + ')'})
        }
    }
    if (method == 'GET') {
        opt.url = url + '?' + data;
    }
    if (method == 'POST') {
        opt.url = url;
        opt.data = JSON.stringify(data || {});
        opt.contentType = 'application/json';
    }
    $.ajax(opt);
}

/* 设置jq组件 */
$(function(){
    console.log('Extend $form...');
    $.fn.extend({
        //显示表单提交错误
        showFormError: function (err) {
            //return this.each
            return this.each(function(){
                var
                    $form = $(this),
                    $alert = $form && $form.find('.Formerror'),
                    fieldName = err && err.data;
                if (! $form.is('form')) {
                    console.error('Cannot call showFormError() on non-form object.');
                    return;
                }
                if ($alert.length === 0) {
                    console.warn('Cannot find .Formerror element.');
                    return;
                }
                if (err) {
                    //向页面显示错误信息，可以结合后台返回文件查看
                    $alert.text('{{----'+(err.message ? err.message : (err.error ? err.error : err))+'----}}');//三元运算
                } else {
                    $alert.text('');
                }
            })
        },
        //
        postJSON:function (url,data,callback){
            if (arguments.length == 2){
                callback = data;
                data = {};
            }
            return this.each(function(){
                var $form = $(this);
                _httpJSON('POST',url,data,function(err,r){
                    //此处if语句是否多余
                    if (err) {
                        $form.showFormError(err);
                    }
                    callback && callback(err,r);//很妙，注意&&的用法
                })
            })
        }
    })
})

/* GET方法 */
function getJSON (url,data,callback){
    if (arguments.length===2) {
        callback = data;
        data = {};
    }
    if (typeof(data) === 'object') {//还可以为字符串,注意比较的语法形式
        var arr = [];
        $.each(data,function(k,v){
            arr.push(k + '=' + encodeURIComponent(v));
        });
        data = arr.join('&');
    }
    _httpJSON('GET',url,data,callback);
}

/* 用于添加评论 */
function refresh (){
    var 
        t = new Date().getTime(),
        url = location.pathname;
    if (location.search) {
        url = url + location.search + '&t=' + t;
    }
    else {
        url = url + '?t=' + t;
    }
    location.assign(url);
}

/* 关于页码 */
function parseQueryString() {
    var
        q = location.search,
        r = {},
        i, pos, s, qs;
    if (q && q.charAt(0)==='?') {
        qs = q.substring(1).split('&');
        for (i=0; i<qs.length; i++) {
            s = qs[i];
            pos = s.indexOf('=');
            if (pos <= 0) {
                continue;
            }
            r[s.substring(0, pos)] = decodeURIComponent(s.substring(pos+1)).replace(/\+/g, ' ');
        }
    }
    return r;
}

function gotoPage(i) {
    var r = parseQueryString();
    r.page = i;
    location.assign('?' + $.param(r));
}

if (typeof(Vue)!=='undefined') {
    Vue.component('pagination', {
        props:['message'],
        template: '<ul>' +
                '<li v-if="! message.has_previous" class="noactive"><i class="icon-chevron-left"></i></li>' +
                '<li v-if="message.has_previous"><a v-on:click="gotoPage(message.page_index-1)" href="#0"><i class="icon-chevron-left"></i></a></li>' +
                '<li v-if="message.page_index-2 &gt; 0"><a v-on:click="gotoPage(message.page_index-2)" href="#0" v-text="message.page_index-2"></a></li>' + 
                '<li v-if="message.page_index-1 &gt; 0"><a v-on:click="gotoPage(message.page_index-1)" href="#0" v-text="message.page_index-1"></a></li>' +
                '<li class="activepage"><span v-text="message.page_index"></span></li>' +
                '<li v-if="message.page_index+1 &lt; message.page_count || message.page_index+1 == message.page_count"><a v-on:click="gotoPage(message.page_index+1)" href="#0" v-text="message.page_index+1"></a></li>' + 
                '<li v-if="message.page_index+2 &lt; message.page_count || message.page_index+2 == message.page_count"><a v-on:click="gotoPage(message.page_index+2)" href="#0" v-text="message.page_index+2"></a></li>' +
                '<li v-if="!message.has_next" class="noactive"><i class="icon-chevron-right"></i></li>' +
                '<li v-if="message.has_next"><a v-on:click="gotoPage(message.page_index+1)" href="#0"><i class="icon-chevron-right"></i></a></li>' +
            '</ul>'
    });//这里头使用v-on能绑定这个文件内的所有函数，然而在导入网页元素时并不能调用该网页初始化vue对象的函数，另外这里不能使用花括号所以定义文本内容要使用v-text
}

function postJSON(url, data, callback) {
    if (arguments.length===2) {
        callback = data;
        data = {};
    }
    _httpJSON('POST', url, data, callback);
}