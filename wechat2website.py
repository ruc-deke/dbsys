import os
import requests
from bs4 import BeautifulSoup
import markdown
import re

def download_image(img_url, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    img_name = img_url.split("/")[-1].split("?")[0]  
    img_path = os.path.join(output_folder, img_name)
    
    response = requests.get(img_url, stream=True)
    if response.status_code == 200:
        with open(img_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        return img_name  
    return None

def wechat_to_markdown(url, output_folder="images"):
    response = requests.get(url)
    if response.status_code != 200:
        print("无法获取微信公众号文章")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 获取标题
    title_tag = soup.find('h1')
    title = title_tag.text.strip() if title_tag else "Untitled"
    
    # 获取正文
    content_div = soup.find('div', class_='rich_media_content')
    if not content_div:
        print("找不到文章内容")
        return None
    
    paragraphs = content_div.find_all(['p', 'span'])
    content = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
    
    # 获取所有图片
    images = content_div.find_all('img')
    image_md_list = []
    for img in images:
        img_url = img.get('data-src') or img.get('src')
        if img_url:
            img_name = download_image(img_url, output_folder)
            if img_name:
                image_md_list.append(f'![{img_name}](./{output_folder}/{img_name})')
    
    # 组合 Markdown 内容
    md_content = f"""---
title: {title}
date: 2024-09-26
image:
  focal_point: 'top'
profile: false
---

{content}

{'\n'.join(image_md_list)}
"""
    
    # 生成 Markdown 文件
    md_filename = f"{title.replace(' ', '_')}.md"
    with open(md_filename, 'w', encoding='utf-8') as md_file:
        md_file.write(md_content)
    
    print(f"Markdown 文件已生成: {md_filename}")
    return md_filename

# 示例使用
wechat_url = "https://mp.weixin.qq.com/s/1hbKSzbiyMn3RzpvMOe-1w"
wechat_to_markdown(wechat_url)
