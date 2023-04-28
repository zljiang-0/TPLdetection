# 导入 os 模块，用于执行命令行操作和文件操作
import os
# 导入 re 模块，用于正则表达式匹配
import re
# 导入 difflib 模块，用于模糊匹配
import difflib
# 导入 csv 模块，用于读写 csv 格式的文件
import csv

# 定义 APK 文件所在的文件夹路径
apk_dir = "../apks"

# 定义输出文件夹的路径
output_dir = "output"

# 定义 SDK 数据库的路径（假设是一个文本文件，每行一个 SDK 名称）
sdk_db_path = "sdk_db.csv"

# 读取 SDK 数据库中的所有 SDK 名称
with open(sdk_db_path, "r") as f:
    sdk_names = f.read().splitlines()

# 读取 SDK 数据库中的所有 SDK 信息
with open(sdk_db_path, "r") as f:
    reader = csv.reader(f)
    next(reader) # 跳过表头
    sdk_db = list(reader) # 将 csv 文件转换为列表

# 定义一个函数，用于从字符串中提取 SDK 名称
def extract_sdk_name(string):
    # 去掉字符串中的空格和标点符号
    string = re.sub(r"\s+|\W+", "", string)
    if len(string) > 2:
        # 遍历所有的 SDK 信息
        for entry in sdk_db:
            path, name, company, url = entry
            # 去掉 SDK 路径和名称中的空格和标点符号
            path = re.sub(r"\s+|\W+", "", path)
            name = re.sub(r"\s+|\W+", "", name)
            # 如果字符串包含 SDK 路径或名称，或者 SDK 路径或名称包含字符串，或者两者有较高的相似度，则返回 SDK 信息
            if len(path) > 2:
                # if string in path or path in string or difflib.SequenceMatcher(None, string, path).ratio() > 0.8:
                if difflib.SequenceMatcher(None, string, path).ratio() > 0.8:
                    return entry
            if len(name) > 2:
                # if string in name or name in string or difflib.SequenceMatcher(None, string, name).ratio() > 0.8:
                if difflib.SequenceMatcher(None, string, name).ratio() > 0.8:
                    return entry
    # 如果没有找到匹配的 SDK 信息，则返回 None
    return None

# 遍历 APK 文件所在的文件夹
for apk_file in os.listdir(apk_dir):
    # 拼接 APK 文件的完整路径
    apk_path = os.path.join(apk_dir, apk_file)
    # 判断是否是 APK 文件
    if apk_path.endswith(".apk"):
        # 判断反编译 APK 文件是否存在
        if os.path.exists(os.path.join(output_dir, apk_file)) == 0:
            # 使用 jadx 反编译 APK 文件
            os.system(f"../jadx-1.4.6/bin/jadx -d {output_dir}/{apk_file} {apk_path}")
        # 定义 SDK 信息列表
        sdk_info = []
        # 拼接 AndroidManifest.xml 文件的完整路径
        manifest_path = os.path.join(output_dir, apk_file, "resources", "AndroidManifest.xml")
        # 判断是否存在 AndroidManifest.xml 文件
        if os.path.exists(manifest_path):
            # 打开 AndroidManifest.xml 文件
            with open(manifest_path, "r") as f:
                # 读取文件内容
                content = f.read()
                # 查找所有 meta-data 标签中的键值对
                matches = re.findall(r'<meta-data android:name="(.+?)" android:value="(.+?)"', content)
                # 遍历每个键值对
                for key, value in matches:
                    # 提取键中的 SDK 名称（去掉 KEY SECRET ID VERSION 等关键字）
                    key_sdk_name = extract_sdk_name(re.sub(r"KEY|SECRET|ID|VERSION", "", key))
                    # 提取值中的 SDK 名称（去掉 KEY SECRET ID VERSION 等关键字）
                    value_sdk_name = extract_sdk_name(re.sub(r"KEY|SECRET|ID|VERSION", "", value))
                    # 如果键或值中有 SDK 名称
                    if key_sdk_name or value_sdk_name:
                        # 将 SDK 名称和键值对添加到 SDK 信息列表中（去重）
                        if (key_sdk_name or value_sdk_name) not in sdk_info:
                            sdk_info.append((key_sdk_name or value_sdk_name))
                            print(f"{key}: {value} 1 ")
        # 拼接源代码文件夹的完整路径
        source_path = os.path.join(output_dir, apk_file, "sources")
        # 判断是否存在源代码文件夹
        if os.path.exists(source_path):
            # 遍历源代码文件夹下的所有文件
            for root, dirs, files in os.walk(source_path):
                # 遍历每个文件
                for file in files:
                    # 判断是否是 Java 文件
                    if file.endswith(".java"):
                        # 拼接 Java 文件的完整路径
                        java_path = os.path.join(root, file)
                        # 打开 Java 文件
                        with open(java_path, "r") as f:
                            # 读取文件内容
                            content = f.read()
                            # 查找所有 private static final String 定义的变量
                            matches = re.findall(r"private static final String (\w+) = \"(.+?)\";", content)
                            # 遍历每个变量
                            for name, value in matches:
                                # 提取变量名中的 SDK 名称（去掉 APPID SDK APP_ID KEY UNIT_ID UID TOKEN VERSION 等关键字）
                                name_sdk_name = extract_sdk_name(re.sub(r"APPID|SDK|APP_ID|KEY|UNIT_ID|UID|TOKEN|VERSION|TAG|NAME", "", name))
                                # 提取变量值中的 SDK 名称（去掉 APPID SDK APP_ID KEY UNIT_ID UID TOKEN VERSION 等关键字）
                                value_sdk_name = extract_sdk_name(re.sub(r"APPID|SDK|APP_ID|KEY|UNIT_ID|UID|TOKEN|VERSION|TAG|NAME", "", value))
                                # 如果变量名或值中有 SDK 名称
                                if name_sdk_name or value_sdk_name:
                                    # 将 SDK 名称和变量定义语句添加到 SDK 信息列表中（去重）
                                    if (name_sdk_name or value_sdk_name) not in sdk_info:
                                        sdk_info.append((name_sdk_name or value_sdk_name))
                                        print(f"{name}:{name_sdk_name} {value}:{value_sdk_name} = ")
                        # 查找所有类名
                        matches = re.findall(r"class (\w+)", content)
                        # 遍历每个类名
                        for class_name in matches:
                            # 提取类名中的 SDK 名称（去掉顶级域名，取三级 class，跳过 APK 本身的包名和 Android 与 java 自带的包）
                            class_sdk_name = extract_sdk_name(re.sub(r"^(?:\w+\.){3}|^(?:com\.whatsapp\.android\.|android\.|androidx\.|java\.)", "", class_name))
                            # 如果类名中有 SDK 名称
                            if class_sdk_name:
                                # 将 SDK 名称和类名添加到 SDK 信息列表中（去重）
                                if (class_sdk_name) not in sdk_info:
                                    sdk_info.append((class_sdk_name))
                                    print(f"{class_name}:{class_sdk_name} 2 ")
        # 拼接 lib 目录的完整路径
        lib_path = os.path.join(output_dir, apk_file, "lib")
        # 判断是否存在 lib 目录
        if os.path.exists(lib_path):
            # 遍历 lib 目录下的所有文件
            for root, dirs, files in os.walk(lib_path):
                # 遍历每个文件
                for file in files:
                    # 判断是否是 .so 文件
                    if file.endswith(".so"):
                        # 提取文件名中的 SDK 名称（去掉 .so 后缀，利用正则提取版本信息）
                        file_sdk_name = extract_sdk_name(re.sub(r"\.so$|\d+\.\d+\.\d+", "", file))
                        # 如果文件名中有 SDK 名称
                        if file_sdk_name:
                            # 将 SDK 名称和文件名添加到 SDK 信息列表中（去重）
                            if (file_sdk_name) not in sdk_info:
                                sdk_info.append((file_sdk_name))
                                print(f"{file_sdk_name} 3 ")
        # 打印 APK 文件名和对应的 SDK 信息列表
        print(f"{apk_file}: {sdk_info}")
