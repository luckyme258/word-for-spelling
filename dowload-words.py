
# //https://fanyi.baidu.com/gettts?lan=uk&text=singer&spd=3
    import os
    import time
    import random
    from gtts import gTTS
    from gtts.tokenizer import pre_processors
    import requests
    from urllib3.exceptions import ReadTimeoutError

    def batch_download_gtts(word_file_path, save_dir, lang="en", slow=False, max_retries=3, file_min_size=100):
        """
        批量使用gTTS生成语音文件（增加空文件检查和自动重试）
        :param file_min_size: 最小文件大小（字节），小于此值视为无效文件
        """
        if not os.path.exists(word_file_path):
            print(f"错误：单词文件 {word_file_path} 不存在！")
            return
        os.makedirs(save_dir, exist_ok=True)
        print(f"保存目录：{os.path.abspath(save_dir)}")

        with open(word_file_path, "r", encoding="utf-8") as f:
            words = [line.strip() for line in f if line.strip()]
        if not words:
            print("错误：未找到有效单词！")
            return
        print(f"共读取到 {len(words)} 个单词，开始生成语音...\n")

        for index, word in enumerate(words, 1):
            safe_filename = word.replace("/", "-").replace("\\", "-").replace("?", "").replace("*", "").replace(":", "").replace("\"", "").replace("<", "").replace(">", "").replace("|", "") + ".mp3"
            save_path = os.path.join(save_dir, safe_filename)

            # 检查已有文件是否有效（即使存在，若为空也需要重新下载）
            if os.path.exists(save_path):
                if os.path.getsize(save_path) >= file_min_size:
                    print(f"[{index}/{len(words)}] 已存在有效文件，跳过：{word}")
                    continue
                else:
                    print(f"[{index}/{len(words)}] 发现空文件，将重新下载：{word}")
                    os.remove(save_path)  # 删除无效文件

            # 核心下载逻辑（增加空文件检查的重试）
            success = False
            for main_try in range(max_retries):  # 主循环：最多完整重试max_retries次
                try:
                    print(f"[{index}/{len(words)}] 第{main_try+1}轮尝试生成：{word}")
                    
                    # 生成语音
                    processed_text = pre_processors.word_sub(word)
                    tts = gTTS(text=processed_text, lang=lang, slow=slow, lang_check=True)
                    tts.save(save_path)
                    
                    # 检查文件大小（关键：确保非空）
                    if os.path.getsize(save_path) < file_min_size:
                        raise Exception(f"生成的文件过小（{os.path.getsize(save_path)}字节），可能无效")

                    # 验证通过
                    file_size = os.path.getsize(save_path) // 1024
                    print(f"[{index}/{len(words)}] 成功生成：{safe_filename}（{file_size}KB）")
                    success = True
                    break

                except (requests.exceptions.RequestException, ReadTimeoutError, Exception) as e:
                    error_msg = str(e).split("\n")[0]
                    # 无论何种错误，先删除可能的无效文件
                    if os.path.exists(save_path):
                        os.remove(save_path)
                    # 决定是否继续重试
                    if main_try < max_retries - 1:
                        wait_time = random.uniform(2, 5) * (main_try + 1)
                        print(f"[{index}/{len(words)}] 第{main_try+1}次失败：{error_msg}，{wait_time:.1f}秒后重试...")
                        time.sleep(wait_time)
                    else:
                        print(f"[{index}/{len(words)}] 达到最大重试次数，跳过：{word}（最后错误：{error_msg}）")

            # 最终检查：如果所有尝试都失败，记录下来（方便后续手动处理）
            if not success:
                with open(os.path.join(save_dir, "failed_words.txt"), "a", encoding="utf-8") as f:
                    f.write(f"{word}\n")

            # 随机延迟
            if index < len(words):
                time.sleep(random.uniform(1, 3))

        # 提示失败的单词（如果有）
        failed_file = os.path.join(save_dir, "failed_words.txt")
        if os.path.exists(failed_file) and os.path.getsize(failed_file) > 0:
            print(f"\n注意：部分单词下载失败，已记录至 {failed_file}")
        else:
            if os.path.exists(failed_file):
                os.remove(failed_file)  # 删除空的失败记录

        print(f"\n全部处理完成！文件保存至：{os.path.abspath(save_dir)}")

    # 执行脚本
    if __name__ == "__main__":
        WORD_FILE = "words.txt"
        SAVE_DIRECTORY = "gtts_mp3"
        LANGUAGE = "en"  # 英语
        SLOW_SPEECH = False
        batch_download_gtts(
            word_file_path=WORD_FILE,
            save_dir=SAVE_DIRECTORY,
            lang=LANGUAGE,
            slow=SLOW_SPEECH,
            max_retries=3,  # 最多重试3次
            file_min_size=200  # 最小文件大小（字节），可根据实际情况调整
        )
