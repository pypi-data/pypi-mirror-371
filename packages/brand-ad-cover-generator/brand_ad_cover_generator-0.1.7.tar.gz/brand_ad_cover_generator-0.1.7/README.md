# 品牌广告封面生成器 MCP 工具

一个基于 MCP 协议的品牌广告封面生成工具，能够根据品牌名称、风格和颜色自动生成高质量的SVG矢量广告封面。

## 🎨 核心功能

### 品牌广告封面生成器

- **工具名**: `brand_cover_generator`
- **功能**: 根据品牌名称生成精美的广告封面
- **支持风格**: 简约/科技/古典中国风/像素风格/分屏式设计
- **支持颜色**: 蓝色/紫色/绿色/红色/橙色/大红/水绿/蓝灰/黑灰
- **输出格式**: SVG矢量图形

### 古典中文标语生成器
- **工具名**: `classical_slogan_generator`
- **功能**: 生成古典格律体广告语，遵循传统诗词格律和韵律
- **支持格律**: 对联/七言绝句/五言绝句/词牌
- **韵律体系**: 平水韵/词林正韵/中华新韵
- **输出格式**: 文本格式


- **工具名**: `generate_brand_ad_cover`
- **功能**: 根据品牌名称生成精美的广告封面
- **支持风格**: 简约/科技
- **支持颜色**: 蓝色/紫色/绿色/红色/橙色
- **输出格式**: SVG矢量图形


## 🚀 使用方法

### 通过JSON配置使用

在支持MCP的环境中，可以通过以下JSON配置使用本工具：

```json
{
  "mcpServers": {
    "generate-brand-ad-cover-mcp": {
      "command": "uvx",
      "args": [
        "--index-url",
        "https://pypi.tuna.tsinghua.edu.cn/simple",
        "generate-brand-ad-cover"
      ]
    }
  }
}
```

### 直接启动服务器

1. 启动 MCP 服务器：
```bash
python run_mcp.py
```

或者安装后使用：
```bash
python -m mcp_plus
```

2. 通过 MCP 客户端调用工具：


```python
# 生成品牌广告封面
generate_brand_ad_cover(
    brand_name="CodeBuddy",
    subtitle="AI编程伙伴",
    slogan="智能代码生成 · 高效开发体验",
    style="简约",  # 可选：简约/科技/古典中国风/像素风格/分屏式设计
    primary_color="蓝色",  # 可选：蓝色、紫色、绿色、红色、橙色、大红、水绿、蓝灰、黑灰
    width=1080,
    height=1080,
    output_path="my_brand_cover.svg"
)

# 生成古典中文标语
generate_classical_chinese_slogan(
    brand_name="太极编程",
    product_type="科技产品",
    brand_concept="创新",
    style="对联",  # 可选：对联/七言绝句/五言绝句/词牌
    rhyme_scheme="平水韵"  # 可选：平水韵/词林正韵/中华新韵
)
```

### 各风格特色示例

```python
# 古典中国风 - 适合传统文化品牌
generate_brand_ad_cover(
    brand_name="墨韵书院",
    subtitle="传承千年文化",
    slogan="笔墨纸砚 · 诗书礼乐",
    style="古典中国风",
    primary_color="大红"
)

# 像素风格 - 适合游戏和科技品牌
generate_brand_ad_cover(
    brand_name="像素工坊",
    subtitle="8位游戏时代",
    slogan="复古像素 · 创意无限",
    style="像素风格",
    primary_color="绿色"
)

# 分屏式设计 - 适合产品对比展示
generate_brand_ad_cover(
    brand_name="双屏体验",
    subtitle="信息分层展示",
    slogan="左右对比 · 一目了然",
    style="分屏式设计",
    primary_color="蓝灰"

```python
# 生成品牌广告封面
generate_brand_ad_cover(
    brand_name="CodeBuddy",
    subtitle="AI编程伙伴",
    slogan="智能代码生成 · 高效开发体验",
    style="简约",  # 或 "科技"
    primary_color="蓝色",  # 可选：蓝色、紫色、绿色、红色、橙色
    width=1080,
    height=1080,
    output_path="my_brand_cover.svg"

)
```

## 📁 项目结构

```
├── run_mcp.py                       # MCP 服务器启动脚本
├── src/
│   └── mcp_plus/
│       ├── __init__.py              # 主要功能实现
│       ├── __main__.py              # 模块入口点
│       └── server_impl.py           # MCP 服务器实现
├── codebuddy_brand_cover.svg        # 示例：品牌封面
├── codebuddy_simple_cover.svg       # 示例：简约风格封面
├── pyproject.toml                   # 项目配置
└── README.md                        # 项目说明
```

## 🎯 设计理念

- **多样化风格**: 支持从简约到艺术的多种设计风格
- **智能配色**: 基于色彩理论的专业配色方案
- **矢量输出**: 生成高质量的 SVG 矢量图形
- **现代适配**: 完美适配各大主流平台规范
- **艺术感**: 融入印象派、抽象表现等艺术元素

- **文化融合**: 古典中国风与现代设计的完美结合
- **创新布局**: 分屏式设计创造视觉对比和信息分层
- **怀旧美学**: 像素风格重现经典游戏时代的视觉魅力

## 🎨 新增设计风格

### 古典中国风格
- **特色**: 展现深厚中华文化底蕴
- **元素**: 传统纹样、书法字体、水墨效果
- **配色**: 朱红、墨绿、金黄等传统色彩
- **适用**: 文化品牌、传统企业、艺术项目

### 像素风格
- **特色**: 点阵式图像，清晰轮廓，明快色彩
- **元素**: 8位游戏风格、卡通造型、复古色调
- **配色**: 高对比度、饱和色彩
- **适用**: 游戏品牌、科技产品、创意项目

### 分屏式设计
- **特色**: 将屏幕一分为二的网页设计方式
- **元素**: 对比布局、信息分层、视觉平衡
- **配色**: 互补色彩、渐变过渡
- **适用**: 产品对比、功能展示、品牌理念阐述


## 🔧 技术特点

- 基于 FastMCP 框架，支持回退到自定义MCP实现
- 纯 Python 实现，无外部依赖
- SVG 矢量图形输出
- 支持自定义尺寸和配色
- 丰富的滤镜和渐变效果

## 📝 示例输出


项目包含多种不同风格的示例封面：

项目包含两个不同风格的示例封面：
1. **简约风格** - 清新现代的简约设计，浅色背景
2. **科技风格** - 霓虹光效的现代科技风格，深色背景


### 设计风格示例
1. **简约风格** - 清新现代的简约设计，浅色背景
2. **科技风格** - 霓虹光效的现代科技风格，深色背景
3. **古典中国风** - 传统文化元素，朱红金黄配色
4. **像素风格** - 8位游戏风格，点阵图像效果
5. **分屏式设计** - 左右分屏布局，信息对比展示


### 生成的示例文件
- `codebuddy_brand_cover.svg` - CodeBuddy品牌封面
- `lantern_chinese_classical_cover.svg` - 灯笼古典风格封面
- `taiji_split_screen_cover.svg` - 太极分屏式设计封面
- `dungeon_pixel_fixed.svg` - 地牢像素风格封面
- `table_shocking_cover.svg` - 震撼风格封面

### 古典标语示例
通过 `generate_classical_chinese_slogan` 工具可生成如下格律标语：
- **对联风格**: "代码如诗韵律美，程序似画意境深"
- **七言绝句**: "智能编程展新颜，代码生花不等闲"
- **五言绝句**: "代码生花，智能无涯"

每个封面都展现了不同的设计理念和视觉效果，可作为实际项目的参考模板。

## 效果图展示
### 1.简约风格


![输入图片说明](666fa492111b2ec850470fa30ec05158.png)

### 2.科技风格

![输入图片说明](2dc5d2ed06a9b708f7fecd4e75768576.png)

### 3.古典中国风


![输入图片说明](dc7d3d3357bfd93a7343f1964f2218f6.png)



### 4.像素风格

![输入图片说明](a87d7826ac6d1ed0a2f4f40c8cc7d51d.png)

### 5.分屏式设计 

![输入图片说明](38007ac19277c5826e4ab7be8e63e33b.png)