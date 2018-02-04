/**
 * Created by Admin on 2017/8/25.
 */
$(document).ready(function () {
    var myeditor;
    $(function () {
        $('#id_content,#editor_id,#id_content_raw').parent().attr('id', 'editormd');
        myeditor = editormd("editormd", {
            width: "100%",
            height: 500,
            watch: false,
            autoFocus: false,
            syncScrolling: "single",
            placeholder: '说点什么吧...',
            saveHTMLToTextarea: true,
            imageUpload: true,
            // dialogMaskOpacity: 0.4, //设置透明遮罩层的透明度，全局通用，默认值为0.1
            // dialogMaskBgColor: "#000",//设置透明遮罩层的背景颜色，全局通用，默认为#fff
            toolbarIcons: function () {
                return [ "bold", "hr", "italic", "del", "quote", "|", "h1", "h2", "h3", "h4", "ucwords",  "|", "list-ul", "list-ol", "table", "link", "image", "code", "preformatted-text", "code-block", "|", "search", "html-entities", "watch", "preview",  "fullscreen"]
            },
            imageFormats: ['jpg', 'jpeg', 'gif', 'png', 'bmp', 'webp'],
            imageUploadURL: "/forum/upload/",
            path: "/forum/static/editor.md/lib/"
        });

        $('.reply').click(function () {
            var content = '@' + $(this).attr('data-nickname') + ' ';
            myeditor.insertValue(content)
        })
    });

    function paste(ev) {
        var items = (ev.clipboardData || ev.dataTransfer || ev.originalEvent.clipboardData).items;
        for (var index in items) {
            var item = items[index];
            if (item.kind === 'file') {
                var blob = item.getAsFile();
                var reader = new FileReader();
                reader.onload = function (event) {
                    var base64 = event.target.result;
                    //ajax上传图片
                    $.post("/forum/upload/", {base: base64}, function (ret) {
                        var result = JSON.parse(ret);
                        if (result.success === 1) {
                            //新一行的图片显示
                            myeditor.insertValue("\n![](" + result.url + ")\n");
                        } else {
                            if (result.message) {
                                alert(result.message)
                            }
                        }
                    });
                }; // data url!
                var url = reader.readAsDataURL(blob);
            }
        }
    }

    document.addEventListener('paste', function (event) {
        paste(event);
    });
    document.addEventListener("dragenter", function (event) {
        event.preventDefault();
    });
    document.addEventListener("dragover", function (event) {
        event.preventDefault();
    });
    document.addEventListener("drop", function (event) {
        event.preventDefault();
        event.stopPropagation();
        //禁止浏览器默认行为
        paste(event);
    });
    document.addEventListener("dragend", function (event) {
        event.preventDefault();
    });


});
