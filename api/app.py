from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import uvicorn
from PIL import Image
import io
import requests
import os
import base64
import time
import tempfile
from typing import List
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取 HuggingFace API Token
HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN')
if not HUGGINGFACE_TOKEN:
    print("警告：未设置 HUGGINGFACE_TOKEN 环境变量，翻译功能可能无法正常工作")

app = FastAPI()

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.imageprompt.vip",
        "https://imageprompt.vip",
        "http://localhost:3000",
        "https://imageprompt.vercel.app",
        "https://imageprompt-production.up.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hugging Face API 配置
HF_TOKEN = "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"

def call_huggingface_api(api_url: str, image_data: bytes, max_retries: int = 5) -> dict:
    """
    调用 Hugging Face API 的通用函数，包含重试机制和增强的错误处理
    """
    # 将图片转换为base64编码
    encoded_image = base64.b64encode(image_data).decode('utf-8')
    
    # 准备请求数据
    payload = {
        "inputs": encoded_image
    }
    
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    
    retry_delay = 2  # 初始重试延迟（秒）
    
    for attempt in range(max_retries):
        try:
            print(f"发送请求到 {api_url}... (尝试 {attempt + 1}/{max_retries})")
            response = requests.post(
                api_url, 
                headers=headers, 
                json=payload,  # 使用json参数而不是data
                timeout=60  # 增加超时时间到60秒
            )
            
            # 打印响应状态和头信息
            print(f"API响应状态码: {response.status_code}")
            print(f"API响应头: {response.headers}")
            
            if response.status_code == 503:
                print(f"服务暂时不可用 (503)，响应内容: {response.text}")
                if attempt < max_retries - 1:
                    print(f"将在 {retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                    continue
            
            # 检查其他可重试的状态码
            if response.status_code in [429, 502, 504]:
                print(f"收到可重试的状态码 {response.status_code}，响应内容: {response.text}")
                if attempt < max_retries - 1:
                    print(f"将在 {retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
            
            response.raise_for_status()
            
            # 尝试解析JSON响应
            try:
                result = response.json()
                print(f"API响应JSON成功解析: {result}")
            except Exception as e:
                print(f"API响应JSON解析失败: {str(e)}, 原始响应: {response.text}")
                if attempt < max_retries - 1:
                    print(f"将在 {retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    raise HTTPException(status_code=502, detail="Invalid API response format")
            
            if isinstance(result, list) and len(result) > 0:
                return result[0]
            else:
                return result  # 返回任何格式的响应
                
        except requests.Timeout:
            print(f"请求超时，已经尝试 {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                print(f"将在 {retry_delay}秒后重试...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            raise HTTPException(status_code=504, detail="请求超时")
            
        except requests.HTTPError as e:
            print(f"HTTP错误: {str(e)}, 状态码: {response.status_code}, 响应: {response.text}")
            if attempt < max_retries - 1 and response.status_code in [503, 502, 500, 429, 504]:
                print(f"将在 {retry_delay}秒后重试...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            raise HTTPException(
                status_code=response.status_code,
                detail=f"API错误: {response.text}"
            )
            
        except Exception as e:
            print(f"发生未知错误: {str(e)}, 类型: {type(e)}")
            if attempt < max_retries - 1:
                print(f"将在 {retry_delay}秒后重试...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            raise
    
    raise HTTPException(status_code=503, detail="服务暂时不可用，请稍后重试")

def translate_to_chinese(text: str) -> str:
    """
    将英文翻译为中文
    """
    try:
        print(f"正在翻译文本为中文: {text}")
        translate_url = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-en-zh"
        headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_TOKEN')}"}
        response = requests.post(translate_url, headers=headers, json={"inputs": text})
        response.raise_for_status()
        result = response.json()
        translated = result[0]['translation_text']
        print(f"翻译结果: {translated}")
        return translated
    except Exception as e:
        print(f"翻译失败: {str(e)}")
        return text

def translate_to_english(text: str) -> str:
    """
    将中文翻译为英文
    """
    try:
        print(f"正在翻译文本为英文: {text}")
        translate_url = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-zh-en"
        headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_TOKEN')}"}
        response = requests.post(translate_url, headers=headers, json={"inputs": text})
        response.raise_for_status()
        result = response.json()
        translated = result[0]['translation_text']
        print(f"翻译结果: {translated}")
        return translated
    except Exception as e:
        print(f"翻译失败: {str(e)}")
        return text

# 添加图片代理路由
@app.get("/api/proxy/image")
async def proxy_image(url: str = Query(...)):
    try:
        # 移除URL前面可能存在的@符号
        if url.startswith('@'):
            url = url[1:]
            print(f"移除了URL中的@符号")
        
        # 验证URL
        if not url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="Invalid URL scheme")

        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            print(f"开始请求图片: {url}")
            response = requests.get(url, headers=headers, timeout=15, stream=True)
            response.raise_for_status()
            print(f"图片请求成功，状态码: {response.status_code}")
        except requests.Timeout:
            raise HTTPException(status_code=504, detail="Image fetch timeout")
        except requests.HTTPError as e:
            print(f"HTTP错误: {str(e)}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Failed to fetch image: {str(e)}")
        except Exception as e:
            print(f"请求失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch image: {str(e)}")

        # 验证内容类型 - 更宽容的检查
        content_type = response.headers.get('content-type', '')
        print(f"原始内容类型: {content_type}")
        
        # 尝试通过文件内容判断图片类型
        try:
            img = Image.open(io.BytesIO(response.content))
            actual_content_type = f"image/{img.format.lower()}" if img.format else "image/jpeg"
            
            # 使用通过内容检测到的MIME类型，而不是响应头中的类型
            content_type = actual_content_type
            print(f"检测到图片类型: {content_type}, 格式: {img.format}")
        except Exception as e:
            print(f"图片内容检测失败: {str(e)}")
            if not content_type.startswith('image/'):
                # 尝试通过文件扩展名判断
                if url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')):
                    print("通过文件扩展名判断为图片")
                    ext = url.split('.')[-1].lower()
                    content_type = f"image/{ext}"
                else:
                    raise HTTPException(status_code=400, detail="URL does not point to a valid image")

        # 验证文件大小
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="Image size exceeds 10MB limit")

        # 返回图片内容
        return Response(
            content=response.content,
            media_type=content_type,
            headers={
                'Cache-Control': 'public, max-age=31536000',
                'Access-Control-Allow-Origin': '*'
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"代理图片失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/joycaption/upload")
async def generate_joycaption(files: UploadFile = File(...), language: str = 'en'):  
    """
    上传图片并生成描述
    """
    print(f"接收到图片描述请求，语言：{language}")
    
    try:
        # 读取上传的文件内容
        contents = await files.read()
        print(f"图片大小: {len(contents)} bytes")
        
        try:
            # 处理图片
            try:
                image = Image.open(io.BytesIO(contents))
            except Exception as e:
                print(f"无法打开图片: {str(e)}")
                raise HTTPException(status_code=400, detail="Invalid image format")

            if image.mode != 'RGB':
                try:
                    image = image.convert('RGB')
                except Exception as e:
                    print(f"图片转换失败: {str(e)}")
                    raise HTTPException(status_code=400, detail="Failed to process image")
            
            # 将图片转换为字节流
            try:
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='JPEG')
                img_byte_arr = img_byte_arr.getvalue()
            except Exception as e:
                print(f"图片编码失败: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to encode image")
            
            # 发送请求到 Hugging Face API
            # 使用不同的模型
            API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
            try:
                result = call_huggingface_api(API_URL, img_byte_arr)
            except HTTPException:
                raise
            except Exception as e:
                print(f"API调用失败: {str(e)}")
                raise HTTPException(status_code=502, detail="Failed to call external API")
            
            # 处理不同格式的API响应
            caption = ""
            if isinstance(result, dict):
                caption = result.get('generated_text', '')
            elif isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict):
                    caption = result[0].get('generated_text', '')
                elif isinstance(result[0], str):
                    caption = result[0]
            elif isinstance(result, str):
                caption = result
            
            print(f"提取的caption: '{caption}'")
            
            if not caption:
                print("API返回但没有生成描述，尝试使用备用方法解析")
                # 尝试在整个响应中寻找描述
                try:
                    # 将结果转为字符串并查找
                    result_str = str(result)
                    import re
                    # 尝试匹配常见的描述模式
                    matches = re.findall(r'"([^"]+)"', result_str)
                    if matches:
                        # 使用最长的匹配作为caption
                        caption = max(matches, key=len)
                        print(f"通过正则表达式找到描述: {caption}")
                except Exception as e:
                    print(f"备用解析失败: {str(e)}")
            
            if not caption:
                raise HTTPException(
                    status_code=502,
                    detail="No caption generated from API"
                )
            
            print("原始API返回:", caption)  
            
            # 只有当明确要求中文时才翻译
            if language.lower() == 'zh':
                try:
                    caption = translate_to_chinese(caption)
                    print("翻译后结果:", caption)
                except Exception as e:
                    print(f"翻译失败: {str(e)}")
                    # 翻译失败时保持英文
            
            print(f"最终描述: {caption}")
            return {"caption": caption}
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"处理图片时出错: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"处理上传文件时出错: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid file upload")

@app.post("/api/interrogator/upload")
async def generate_interrogator(files: UploadFile = File(...), language: str = 'en'):  
    try:
        print(f"接收到 CLIP-Interrogator 请求，语言：{language}")
        
        # 验证文件类型
        content_type = files.content_type
        if not content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="只支持图片文件")
        
        contents = await files.read()
        print(f"图片大小: {len(contents)} bytes")
        
        try:
            # 处理图片
            try:
                image = Image.open(io.BytesIO(contents))
            except Exception as e:
                print(f"无法打开图片: {str(e)}")
                raise HTTPException(status_code=400, detail="Invalid image format")

            if image.mode != 'RGB':
                try:
                    image = image.convert('RGB')
                except Exception as e:
                    print(f"图片转换失败: {str(e)}")
                    raise HTTPException(status_code=400, detail="Failed to process image")
            
            # 将图片转换为字节流
            try:
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='JPEG')
                img_byte_arr = img_byte_arr.getvalue()
            except Exception as e:
                print(f"图片编码失败: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to encode image")
            
            # 发送请求到 Image Captioning API - 使用与JoyCaption相同的模型
            API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
            try:
                result = call_huggingface_api(API_URL, img_byte_arr)
            except HTTPException:
                raise
            except Exception as e:
                print(f"API调用失败: {str(e)}")
                raise HTTPException(status_code=502, detail="Failed to call external API")
            
            # 处理不同格式的API响应
            caption = ""
            if isinstance(result, dict):
                caption = result.get('generated_text', '')
            elif isinstance(result, list) and len(result) > 0:
                caption = result[0].get('generated_text', '')
            
            if not caption:
                raise HTTPException(
                    status_code=502,
                    detail="No caption generated from API"
                )
            
            print("原始API返回:", caption)  
            
            # 只有当明确要求中文时才翻译
            if language.lower() == 'zh':
                try:
                    caption = translate_to_chinese(caption)
                    print("翻译后结果:", caption)
                except Exception as e:
                    print(f"翻译失败: {str(e)}")
                    # 翻译失败时保持英文
            
            print(f"最终描述: {caption}")
            return {"caption": caption}
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"处理图片时出错: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test/image")
async def test_image_url(url: str = Query(...)):
    """
    测试图片URL并返回详细信息，用于诊断
    """
    try:
        # 首先移除可能的@符号
        if url.startswith('@'):
            cleaned_url = url[1:]
            print(f"移除了URL中的@符号: {url} -> {cleaned_url}")
            url = cleaned_url
            
        # 验证URL
        if not url.startswith(('http://', 'https://')):
            return {"error": "Invalid URL scheme", "url": url}

        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # 尝试获取URL响应
        try:
            response = requests.get(url, headers=headers, timeout=15, stream=True)
            status_code = response.status_code
            headers_dict = dict(response.headers)
            content_type = response.headers.get('content-type', 'unknown')
            content_length = response.headers.get('content-length', 'unknown')
            
            # 尝试判断内容
            image_detected = False
            image_format = "unknown"
            error_message = None
            
            try:
                img = Image.open(io.BytesIO(response.content))
                image_detected = True
                image_format = img.format
            except Exception as e:
                error_message = str(e)
            
            return {
                "url": url,
                "status_code": status_code,
                "headers": headers_dict,
                "content_type": content_type,
                "content_length": content_length,
                "image_detected": image_detected,
                "image_format": image_format,
                "error_message": error_message
            }
            
        except Exception as e:
            return {"error": str(e), "url": url}
            
    except Exception as e:
        return {"error": str(e), "url": url}

@app.get("/api/health")
async def health_check():
    """
    健康检查端点
    """
    return {"status": "ok", "version": "1.0.1"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088)
