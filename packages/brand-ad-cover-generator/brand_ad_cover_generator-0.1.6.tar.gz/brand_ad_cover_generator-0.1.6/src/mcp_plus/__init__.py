 # -*- coding: utf-8 -*-  
"""
MCP广告封面生成器服务器 - 基于CodeBuddy风格设计
"""
import json
import random
import os
from typing import Dict, List, Optional

try:
    from mcp.server.fastmcp import FastMCP
    # 创建MCP服务器实例
    mcp = FastMCP("mcp-plus")
except ImportError:
    print("警告: 无法导入 mcp.server.fastmcp 模块，使用自定义实现")
    # 使用我们的自定义实现
    from .server_impl import SimpleMCP
    mcp = SimpleMCP("mcp-plus")

def main():
    """
    MCP Plus 主函数 - 启动MCP服务器
    """
    import sys
    import asyncio
    
    # 打印当前工作目录
    print(f"当前工作目录: {os.getcwd()}", file=sys.stderr)
    
    # 打印已注册的工具
    print("已注册的工具:", file=sys.stderr)
    print("- generate_brand_ad_cover", file=sys.stderr)
    print("- generate_classical_chinese_slogan", file=sys.stderr)
    print("MCP服务器启动中...", file=sys.stderr)
    
    try:
        # 使用异步方式运行MCP服务器
        asyncio.run(mcp.run())
    except KeyboardInterrupt:
        print("MCP服务器已停止", file=sys.stderr)
    except Exception as e:
        print(f"MCP服务器错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

@mcp.tool()
def brand_cover(
    brand_name: str,
    subtitle: str = "",
    slogan: str = "",
    style: str = "简约",
    primary_color: str = "蓝色",
    width: int = 1080,
    height: int = 1080,
    output_path: str = "brand_ad_cover.svg"
) -> str:
    """
    生成品牌广告封面，参考CodeBuddy风格设计。
    
    参数说明：
    - brand_name: 品牌名称
    - subtitle: 副标题（如：AI编程伙伴）
    - slogan: 品牌标语（如：智能代码生成 · 高效开发体验）
    - style: 设计风格（科技/简约/专业/未来/古典中国风/像素风格）
    - primary_color: 主色调（蓝色/紫色/绿色/橙色/大红/水绿/蓝灰/黑灰）
    - width: 图片宽度（像素）
    - height: 图片高度（像素）
    - output_path: 输出文件路径
    """
    
    try:
        # 确保使用当前工作目录的绝对路径
        current_dir = os.getcwd()
        abs_output_path = os.path.join(current_dir, output_path)
        
        # 颜色方案
        color_schemes = {
            "蓝色": {
                "primary": "#1E40AF", "secondary": "#3B82F6", "accent": "#60A5FA", 
                "light": "#93C5FD", "dark": "#1E3A8A", "text": "#1E3A8A", 
                "bg": "#FFFFFF", "glow": "#3B82F6", "energy": "#F59E0B"
            },
            "紫色": {
                "primary": "#6B21A8", "secondary": "#8B5CF6", "accent": "#A78BFA", 
                "light": "#C4B5FD", "dark": "#581C87", "text": "#581C87",
                "bg": "#FFFFFF", "glow": "#8B5CF6", "energy": "#F59E0B"
            },
            "绿色": {
                "primary": "#047857", "secondary": "#10B981", "accent": "#34D399", 
                "light": "#6EE7B7", "dark": "#064E3B", "text": "#064E3B",
                "bg": "#FFFFFF", "glow": "#10B981", "energy": "#F59E0B"
            },
            "红色": {
                "primary": "#DC2626", "secondary": "#EF4444", "accent": "#F87171", 
                "light": "#FCA5A5", "dark": "#991B1B", "text": "#991B1B",
                "bg": "#FFFFFF", "glow": "#EF4444", "energy": "#F59E0B"
            },
            "橙色": {
                "primary": "#EA580C", "secondary": "#F97316", "accent": "#FB923C", 
                "light": "#FDBA74", "dark": "#9A3412", "text": "#9A3412",
                "bg": "#FFFFFF", "glow": "#F97316", "energy": "#06B6D4"
            },
            "大红": {
                "primary": "#DC143C", "secondary": "#FF6B6B", "accent": "#FFB6C1", 
                "light": "#FFC0CB", "dark": "#8B0000", "text": "#8B0000",
                "bg": "#FFF8DC", "glow": "#FF4500", "energy": "#FFD700"
            },
            "水绿": {
                "primary": "#20B2AA", "secondary": "#48CAE4", "accent": "#90E0EF", 
                "light": "#CAF0F8", "dark": "#006A6B", "text": "#006A6B",
                "bg": "#F0FFFF", "glow": "#00CED1", "energy": "#FFD700"
            },
            "蓝灰": {
                "primary": "#4682B4", "secondary": "#6495ED", "accent": "#87CEEB", 
                "light": "#B0C4DE", "dark": "#2F4F4F", "text": "#2F4F4F",
                "bg": "#F5F5DC", "glow": "#4169E1", "energy": "#FF6347"
            },
            "黑灰": {
                "primary": "#2F4F4F", "secondary": "#696969", "accent": "#A9A9A9", 
                "light": "#D3D3D3", "dark": "#000000", "text": "#000000",
                "bg": "#F5F5F5", "glow": "#708090", "energy": "#DC143C"
            }
        }
        
        colors = color_schemes.get(primary_color, color_schemes["蓝色"])
        
        # 根据风格选择不同的模板
        if style == "科技":
            return tech_cvr(brand_name, subtitle, slogan, colors, width, height, abs_output_path)
        elif style == "古典中国风" or "中国风" in style or style == "中国风":
            return classic_cvr(brand_name, subtitle, slogan, colors, width, height, abs_output_path)
        elif style == "像素风格" or style == "像素" or "像素" in style:
            return pixel_cvr(brand_name, subtitle, slogan, colors, width, height, abs_output_path)
        elif style == "分屏式设计" or ("分屏" in style):
            return split_cvr(brand_name, subtitle, slogan, colors, width, height, abs_output_path)
        else:  # 默认使用简约风格
            return simple_cvr(brand_name, subtitle, slogan, colors, width, height, abs_output_path)
    except Exception as e:
        return f"生成封面时出现错误: {str(e)}"

def simple_cvr(brand_name, subtitle, slogan, colors, width, height, output_path):
    """生成简约风格的品牌广告封面"""
    try:
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="pureWhiteBg" cx="50%" cy="50%" r="80%">
      <stop offset="0%" style="stop-color:#FEFEFE;stop-opacity:1" />
      <stop offset="70%" style="stop-color:#FDFDFD;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#F0F4F8;stop-opacity:1" />
    </radialGradient>
    
    <linearGradient id="brandGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{colors['primary']};stop-opacity:0.6" />
      <stop offset="30%" style="stop-color:{colors['secondary']};stop-opacity:0.7" />
      <stop offset="70%" style="stop-color:{colors['accent']};stop-opacity:0.5" />
      <stop offset="100%" style="stop-color:{colors['light']};stop-opacity:0.3" />
    </linearGradient>
    
    <linearGradient id="brandBrush" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{colors['dark']};stop-opacity:0" />
      <stop offset="20%" style="stop-color:{colors['primary']};stop-opacity:0.8" />
      <stop offset="50%" style="stop-color:{colors['secondary']};stop-opacity:1" />
      <stop offset="80%" style="stop-color:{colors['accent']};stop-opacity:0.8" />
      <stop offset="100%" style="stop-color:{colors['light']};stop-opacity:0" />
    </linearGradient>
    
    <radialGradient id="brandGlow" cx="50%" cy="50%" r="60%">
      <stop offset="0%" style="stop-color:{colors['energy']};stop-opacity:0.4" />
      <stop offset="50%" style="stop-color:{colors['primary']};stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:#FEFEFE;stop-opacity:0" />
    </radialGradient>
    
    <filter id="brandGlowFilter" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    
    <filter id="brandShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="{colors['primary']}" flood-opacity="0.15"/>
    </filter>
    
    <filter id="textGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="1" stdDeviation="3" flood-color="{colors['primary']}" flood-opacity="0.2"/>
    </filter>
  </defs>
  
  <rect width="{width}" height="{height}" fill="url(#pureWhiteBg)" />
  
  <!-- 装饰元素 - 左上角 -->
  <text x="150" y="200" font-family="'Courier New', monospace" font-size="48" 
        fill="url(#brandGradient)" opacity="0.6" filter="url(#brandShadow)">&lt;/&gt;</text>
  
  <!-- 装饰元素 - 右上角 -->
  <text x="850" y="180" font-family="'Courier New', monospace" font-size="36" 
        fill="url(#brandGradient)" opacity="0.5" filter="url(#brandShadow)">{{ }}</text>
  
  <!-- 装饰节点 -->
  <circle cx="200" cy="350" r="4" fill="{colors['secondary']}" opacity="0.8" filter="url(#brandGlowFilter)"/>
  <circle cx="280" cy="320" r="3" fill="{colors['accent']}" opacity="0.7" filter="url(#brandGlowFilter)"/>
  <circle cx="320" cy="380" r="3.5" fill="{colors['primary']}" opacity="0.9" filter="url(#brandGlowFilter)"/>
  
  <!-- 连接线 -->
  <line x1="200" y1="350" x2="280" y2="320" 
        stroke="url(#brandBrush)" stroke-width="1.5" opacity="0.6" filter="url(#brandShadow)"/>
  <line x1="280" y1="320" x2="320" y2="380" 
        stroke="url(#brandBrush)" stroke-width="1.5" opacity="0.6" filter="url(#brandShadow)"/>
  <line x1="200" y1="350" x2="320" y2="380" 
        stroke="{colors['light']}" stroke-width="1" opacity="0.4"/>
  
  <!-- 装饰元素 - 右下角 -->
  <path d="M750,700 L850,650 L850,750 Z" 
        fill="url(#brandGradient)" opacity="0.3" filter="url(#brandShadow)"/>
  <rect x="780" y="720" width="40" height="8" 
        fill="{colors['energy']}" opacity="0.6" rx="4" filter="url(#brandGlowFilter)"/>
  
  <!-- 主标题背景装饰 -->
  <ellipse cx="{width//2}" cy="480" rx="280" ry="60" 
           fill="url(#brandGlow)" opacity="0.2" filter="url(#brandShadow)"/>
  
  <!-- 主标题 -->
  <text x="{width//2}" y="500" text-anchor="middle" 
        font-family="'Microsoft YaHei', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif" 
        font-size="72" font-weight="700" 
        fill="{colors['text']}" filter="url(#textGlow)">{brand_name}</text>'''
        
        if subtitle:
            svg_content += f'''
  
  <!-- 副标题装饰线 -->
  <path d="M{width*0.35},540 Q{width//2},530 {width*0.65},540" 
        fill="none" stroke="url(#brandBrush)" stroke-width="2" opacity="0.5" filter="url(#brandGlowFilter)"/>
  
  <!-- 副标题 -->
  <text x="{width//2}" y="570" text-anchor="middle" 
        font-family="'Microsoft YaHei', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif" 
        font-size="36" font-weight="300" 
        fill="{colors['secondary']}" filter="url(#textGlow)">{subtitle}</text>'''
        
        if slogan:
            svg_content += f'''
  
  <!-- Slogan -->
  <text x="{width//2}" y="620" text-anchor="middle" 
        font-family="'Microsoft YaHei', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif" 
        font-size="24" font-weight="200" 
        fill="{colors['accent']}" filter="url(#brandShadow)">{slogan}</text>'''
        
        svg_content += f'''
  
  <!-- 底部装饰 -->
  <path d="M{width*0.28},900 Q{width//2},880 {width*0.72},900" 
        fill="none" stroke="url(#brandBrush)" stroke-width="3" opacity="0.4" filter="url(#brandShadow)"/>
  
  <!-- 品牌标识点 -->
  <circle cx="{width//2}" cy="920" r="6" 
          fill="{colors['energy']}" opacity="0.8" filter="url(#brandGlowFilter)"/>
  
  <!-- 装饰元素 -->
  <text x="100" y="950" font-family="'Courier New', monospace" font-size="14" 
        fill="{colors['light']}" opacity="0.6">console.log("{brand_name}");</text>
  
  <!-- 装饰点 -->
  <circle cx="80" cy="80" r="2" 
          fill="{colors['secondary']}" opacity="0.4" filter="url(#brandGlowFilter)"/>
  <circle cx="1000" cy="1000" r="2.5" 
          fill="{colors['primary']}" opacity="0.5" filter="url(#brandGlowFilter)"/>
</svg>'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return f"🚀 品牌广告封面已生成: {output_path} ({width}x{height}px, 简约风格, {colors['primary']}主色调)"
    except Exception as e:
        return f"生成封面时出现错误: {str(e)}"

def tech_cvr(brand_name, subtitle, slogan, colors, width, height, output_path):
    """生成科技风格的品牌广告封面"""
    try:
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="techBg" cx="30%" cy="20%" r="120%">
      <stop offset="0%" style="stop-color:{colors['glow']};stop-opacity:0.2" />
      <stop offset="30%" style="stop-color:{colors['primary']};stop-opacity:0.5" />
      <stop offset="70%" style="stop-color:#0F172A;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1E293B;stop-opacity:1" />
    </radialGradient>
    
    <linearGradient id="brandGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{colors['secondary']};stop-opacity:0.9" />
      <stop offset="50%" style="stop-color:{colors['glow']};stop-opacity:0.8" />
      <stop offset="100%" style="stop-color:{colors['energy']};stop-opacity:0.7" />
    </linearGradient>
    
    <filter id="neonGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="6" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    
    <filter id="textGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    
    <linearGradient id="lightBeam" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{colors['glow']};stop-opacity:0" />
      <stop offset="50%" style="stop-color:{colors['glow']};stop-opacity:0.8" />
      <stop offset="100%" style="stop-color:{colors['glow']};stop-opacity:0" />
    </linearGradient>
  </defs>
  
  <rect width="{width}" height="{height}" fill="url(#techBg)" />'''
        
        # 添加科技网格背景
        for i in range(0, width, 60):
            svg_content += f'  <line x1="{i}" y1="0" x2="{i}" y2="{height}" stroke="{colors["glow"]}" stroke-width="0.3" opacity="0.2" filter="url(#neonGlow)"/>\n'
        for i in range(0, height, 60):
            svg_content += f'  <line x1="0" y1="{i}" x2="{width}" y2="{i}" stroke="{colors["glow"]}" stroke-width="0.3" opacity="0.2" filter="url(#neonGlow)"/>\n'
        
        # 代码符号装饰
        svg_content += f'''
  
  <!-- 代码符号装饰 -->
  <text x="{width*0.14}" y="{height*0.18}" font-family="'Courier New', monospace" font-size="42" 
        fill="{colors['glow']}" opacity="0.7" filter="url(#neonGlow)">&lt;/&gt;</text>
  <text x="{width*0.79}" y="{height*0.17}" font-family="'Courier New', monospace" font-size="32" 
        fill="{colors['secondary']}" opacity="0.6" filter="url(#neonGlow)">{{ }}</text>
  
  <!-- AI神经网络节点 -->
  <circle cx="{width*0.18}" cy="{height*0.32}" r="5" fill="{colors['glow']}" opacity="0.8" filter="url(#neonGlow)"/>
  <circle cx="{width*0.26}" cy="{height*0.30}" r="4" fill="{colors['secondary']}" opacity="0.7" filter="url(#neonGlow)"/>
  <circle cx="{width*0.30}" cy="{height*0.35}" r="4.5" fill="{colors['energy']}" opacity="0.9" filter="url(#neonGlow)"/>
  <circle cx="{width*0.35}" cy="{height*0.31}" r="3.5" fill="{colors['glow']}" opacity="0.6" filter="url(#neonGlow)"/>
  
  <!-- 神经网络连接线 -->
  <line x1="{width*0.18}" y1="{height*0.32}" x2="{width*0.26}" y2="{height*0.30}" 
        stroke="url(#brandGrad)" stroke-width="2" opacity="0.7" filter="url(#neonGlow)"/>
  <line x1="{width*0.26}" y1="{height*0.30}" x2="{width*0.30}" y2="{height*0.35}" 
        stroke="url(#brandGrad)" stroke-width="2" opacity="0.7" filter="url(#neonGlow)"/>
  <line x1="{width*0.30}" y1="{height*0.35}" x2="{width*0.35}" y2="{height*0.31}" 
        stroke="url(#brandGrad)" stroke-width="1.5" opacity="0.6" filter="url(#neonGlow)"/>
  <line x1="{width*0.18}" y1="{height*0.32}" x2="{width*0.35}" y2="{height*0.31}" 
        stroke="{colors['glow']}" stroke-width="1" opacity="0.4" filter="url(#neonGlow)"/>'''
        
        # 主标题区域
        title_y = height * 0.46
        svg_content += f'''
  
  <!-- 主标题背景光效 -->
  <rect x="{width*0.05}" y="{title_y-70}" width="{width*0.9}" height="140" 
        fill="url(#brandGrad)" opacity="0.1" rx="20" filter="url(#neonGlow)"/>
  <rect x="{width*0.1}" y="{title_y-4}" width="{width*0.8}" height="8" 
        fill="url(#lightBeam)" opacity="0.6" rx="4"/>
  
  <!-- 主标题 -->
  <text x="{width//2}" y="{title_y}" text-anchor="middle" 
        font-family="'SF Pro Display', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif" 
        font-size="84" font-weight="800" 
        fill="{colors['text']}" filter="url(#textGlow)">{brand_name}</text>'''
        
        if subtitle:
            subtitle_y = height * 0.53
            svg_content += f'''
  
  <!-- 副标题背景 -->
  <rect x="{width*0.2}" y="{subtitle_y-25}" width="{width*0.6}" height="50" 
        fill="{colors['primary']}" opacity="0.1" rx="25" filter="url(#neonGlow)"/>
  <line x1="{width*0.25}" y1="{subtitle_y-20}" x2="{width*0.75}" y2="{subtitle_y-20}" 
        stroke="url(#brandGrad)" stroke-width="2" opacity="0.8" filter="url(#neonGlow)"/>
  
  <!-- 副标题 -->
  <text x="{width//2}" y="{subtitle_y}" text-anchor="middle" 
        font-family="'SF Pro Display', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif" 
        font-size="42" font-weight="400" 
        fill="{colors['glow']}" filter="url(#textGlow)">{subtitle}</text>'''
        
        if slogan:
            slogan_y = height * 0.57
            svg_content += f'''
  
  <!-- Slogan -->
  <text x="{width//2}" y="{slogan_y}" text-anchor="middle" 
        font-family="'SF Pro Display', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif" 
        font-size="28" font-weight="300" 
        fill="{colors['light']}" filter="url(#textGlow)">{slogan}</text>'''
        
        # 代码装饰
        svg_content += f'''
  
  <!-- 代码装饰 -->
  <text x="{width*0.09}" y="{height*0.69}" font-family="'Courier New', monospace" font-size="16" 
        fill="{colors['glow']}" opacity="0.6" filter="url(#neonGlow)">function createMagic() {{</text>
  <text x="{width*0.11}" y="{height*0.72}" font-family="'Courier New', monospace" font-size="16" 
        fill="{colors['secondary']}" opacity="0.6" filter="url(#neonGlow)">  return "{brand_name}";</text>
  <text x="{width*0.09}" y="{height*0.75}" font-family="'Courier New', monospace" font-size="16" 
        fill="{colors['glow']}" opacity="0.6" filter="url(#neonGlow)">}}</text>
  
  <!-- 底部装饰 -->
  <rect x="{width*0.35}" y="{height*0.88}" width="{width*0.3}" height="4" 
        fill="url(#brandGrad)" opacity="0.9" rx="2" filter="url(#neonGlow)"/>
  <circle cx="{width*0.4}" cy="{height*0.91}" r="6" fill="{colors['glow']}" opacity="0.8" filter="url(#neonGlow)"/>
  <circle cx="{width*0.6}" cy="{height*0.91}" r="6" fill="{colors['energy']}" opacity="0.8" filter="url(#neonGlow)"/>
  
  <!-- 背景粒子效果 -->
  <circle cx="{width*0.74}" cy="{height*0.28}" r="3" fill="{colors['glow']}" opacity="0.3" filter="url(#neonGlow)"/>
  <circle cx="{width*0.28}" cy="{height*0.74}" r="4" fill="{colors['secondary']}" opacity="0.2" filter="url(#neonGlow)"/>
  <circle cx="{width*0.83}" cy="{height*0.65}" r="2" fill="{colors['energy']}" opacity="0.4" filter="url(#neonGlow)"/>
</svg>'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return f"🚀 品牌广告封面已生成: {output_path} ({width}x{height}px, 科技风格, {colors['primary']}主色调)"
    except Exception as e:
        return f"生成封面时出现错误: {str(e)}"

def classic_cvr(brand_name, subtitle, slogan, colors, width, height, output_path):
    """生成丰富多彩的古典中国风格品牌广告封面 - 展现深厚中华文化底蕴"""
    try:
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- 传统水墨渐变背景 -->
    <radialGradient id="inkWashBg" cx="50%" cy="30%" r="80%">
      <stop offset="0%" style="stop-color:{colors['bg']};stop-opacity:1" />
      <stop offset="40%" style="stop-color:#FFF8DC;stop-opacity:1" />
      <stop offset="70%" style="stop-color:#F0F8FF;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#E6F3FF;stop-opacity:1" />
    </radialGradient>
    
    <!-- 中国风渐变 -->
    <linearGradient id="chineseGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{colors['primary']};stop-opacity:0.8" />
      <stop offset="30%" style="stop-color:{colors['secondary']};stop-opacity:0.6" />
      <stop offset="70%" style="stop-color:{colors['accent']};stop-opacity:0.4" />
      <stop offset="100%" style="stop-color:{colors['light']};stop-opacity:0.2" />
    </linearGradient>
    
    <!-- 印章效果渐变 -->
    <radialGradient id="sealGradient" cx="50%" cy="50%" r="50%">
      <stop offset="0%" style="stop-color:{colors['primary']};stop-opacity:0.9" />
      <stop offset="70%" style="stop-color:{colors['dark']};stop-opacity:0.8" />
      <stop offset="100%" style="stop-color:{colors['dark']};stop-opacity:0.6" />
    </radialGradient>
    
    <!-- 水墨扩散效果 -->
    <filter id="inkBlur" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feOffset dx="1" dy="1" result="offset"/>
      <feMerge><feMergeNode in="offset"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    
    <!-- 古典阴影 -->
    <filter id="classicalShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="2" dy="3" stdDeviation="3" flood-color="{colors['dark']}" flood-opacity="0.3"/>
    </filter>
    
    <!-- 书法笔触效果 -->
    <filter id="brushStroke" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="1" result="blur"/>
      <feOffset dx="0.5" dy="0.5" result="offset"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    
    <!-- 青花瓷纹样 -->
    <!-- 丰富的青花瓷纹样 -->
    <pattern id="porcelainPattern" x="0" y="0" width="60" height="60" patternUnits="userSpaceOnUse">
      <circle cx="30" cy="30" r="3" fill="{colors['secondary']}" opacity="0.4"/>
      <path d="M15,15 Q30,8 45,15 Q38,30 45,45 Q30,52 15,45 Q22,30 15,15" 
            fill="none" stroke="{colors['primary']}" stroke-width="1" opacity="0.3"/>
      <circle cx="15" cy="15" r="1.5" fill="{colors['accent']}" opacity="0.5"/>
      <circle cx="45" cy="45" r="1.5" fill="{colors['accent']}" opacity="0.5"/>
    </pattern>
    
    <!-- 龙纹图案 -->
    <pattern id="dragonPattern" x="0" y="0" width="80" height="80" patternUnits="userSpaceOnUse">
      <path d="M10,40 Q20,20 40,30 Q60,20 70,40 Q60,60 40,50 Q20,60 10,40" 
            fill="none" stroke="{colors['primary']}" stroke-width="2" opacity="0.2"/>
      <circle cx="25" cy="35" r="2" fill="{colors['energy']}" opacity="0.4"/>
      <circle cx="55" cy="35" r="2" fill="{colors['energy']}" opacity="0.4"/>
    </pattern>
    
    <!-- 凤凰纹样 -->
    <pattern id="phoenixPattern" x="0" y="0" width="100" height="100" patternUnits="userSpaceOnUse">
      <path d="M20,50 Q30,30 50,40 Q70,30 80,50 Q70,70 50,60 Q30,70 20,50" 
            fill="{colors['light']}" stroke="{colors['secondary']}" stroke-width="1" opacity="0.15"/>
      <path d="M40,35 Q50,25 60,35 Q55,45 50,40 Q45,45 40,35" 
            fill="{colors['accent']}" opacity="0.2"/>
    </pattern>
  </defs>
  
  <!-- 背景 -->
  <rect width="{width}" height="{height}" fill="url(#inkWashBg)" />
  
  <!-- 多层纹样背景 -->
  <rect width="{width}" height="{height}" fill="url(#porcelainPattern)" opacity="0.15" />
  <rect width="{width}" height="{height}" fill="url(#dragonPattern)" opacity="0.08" />
  <rect width="{width}" height="{height}" fill="url(#phoenixPattern)" opacity="0.06" />
  
  <!-- 传统边框装饰 -->
  <rect x="50" y="50" width="{width-100}" height="{height-100}" 
        fill="none" stroke="url(#chineseGradient)" stroke-width="3" 
        rx="20" opacity="0.6" filter="url(#classicalShadow)"/>
  
  <!-- 四角装饰 - 传统回纹 -->
  <g opacity="0.7" filter="url(#brushStroke)">
    <!-- 左上角 -->
    <path d="M80,80 L120,80 L120,90 L90,90 L90,120 L80,120 Z" fill="{colors['primary']}"/>
    <rect x="85" y="85" width="10" height="10" fill="{colors['energy']}"/>
    
    <!-- 右上角 -->
    <path d="M{width-120},80 L{width-80},80 L{width-80},120 L{width-90},120 L{width-90},90 L{width-120},90 Z" fill="{colors['primary']}"/>
    <rect x="{width-95}" y="85" width="10" height="10" fill="{colors['energy']}"/>
    
    <!-- 左下角 -->
    <path d="M80,{height-120} L90,{height-120} L90,{height-90} L120,{height-90} L120,{height-80} L80,{height-80} Z" fill="{colors['primary']}"/>
    <rect x="85" y="{height-95}" width="10" height="10" fill="{colors['energy']}"/>
    
    <!-- 右下角 -->
    <path d="M{width-120},{height-90} L{width-90},{height-90} L{width-90},{height-120} L{width-80},{height-120} L{width-80},{height-80} L{width-120},{height-80} Z" fill="{colors['primary']}"/>
    <rect x="{width-95}" y="{height-95}" width="10" height="10" fill="{colors['energy']}"/>
  </g>
  
  <!-- 传统中国结装饰 - 左侧 -->
  <!-- 精美中国结装饰 - 左侧 -->
  <g transform="translate(150, 280)" opacity="0.7" filter="url(#inkBlur)">
    <circle cx="0" cy="0" r="35" fill="none" stroke="{colors['primary']}" stroke-width="5"/>
    <circle cx="0" cy="0" r="25" fill="none" stroke="{colors['secondary']}" stroke-width="3"/>
    <circle cx="0" cy="0" r="15" fill="none" stroke="{colors['accent']}" stroke-width="2"/>
    <path d="M-20,-20 Q0,-35 20,-20 Q35,0 20,20 Q0,35 -20,20 Q-35,0 -20,-20" 
          fill="none" stroke="{colors['energy']}" stroke-width="3"/>
    <circle cx="0" cy="0" r="8" fill="{colors['energy']}" opacity="0.8"/>
    <!-- 中国结流苏 -->
    <line x1="0" y1="35" x2="0" y2="60" stroke="{colors['primary']}" stroke-width="3"/>
    <circle cx="-5" cy="65" r="3" fill="{colors['secondary']}"/>
    <circle cx="5" cy="65" r="3" fill="{colors['secondary']}"/>
    <circle cx="0" cy="70" r="4" fill="{colors['energy']}"/>
  </g>
  
  <!-- 传统灯笼装饰 - 右上 -->
  <g transform="translate({width-120}, 200)" opacity="0.6" filter="url(#classicalShadow)">
    <ellipse cx="0" cy="0" rx="25" ry="35" fill="{colors['primary']}" opacity="0.8"/>
    <ellipse cx="0" cy="0" rx="20" ry="30" fill="{colors['energy']}" opacity="0.6"/>
    <rect x="-20" y="-5" width="40" height="10" fill="{colors['dark']}" opacity="0.7"/>
    <line x1="0" y1="-40" x2="0" y2="-35" stroke="{colors['dark']}" stroke-width="3"/>
    <circle cx="0" cy="-42" r="3" fill="{colors['dark']}"/>
    <!-- 灯笼流苏 -->
    <line x1="0" y1="35" x2="0" y2="50" stroke="{colors['primary']}" stroke-width="2"/>
    <circle cx="0" cy="52" r="2" fill="{colors['energy']}"/>
  </g>
  
  <!-- 祥云装饰群 - 右侧 -->
  <g transform="translate({width-180}, 350)" opacity="0.5" filter="url(#brushStroke)">
    <path d="M-40,0 Q-30,-20 0,-15 Q30,-20 40,0 Q30,20 0,15 Q-30,20 -40,0" 
          fill="{colors['light']}" stroke="{colors['secondary']}" stroke-width="2"/>
    <path d="M-25,-8 Q-15,-15 15,-8 Q25,-15 35,0 Q25,15 -5,8 Q-20,15 -25,-8" 
          fill="{colors['accent']}" opacity="0.7"/>
    <path d="M-15,-12 Q-5,-18 10,-12 Q18,-18 25,-5 Q18,8 5,3 Q-8,8 -15,-12" 
          fill="{colors['primary']}" opacity="0.4"/>
  </g>
  
  <!-- 传统茶具装饰 - 左下 -->
  <g transform="translate(120, {height-200})" opacity="0.5" filter="url(#inkBlur)">
    <!-- 茶壶 -->
    <ellipse cx="0" cy="0" rx="20" ry="15" fill="{colors['secondary']}" opacity="0.7"/>
    <rect x="-15" y="-5" width="30" height="10" fill="{colors['primary']}" opacity="0.6"/>
    <path d="M20,0 Q30,-5 35,0 Q30,5 20,0" fill="none" stroke="{colors['dark']}" stroke-width="2"/>
    <line x1="-5" y1="-15" x2="-5" y2="-25" stroke="{colors['dark']}" stroke-width="2"/>
    <circle cx="-5" cy="-27" r="2" fill="{colors['dark']}"/>
    <!-- 茶杯 -->
    <ellipse cx="40" cy="5" rx="8" ry="6" fill="{colors['accent']}" opacity="0.6"/>
    <ellipse cx="40" cy="2" rx="6" ry="4" fill="{colors['light']}" opacity="0.8"/>
  </g>
  
  <!-- 主标题区域背景 - 水墨效果 -->
  <ellipse cx="{width//2}" cy="{height*0.45}" rx="350" ry="80" 
           fill="url(#chineseGradient)" opacity="0.15" filter="url(#inkBlur)"/>
  
  <!-- 主标题 -->
  <text x="{width//2}" y="{height*0.45}" text-anchor="middle" 
        font-family="'STKaiti', '楷体', 'KaiTi', 'Microsoft YaHei', serif" 
        font-size="78" font-weight="bold" 
        fill="{colors['text']}" filter="url(#classicalShadow)">{brand_name}</text>'''
        
        if subtitle:
            svg_content += f'''
  
  <!-- 副标题装饰线 - 书法笔触 -->
  <path d="M{width*0.3},{height*0.52} Q{width*0.4},{height*0.51} {width*0.5},{height*0.52} Q{width*0.6},{height*0.51} {width*0.7},{height*0.52}" 
        fill="none" stroke="{colors['primary']}" stroke-width="2" opacity="0.6" filter="url(#brushStroke)"/>
  
  <!-- 副标题 -->
  <text x="{width//2}" y="{height*0.55}" text-anchor="middle" 
        font-family="'STKaiti', '楷体', 'KaiTi', 'Microsoft YaHei', serif" 
        font-size="38" font-weight="normal" 
        fill="{colors['secondary']}" filter="url(#brushStroke)">{subtitle}</text>'''
        
        if slogan:
            svg_content += f'''
  
  <!-- Slogan -->
  <text x="{width//2}" y="{height*0.62}" text-anchor="middle" 
        font-family="'STKaiti', '楷体', 'KaiTi', 'Microsoft YaHei', serif" 
        font-size="26" font-weight="300" 
        fill="{colors['accent']}" filter="url(#brushStroke)">{slogan}</text>'''
        
        svg_content += f'''
  
  <!-- 传统印章装饰 -->
  <!-- 传统古建筑装饰 - 亭台楼阁 -->
  <g transform="translate({width*0.85}, 150)" opacity="0.4" filter="url(#brushStroke)">
    <!-- 屋顶 -->
    <path d="M-30,0 Q-20,-15 0,-12 Q20,-15 30,0 L25,5 L-25,5 Z" 
          fill="{colors['primary']}" opacity="0.7"/>
    <path d="M-25,5 L25,5 L20,15 L-20,15 Z" 
          fill="{colors['secondary']}" opacity="0.6"/>
    <!-- 柱子 -->
    <rect x="-20" y="15" width="5" height="25" fill="{colors['dark']}" opacity="0.8"/>
    <rect x="15" y="15" width="5" height="25" fill="{colors['dark']}" opacity="0.8"/>
    <!-- 基座 -->
    <rect x="-25" y="40" width="50" height="5" fill="{colors['accent']}" opacity="0.5"/>
  </g>
  
  <!-- 传统乐器装饰 - 古琴 -->
  <g transform="translate(100, {height*0.6})" opacity="0.5" filter="url(#inkBlur)">
    <ellipse cx="0" cy="0" rx="40" ry="8" fill="{colors['dark']}" opacity="0.6"/>
    <ellipse cx="0" cy="-2" rx="35" ry="6" fill="{colors['secondary']}" opacity="0.4"/>
    <!-- 琴弦 -->
    <line x1="-35" y1="-2" x2="35" y2="-2" stroke="{colors['primary']}" stroke-width="0.5"/>
    <line x1="-35" y1="0" x2="35" y2="0" stroke="{colors['primary']}" stroke-width="0.5"/>
    <line x1="-35" y1="2" x2="35" y2="2" stroke="{colors['primary']}" stroke-width="0.5"/>
    <!-- 琴码 -->
    <rect x="-10" y="-4" width="2" height="8" fill="{colors['energy']}" opacity="0.7"/>
    <rect x="10" y="-4" width="2" height="8" fill="{colors['energy']}" opacity="0.7"/>
  </g>
  
  <!-- 书法卷轴装饰 -->
  <g transform="translate({width*0.15}, {height*0.7})" opacity="0.6" filter="url(#classicalShadow)">
    <rect x="0" y="0" width="60" height="80" fill="{colors['bg']}" opacity="0.9" rx="3"/>
    <rect x="2" y="2" width="56" height="76" fill="{colors['light']}" opacity="0.7" rx="2"/>
    <!-- 书法文字装饰 -->
    <text x="30" y="20" text-anchor="middle" font-family="'STKaiti', '楷体', serif" 
          font-size="12" fill="{colors['dark']}" opacity="0.8">传</text>
    <text x="30" y="35" text-anchor="middle" font-family="'STKaiti', '楷体', serif" 
          font-size="12" fill="{colors['dark']}" opacity="0.8">承</text>
    <text x="30" y="50" text-anchor="middle" font-family="'STKaiti', '楷体', serif" 
          font-size="12" fill="{colors['dark']}" opacity="0.8">文</text>
    <text x="30" y="65" text-anchor="middle" font-family="'STKaiti', '楷体', serif" 
          font-size="12" fill="{colors['dark']}" opacity="0.8">化</text>
    <!-- 卷轴轴心 -->
    <circle cx="5" cy="40" r="3" fill="{colors['dark']}" opacity="0.6"/>
    <circle cx="55" cy="40" r="3" fill="{colors['dark']}" opacity="0.6"/>
  </g>
  
  <!-- 传统印章装饰 -->
  <g transform="translate({width*0.8}, {height*0.75})" filter="url(#classicalShadow)">
    <rect x="-30" y="-30" width="60" height="60" 
          fill="url(#sealGradient)" rx="8" opacity="0.9"/>
    <rect x="-25" y="-25" width="50" height="50" 
          fill="none" stroke="{colors['bg']}" stroke-width="2" rx="5"/>
    <text x="0" y="-5" text-anchor="middle" 
          font-family="'STKaiti', '楷体', 'KaiTi', serif" 
          font-size="14" font-weight="bold" 
          fill="{colors['bg']}">{brand_name[:2] if len(brand_name) >= 2 else brand_name}</text>
    <text x="0" y="15" text-anchor="middle" 
          font-family="'STKaiti', '楷体', 'KaiTi', serif" 
          font-size="10" font-weight="bold" 
          fill="{colors['bg']}">印</text>
  </g>
  
  <!-- 竹叶装饰 - 左下 -->
  <!-- 竹林装饰 - 左下 -->
  <g transform="translate(120, {height-180})" opacity="0.5" filter="url(#inkBlur)">
    <!-- 竹竿 -->
    <line x1="0" y1="0" x2="0" y2="-60" stroke="{colors['secondary']}" stroke-width="4"/>
    <line x1="15" y1="5" x2="15" y2="-55" stroke="{colors['secondary']}" stroke-width="3"/>
    <line x1="-12" y1="3" x2="-12" y2="-50" stroke="{colors['secondary']}" stroke-width="3"/>
    <!-- 竹节 -->
    <line x1="-3" y1="-20" x2="3" y2="-20" stroke="{colors['primary']}" stroke-width="2"/>
    <line x1="-3" y1="-40" x2="3" y2="-40" stroke="{colors['primary']}" stroke-width="2"/>
    <line x1="12" y1="-18" x2="18" y2="-18" stroke="{colors['primary']}" stroke-width="2"/>
    <line x1="12" y1="-35" x2="18" y2="-35" stroke="{colors['primary']}" stroke-width="2"/>
    <!-- 竹叶 -->
    <path d="M5,-15 Q15,-25 25,-15 Q15,-5 5,-15" fill="{colors['accent']}" opacity="0.7"/>
    <path d="M-8,-30 Q-18,-40 -8,-50 Q2,-40 -8,-30" fill="{colors['accent']}" opacity="0.7"/>
    <path d="M18,-25 Q28,-35 38,-25 Q28,-15 18,-25" fill="{colors['accent']}" opacity="0.7"/>
  </g>
  
  <!-- 梅兰竹菊装饰 - 右下 -->
  <g transform="translate({width-150}, {height-150})" opacity="0.6" filter="url(#brushStroke)">
    <!-- 梅花 -->
    <circle cx="0" cy="0" r="10" fill="{colors['energy']}" opacity="0.8"/>
    <circle cx="-15" cy="-10" r="8" fill="{colors['primary']}" opacity="0.7"/>
    <circle cx="15" cy="-10" r="8" fill="{colors['primary']}" opacity="0.7"/>
    <circle cx="-10" cy="15" r="8" fill="{colors['primary']}" opacity="0.7"/>
    <circle cx="10" cy="15" r="8" fill="{colors['primary']}" opacity="0.7"/>
    <line x1="0" y1="0" x2="0" y2="-40" stroke="{colors['dark']}" stroke-width="3"/>
    <!-- 兰花 -->
    <g transform="translate(40, -20)">
      <path d="M0,0 Q-5,-10 0,-20 Q5,-10 0,0" fill="{colors['secondary']}" opacity="0.6"/>
      <path d="M-3,-5 Q-8,-8 -3,-12 Q2,-8 -3,-5" fill="{colors['accent']}" opacity="0.7"/>
      <path d="M3,-5 Q8,-8 3,-12 Q-2,-8 3,-5" fill="{colors['accent']}" opacity="0.7"/>
    </g>
    <!-- 菊花 -->
    <g transform="translate(-40, 20)">
      <circle cx="0" cy="0" r="6" fill="{colors['energy']}" opacity="0.6"/>
      <path d="M0,-6 L0,-12 M6,0 L12,0 M0,6 L0,12 M-6,0 L-12,0" 
            stroke="{colors['primary']}" stroke-width="2" opacity="0.7"/>
      <path d="M4,-4 L8,-8 M4,4 L8,8 M-4,4 L-8,8 M-4,-4 L-8,-8" 
            stroke="{colors['secondary']}" stroke-width="1.5" opacity="0.6"/>
    </g>
  </g>
  
  <!-- 太极八卦装饰 - 右上角 -->
  <g transform="translate({width-200}, 120)" opacity="0.4" filter="url(#classicalShadow)">
    <circle cx="0" cy="0" r="25" fill="{colors['primary']}" opacity="0.6"/>
    <path d="M0,-25 A12.5,12.5 0 0,1 0,0 A12.5,12.5 0 0,0 0,25 A25,25 0 0,1 0,-25" 
          fill="{colors['bg']}" opacity="0.8"/>
    <circle cx="0" cy="-12.5" r="6" fill="{colors['bg']}" opacity="0.8"/>
    <circle cx="0" cy="12.5" r="6" fill="{colors['primary']}" opacity="0.8"/>
    <circle cx="0" cy="-12.5" r="2" fill="{colors['primary']}" opacity="0.8"/>
    <circle cx="0" cy="12.5" r="2" fill="{colors['bg']}" opacity="0.8"/>
  </g>
  
  <!-- 十二生肖装饰 - 鼠标主题 -->
  <g transform="translate(80, 180)" opacity="0.3" filter="url(#inkBlur)">
    <!-- 鼠的简化图案 -->
    <ellipse cx="0" cy="0" rx="12" ry="8" fill="{colors['secondary']}" opacity="0.7"/>
    <circle cx="-8" cy="-3" r="3" fill="{colors['primary']}" opacity="0.8"/>
    <circle cx="8" cy="-3" r="3" fill="{colors['primary']}" opacity="0.8"/>
    <circle cx="-6" cy="-4" r="1" fill="{colors['dark']}"/>
    <circle cx="6" cy="-4" r="1" fill="{colors['dark']}"/>
    <path d="M0,8 Q-3,12 -6,10 Q-3,8 0,8" fill="{colors['accent']}" opacity="0.6"/>
    <path d="M0,8 Q3,12 6,10 Q3,8 0,8" fill="{colors['accent']}" opacity="0.6"/>
  </g>
  
  <!-- 古典诗句装饰 -->
  <!-- 传统节日装饰 - 春联 -->
  <g transform="translate(50, {height*0.3})" opacity="0.4" filter="url(#brushStroke)">
    <rect x="0" y="0" width="15" height="120" fill="{colors['primary']}" opacity="0.8" rx="2"/>
    <text x="7.5" y="20" text-anchor="middle" font-family="'STKaiti', serif" 
          font-size="10" fill="{colors['bg']}" transform="rotate(0 7.5 20)">鼠</text>
    <text x="7.5" y="35" text-anchor="middle" font-family="'STKaiti', serif" 
          font-size="10" fill="{colors['bg']}" transform="rotate(0 7.5 35)">标</text>
    <text x="7.5" y="50" text-anchor="middle" font-family="'STKaiti', serif" 
          font-size="10" fill="{colors['bg']}" transform="rotate(0 7.5 50)">精</text>
    <text x="7.5" y="65" text-anchor="middle" font-family="'STKaiti', serif" 
          font-size="10" fill="{colors['bg']}" transform="rotate(0 7.5 65)">工</text>
    <text x="7.5" y="80" text-anchor="middle" font-family="'STKaiti', serif" 
          font-size="10" fill="{colors['bg']}" transform="rotate(0 7.5 80)">细</text>
    <text x="7.5" y="95" text-anchor="middle" font-family="'STKaiti', serif" 
          font-size="10" fill="{colors['bg']}" transform="rotate(0 7.5 95)">作</text>
  </g>
  
  <g transform="translate({width-65}, {height*0.3})" opacity="0.4" filter="url(#brushStroke)">
    <rect x="0" y="0" width="15" height="120" fill="{colors['primary']}" opacity="0.8" rx="2"/>
    <text x="7.5" y="20" text-anchor="middle" font-family="'STKaiti', serif" 
          font-size="10" fill="{colors['bg']}" transform="rotate(0 7.5 20)">科</text>
    <text x="7.5" y="35" text-anchor="middle" font-family="'STKaiti', serif" 
          font-size="10" fill="{colors['bg']}" transform="rotate(0 7.5 35)">技</text>
    <text x="7.5" y="50" text-anchor="middle" font-family="'STKaiti', serif" 
          font-size="10" fill="{colors['bg']}" transform="rotate(0 7.5 50)">传</text>
    <text x="7.5" y="65" text-anchor="middle" font-family="'STKaiti', serif" 
          font-size="10" fill="{colors['bg']}" transform="rotate(0 7.5 65)">承</text>
    <text x="7.5" y="80" text-anchor="middle" font-family="'STKaiti', serif" 
          font-size="10" fill="{colors['bg']}" transform="rotate(0 7.5 80)">文</text>
    <text x="7.5" y="95" text-anchor="middle" font-family="'STKaiti', serif" 
          font-size="10" fill="{colors['bg']}" transform="rotate(0 7.5 95)">化</text>
  </g>
  
  <!-- 古典诗句装饰 -->
  <text x="100" y="{height-100}" 
        font-family="'STKaiti', '楷体', 'KaiTi', serif" 
        font-size="16" 
        fill="{colors['primary']}" opacity="0.7">千年文化传承，一键精准操控</text>
  
  <text x="100" y="{height-80}" 
        font-family="'STKaiti', '楷体', 'KaiTi', serif" 
        font-size="14" 
        fill="{colors['secondary']}" opacity="0.6">古韵今风，匠心独运</text>
  
  <!-- 传统云纹装饰线 -->
  <path d="M{width*0.15},{height-60} Q{width*0.25},{height-70} {width*0.35},{height-60} Q{width*0.45},{height-50} {width*0.55},{height-60} Q{width*0.65},{height-70} {width*0.75},{height-60} Q{width*0.85},{height-50} {width*0.95},{height-60}" 
        fill="none" stroke="url(#chineseGradient)" stroke-width="3" opacity="0.6" filter="url(#brushStroke)"/>
  
  <!-- 传统装饰圆点和符号 -->
  <circle cx="{width*0.15}" cy="{height-60}" r="4" fill="{colors['energy']}" opacity="0.8"/>
  <circle cx="{width*0.85}" cy="{height-60}" r="4" fill="{colors['energy']}" opacity="0.8"/>
  <text x="{width*0.5}" y="{height-55}" text-anchor="middle" 
        font-family="'STKaiti', serif" font-size="12" 
        fill="{colors['primary']}" opacity="0.7">❋</text>
</svg>'''
        
        # 确保使用UTF-8编码写入文件
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            f.write(svg_content)
        
        return f"🏮 品牌广告封面已生成: {output_path} ({width}x{height}px, 古典中国风格, {colors['primary']}主色调)"
    except Exception as e:
        return f"生成封面时出现错误: {str(e)}"

@mcp.tool()
def slogan_gen(
    brand_name: str,
    product_type: str = "",
    brand_concept: str = "",
    style: str = "对联",
    rhyme_scheme: str = "平水韵"
) -> str:
    """
    生成古典格律体广告语，遵循传统诗词格律和韵律。
    
    参数说明：
    - brand_name: 品牌名称
    - product_type: 产品类型（如：科技产品、奢侈品、日用品等）
    - brand_concept: 品牌理念（如：创新、传承、品质等）
    - style: 格律风格（对联/七言绝句/五言绝句/词牌）
    - rhyme_scheme: 韵律体系（平水韵/词林正韵/中华新韵）
    """
    
    try:
        # 古典广告语创意库
        classical_templates = {
            "科技产品": {
                "对联": [
                    f"{brand_name}开启智慧门，科技创新惠万民",
                    f"一键{brand_name}通天下，智能时代入万家",
                    f"{brand_name}在手天下通，科技助力梦成功"
                ],
                "七言": [
                    f"{brand_name}一出天下知，智能科技展雄姿",
                    f"创新{brand_name}领风骚，科技兴邦志气高"
                ]
            },
            "AI产品": {
                "对联": [
                    f"{brand_name}慧眼识天机，人工智能助君行",
                    f"一朝{brand_name}入手来，智慧人生自然开",
                    f"{brand_name}伴君如良师，编程路上不迷离"
                ],
                "七言": [
                    f"{brand_name}助君编程路，智能伙伴解千愁",
                    f"代码千行{brand_name}成，程序人生更从容"
                ]
            },
            "编程工具": {
                "对联": [
                    f"{brand_name}在手码如飞，智能编程不用愁",
                    f"千行代码{brand_name}生，程序员的贴心朋",
                    f"一键{brand_name}解难题，编程路上好伙伴"
                ],
                "七言": [
                    f"{brand_name}相伴写春秋，代码人生更自由",
                    f"智能{brand_name}助开发，程序世界任遨游"
                ]
            }
        }
        
        # 根据品牌名和产品类型选择合适的模板
        category = "编程工具"
        if "AI" in brand_name.upper() or "智能" in brand_name:
            category = "AI产品"
        elif any(word in product_type for word in ["科技", "技术", "数码"]):
            category = "科技产品"
        elif any(word in brand_name for word in ["Code", "程序", "编程"]):
            category = "编程工具"
        
        # 获取对应的广告语模板
        templates = classical_templates.get(category, classical_templates["编程工具"])
        style_templates = templates.get(style, templates.get("对联", []))
        
        if not style_templates:
            style_templates = templates["对联"]
        
        # 选择最适合的广告语
        selected_slogan = style_templates[0] if style_templates else f"{brand_name}品质如山，信誉传千年"
        
        # 添加格律说明
        rhythm_note = ""
        if style == "对联":
            rhythm_note = "（对仗工整，平仄协调）"
        elif "七言" in style:
            rhythm_note = "（七言格律，韵律和谐）"
        elif "五言" in style:
            rhythm_note = "（五言古风，朗朗上口）"
        
        return f"""🏮 古典格律广告语已生成：

"{selected_slogan}"

格律风格：{style} {rhythm_note}
韵律体系：{rhyme_scheme}
品牌理念：传承古典文化，融合现代创新

💡 创意说明：
此广告语借鉴古典诗词的对偶、平仄和韵律特点，既保持了传统文化的韵味，
又体现了现代品牌的特色，朗朗上口，易于传播记忆。

古人云："文以载道，诗以言志"，好的广告语如诗如画，
能在瞬间打动人心，传承千年文化底蕴。"""
        
    except Exception as e:
        return f"生成古典格律广告语时出现错误: {str(e)}"

def pixel_cvr(brand_name, subtitle, slogan, colors, width, height, output_path):
    """生成像素风格的品牌广告封面 - 点阵式图像，清晰轮廓，明快色彩，卡通造型"""
    try:
        # 像素风格专用颜色调整 - 更鲜艳明快
        pixel_colors = {
            "primary": colors['primary'],
            "secondary": colors['secondary'], 
            "accent": colors['accent'],
            "light": colors['light'],
            "dark": colors['dark'],
            "text": colors['text'],
            "bg": "#F8F9FA",  # 像素风格背景
            "pixel_green": "#00FF00",  # 经典像素绿
            "pixel_blue": "#0080FF",   # 经典像素蓝
            "pixel_red": "#FF4040",    # 经典像素红
            "pixel_yellow": "#FFFF00", # 经典像素黄
            "pixel_purple": "#FF00FF", # 经典像素紫
            "pixel_cyan": "#00FFFF"    # 经典像素青
        }
        
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- 像素风格渐变 -->
    <linearGradient id="pixelBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{pixel_colors['bg']};stop-opacity:1" />
      <stop offset="50%" style="stop-color:#E3F2FD;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#F3E5F5;stop-opacity:1" />
    </linearGradient>
    
    <!-- 像素点阵图案 -->
    <pattern id="pixelGrid" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
      <rect width="20" height="20" fill="none" stroke="{pixel_colors['light']}" stroke-width="0.5" opacity="0.3"/>
      <rect x="8" y="8" width="4" height="4" fill="{pixel_colors['accent']}" opacity="0.2"/>
    </pattern>
    
    <!-- 像素风格滤镜 - 清晰边缘 -->
    <filter id="pixelSharp" x="0%" y="0%" width="100%" height="100%">
      <feColorMatrix type="saturate" values="1.5"/>
      <feComponentTransfer>
        <feFuncA type="discrete" tableValues="0 .5 1"/>
      </feComponentTransfer>
    </filter>
    
    <!-- 像素发光效果 -->
    <filter id="pixelGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  
  <!-- 背景 -->
  <rect width="{width}" height="{height}" fill="url(#pixelBg)" />
  
  <!-- 像素网格背景 -->
  <rect width="{width}" height="{height}" fill="url(#pixelGrid)" opacity="0.4" />
  
  <!-- 像素风格装饰边框 -->
  <rect x="40" y="40" width="{width-80}" height="{height-80}" 
        fill="none" stroke="{pixel_colors['primary']}" stroke-width="8" 
        opacity="0.8" filter="url(#pixelSharp)"/>
  <rect x="50" y="50" width="{width-100}" height="{height-100}" 
        fill="none" stroke="{pixel_colors['secondary']}" stroke-width="4" 
        opacity="0.6" filter="url(#pixelSharp)"/>
  
  <!-- 像素风格角落装饰 -->
  <!-- 左上角 -->
  <g filter="url(#pixelGlow)">
    <rect x="80" y="80" width="60" height="20" fill="{pixel_colors['pixel_green']}" opacity="0.9"/>
    <rect x="80" y="100" width="20" height="40" fill="{pixel_colors['pixel_green']}" opacity="0.9"/>
    <rect x="100" y="100" width="20" height="20" fill="{pixel_colors['pixel_yellow']}" opacity="0.8"/>
    <rect x="120" y="80" width="20" height="20" fill="{pixel_colors['pixel_yellow']}" opacity="0.8"/>
  </g>
  
  <!-- 右上角 -->
  <g filter="url(#pixelGlow)">
    <rect x="{width-140}" y="80" width="60" height="20" fill="{pixel_colors['pixel_blue']}" opacity="0.9"/>
    <rect x="{width-100}" y="100" width="20" height="40" fill="{pixel_colors['pixel_blue']}" opacity="0.9"/>
    <rect x="{width-120}" y="100" width="20" height="20" fill="{pixel_colors['pixel_cyan']}" opacity="0.8"/>
    <rect x="{width-140}" y="100" width="20" height="20" fill="{pixel_colors['pixel_cyan']}" opacity="0.8"/>
  </g>
  
  <!-- 左下角 -->
  <g filter="url(#pixelGlow)">
    <rect x="80" y="{height-120}" width="20" height="40" fill="{pixel_colors['pixel_red']}" opacity="0.9"/>
    <rect x="100" y="{height-100}" width="40" height="20" fill="{pixel_colors['pixel_red']}" opacity="0.9"/>
    <rect x="100" y="{height-120}" width="20" height="20" fill="{pixel_colors['pixel_purple']}" opacity="0.8"/>
    <rect x="120" y="{height-120}" width="20" height="20" fill="{pixel_colors['pixel_purple']}" opacity="0.8"/>
  </g>
  
  <!-- 右下角 -->
  <g filter="url(#pixelGlow)">
    <rect x="{width-100}" y="{height-120}" width="20" height="40" fill="{pixel_colors['pixel_yellow']}" opacity="0.9"/>
    <rect x="{width-140}" y="{height-100}" width="40" height="20" fill="{pixel_colors['pixel_yellow']}" opacity="0.9"/>
    <rect x="{width-120}" y="{height-120}" width="20" height="20" fill="{pixel_colors['pixel_green']}" opacity="0.8"/>
    <rect x="{width-140}" y="{height-120}" width="20" height="20" fill="{pixel_colors['pixel_green']}" opacity="0.8"/>
  </g>
  
  <!-- 像素风格游戏元素装饰 -->
  <!-- 8位风格小精灵 - 左侧 -->
  <g transform="translate(200, 300)" filter="url(#pixelGlow)">
    <!-- 身体 -->
    <rect x="0" y="0" width="40" height="40" fill="{pixel_colors['pixel_blue']}" opacity="0.9"/>
    <rect x="10" y="10" width="20" height="20" fill="{pixel_colors['pixel_cyan']}" opacity="0.8"/>
    <!-- 眼睛 -->
    <rect x="10" y="10" width="5" height="5" fill="{pixel_colors['dark']}" opacity="1"/>
    <rect x="25" y="10" width="5" height="5" fill="{pixel_colors['dark']}" opacity="1"/>
    <!-- 嘴巴 -->
    <rect x="15" y="25" width="10" height="5" fill="{pixel_colors['pixel_red']}" opacity="0.8"/>
    <!-- 手臂 -->
    <rect x="-10" y="15" width="10" height="10" fill="{pixel_colors['pixel_blue']}" opacity="0.7"/>
    <rect x="40" y="15" width="10" height="10" fill="{pixel_colors['pixel_blue']}" opacity="0.7"/>
  </g>
  
  <!-- 8位风格道具 - 右侧 -->
  <g transform="translate({width-250}, 350)" filter="url(#pixelGlow)">
    <!-- 宝石 -->
    <rect x="0" y="10" width="30" height="30" fill="{pixel_colors['pixel_purple']}" opacity="0.9"/>
    <rect x="5" y="5" width="20" height="20" fill="{pixel_colors['pixel_cyan']}" opacity="0.8"/>
    <rect x="10" y="0" width="10" height="10" fill="{pixel_colors['pixel_yellow']}" opacity="0.9"/>
    <rect x="10" y="40" width="10" height="10" fill="{pixel_colors['pixel_yellow']}" opacity="0.9"/>
    <!-- 光芒效果 -->
    <rect x="15" y="-5" width="2" height="60" fill="{pixel_colors['pixel_yellow']}" opacity="0.6"/>
    <rect x="-5" y="25" width="40" height="2" fill="{pixel_colors['pixel_yellow']}" opacity="0.6"/>
  </g>
  
  <!-- 像素风格代码符号 -->
  <g transform="translate(150, 200)" filter="url(#pixelSharp)">
    <!-- < 符号 -->
    <rect x="0" y="20" width="10" height="10" fill="{pixel_colors['primary']}" opacity="0.8"/>
    <rect x="10" y="10" width="10" height="10" fill="{pixel_colors['primary']}" opacity="0.8"/>
    <rect x="10" y="30" width="10" height="10" fill="{pixel_colors['primary']}" opacity="0.8"/>
    
    <!-- / 符号 -->
    <rect x="40" y="0" width="10" height="10" fill="{pixel_colors['secondary']}" opacity="0.8"/>
    <rect x="30" y="10" width="10" height="10" fill="{pixel_colors['secondary']}" opacity="0.8"/>
    <rect x="20" y="20" width="10" height="10" fill="{pixel_colors['secondary']}" opacity="0.8"/>
    <rect x="10" y="30" width="10" height="10" fill="{pixel_colors['secondary']}" opacity="0.8"/>
    <rect x="0" y="40" width="10" height="10" fill="{pixel_colors['secondary']}" opacity="0.8"/>
    
    <!-- > 符号 -->
    <rect x="60" y="20" width="10" height="10" fill="{pixel_colors['primary']}" opacity="0.8"/>
    <rect x="50" y="10" width="10" height="10" fill="{pixel_colors['primary']}" opacity="0.8"/>
    <rect x="50" y="30" width="10" height="10" fill="{pixel_colors['primary']}" opacity="0.8"/>
  </g>
  
  <!-- 主标题区域 - 像素风格 -->
  <g transform="translate({width//2}, {height*0.45})" filter="url(#pixelSharp)">
    <!-- 标题背景装饰 -->
    <rect x="-200" y="-40" width="400" height="80" fill="{pixel_colors['primary']}" opacity="0.1"/>
    <rect x="-190" y="-35" width="380" height="70" fill="{pixel_colors['secondary']}" opacity="0.1"/>
    
    <!-- 像素风格标题文字效果 -->
    <text x="0" y="0" text-anchor="middle" 
          font-family="'Courier New', 'Monaco', 'Consolas', monospace" 
          font-size="64" font-weight="bold" 
          fill="{pixel_colors['text']}" filter="url(#pixelGlow)">{brand_name}</text>
    
    <!-- 像素点装饰 -->
    <rect x="-220" y="-10" width="10" height="10" fill="{pixel_colors['pixel_green']}" opacity="0.8"/>
    <rect x="-220" y="5" width="10" height="10" fill="{pixel_colors['pixel_blue']}" opacity="0.8"/>
    <rect x="210" y="-10" width="10" height="10" fill="{pixel_colors['pixel_red']}" opacity="0.8"/>
    <rect x="210" y="5" width="10" height="10" fill="{pixel_colors['pixel_yellow']}" opacity="0.8"/>
  </g>'''
        
        if subtitle:
            svg_content += f'''
  
  <!-- 副标题 - 像素风格 -->
  <g transform="translate({width//2}, {height*0.55})" filter="url(#pixelSharp)">
    <text x="0" y="0" text-anchor="middle" 
          font-family="'Courier New', 'Monaco', 'Consolas', monospace" 
          font-size="32" font-weight="normal" 
          fill="{pixel_colors['secondary']}" filter="url(#pixelGlow)">{subtitle}</text>
    
    <!-- 装饰像素点 -->
    <rect x="-150" y="-5" width="8" height="8" fill="{pixel_colors['pixel_cyan']}" opacity="0.7"/>
    <rect x="142" y="-5" width="8" height="8" fill="{pixel_colors['pixel_purple']}" opacity="0.7"/>
  </g>'''
        
        if slogan:
            svg_content += f'''
  
  <!-- Slogan - 像素风格 -->
  <g transform="translate({width//2}, {height*0.65})" filter="url(#pixelSharp)">
    <text x="0" y="0" text-anchor="middle" 
          font-family="'Courier New', 'Monaco', 'Consolas', monospace" 
          font-size="20" font-weight="300" 
          fill="{pixel_colors['accent']}" filter="url(#pixelGlow)">{slogan}</text>
  </g>'''
        
        svg_content += f'''
  
  <!-- 像素风格游戏UI元素 -->
  <!-- 生命值条 -->
  <g transform="translate(100, {height-200})" filter="url(#pixelGlow)">
    <rect x="0" y="0" width="200" height="20" fill="{pixel_colors['dark']}" opacity="0.8"/>
    <rect x="5" y="5" width="190" height="10" fill="{pixel_colors['pixel_green']}" opacity="0.9"/>
    <rect x="5" y="5" width="150" height="10" fill="{pixel_colors['pixel_yellow']}" opacity="0.8"/>
    <rect x="5" y="5" width="100" height="10" fill="{pixel_colors['pixel_red']}" opacity="0.7"/>
    <!-- HP 文字 -->
    <text x="10" y="13" font-family="'Courier New', monospace" font-size="10" 
          fill="{pixel_colors['bg']}" font-weight="bold">HP</text>
  </g>
  
  <!-- 经验值条 -->
  <g transform="translate(100, {height-170})" filter="url(#pixelGlow)">
    <rect x="0" y="0" width="200" height="15" fill="{pixel_colors['dark']}" opacity="0.8"/>
    <rect x="5" y="5" width="190" height="5" fill="{pixel_colors['pixel_blue']}" opacity="0.9"/>
    <rect x="5" y="5" width="120" height="5" fill="{pixel_colors['pixel_cyan']}" opacity="0.8"/>
    <!-- EXP 文字 -->
    <text x="10" y="11" font-family="'Courier New', monospace" font-size="8" 
          fill="{pixel_colors['bg']}" font-weight="bold">EXP</text>
  </g>
  
  <!-- 像素风格按钮 -->
  <g transform="translate({width-300}, {height-200})" filter="url(#pixelGlow)">
    <!-- START 按钮 -->
    <rect x="0" y="0" width="120" height="40" fill="{pixel_colors['pixel_green']}" opacity="0.9"/>
    <rect x="5" y="5" width="110" height="30" fill="{pixel_colors['pixel_yellow']}" opacity="0.8"/>
    <text x="60" y="25" text-anchor="middle" 
          font-family="'Courier New', monospace" font-size="14" font-weight="bold" 
          fill="{pixel_colors['dark']}">START</text>
    
    <!-- SELECT 按钮 -->
    <rect x="0" y="50" width="120" height="40" fill="{pixel_colors['pixel_blue']}" opacity="0.9"/>
    <rect x="5" y="55" width="110" height="30" fill="{pixel_colors['pixel_cyan']}" opacity="0.8"/>
    <text x="60" y="75" text-anchor="middle" 
          font-family="'Courier New', monospace" font-size="14" font-weight="bold" 
          fill="{pixel_colors['dark']}">SELECT</text>
  </g>
  
  <!-- 像素风格星星装饰 -->
  <g filter="url(#pixelGlow)">
    <!-- 星星1 -->
    <g transform="translate(300, 150)">
      <rect x="10" y="0" width="10" height="10" fill="{pixel_colors['pixel_yellow']}" opacity="0.9"/>
      <rect x="0" y="10" width="30" height="10" fill="{pixel_colors['pixel_yellow']}" opacity="0.9"/>
      <rect x="10" y="20" width="10" height="10" fill="{pixel_colors['pixel_yellow']}" opacity="0.9"/>
      <rect x="5" y="5" width="5" height="5" fill="{pixel_colors['pixel_red']}" opacity="0.7"/>
      <rect x="20" y="5" width="5" height="5" fill="{pixel_colors['pixel_red']}" opacity="0.7"/>
      <rect x="5" y="15" width="5" height="5" fill="{pixel_colors['pixel_red']}" opacity="0.7"/>
      <rect x="20" y="15" width="5" height="5" fill="{pixel_colors['pixel_red']}" opacity="0.7"/>
    </g>
    
    <!-- 星星2 -->
    <g transform="translate({width-350}, 180)">
      <rect x="5" y="0" width="5" height="5" fill="{pixel_colors['pixel_purple']}" opacity="0.8"/>
      <rect x="0" y="5" width="15" height="5" fill="{pixel_colors['pixel_purple']}" opacity="0.8"/>
      <rect x="5" y="10" width="5" height="5" fill="{pixel_colors['pixel_purple']}" opacity="0.8"/>
    </g>
    
    <!-- 星星3 -->
    <g transform="translate(250, {height-300})">
      <rect x="5" y="0" width="5" height="5" fill="{pixel_colors['pixel_cyan']}" opacity="0.8"/>
      <rect x="0" y="5" width="15" height="5" fill="{pixel_colors['pixel_cyan']}" opacity="0.8"/>
      <rect x="5" y="10" width="5" height="5" fill="{pixel_colors['pixel_cyan']}" opacity="0.8"/>
    </g>
  </g>
  
  <!-- 像素风格底部装饰 -->
  <g transform="translate({width//2}, {height-100})" filter="url(#pixelGlow)">
    <!-- 像素化品牌标识 -->
    <rect x="-50" y="0" width="100" height="20" fill="{pixel_colors['primary']}" opacity="0.8"/>
    <rect x="-45" y="5" width="90" height="10" fill="{pixel_colors['secondary']}" opacity="0.7"/>
    <rect x="-40" y="7" width="80" height="6" fill="{pixel_colors['pixel_yellow']}" opacity="0.9"/>
    
    <!-- 像素点装饰 -->
    <rect x="-70" y="5" width="10" height="10" fill="{pixel_colors['pixel_green']}" opacity="0.8"/>
    <rect x="60" y="5" width="10" height="10" fill="{pixel_colors['pixel_red']}" opacity="0.8"/>
  </g>
  
  <!-- 像素风格代码装饰 -->
  <text x="80" y="{height-50}" 
        font-family="'Courier New', monospace" font-size="12" 
        fill="{pixel_colors['accent']}" opacity="0.7" filter="url(#pixelSharp)">
    console.log("Welcome to {brand_name} Pixel World!");
  </text>
  
  <!-- 像素风格版权信息 -->
  <text x="{width-200}" y="{height-30}" 
        font-family="'Courier New', monospace" font-size="10" 
        fill="{pixel_colors['secondary']}" opacity="0.6">
    © 2024 {brand_name} - Pixel Art Style
  </text>
</svg>'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return f"🎮 像素风格品牌广告封面已生成: {output_path} ({width}x{height}px, 像素风格, {colors['primary']}主色调)"
    except Exception as e:
        return f"生成像素风格封面时出现错误: {str(e)}"

def split_cvr(brand_name, subtitle, slogan, colors, width, height, output_path):
    """生成分屏式设计风格的品牌广告封面 - 将频幕一分为二甚至是 的网页设计方式，方便呈现不同的信息，创造对比"""
    try:
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- 震撼左侧渐变背景 -->
    <radialGradient id="leftGradient" cx="30%" cy="40%" r="120%">
      <stop offset="0%" style="stop-color:#FF1493;stop-opacity:1" />
      <stop offset="25%" style="stop-color:#8A2BE2;stop-opacity:0.95" />
      <stop offset="50%" style="stop-color:#4B0082;stop-opacity:0.9" />
      <stop offset="75%" style="stop-color:#2F4F4F;stop-opacity:0.85" />
      <stop offset="100%" style="stop-color:#000000;stop-opacity:0.8" />
    </radialGradient>
    
    <!-- 震撼右侧渐变背景 -->
    <radialGradient id="rightGradient" cx="70%" cy="60%" r="130%">
      <stop offset="0%" style="stop-color:#FFD700;stop-opacity:1" />
      <stop offset="20%" style="stop-color:#FF8C00;stop-opacity:0.98" />
      <stop offset="40%" style="stop-color:#FF4500;stop-opacity:0.95" />
      <stop offset="60%" style="stop-color:#DC143C;stop-opacity:0.9" />
      <stop offset="80%" style="stop-color:#8B0000;stop-opacity:0.85" />
      <stop offset="100%" style="stop-color:#2F1B14;stop-opacity:0.8" />
    </radialGradient>
    
    <!-- 中间分隔线渐变 -->
    <linearGradient id="dividerGradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:{colors['dark']};stop-opacity:0.1" />
      <stop offset="50%" style="stop-color:{colors['primary']};stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:{colors['dark']};stop-opacity:0.1" />
    </linearGradient>
    
    <!-- 文字阴影效果 -->
    <filter id="textShadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="2" dy="2" stdDeviation="2" flood-color="#000000" flood-opacity="0.3"/>
    </filter>
    
    <!-- 分隔线发光效果 -->
    <filter id="dividerGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
    
    <!-- 装饰元素效果 -->
    <filter id="decorationEffect" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feOffset dx="1" dy="1" result="offsetBlur"/>
      <feMerge>
        <feMergeNode in="offsetBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  
  <!-- 左侧背景 -->
  <rect x="0" y="0" width="{width//2}" height="{height}" fill="url(#leftGradient)" />
  
  <!-- 右侧背景 -->
  <rect x="{width//2}" y="0" width="{width//2}" height="{height}" fill="url(#rightGradient)" />
  
  <!-- 中间分隔线 -->
  <rect x="{width//2-2}" y="50" width="4" height="{height-100}" fill="url(#dividerGradient)" filter="url(#dividerGlow)" />
  
  <!-- 左侧装饰元素 -->
  <g transform="translate({width*0.25}, {height*0.3})" filter="url(#decorationEffect)">
    <circle cx="0" cy="0" r="60" fill="{colors['primary']}" opacity="0.2" />
    <circle cx="0" cy="0" r="40" fill="{colors['secondary']}" opacity="0.3" />
    <circle cx="0" cy="0" r="20" fill="{colors['primary']}" opacity="0.4" />
    
    <!-- 代码符号装饰 -->
    <text x="-30" y="10" font-family="'Courier New', monospace" font-size="36" 
          fill="{colors['primary']}" opacity="0.8">&lt;</text>
    <text x="10" y="10" font-family="'Courier New', monospace" font-size="36" 
          fill="{colors['primary']}" opacity="0.8">/&gt;</text>
  </g>
  
  <!-- 右侧装饰元素 -->
  <g transform="translate({width*0.75}, {height*0.3})" filter="url(#decorationEffect)">
    <rect x="-50" y="-50" width="100" height="100" rx="10" fill="{colors['accent']}" opacity="0.2" />
    <rect x="-35" y="-35" width="70" height="70" rx="8" fill="{colors['light']}" opacity="0.3" />
    <rect x="-20" y="-20" width="40" height="40" rx="5" fill="{colors['accent']}" opacity="0.4" />
    
    <!-- 图形符号装饰 -->
    <circle cx="-10" cy="-10" r="5" fill="{colors['energy']}" opacity="0.8" />
    <circle cx="10" cy="-10" r="5" fill="{colors['energy']}" opacity="0.8" />
    <circle cx="0" cy="10" r="5" fill="{colors['energy']}" opacity="0.8" />
  </g>
  
  <!-- 主标题 - 跨越两侧 -->
  <text x="{width//2}" y="{height*0.15}" text-anchor="middle" 
        font-family="'SF Pro Display', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif" 
        font-size="72" font-weight="700" 
        fill="{colors['text']}" filter="url(#textShadow)">{brand_name}</text>
  
  <!-- 左侧副标题 -->
  <text x="{width*0.25}" y="{height*0.5}" text-anchor="middle" 
        font-family="'SF Pro Display', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif" 
        font-size="36" font-weight="500" 
        fill="{colors['text']}" opacity="0.9" filter="url(#textShadow)">
    {subtitle.split(' ')[0] if subtitle and ' ' in subtitle else (subtitle if subtitle else '创新设计')}
  </text>
  
  <!-- 右侧副标题 -->
  <text x="{width*0.75}" y="{height*0.5}" text-anchor="middle" 
        font-family="'SF Pro Display', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif" 
        font-size="36" font-weight="500" 
        fill="{colors['text']}" opacity="0.9" filter="url(#textShadow)">
    {subtitle.split(' ')[1] if subtitle and ' ' in subtitle else '多栏体验'}
  </text>'''
        
        # 添加slogan（如果有）
        if slogan:
            svg_content += f'''
  
  <!-- Slogan - 跨越两侧 -->
  <text x="{width//2}" y="{height*0.65}" text-anchor="middle" 
        font-family="'SF Pro Display', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif" 
        font-size="24" font-weight="300" 
        fill="{colors['dark']}" opacity="0.8" filter="url(#textShadow)">{slogan}</text>'''
        
        # 添加左侧特性描述
        svg_content += f'''
  
  <!-- 左侧特性描述 -->
  <g transform="translate({width*0.25}, {height*0.75})">
    <text x="0" y="0" text-anchor="middle" 
          font-family="'SF Pro Display', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif" 
          font-size="18" font-weight="400" 
          fill="{colors['text']}" opacity="0.8">方便呈现不同的信息</text>
    <text x="0" y="30" text-anchor="middle" 
          font-family="'SF Pro Display', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif" 
          font-size="18" font-weight="400" 
          fill="{colors['text']}" opacity="0.8">创造视觉对比</text>
  </g>
  
  <!-- 右侧特性描述 -->
  <g transform="translate({width*0.75}, {height*0.75})">
    <text x="0" y="0" text-anchor="middle" 
          font-family="'SF Pro Display', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif" 
          font-size="18" font-weight="400" 
          fill="{colors['text']}" opacity="0.8">划分有效区域</text>
    <text x="0" y="30" text-anchor="middle" 
          font-family="'SF Pro Display', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif" 
          font-size="18" font-weight="400" 
          fill="{colors['text']}" opacity="0.8">方便用户快速选择</text>
  </g>
  
  <!-- 底部装饰线 - 左侧 -->
  <line x1="50" y1="{height-50}" x2="{width//2-20}" y2="{height-50}" 
        stroke="{colors['primary']}" stroke-width="3" opacity="0.6" />
  
  <!-- 底部装饰线 - 右侧 -->
  <line x1="{width//2+20}" y1="{height-50}" x2="{width-50}" y2="{height-50}" 
        stroke="{colors['accent']}" stroke-width="3" opacity="0.6" />
  
  <!-- 底部品牌标识 - 左侧 -->
  <circle cx="80" cy="{height-50}" r="6" fill="{colors['primary']}" opacity="0.8" />
  
  <!-- 底部品牌标识 - 右侧 -->
  <circle cx="{width-80}" cy="{height-50}" r="6" fill="{colors['accent']}" opacity="0.8" />
  
  <!-- 底部版权信息 -->
  <text x="{width//2}" y="{height-20}" text-anchor="middle" 
        font-family="'SF Pro Display', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif" 
        font-size="14" font-weight="300" 
        fill="{colors['dark']}" opacity="0.6">© 2024 {brand_name} - 分屏式设计</text>
</svg>'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return f"🖥️ 品牌广告封面已生成: {output_path} ({width}x{height}px, 分屏式设计风格, {colors['primary']}主色调)"
    except Exception as e:
        return f"生成封面时出现错误: {str(e)}"

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """
    根据提供的名称，获取一句个性化的问候语。
    """
    return f"Hello, {name}!"

if __name__ == "__main__":
    import sys
    
    # 打印当前工作目录
    print(f"当前工作目录: {os.getcwd()}", file=sys.stderr)
    
    # 打印已注册的工具
    print("已注册的工具:", file=sys.stderr)
    print("- generate_brand_ad_cover", file=sys.stderr)
    print("- generate_classical_chinese_slogan", file=sys.stderr)
    print("MCP服务器启动中...", file=sys.stderr)
    
    try:
        import asyncio
        asyncio.run(mcp.run())
    except KeyboardInterrupt:
        print("MCP服务器已停止", file=sys.stderr)
    except Exception as e:
        print(f"MCP服务器错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
