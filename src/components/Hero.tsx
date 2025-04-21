'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import axios from 'axios';

interface Feature {
  title: string;
  description: string;
}
const features: Feature[] = [];

export default function Hero() {
  const [imageUrl, setImageUrl] = useState('');
  const [previewImage, setPreviewImage] = useState('');
  const [generatedPrompt, setGeneratedPrompt] = useState('');
  const [selectedModel, setSelectedModel] = useState('joycaption');
  const [isGenerating, setIsGenerating] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [error, setError] = useState('');
  const [inputMethod, setInputMethod] = useState<'upload' | 'url'>('upload');

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        if (reader.result) {
          const base64String = reader.result.toString().split(',')[1];
          resolve(base64String);
        } else {
          reject(new Error('Failed to convert file to base64'));
        }
      };
      reader.onerror = error => reject(error);
    });
  };

  // API基础URL配置 - 使用相对URL避免跨域问题
  const API_BASE_URL = 'https://imagepromt-production.up.railway.app';  // 空字符串表示使用相对路径

  const generatePromptWithJoyCaption = async (imageFile: File) => {
    try {
      setIsGenerating(true);
      setError('');

      // 验证文件大小
      const maxSize = 10 * 1024 * 1024; // 10MB
      if (imageFile.size > maxSize) {
        throw new Error('Image size exceeds 10MB limit');
      }

      // 验证文件类型
      if (!imageFile.type.startsWith('image/')) {
        throw new Error('Only image files are supported');
      }

      const formData = new FormData();
      formData.append('files', imageFile);
      formData.append('language', 'en');
      
      console.log('Sending request to JoyCaption API...');
      console.log(`File size: ${(imageFile.size / 1024).toFixed(2)}KB, File type: ${imageFile.type}`);
      
      // 记录当前时间，用于计算请求耗时
      const startTime = new Date().getTime();
      
      console.log(`API endpoint: ${API_BASE_URL}/api/joycaption/upload`);
      
      try {
        // 设置更长的超时时间，生产环境可能需要更长的处理时间
        const response = await axios.post(
          `${API_BASE_URL}/api/joycaption/upload`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
            timeout: 90000, // 增加到90秒，考虑到HuggingFace模型加载时间
            timeoutErrorMessage: 'Request timed out, please try again later',
            maxContentLength: maxSize,
            maxBodyLength: maxSize,
            validateStatus: function (status) {
              return status >= 200 && status < 500;
            }
          }
        );
        
        const endTime = new Date().getTime();
        console.log(`API request completed in ${endTime - startTime}ms`);
        console.log('JoyCaption API response:', response.data);

        if (response.status >= 400) {
          console.error('API error:', response.data);
          throw new Error(response.data?.detail || 'Failed to generate prompt');
        }

        if (response.data?.caption) {
          return response.data.caption;
        } else {
          console.error('No caption in response:', response.data);
          setError('No caption generated. Please try again with a different image.');
          return '';
        }
      } catch (axiosError) {
        // 添加专门针对超时的处理
        const endTime = new Date().getTime();
        const elapsedTime = endTime - startTime;
        console.error(`API request failed after ${elapsedTime}ms`);
        
        if (axios.isAxiosError(axiosError)) {
          // 处理网络错误
          if (axiosError.code === 'ECONNABORTED') {
            console.error('Request timeout error');
            throw new Error('Request timed out. The server is taking too long to respond. Please try with a smaller image or try again later.');
          } else if (axiosError.response) {
            // 服务器返回了错误状态码
            console.error(`Server error with status: ${axiosError.response.status}`);
            console.error('Response data:', axiosError.response.data);
            throw axiosError;
          } else if (axiosError.request) {
            // 请求已发送但没有收到响应
            console.error('No response received from server');
            throw new Error('No response from server. Please check your connection and try again.');
          } else {
            // 其他类型的错误
            console.error('Error details:', axiosError.message);
            throw axiosError;
          }
        } else {
          // 非Axios错误
          console.error('Non-Axios error:', axiosError);
          throw axiosError;
        }
      }
    } catch (error: any) {
      console.error('Full error object:', error);
      if (axios.isAxiosError(error)) {
        if (error.code === 'ECONNABORTED') {
          setError('Request timed out. Please try again later or use a smaller image.');
        } else if (error.response) {
          const errorMessage = error.response.data?.detail || 'Server error. Please try again.';
          console.error('Server error response:', error.response.data);
          setError(errorMessage);
        } else if (error.request) {
          console.error('No response received:', error.request);
          setError('No response from server. Please check your connection.');
        } else {
          console.error('Axios error:', error.message);
          setError('An error occurred. Please try again.');
        }
      } else {
        console.error('Non-Axios error:', error);
        setError(error.message || 'An unexpected error occurred.');
      }
      return '';
    } finally {
      setIsGenerating(false);
    }
  };

  const handleApiError = (error: any) => {
    setError('Please re-upload the photo to generate prompts');
  };

  const generatePrompt = async () => {
    if (!uploadedFile && !previewImage) {
      alert('Please upload an image or provide an image URL');
      return;
    }

    setIsGenerating(true);
    setError('');
    setGeneratedPrompt('');

    try {
      let fileToProcess = uploadedFile;

      if (!fileToProcess && previewImage) {
        try {
          const response = await fetch(previewImage);
          const blob = await response.blob();
          fileToProcess = new File([blob], 'image.jpg', { type: 'image/jpeg' });
        } catch (error: any) {
          console.error('Error downloading image:', error);
          setError('Please re-upload the photo to generate prompts');
          setIsGenerating(false);
          return;
        }
      }

      let prompt = '';

      if (fileToProcess) {
        console.log(`Generating prompt using ${selectedModel} model...`);
        
        try {
          switch (selectedModel) {
            case 'joycaption':
              prompt = await generatePromptWithJoyCaption(fileToProcess);
              break;
            case 'interrogator':
              alert("CLIP-Interrogator model is under development, please choose another model");
              setIsGenerating(false);
              return;
            default:
              setError('Please re-upload the photo to generate prompts');
          }

          if (prompt) {
            console.log(`${selectedModel} model result:`, prompt);
            setGeneratedPrompt(prompt);
          } else {
            console.error(`${selectedModel} model did not return a result`);
          }
        } catch (error: any) {
          console.error(`${selectedModel} model error:`, error);
          throw error;
        }
      }
    } catch (error: any) {
      console.error('Error generating prompt:', error);
      setError('Please re-upload the photo to generate prompts');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleImageUpload = (file: File) => {
    if (file) {
      if (file.size > 4 * 1024 * 1024) {
        setError('Please re-upload the photo to generate prompts');
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        if (e.target?.result) {
          setPreviewImage(e.target.result.toString());
          setUploadedFile(file);
          setError('');
        }
      };
      reader.readAsDataURL(file);
    }
  };

  // 处理文件拖放
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleImageUpload(e.dataTransfer.files[0]);
    }
  };

  // 处理拖拽悬停
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setImageUrl(e.target.value);
  };

  const loadImageFromUrl = async () => {
    if (!imageUrl) {
      setError('Please enter an image URL');
      return;
    }

    try {
      setError('');
      console.log('Loading image from URL:', imageUrl);
      
      // 添加更好的URL验证
      let urlToLoad = imageUrl.trim();
      
      // 移除URL前面可能存在的@符号
      if (urlToLoad.startsWith('@')) {
        urlToLoad = urlToLoad.substring(1);
        console.log('Removed @ symbol from URL:', urlToLoad);
      }
      
      // 确保URL有协议
      if (!urlToLoad.startsWith('http://') && !urlToLoad.startsWith('https://')) {
        urlToLoad = 'https://' + urlToLoad;
        console.log('Updated URL with protocol:', urlToLoad);
      }
      
      // 尝试检查URL是否包含图片扩展名
      const hasImageExtension = /\.(jpg|jpeg|png|gif|webp|bmp)$/i.test(urlToLoad);
      if (!hasImageExtension) {
        console.warn('URL does not end with a common image extension:', urlToLoad);
      }
      
      const proxyUrl = `${API_BASE_URL}/api/proxy/image?url=${encodeURIComponent(urlToLoad)}`;
      console.log('Proxy URL:', proxyUrl);
      
      const response = await fetch(proxyUrl, {
        method: 'GET',
        // 增加超时设置
        signal: AbortSignal.timeout(30000) // 30秒超时
      });
      
      if (!response.ok) {
        console.error('Proxy error status:', response.status);
        
        // 尝试解析错误响应
        let errorMessage = 'Failed to load image';
        try {
          const errorData = await response.json();
          console.error('Proxy error details:', errorData);
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          console.error('Could not parse error response:', e);
          // 如果无法解析JSON，尝试读取文本
          try {
            const textResponse = await response.text();
            console.error('Error response text:', textResponse);
            errorMessage = textResponse || errorMessage;
          } catch (textError) {
            console.error('Could not get response text:', textError);
          }
        }
        
        throw new Error(errorMessage);
      }

      const contentType = response.headers.get('content-type');
      console.log('Response content type:', contentType);
      
      // 更宽容的内容类型检查
      if (contentType) {
        // 接受所有图片类型
        if (!contentType.includes('image/')) {
          console.error('Invalid content type:', contentType);
          throw new Error('Invalid image type');
        }
      } else {
        // 如果没有content-type，尝试通过响应内容判断
        console.warn('No content-type in response, trying to handle as image anyway');
      }

      try {
        const blob = await response.blob();
        console.log('Blob size:', blob.size, 'type:', blob.type);
        
        if (blob.size === 0) {
          throw new Error('Received empty image data');
        }
        
        // 使用更通用的mime类型或从blob中检测
        const mimeType = blob.type || 'image/jpeg';
        const file = new File([blob], 'image.jpg', { type: mimeType });
        console.log('Image loaded successfully');
        handleImageUpload(file);
      } catch (error: any) {
        console.error('Blob processing error:', error);
        throw new Error('Invalid image data received');
      }
    } catch (error: any) {
      console.error('Error loading image:', error);
      setError(error.message || 'Failed to load image. Please check the URL and try again.');
    }
  };

  return (
    <div className="bg-gradient-to-b from-[#F1F7FE] to-[#FFFFFF] min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <div className="text-center">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 tracking-tight">
            Free Image to Text Generator
          </h1>
          <p className="mt-4 max-w-2xl mx-auto text-xl text-gray-500">
            Convert Image to Text to generate your own image
          </p>
        </div>

        <div className="mt-12 max-w-4xl mx-auto bg-white rounded-2xl shadow-sm p-6 sm:p-8 border border-gray-100">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex flex-col">
              <div className="flex mb-4">
                <button
                  onClick={() => setInputMethod('upload')}
                  className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                    inputMethod === 'upload'
                      ? 'bg-[#3566E3] text-white'
                      : 'text-gray-700'
                  }`}
                >
                  Upload Image
                </button>
                <button
                  onClick={() => setInputMethod('url')}
                  className={`ml-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                    inputMethod === 'url'
                      ? 'bg-[#3566E3] text-white'
                      : 'text-gray-700'
                  }`}
                >
                  Image URL
                </button>
              </div>

              <div className="flex-grow">
                {inputMethod === 'upload' ? (
                  <div
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                    className="h-[300px] flex flex-col justify-center items-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer hover:border-[#3566E3] transition-colors"
                    onClick={() => document.getElementById('file-upload')?.click()}
                  >
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      className="sr-only"
                      onChange={(e) => handleImageUpload(e.target.files![0])}
                      accept="image/*"
                    />
                    <div className="space-y-1 text-center">
                      <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
                        <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4h-8m-12 0H8m12 0a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                      <div className="text-sm text-gray-600">
                        <p>Drag and drop files here or click to upload</p>
                        <p className="text-xs text-gray-500">PNG, JPG, WEBP files up to 4MB</p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="h-[280px] flex items-start">
                    <div className="flex space-x-2 w-full">
                      <input
                        type="text"
                        id="image-url"
                        value={imageUrl}
                        onChange={handleUrlChange}
                        placeholder="https://example.com/image.jpg"
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#3566E3] focus:border-[#3566E3] sm:text-sm"
                      />
                      <button
                        onClick={loadImageFromUrl}
                        className="px-4 py-2 bg-[#3566E3] text-white rounded-lg hover:bg-[#2952c8] transition-colors whitespace-nowrap"
                      >
                        Load
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="flex flex-col">
              <div className="flex items-center mb-4">
                <h3 className="text-sm font-bold text-gray-700">Image Preview</h3>
              </div>
              <div className="flex-grow border rounded-lg bg-gray-50 overflow-hidden h-[280px]">
                {previewImage ? (
                  <div className="relative h-full w-full">
                    <Image
                      src={previewImage}
                      alt="Preview"
                      fill
                      className="object-contain"
                    />
                  </div>
                ) : (
                  <div className="h-full flex items-center justify-center text-gray-400">
                    <div className="text-center">
                      <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <p className="mt-2">Your image will be displayed here</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* 模型选择 */}
          <div className="mt-8">
            <label className="block text-sm font-bold text-gray-700 mb-3">Select Model</label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div 
                className={`p-4 border rounded-lg cursor-pointer transition-all hover:shadow-sm ${selectedModel === 'joycaption' ? 'border-[#3566E3] bg-blue-50' : 'border-gray-200'}`}
                onClick={() => setSelectedModel('joycaption')}
              >
                <div className="font-medium">JoyCaption</div>
                <p className="mt-1 text-sm text-gray-500">Fast and accurate image description</p>
              </div>
              <div 
                className={`p-4 border rounded-lg cursor-pointer transition-all hover:shadow-sm ${selectedModel === 'interrogator' ? 'border-[#3566E3] bg-blue-50' : 'border-gray-200'}`}
                onClick={() => setSelectedModel('interrogator')}
              >
                <div className="font-medium">CLIP Interrogator</div>
                <p className="mt-1 text-sm text-gray-500">Detailed image analysis</p>
              </div>
            </div>
          </div>

          {/* 生成控制区 */}
          <div className="mt-8 flex gap-4 items-center">
            <div className="flex-1 flex items-center space-x-4">
              <button
                onClick={generatePrompt}
                disabled={isGenerating || (!uploadedFile && !previewImage)}
                className={`flex-1 py-3 ${isGenerating || !previewImage ? 'bg-gray-400' : 'bg-[#3566E3] hover:bg-[#2952c8]'} text-white rounded-lg text-sm transition-colors flex items-center justify-center`}
              >
                {isGenerating ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating...
                  </>
                ) : 'Generate Prompt'}
              </button>

              <button
                onClick={() => window.open('https://plisio.net/donate/rami970O', '_blank')}
                className="px-6 py-3 bg-green-500 hover:bg-green-600 text-white rounded-lg text-sm transition-colors"
              >
                Endowment
              </button>
            </div>
          </div>

          {error && (
            <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {generatedPrompt && (
            <div className="mt-8 bg-white rounded-xl shadow-sm p-6 border border-gray-100">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold">Generated Cue Words</h2>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(generatedPrompt);
                    alert('Cue words copied to clipboard');
                  }}
                  className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-[#3566E3] hover:bg-[#2952c8] focus:outline-none"
                >
                  Copy
                </button>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="whitespace-pre-wrap">{generatedPrompt}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
