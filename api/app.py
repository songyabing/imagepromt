from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Form
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
import traceback
import asyncio
import re

# 加载环境变量
load_dotenv()

# 直接硬编码HuggingFace API Token
HUGGINGFACE_TOKEN =  "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"
print("使用硬编码的HUGGINGFACE_TOKEN进行API调用")

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
        headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
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
        headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
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

        # 添加更丰富的请求头，模拟真实浏览器行为
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Referer': 'https://imageprompt.vip/',
            'Sec-Fetch-Dest': 'image',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site'
        }

        try:
            # 记录详细日志，帮助诊断问题
            print(f"开始请求图片URL: {url}")
            print(f"请求头: {headers}")
            
            # 使用会话来处理cookies和重定向
            session = requests.Session()
            response = session.get(
                url, 
                headers=headers, 
                timeout=20,  # 增加超时时间
                stream=True,
                allow_redirects=True,  # 允许重定向
                verify=True  # SSL验证
            )
            
            # 记录响应信息
            print(f"响应状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            print(f"响应URL(可能重定向): {response.url}")
            
            response.raise_for_status()
            print(f"图片请求成功")
        except requests.Timeout:
            print(f"请求超时: {url}")
            raise HTTPException(status_code=504, detail="Image fetch timeout")
        except requests.TooManyRedirects:
            print(f"重定向过多: {url}")
            raise HTTPException(status_code=400, detail="Too many redirects")
        except requests.SSLError as e:
            print(f"SSL错误: {str(e)}")
            # 尝试不验证SSL
            try:
                print("尝试不验证SSL重新请求...")
                response = session.get(url, headers=headers, timeout=20, stream=True, verify=False)
                response.raise_for_status()
                print("不验证SSL的请求成功")
            except Exception as retry_e:
                print(f"不验证SSL的重试也失败: {str(retry_e)}")
                raise HTTPException(status_code=502, detail=f"SSL Error: {str(e)}")
        except requests.HTTPError as e:
            print(f"HTTP错误: {str(e)}")
            raise HTTPException(
                status_code=e.response.status_code, 
                detail=f"Failed to fetch image: {str(e)}"
            )
        except Exception as e:
            print(f"请求失败: {str(e)}, 类型: {type(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch image: {str(e)}")

        # 验证内容类型 - 更宽容的检查
        content_type = response.headers.get('content-type', '')
        print(f"原始内容类型: {content_type}")
        
        # 读取内容
        content = response.content
        if not content:
            print("响应内容为空")
            raise HTTPException(status_code=400, detail="Empty response")
            
        print(f"响应内容大小: {len(content)} bytes")
        
        # 尝试通过文件内容判断图片类型
        try:
            img = Image.open(io.BytesIO(content))
            actual_content_type = f"image/{img.format.lower()}" if img.format else "image/jpeg"
            
            # 使用通过内容检测到的MIME类型，而不是响应头中的类型
            content_type = actual_content_type
            print(f"检测到图片类型: {content_type}, 格式: {img.format}, 尺寸: {img.size}")
            
            # 如果图片太大，进行压缩处理
            if len(content) > 5 * 1024 * 1024:  # 如果大于5MB
                print("图片过大，进行压缩处理")
                # 将大图片缩小到合理尺寸
                max_size = (1200, 1200)
                img.thumbnail(max_size)
                
                # 压缩质量
                output = io.BytesIO()
                if img.format == 'JPEG' or img.format == 'JPG':
                    img.save(output, format=img.format, quality=85)
                elif img.format == 'PNG':
                    img.save(output, format=img.format, optimize=True)
                else:
                    img.save(output, format=img.format)
                
                content = output.getvalue()
                print(f"压缩后大小: {len(content)} bytes")
        except Exception as e:
            print(f"图片内容检测/处理失败: {str(e)}")
            if not content_type.startswith('image/'):
                # 尝试通过文件扩展名判断
                if url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg')):
                    print("通过文件扩展名判断为图片")
                    ext = url.split('.')[-1].lower()
                    content_type = f"image/{ext}"
                else:
                    print("无法确定内容是图片")
                    raise HTTPException(status_code=400, detail="URL does not point to a valid image")

        # 验证文件大小
        if len(content) > 10 * 1024 * 1024:  # 10MB
            print("图片大小超过限制")
            raise HTTPException(status_code=400, detail="Image size exceeds 10MB limit")

        # 返回图片内容
        print("返回图片内容")
        return Response(
            content=content,
            media_type=content_type,
            headers={
                'Cache-Control': 'public, max-age=31536000',
                'Access-Control-Allow-Origin': '*',
                'X-Image-Source': url,
                'X-Image-Size': str(len(content))
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"代理图片失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/joycaption/upload")
async def upload_joycaption(files: List[UploadFile] = File(...), language: str = Form(...)):
    try:
        print(f"接收到新的JoyCaption请求，语言: {language}")
        start_time = time.time()  # 记录开始时间
        
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        file = files[0]
        print(f"处理文件: {file.filename}, 内容类型: {file.content_type}")
        
        # 验证文件类型
        if not file.content_type.startswith('image/'):
            print(f"无效的文件类型: {file.content_type}")
            raise HTTPException(status_code=400, detail="Only image files are supported")
        
        # 读取文件内容
        try:
            content = await file.read()
            file_size = len(content)
            print(f"图片大小: {file_size / 1024:.2f} KB")
            
            if file_size > 10 * 1024 * 1024:  # 10MB
                raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
            
            if file_size == 0:
                raise HTTPException(status_code=400, detail="Empty file")
                
            # 使用PIL验证图片格式
            try:
                img = Image.open(io.BytesIO(content))
                img_format = img.format
                img_size = img.size
                print(f"图片格式: {img_format}, 尺寸: {img_size}")
            except Exception as e:
                print(f"图片验证失败: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")
                
            # 转换为base64
            base64_str = base64.b64encode(content).decode('utf-8')
            print("图片已成功转换为base64")
            
            # 调用Hugging Face API
            API_URL = "https://api-inference.huggingface.co/models/joytag/JoyCaption"
            headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
            payload = {"inputs": {"image": base64_str, "language": language}}
            
            print("开始请求HuggingFace API...")
            
            # 增加重试和超时设置
            max_retries = 3
            retry_count = 0
            timeout_value = 50  # 增加超时时间到50秒
            
            while retry_count < max_retries:
                try:
                    response = requests.post(
                        API_URL, 
                        headers=headers, 
                        json=payload,
                        timeout=timeout_value
                    )
                    print(f"API响应状态码: {response.status_code}")
                    
                    if response.status_code == 200:
                        try:
                            result = response.json()
                            
                            # 增强对不同响应格式的处理
                            caption = ""
                            if isinstance(result, list) and len(result) > 0:
                                if isinstance(result[0], dict):
                                    caption = result[0].get('caption', result[0].get('generated_text', ''))
                                elif isinstance(result[0], str):
                                    caption = result[0]
                            elif isinstance(result, dict):
                                caption = result.get('caption', result.get('generated_text', ''))
                            
                            print(f"解析到的描述: {caption}")
                            
                            if not caption:
                                print("未从API响应中解析到描述")
                                raise HTTPException(status_code=500, detail="No caption in API response")
                                
                            elapsed_time = time.time() - start_time
                            print(f"请求完成，总耗时: {elapsed_time:.2f}秒")
                            return {"caption": caption, "elapsed_time": elapsed_time}
                        except ValueError as e:
                            print(f"无法解析JSON响应: {str(e)}")
                            print(f"原始响应: {response.text}")
                            raise HTTPException(status_code=500, detail=f"Failed to parse API response: {str(e)}")
                    elif response.status_code == 503:
                        # 模型正在加载，尝试重试
                        retry_count += 1
                        wait_time = 2 ** retry_count  # 指数退避
                        print(f"模型正在加载，等待{wait_time}秒后重试 ({retry_count}/{max_retries})")
                        time.sleep(wait_time)
                    else:
                        print(f"API错误，状态码: {response.status_code}")
                        try:
                            error_msg = response.json()
                            print(f"错误详情: {error_msg}")
                        except:
                            error_msg = response.text
                            print(f"错误响应: {error_msg}")
                        
                        raise HTTPException(
                            status_code=response.status_code, 
                            detail=f"API error: {error_msg}"
                        )
                except requests.exceptions.Timeout:
                    retry_count += 1
                    if retry_count >= max_retries:
                        print(f"请求超时，已达到最大重试次数 {max_retries}")
                        raise HTTPException(status_code=504, detail="API request timed out after multiple retries")
                    
                    wait_time = 2 ** retry_count
                    print(f"请求超时，等待{wait_time}秒后重试 ({retry_count}/{max_retries})")
                    time.sleep(wait_time)
                except Exception as e:
                    print(f"请求出错: {str(e)}")
                    raise HTTPException(status_code=500, detail=f"Error calling API: {str(e)}")
            
            # 如果达到最大重试次数仍未成功
            raise HTTPException(status_code=500, detail="Failed after maximum retries")
            
        except Exception as e:
            print(f"文件处理错误: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        # 捕获所有其他异常
        print(f"处理请求时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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

async def query_huggingface(base64_image):
    """
    调用HuggingFace API获取图片描述，支持重试
    """
    API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
    max_retries = 3
    retry_delay = 2  # 初始延迟2秒
    
    # 构建请求数据
    payload = {
        "inputs": f"data:image/jpeg;base64,{base64_image}"
    }
    
    print(f"准备调用HuggingFace API，模型：Salesforce/blip-image-captioning-large")
    
    for attempt in range(max_retries):
        try:
            print(f"API调用尝试 {attempt + 1}/{max_retries}")
            
            response = requests.post(
                API_URL, 
                headers=headers, 
                json=payload,
                timeout=30  # 30秒超时
            )
            
            # 检查响应状态
            if response.status_code != 200:
                print(f"API返回错误状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
                
                # 检查是否需要等待模型加载
                if response.status_code == 503 and "loading" in response.text.lower():
                    wait_time = retry_delay * (2 ** attempt)  # 指数退避
                    print(f"模型正在加载，等待 {wait_time} 秒后重试")
                    await asyncio.sleep(wait_time)
                    continue
                    
                # 如果是最后一次尝试，抛出异常
                if attempt == max_retries - 1:
                    raise HTTPException(
                        status_code=502, 
                        detail=f"HuggingFace API错误: {response.status_code}, {response.text}"
                    )
                    
                # 否则继续重试
                wait_time = retry_delay * (2 ** attempt)
                await asyncio.sleep(wait_time)
                continue
            
            # 处理成功响应
            result = response.json()
            print(f"API调用成功，处理响应")
            print(f"原始响应: {result}")
            
            # 解析不同格式的响应
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
            
            # 如果没有找到caption，尝试备用解析方法
            if not caption:
                print("无法从标准格式中提取描述，尝试备用解析")
                try:
                    # 转换为字符串并用正则表达式查找
                    result_str = str(result)
                    # 尝试匹配引号中的文本
                    matches = re.findall(r'"([^"]+)"', result_str)
                    if matches:
                        # 使用最长的匹配作为caption
                        caption = max(matches, key=len)
                        print(f"通过正则表达式找到描述: {caption}")
                except Exception as e:
                    print(f"备用解析失败: {str(e)}")
            
            # 如果仍然没有找到描述，尝试将整个响应作为字符串
            if not caption and result:
                print("尝试将整个响应作为描述")
                try:
                    caption = str(result)
                    # 清理字符串
                    caption = caption.replace('[', '').replace(']', '').replace('{', '').replace('}', '')
                    caption = caption.replace("'", "").replace('"', "")
                    if 'generated_text' in caption:
                        # 提取generated_text之后的内容
                        caption = caption.split('generated_text:')[-1].strip()
                    caption = caption.strip()
                except Exception as e:
                    print(f"响应清理失败: {str(e)}")
            
            if caption:
                print(f"成功提取描述: '{caption}'")
                return caption
            else:
                print("无法从响应中提取有效描述")
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    print(f"等待 {wait_time} 秒后重试")
                    await asyncio.sleep(wait_time)
                else:
                    return "An image"  # 如果所有尝试都失败，返回一个默认值
                
        except Exception as e:
            print(f"API调用异常: {str(e)}")
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                print(f"等待 {wait_time} 秒后重试")
                await asyncio.sleep(wait_time)
            else:
                print("所有重试尝试都失败")
                # 如果是关键错误如认证问题，抛出异常
                if "unauthorized" in str(e).lower() or "authentication" in str(e).lower():
                    raise HTTPException(
                        status_code=401, 
                        detail="HuggingFace API 认证失败，请检查API密钥"
                    )
                # 否则返回一个默认值
                return "An image"
    
    # 如果出现意外情况导致循环结束但没有返回，使用默认值
    return "An image"

@app.get("/api/debug/image")
async def debug_image_url(url: str = Query(...)):
    """
    详细调试图片URL，测试不同的请求方法并返回完整诊断信息
    """
    try:
        print(f"\n[DEBUG] 开始诊断URL: {url}")
        
        # 移除URL前面可能存在的@符号
        if url.startswith('@'):
            url = url[1:]
            print(f"[DEBUG] 移除了URL中的@符号，现在是: {url}")
        
        # 验证URL
        if not url.startswith(('http://', 'https://')):
            return {"status": "error", "message": "Invalid URL scheme", "url": url}

        result = {
            "url": url,
            "tests": [],
            "successful_method": None,
            "image_detected": False,
            "image_info": None,
            "content_preview": None
        }
        
        # 测试方法1：基本请求
        try:
            print("[DEBUG] 测试方法1：基本请求")
            response = requests.get(url, timeout=10)
            test_result = {
                "method": "basic",
                "status_code": response.status_code,
                "content_type": response.headers.get('content-type'),
                "content_length": len(response.content),
                "success": response.status_code == 200
            }
            
            if test_result["success"]:
                try:
                    img = Image.open(io.BytesIO(response.content))
                    test_result["image_detected"] = True
                    test_result["image_format"] = img.format
                    test_result["image_size"] = img.size
                    result["image_detected"] = True
                    result["image_info"] = {
                        "format": img.format,
                        "size": img.size,
                        "mode": img.mode
                    }
                    result["successful_method"] = "basic"
                except Exception as e:
                    test_result["image_detected"] = False
                    test_result["image_error"] = str(e)
            
            result["tests"].append(test_result)
        except Exception as e:
            result["tests"].append({
                "method": "basic",
                "error": str(e),
                "success": False
            })
        
        # 测试方法2：带浏览器头的请求
        try:
            print("[DEBUG] 测试方法2：带浏览器头的请求")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'Referer': 'https://imageprompt.vip/'
            }
            response = requests.get(url, headers=headers, timeout=10)
            test_result = {
                "method": "browser_headers",
                "status_code": response.status_code,
                "content_type": response.headers.get('content-type'),
                "content_length": len(response.content),
                "success": response.status_code == 200
            }
            
            if test_result["success"] and not result["image_detected"]:
                try:
                    img = Image.open(io.BytesIO(response.content))
                    test_result["image_detected"] = True
                    test_result["image_format"] = img.format
                    test_result["image_size"] = img.size
                    result["image_detected"] = True
                    result["image_info"] = {
                        "format": img.format,
                        "size": img.size,
                        "mode": img.mode
                    }
                    result["successful_method"] = "browser_headers"
                except Exception as e:
                    test_result["image_detected"] = False
                    test_result["image_error"] = str(e)
            
            result["tests"].append(test_result)
        except Exception as e:
            result["tests"].append({
                "method": "browser_headers",
                "error": str(e),
                "success": False
            })
        
        # 测试方法3：带会话的请求
        try:
            print("[DEBUG] 测试方法3：带会话的请求")
            session = requests.Session()
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'
            }
            response = session.get(url, headers=headers, timeout=10, allow_redirects=True)
            test_result = {
                "method": "session",
                "status_code": response.status_code,
                "content_type": response.headers.get('content-type'),
                "content_length": len(response.content),
                "final_url": str(response.url),  # 记录可能重定向后的URL
                "success": response.status_code == 200
            }
            
            if test_result["success"] and not result["image_detected"]:
                try:
                    img = Image.open(io.BytesIO(response.content))
                    test_result["image_detected"] = True
                    test_result["image_format"] = img.format
                    test_result["image_size"] = img.size
                    result["image_detected"] = True
                    result["image_info"] = {
                        "format": img.format,
                        "size": img.size,
                        "mode": img.mode
                    }
                    result["successful_method"] = "session"
                except Exception as e:
                    test_result["image_detected"] = False
                    test_result["image_error"] = str(e)
            
            result["tests"].append(test_result)
        except Exception as e:
            result["tests"].append({
                "method": "session",
                "error": str(e),
                "success": False
            })

        # 测试方法4：不验证SSL的请求
        try:
            print("[DEBUG] 测试方法4：不验证SSL的请求")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            test_result = {
                "method": "no_ssl_verify",
                "status_code": response.status_code,
                "content_type": response.headers.get('content-type'),
                "content_length": len(response.content),
                "success": response.status_code == 200
            }
            
            if test_result["success"] and not result["image_detected"]:
                try:
                    img = Image.open(io.BytesIO(response.content))
                    test_result["image_detected"] = True
                    test_result["image_format"] = img.format
                    test_result["image_size"] = img.size
                    result["image_detected"] = True
                    result["image_info"] = {
                        "format": img.format,
                        "size": img.size,
                        "mode": img.mode
                    }
                    result["successful_method"] = "no_ssl_verify"
                except Exception as e:
                    test_result["image_detected"] = False
                    test_result["image_error"] = str(e)
            
            result["tests"].append(test_result)
        except Exception as e:
            result["tests"].append({
                "method": "no_ssl_verify",
                "error": str(e),
                "success": False
            })
            
        # 对于成功的方法，保存少量内容预览（用于检查是否真的是图片）
        if result["successful_method"]:
            # 找到成功的测试
            for test in result["tests"]:
                if test.get("method") == result["successful_method"]:
                    # 仅保存前100字节的十六进制表示，用于检查文件头
                    if "content_length" in test and test["content_length"] > 0:
                        for response in [r for r in [requests.get(url, timeout=10, stream=True)] if r.status_code == 200]:
                            content_preview = response.content[:100].hex()
                            result["content_preview"] = content_preview
                            # 分析文件头以确认是否为图片
                            is_jpg = content_preview.startswith("ffd8")
                            is_png = content_preview.startswith("89504e47")
                            is_gif = content_preview.startswith("474946")
                            is_webp = "57454250" in content_preview[:24]
                            result["file_signatures"] = {
                                "is_jpg": is_jpg,
                                "is_png": is_png, 
                                "is_gif": is_gif,
                                "is_webp": is_webp
                            }
                            break
                    break

        print(f"[DEBUG] 诊断完成: 检测到图片 = {result['image_detected']}, 成功方法 = {result['successful_method']}")
        return result
            
    except Exception as e:
        print(f"[DEBUG] 总体诊断失败: {str(e)}")
        return {
            "status": "error",
            "message": f"诊断过程中发生错误: {str(e)}",
            "url": url
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088)
