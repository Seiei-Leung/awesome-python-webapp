/* 顶上栏 */
$(function(){
    var $signed = $('.signed');
    var $username = $('.username');
    var $userdropdownbar = $('.userdropdownbar');
    var $userdropdownbarli = $('.userdropdownbar li');
    var $messageslistli = $('.messageslist li');
    $signed.mouseenter(function(){
        $username.css('color','#ff7e00');
        $userdropdownbar.removeClass('hid');
    }).mouseleave(function(){
        $username.css('color','#fff');
        $userdropdownbar.addClass('hid');
    })
    $userdropdownbarli.mouseenter(function(){
        $userdropdownbarli.removeClass('active').find('a').css('color','#fff');
        $(this).addClass('active').find('a').css('color','#ff7e00')
    }).mouseleave(function(){
        $userdropdownbarli.removeClass('active').find('a').css('color','#fff');
    })
    /* 左侧样式 */
    $messageslistli.mouseenter(function(){
        $messageslistli.removeClass('messageslist_active').find('a').css('color','#fff');
        $(this).addClass('messageslist_active').find('a').css('color','#ff7e00')
    }).mouseleave(function(){
        $messageslistli.removeClass('messageslist_active').find('a').css('color','#fff');
    })
})

/* 左侧条栏 */
$(function(){
    /* 邮箱 */
    var $messageemail = $('.messageemail');
    var $messageemaila = $('.messageemail').find('a');
    var $messageclose = $('.messageclose');
    var $blogmessages = $('.blogmessages');
    var $messagepull = $('.messagepull');
    var $article = $('.article');
    $messageemail.mouseenter(function(){
        $messageemaila.text('786883603@qq.com');
    }).mouseleave(function(){
        $messageemaila.text('我的邮箱');
    });
    /* 拉伸条栏 */
    $messageclose.click(function(){
        if (!$blogmessages.is('animated')) {
            $blogmessages.animate({left:'-295px'},'slow');
            $article.animate({margin:'20px 80px'},'slow');//拉伸首页日志
            $messagepull.removeClass('hid');
        }
    })
    $messagepull.click(function(){
        if (!$blogmessages.is('animated')) {
            $blogmessages.animate({left:'0px'},'slow');
            $article.animate({margin:'20px 60px 20px 340px'},'slow');
            $messagepull.addClass('hid');
        }
    })

    /*---- 检测开始时可视窗口大小 ----*/
    var $topbartitle = $('.topbartitle');
    var animate_time = true;//用于窗口缩放时，不重复执行关闭左侧栏操作
    var $topbarlist_small = $('#topbarlist_small');
    var $topbarlist_label = $('.topbarlist_label');
    if ($(window).width()<860) {
        $topbartitle.css('margin','0px');
        $topbarlist_small.addClass('topbarlist_small').addClass('hid');//用于头部条生成按钮下拉菜单
        $topbarlist_label.removeClass('hid');
            if ($(window).width()<640) {
                $messageclose.click();//必须要在同一个`$(function(){}`环境下才能执行调用该事件函数
                animate_time = false;
            }
    }
    /* 检测浏览器窗口缩放 */
    $(window).resize(function(){
        if ($(window).width()<860) {
            $topbartitle.css('margin','0px');
            $topbarlist_small.addClass('topbarlist_small').addClass('hid');
            $topbarlist_label.removeClass('hid');
            if ($(window).width()<640 && animate_time) {
                    $messageclose.click();
                    animate_time = false;
            }
        } else {
            $topbartitle.css('margin','auto');
            animate_time = true;
            $topbarlist_small.removeClass('topbarlist_small').removeClass('hid');
            $topbarlist_label.addClass('hid');
        }
    })
    /* 按钮事件---缩小头部下拉菜单 */
    var $topbarlist_label_i = $('.topbarlist_label a i');
    $topbarlist_label.click(function(){
        $topbarlist_small.toggleClass('hid');
        if ($topbarlist_small.hasClass('hid')) {
            $topbarlist_label_i.removeClass('icon-cancel-circle').addClass('icon-menu3')
        } else {
            $topbarlist_label_i.removeClass('icon-menu3').addClass('icon-cancel-circle')
        }
    })
})


/* 后台管理，用户与评论链接内容切换 */