# //https://fanyi.baidu.com/gettts?lan=uk&text=singer&spd=3
import os
import time
import glob
from urllib.parse import quote  # 用于URL编码（处理空格、特殊字符）
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def batch_download_tts(word_file_path, save_dir, lan="uk", spd=3):
    """
    批量下载百度翻译TTS音频
    :param word_file_path: words.txt的路径
    :param save_dir: MP3文件的保存目录
    :param lan: 语言类型（uk=英语，zh=中文，更多语言可查百度TTS文档）
    :param spd: 语速（1-9，数字越大越快，默认4）
    """
    # 1. 检查单词文件是否存在
    if not os.path.exists(word_file_path):
        print(f"错误：单词文件 {word_file_path} 不存在！")
        return

    # 2. 创建保存MP3的目录（不存在则自动创建）
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"已创建保存目录：{save_dir}")

    # 3. 读取单词列表（按行读取，去除空行和前后空格）
    with open(word_file_path, "r", encoding="utf-8") as f:
        words = [line.strip() for line in f if line.strip()]  # 过滤空行
    if not words:
        print("错误：words.txt中没有有效单词！")
        return
    print(f"共读取到 {len(words)} 个单词/词组，开始下载...")

    # 4. 配置浏览器下载选项
    chrome_options = Options()
    
    # 设置下载路径
    prefs = {
        "download.default_directory": os.path.abspath(save_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # 启动浏览器（有头模式）
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # 5. 循环下载每个单词的MP3
        for index, word in enumerate(words, start=1):
            try:
                # 生成目标文件名
                safe_filename = word.replace("/", "-").replace("\\", "-").replace("?", "").replace("*", "").replace(":", "").replace("\"", "").replace("<", "").replace(">", "").replace("|", "") + ".mp3"
                save_path = os.path.join(save_dir, safe_filename)
                
                # 检查文件是否已存在
                if os.path.exists(save_path) and os.path.getsize(save_path) > 1000:
                    print(f"[{index}/{len(words)}] 已存在，跳过：{word}")
                    continue

                # 构造TTS请求URL
                encoded_word = quote(word, encoding="utf-8")
                tts_url = f"https://fanyi.baidu.com/gettts?lan={lan}&text={encoded_word}&spd={spd}"

                print(f"[{index}/{len(words)}] 正在下载：{word}")
                
                # 记录下载前的文件列表
                before_download = set(os.listdir(save_dir))
                
                # 直接访问TTS URL，浏览器会自动下载
                driver.get(tts_url)
                
                # 等待下载完成
                time.sleep(5)
                
                # 查找新下载的文件
                after_download = set(os.listdir(save_dir))
                new_files = after_download - before_download
                
                # 重命名新下载的MP3文件
                if new_files:
                    for new_file in new_files:
                        if new_file.endswith('.mp3'):
                            old_path = os.path.join(save_dir, new_file)
                            # 重命名为单词名称
                            os.rename(old_path, save_path)
                            break
                
                # 检查文件是否下载成功
                if os.path.exists(save_path) and os.path.getsize(save_path) > 1000:
                    file_size = os.path.getsize(save_path) // 1024
                    print(f"[{index}/{len(words)}] 成功下载：{safe_filename} ({file_size}KB)")
                else:
                    print(f"[{index}/{len(words)}] 下载失败：{word}")

                # 下载间隔
                if index < len(words):
                    print("等待5秒...")
                    time.sleep(5)

            except Exception as e:
                print(f"[{index}/{len(words)}] 失败：{word}，错误信息：{str(e)}")

    finally:
        # 关闭浏览器
        driver.quit()
        print("浏览器已关闭")

    print(f"\n批量下载完成！MP3文件已保存至：{os.path.abspath(save_dir)}")

# ------------------- 执行脚本 -------------------
if __name__ == "__main__":
    # 配置参数（可根据需求修改）
    WORD_FILE = "words.txt"  # 单词文件路径（与脚本同目录）
    SAVE_DIRECTORY = "tts_mp3"  # 保存MP3的文件夹名
    SPEED = 3  # 语速（1-9，建议4-5）
    LANGUAGE = "uk"  # 语言（uk=英语，zh=中文，jp=日语等）

    # 调用函数开始下载
    batch_download_tts(WORD_FILE, SAVE_DIRECTORY, LANGUAGE, SPEED)