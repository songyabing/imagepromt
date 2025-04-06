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
        "https://imagepromt.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hugging Face API 配置
HF_TOKEN = "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"

def call_huggingface_api(api_url: str, image_data: bytes, max_retries: int = 3) -> dict:
    """
    调用 Hugging Face API 的通用函数，包含重试机制
    """
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    retry_delay = 2  # 初始重试延迟（秒）
    
    for attempt in range(max_retries):
        try:
            print(f"发送请求到 {api_url}... (尝试 {attempt + 1}/{max_retries})")
            response = requests.post(api_url, headers=headers, data=image_data, timeout=30)
            
            if response.status_code == 503:
                if attempt < max_retries - 1:
                    print(f"服务暂时不可用，{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                    continue
            
            response.raise_for_status()
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                return result[0]
            else:
                raise ValueError("API 返回了无效的响应格式")
                
        except requests.Timeout:
            if attempt < max_retries - 1:
                print(f"请求超时，{retry_delay}秒后重试...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            raise HTTPException(status_code=504, detail="请求超时")
            
        except requests.HTTPError as e:
            if attempt < max_retries - 1 and response.status_code in [503, 502, 500]:
                print(f"HTTP错误 {response.status_code}，{retry_delay}秒后重试...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            raise HTTPException(
                status_code=response.status_code,
                detail=f"API错误: {response.text}"
            )
            
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"发生错误: {str(e)}，{retry_delay}秒后重试...")
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
        # 验证URL
        if not url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="Invalid URL scheme")

        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10, stream=True)
            response.raise_for_status()
        except requests.Timeout:
            raise HTTPException(status_code=504, detail="Image fetch timeout")
        except requests.HTTPError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Failed to fetch image: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch image: {str(e)}")

        # 验证内容类型
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
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
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/joycaption/upload")
async def generate_joycaption(files: UploadFile = File(...), language: str = 'en'):  
    try:
        print(f"接收到图片描述请求，语言：{language}")
        
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
            
            # 发送请求到 Hugging Face API
            API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
            try:
                result = call_huggingface_api(API_URL, img_byte_arr)
            except HTTPException:
                raise
            except Exception as e:
                print(f"API调用失败: {str(e)}")
                raise HTTPException(status_code=502, detail="Failed to call external API")
            
            caption = result.get('generated_text', '')
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
            
            # 发送请求到 Image Captioning API
            API_URL = "https://api-inference.huggingface.co/models/nlpconnect/vit-gpt2-image-captioning"
            try:
                result = call_huggingface_api(API_URL, img_byte_arr)
            except HTTPException:
                raise
            except Exception as e:
                print(f"API调用失败: {str(e)}")
                raise HTTPException(status_code=502, detail="Failed to call external API")
            
            caption = result.get('generated_text', '')
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088)
