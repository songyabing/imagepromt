import { NextRequest, NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';
import os from 'os';
import axios from 'axios';

// 直接使用 Hugging Face API
const HF_API_URL = 'https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base';
const HF_API_KEY = process.env.HUGGINGFACE_API_KEY || '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';
const MAX_RETRIES = 2; // 最大重试次数
const TIMEOUT = 60000; // 超时时间设置为60秒

export async function POST(request: NextRequest) {
  try {
    console.log('接收到 BLIP API 请求');
    
    // 创建临时目录用于存储上传的文件
    const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'blip-'));
    console.log('创建临时目录:', tempDir);
    
    // 解析 multipart/form-data 请求
    const formData = await request.formData();
    const file = formData.get('files') as File;
    
    if (!file) {
      console.log('没有上传文件');
      return NextResponse.json({ error: '没有上传文件' }, { status: 400 });
    }
    
    console.log('接收到文件:', file.name, '类型:', file.type, '大小:', file.size);
    
    // 检查文件类型
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      console.log('不支持的文件格式:', file.type);
      return NextResponse.json({ error: '不支持的文件格式' }, { status: 400 });
    }
    
    // 转换文件为 buffer
    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);
    console.log('文件已转换为 buffer, 大小:', buffer.length);
    
    try {
      console.log('开始调用 Hugging Face API');
      
      // 使用重试机制调用 API
      let lastError = null;
      for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
        try {
          if (attempt > 0) {
            console.log(`第 ${attempt} 次重试...`);
          }
          
          // 使用 Hugging Face 的 BLIP 模型
          const response = await axios.post(
            HF_API_URL,
            buffer,
            {
              headers: {
                'Content-Type': 'application/octet-stream',
                'Authorization': `Bearer ${HF_API_KEY}`,
              },
              timeout: TIMEOUT, // 增加超时时间
            }
          );
          
          console.log('Hugging Face API 响应:', response.data);
          
          // 处理响应
          if (response.data && Array.isArray(response.data) && response.data.length > 0) {
            const caption = response.data[0].generated_text;
            console.log('生成的描述:', caption);
            
            return NextResponse.json({
              captions: [{ caption }]
            });
          } else if (response.data && typeof response.data === 'object' && response.data.error) {
            // 处理 Hugging Face 返回的错误
            console.error('Hugging Face API 返回错误:', response.data.error);
            
            // 如果是模型加载中的错误，则重试
            if (response.data.error.includes('loading') || response.data.error.includes('starting')) {
              lastError = response.data.error;
              // 等待一段时间后重试
              if (attempt < MAX_RETRIES) {
                await new Promise(resolve => setTimeout(resolve, 5000)); // 等待5秒
                continue;
              }
            }
            
            return NextResponse.json({ 
              error: `Hugging Face API 错误: ${response.data.error}`,
              details: response.data,
              captions: [{ caption: `生成失败: ${response.data.error}` }]
            }, { status: 500 });
          } else {
            console.log('未能从响应中提取描述:', response.data);
            return NextResponse.json({
              captions: [{ caption: '无法从响应中提取描述' }]
            });
          }
        } catch (error: any) {
          console.error(`尝试 ${attempt} 失败:`, error.message);
          lastError = error;
          
          // 如果是超时错误或者网络错误，则重试
          if (axios.isAxiosError(error) && 
             (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT' || !error.response)) {
            if (attempt < MAX_RETRIES) {
              await new Promise(resolve => setTimeout(resolve, 3000)); // 等待3秒
              continue;
            }
          } else if (axios.isAxiosError(error) && error.response && error.response.status === 503) {
            // 如果是服务暂时不可用，也重试
            if (attempt < MAX_RETRIES) {
              await new Promise(resolve => setTimeout(resolve, 5000)); // 等待5秒
              continue;
            }
          } else {
            // 其他错误直接抛出
            break;
          }
        }
      }
      
      // 所有重试都失败了，处理最后的错误
      if (lastError) {
        console.error('所有重试都失败了，最后的错误:', lastError);
        
        if (axios.isAxiosError(lastError)) {
          if (lastError.code === 'ECONNABORTED' || lastError.code === 'ETIMEDOUT') {
            return NextResponse.json({ 
              error: '请求超时',
              captions: [{ caption: `生成失败: 模型处理超时，请尝试上传更小的图片或稍后重试` }]
            }, { status: 408 });
          }
          
          if (lastError.response) {
            console.error('API 错误状态码:', lastError.response.status);
            console.error('API 错误详情:', lastError.response.data);
            
            // 检查是否是模型加载中的错误
            if (lastError.response.status === 503 && lastError.response.data.estimated_time) {
              return NextResponse.json({ 
                captions: [{ 
                  caption: `模型正在加载中，预计等待时间: ${lastError.response.data.estimated_time}秒，请稍后重试` 
                }] 
              });
            }
            
            return NextResponse.json({ 
              error: `API 错误: ${lastError.response.status}`,
              details: lastError.response.data,
              captions: [{ caption: `生成失败: API 错误 ${lastError.response.status}` }]
            }, { status: lastError.response.status });
          }
        }
        
        return NextResponse.json({ 
          error: `调用 API 失败: ${lastError.message}`,
          captions: [{ caption: `生成失败: ${lastError.message}` }]
        }, { status: 500 });
      }
      
      return NextResponse.json({ 
        error: '未知错误',
        captions: [{ caption: '生成失败: 未知错误，请重试' }]
      }, { status: 500 });
    } catch (error: any) {
      console.error('调用 Hugging Face API 失败:', error.message);
      
      // 详细记录错误信息
      if (axios.isAxiosError(error) && error.response) {
        console.error('API 错误状态码:', error.response.status);
        console.error('API 错误详情:', error.response.data);
        
        // 检查是否是模型加载中的错误
        if (error.response.status === 503 && error.response.data.estimated_time) {
          return NextResponse.json({ 
            captions: [{ 
              caption: `模型正在加载中，预计等待时间: ${error.response.data.estimated_time}秒，请稍后重试` 
            }] 
          });
        }
        
        return NextResponse.json({ 
          error: `API 错误: ${error.response.status}`,
          details: error.response.data,
          captions: [{ caption: `生成失败: API 错误 ${error.response.status}` }]
        }, { status: error.response.status });
      }
      
      return NextResponse.json({ 
        error: `调用 API 失败: ${error.message}`,
        captions: [{ caption: `生成失败: ${error.message}` }]
      }, { status: 500 });
    } finally {
      // 清理临时文件
      try {
        await fs.rm(tempDir, { recursive: true, force: true });
        console.log('已清理临时目录:', tempDir);
      } catch (cleanupError) {
        console.error('清理临时目录失败:', cleanupError);
      }
    }
  } catch (error: any) {
    console.error('处理请求时出错:', error.message);
    return NextResponse.json({ 
      error: '服务器内部错误',
      message: error.message,
      captions: [{ caption: '服务器处理请求时出错，请重试' }]
    }, { status: 500 });
  }
}
