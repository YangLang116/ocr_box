import os
import shutil

class TesseractFinder:
    """查找系统中安装的Tesseract OCR引擎"""
    
    @staticmethod
    def find_tesseract_path():
        """
        查找Tesseract OCR引擎的路径
        
        优先尝试从系统PATH中查找, 然后是默认安装路径
        
        Returns:
            str: Tesseract可执行文件路径, 如果找不到则返回空字符串
        """
        # 首先尝试从PATH中查找tesseract
        tesseract_cmd = shutil.which('tesseract')
        if tesseract_cmd:
            return tesseract_cmd
        
        # 如果PATH中找不到, 尝试常见的安装路径
        possible_paths = [
            # Windows 默认路径
            r'',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            # Linux 常见路径
            '/usr/bin/tesseract',
            '/usr/local/bin/tesseract',
            # macOS 通过 Homebrew 安装的路径
            '/usr/local/Cellar/tesseract/*/bin/tesseract',
            '/opt/homebrew/bin/tesseract'
        ]
        
        for path in possible_paths:
            # 处理带通配符的路径(用于macOS的Homebrew安装)
            if '*' in path:
                import glob
                matching_paths = glob.glob(path)
                if matching_paths:
                    # 获取最新版本
                    return sorted(matching_paths)[-1]
            elif os.path.exists(path):
                return path
        
        # 如果所有路径都不存在, 返回空
        return ""
    
    @staticmethod
    def check_tesseract_languages(tesseract_path):
        """
        检查Tesseract支持的语言包
        
        Args:
            tesseract_path: Tesseract可执行文件路径
            
        Returns:
            list: 支持的语言列表, 如果无法检测则返回空列表
        """
        if not tesseract_path or not os.path.exists(tesseract_path):
            return []
        
        languages = []
        
        # 方法1: 使用命令行参数 --list-langs 检测
        try:
            import subprocess
            # 运行tesseract --list-langs命令
            process = subprocess.Popen(
                [tesseract_path, '--list-langs'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            stdout, stderr = process.communicate()
            
            # Tesseract将语言列表输出到stderr
            if stderr:
                # 分割输出并删除第一行(通常是"List of available languages:")
                langs_output = stderr.strip().split('\n')
                if len(langs_output) > 1:
                    languages = [lang.strip() for lang in langs_output[1:]]
        except Exception as e:
            print(f"通过命令行检查Tesseract语言包出错: {str(e)}")
        
        # 如果方法1失败, 尝试方法2: 直接检查Tesseract安装目录中的语言数据文件
        if not languages:
            try:
                # 从Tesseract路径推断出可能的tessdata目录位置
                tesseract_dir = os.path.dirname(tesseract_path)
                possible_tessdata_dirs = [
                    os.path.join(tesseract_dir, 'tessdata'),  # 标准位置
                    os.path.join(tesseract_dir, '..', 'tessdata'),  # 上级目录
                    os.path.join(tesseract_dir, '..', 'share', 'tessdata'),  # Linux/macOS常见位置
                    os.path.join(tesseract_dir, '..', '..', 'share', 'tessdata'),  # 另一种常见位置
                ]
                
                # 检查系统环境变量中的TESSDATA_PREFIX
                if 'TESSDATA_PREFIX' in os.environ:
                    possible_tessdata_dirs.insert(0, os.environ['TESSDATA_PREFIX'])
                
                # 检查每个可能的tessdata目录
                for tessdata_dir in possible_tessdata_dirs:
                    if os.path.isdir(tessdata_dir):
                        # 查找所有.traineddata文件
                        for file in os.listdir(tessdata_dir):
                            if file.endswith('.traineddata'):
                                lang = file.replace('.traineddata', '')
                                languages.append(lang)
                        if languages:
                            break
            except Exception as e:
                print(f"通过文件检查Tesseract语言包出错: {str(e)}")
        
        return languages
    
    @staticmethod
    def has_chinese_support(tesseract_path):
        """
        检查Tesseract是否支持中文
        
        Args:
            tesseract_path: Tesseract可执行文件路径
            
        Returns:
            bool: 是否支持中文
        """
        # 获取所有支持的语言
        langs = TesseractFinder.check_tesseract_languages(tesseract_path)
        
        # 不同版本的Tesseract可能使用不同的中文语言标识
        chinese_lang_codes = [
            'chi_sim',       # 简体中文(标准)
            'chi_tra',       # 繁体中文(标准)
            'chinese',       # 一些旧版本使用
            'chinese_simplified',  # 一些版本使用
            'chinese_traditional',  # 一些版本使用
            'zh',            # ISO语言代码
            'zh-Hans',       # 简体中文(ISO)
            'zh-Hant',       # 繁体中文(ISO)
            'zh_CN',         # 中国大陆(地区代码)
            'zh_TW',         # 台湾(地区代码)
            'zh_HK'          # 香港(地区代码)
        ]
        
        # 检查是否有任何中文语言代码在支持的语言列表中
        has_chinese = any(lang in langs for lang in chinese_lang_codes)
        
        # 调试信息
        print(f"检测到的语言: {langs}")
        print(f"是否支持中文: {has_chinese}")
        
        return has_chinese


if __name__ == "__main__":
    # 测试查找Tesseract
    path = TesseractFinder.find_tesseract_path()
    print(f"Tesseract路径: {path}")
    
    if path:
        langs = TesseractFinder.check_tesseract_languages(path)
        print(f"支持的语言: {langs}")
        
        has_chinese = TesseractFinder.has_chinese_support(path)
        print(f"支持中文: {has_chinese}") 