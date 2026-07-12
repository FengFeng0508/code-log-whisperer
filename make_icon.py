from PIL import Image, ImageDraw

def create_app_icon():
    # 创建一个 256x256 的透明背景图像
    size = 256
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # 1. 画一个绿色的圆形底底板 (使用深绿色 #2E7D32)
    margin = 16
    draw.ellipse((margin, margin, size - margin, size - margin), fill='#2E7D32')

    # 2. 画一个终端符号 ">_"
    # 画 ">"
    draw.polygon([(80, 90), (120, 128), (80, 166), (95, 175), (140, 128), (95, 80)], fill='white')
    # 画 "_"
    draw.rectangle([(140, 160), (180, 175)], fill='white')

    # 保存为 Windows 支持的高清 ICO 格式
    image.save('app_icon.ico', format='ICO', sizes=[(256, 256)])
    print("✅ 专属图标已成功生成：app_icon.ico")

if __name__ == '__main__':
    create_app_icon()