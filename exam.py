import os
import pygame
import time

def init_pygame_mixer():
    """初始化pygame音频播放器，解决首次播放无声音问题"""
    pygame.mixer.init()
    time.sleep(0.5)  # 等待音频设备初始化完成

def play_mp3(mp3_path):
    """播放指定路径的MP3文件，等待播放结束后返回"""
    try:
        pygame.mixer.music.load(mp3_path)
        pygame.mixer.music.play()
        # 循环检测音频播放状态，避免提前退出
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    except Exception as e:
        print(f"❌ 音频播放失败：{e}（请检查MP3文件是否损坏或路径正确）")

def get_word_mp3_list(mp3_dir="tts_mp3"):
    """获取tts_mp3文件夹下所有有效单词MP3的信息（单词名、文件路径）"""
    word_mp3_list = []
    # 检查目标文件夹是否存在
    if not os.path.exists(mp3_dir):
        print(f"❌ 错误：未找到 {mp3_dir} 文件夹，请确认文件夹与脚本在同一目录！")
        return word_mp3_list
    
    # 筛选MP3文件并提取单词（去掉.mp3后缀）
    for filename in os.listdir(mp3_dir):
        if filename.lower().endswith(".mp3"):
            word = os.path.splitext(filename)[0].strip()  # 提取单词（保留原始格式）
            mp3_path = os.path.join(mp3_dir, filename)    # 拼接完整MP3路径
            word_mp3_list.append({"word": word, "mp3_path": mp3_path})
    
    # 检查是否加载到有效单词
    if not word_mp3_list:
        print(f"⚠️ 提示：{mp3_dir} 文件夹下未找到MP3文件，请确认文件格式为「单词.mp3」！")
    else:
        print(f"✅ 成功加载 {len(word_mp3_list)} 个单词，开始拼写练习！\n")
    return word_mp3_list

def show_dash(word):
    """根据单词长度显示短横线提示（如 'apple' 显示 '_____'）"""
    dash = "_ " * len(word)
    print(f"\n当前单词（长度：{len(word)}）：{dash.strip()}")

def spelling_practice():
    """核心拼写练习逻辑：连续3次错误直接提示答案，正确则跳转下一个单词"""
    # 初始化音频和单词列表
    init_pygame_mixer()
    word_mp3_list = get_word_mp3_list()
    if not word_mp3_list:
        return  # 无有效单词时直接退出
    
    # 遍历每个单词进行练习
    for idx, item in enumerate(word_mp3_list, start=1):
        word = item["word"]
        mp3_path = item["mp3_path"]
        total_words = len(word_mp3_list)
        error_count = 0  # 错误次数计数器（每个单词重置为0）
        max_errors = 3   # 最大错误次数（超过则提示答案）
        
        print(f"="*40)
        print(f"📝 第 {idx}/{total_words} 个单词")
        print("="*40)
        
        # 循环：播放音频→输入拼写→验证（直到正确或3次错误）
        while True:
            # 1. 播放单词音频
            print(f"\n🔊 正在播放单词发音...")
            play_mp3(mp3_path)
            
            # 2. 显示横线提示并获取用户输入
            show_dash(word)
            user_input = input("✏️ 请输入你听到的单词：").strip()
            correct_word = word.lower()  # 统一小写对比，忽略大小写差异
            
            # 3. 验证拼写结果
            if user_input.lower() == correct_word:
                print(f"\n🎉 恭喜！拼写正确！")
                time.sleep(1.5)  # 短暂停顿，让用户确认结果
                break  # 正确则跳出循环，进入下一个单词
            
            else:
                error_count += 1
                # 若未达3次错误：提示错误并重新尝试
                if error_count < max_errors:
                    print(f"\n❌ 拼写错误，请重新尝试～")
                    time.sleep(1)
                # 达3次错误：提示正确答案并跳转
                else:
                    print(f"\n❌ 已连续3次错误，正确答案是：【{word}】")
                    time.sleep(2)  # 给用户时间记忆正确答案
                    break
    
    # 所有单词练习完成
    print(f"\n" + "="*50)
    print("🏆 所有单词拼写练习已完成！继续加油哦～")
    print("="*50)
    # 关闭pygame音频设备
    pygame.mixer.quit()

# 启动拼写练习
if __name__ == "__main__":
    spelling_practice()