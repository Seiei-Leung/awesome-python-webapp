
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

//制作toDateTime方法
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
    Number.prototype.toDateTime = function(format) {
        var fmt = format || 'yyyy-MM-dd hh:mm:ss';
        var dt = new Date(this * 1000);
        var arr = fmt.replace(/:/g,'-').replace(/\s/g,'-').split('-');//不能结合正则以及split对字符串操作，因为ie8有bug
        for (var i=0; i<arr.length; i++) {
            var s = arr[i];
            if (s && s in replaces) {
                
                arr[i] = replaces[s](dt);
            }

        }
        return arr.slice(0,3).join('-') + ' ' + arr.slice(3,6).join(':');
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
        error:function(XMLHttpResquest,statustext){
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
        /*
        var arr = [];
        $.each(data,function(k,v){
            arr.push(k + '=' + encodeURIComponent(v));
        });
        data = arr.join('&');
        */
        data = $.param(data);
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

function postJSON(url, data, callback) {
    if (arguments.length===2) {
        callback = data;
        data = {};
    }
    _httpJSON('POST', url, data, callback);
}

/* 页码 */
function makepage (message) {
    var 
        $page = $('.page'),
        nohas_previous = (!message.has_previous) ? ('<li class="noactive"><i class="icon-chevron-left"></i></li>') : (''),
        has_previous = (message.has_previous) ? ('<li><a href="#0" data-page="' + (message.page_index-1) + '"><i class="icon-chevron-left"></i></a></li>') : (''),
        page_m2 = (message.page_index-2 > 0) ? ('<li><a href="#0" data-page="' + (message.page_index-2) + '">' + (message.page_index-2) + '</a></li>') : (''),
        page_m1 = (message.page_index-1 > 0) ? ('<li><a href="#0" data-page="' + (message.page_index-1) + '">' + (message.page_index-1) + '</a></li>') : (''),
        pageactive = '<li class="activepage"><span>' + message.page_index + '</span></li>',
        page_a1 = (message.page_index+1 < message.page_count || message.page_index+1 == message.page_count) ? ('<li><a href="#0" data-page="' + (message.page_index+1) + '">'+ (message.page_index+1) +'</a></li>'):(''),
        page_a2 = (message.page_index+2 < message.page_count || message.page_index+2 == message.page_count) ? ('<li><a href="#0" data-page="' + (message.page_index+2) + '">'+ (message.page_index+2) +'</a></li>'):(''),
        nohas_next = (!message.has_next) ? ('<li class="noactive"><i class="icon-chevron-right"></i></li>') : (''),
        has_next = (message.has_next) ? ('<li><a href="#0" data-page="' + (message.page_index+1) + '"><i class="icon-chevron-right"></i></a></li>') : (''),
        $template = '<ul>' + nohas_previous + has_previous + page_m2 + page_m1 + pageactive + page_a1 + page_a2 + nohas_next + has_next +'</ul>';
    $page.append($template);
    var $pagelink = $('.page a');
    $pagelink.click(function(){
        gotoPage($(this).data('page'));
    })
}

/* 转义 */
function changetotext (content) {
    content = content.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    return content
}
/* event.preventDefault()兼容IE8 */
function stopDefault(event){
 if ( event && event.preventDefault ){ 
    event.preventDefault();
} else { 
    window.event.returnValue = false;
} 
}