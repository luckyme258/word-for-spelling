
# //https://fanyi.baidu.com/gettts?lan=uk&text=singer&spd=3
import requests
import os
from urllib.parse import quote  # 用于URL编码（处理空格、特殊字符）

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

    # 4. 循环下载每个单词的MP3
    for index, word in enumerate(words, start=1):
        try:
            # 构造TTS请求URL（需对单词进行URL编码，处理空格/特殊字符）
            encoded_word = quote(word, encoding="utf-8")  # 如 "high technology" → "high%20technology"
            tts_url = f"https://fanyi.baidu.com/gettts?lan={lan}&text={encoded_word}&spd={spd}"

            # 发送请求（模拟浏览器请求头，避免被接口拦截）
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
            }
            response = requests.get(tts_url, headers=headers, timeout=10)  # 超时10秒防止卡住

            # 检查请求是否成功（百度TTS成功时返回200，且内容为MP3二进制）
            if response.status_code == 200 and "audio/mpeg" in response.headers.get("Content-Type", ""):
                # 生成保存文件名（用单词命名，避免特殊字符，如将"/"替换为"-"）
                safe_filename = word.replace("/", "-").replace("\\", "-") + ".mp3"
                save_path = os.path.join(save_dir, safe_filename)

                # 写入MP3文件（二进制模式）
                with open(save_path, "wb") as mp3_file:
                    mp3_file.write(response.content)
                print(f"[{index}/{len(words)}] 成功下载：{save_path}")
            else:
                print(f"[{index}/{len(words)}] 失败（无效响应）：{word}")

        except requests.exceptions.Timeout:
            print(f"[{index}/{len(words)}] 失败（请求超时）：{word}")
        except requests.exceptions.ConnectionError:
            print(f"[{index}/{len(words)}] 失败（网络错误）：{word}")
        except Exception as e:
            print(f"[{index}/{len(words)}] 失败（未知错误）：{word}，错误信息：{str(e)}")

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