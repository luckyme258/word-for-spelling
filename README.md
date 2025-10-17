# word-for-spelling
背单词专用，用于检测记忆效果

- 首先，通过word.txt里面的单词，下载音频文件。单词.mp3,存储在tts_mp3文件夹
- exam.py将进行拼写测试
- 三次拼写机会，如果不通过，会自动切换到新的单词
- 按字母顺序进行测试
- dowload_new.py用于预先下载MP3文件

- 补充文件 exam_dir.py,通用型框架，支持任何 单词.mp3 组成的文件夹
- exam_dir.exe 适配win11. 直接使用

---
- 由于百度翻译无法正常下载，切换成谷歌tts进行语音合成（dowload_gtts.py），获取单词发音，这个代码是美音
- exam_dir_bigger.py是pyside6做的界面
- exam_dir_small_exe.py是更简单的ui做的界面
- 二者如果都是用python脚本，没太大区别。唯一的不同就是。pyside版本的exe很大，接近300MB，后者是30MB
- exe暂时不会上传，超过25MB不能直接上传，使用pyexe.py自己转换一下吧

