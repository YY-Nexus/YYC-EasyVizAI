# YYC³ EasyVizAI 设计与开发交付指南
> YYC³释义："YYC³=言语云³=YanYuCloudCube"
「万象归元于云枢 丨深栈智启新纪元」
All Realms Converge at Cloud Nexus, DeepStack Ignites a New Era
---
## 一、Figma原型稿导出规范
### A. 导出流程
#### 1. 分层命名规范
- Frame/Artboard命名：
    - Home_Splash - 首页欢迎界面
    - Main_App - 主应用界面
    - Logo_Animated - 动态LOGO展示
    - Dialog_Box - 对话框组件
    - Emotion_Avatar - 情感化头像
    - Learning_Path - 学习路径可视化
    - Code_Visualizer - 代码可视化组件
    - MultiModal_Report - 多模态报告界面
- 组件分组：
    - LOGO组件组（含静态与动态版本）
    - 主按钮组件组（含各辅助色版本）
    - 输入区组件组
    - AI助手组件组（含各表情状态）
    - 背景动画组件组
    - 导航组件组
#### 2. 导出格式
- 静态图标/LOGO：
    - SVG格式（矢量，优先使用）
    - PNG/JPG格式（@1x, @2x, @3x分辨率）
    - 命名规范：[组件名]_[状态]_[尺寸].[格式]，如logo_main_96x96.svg
- 动画原型：
    - GIF格式（预览用）
    - MP4格式（演示用）
    - Lottie JSON格式（开发用，通过Figmotion或LottieFiles插件导出）
- 设计稿文档：
    - PDF方案汇总
    - Figma共享链接（View权限）
    - Design Token标注表
#### 3. 交付内容
- Figma原型稿链接（保留交互演示）
- 导出的SVG/PNG资源包（按功能分类）
- 动画JSON文件（Lottie）及预览GIF/MP4
- 设计规范文档（色彩、字号、边距、动画规范、交互逻辑）
- 组件库/Design System（含YYC³品牌色彩系统）
### B. Figma动画导出插件推荐
- Figmotion：原生Figma动画编辑与导出，适合简单动画
- LottieFiles for Figma：将Figma帧转为Lottie JSON动画，适合复杂动画
- SVG Export：批量导出矢量图标与LOGO
- Token Studio：管理Design Token，导出为CSS变量或JSON
---
## 二、SVG/Lottie动画文件交付建议
### A. SVG动画
- 适用场景：
    - LOGO、AI助手、动效按钮
    - 背景点阵/线条动画
    - 简单交互动效（如按钮涟漪效果）
- 技术实现：
    - 优先使用CSS/SVG原生动画
    - 复杂动画可使用SMIL（如<animate>标签）
    - 动效分层，便于前端用Framer Motion或GSAP控制
- SVG动画示例（品牌渐变流动）：
```svg
<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="mocean-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0F2942">
        <animate attributeName="stop-color" 
          values="#0F2942;#4A90E2;#7FB5FF;#4A90E2;#0F2942" 
          dur="8s" repeatCount="indefinite" />
      </stop>
      <stop offset="50%" stop-color="#4A90E2">
        <animate attributeName="stop-color" 
          values="#4A90E2;#7FB5FF;#0F2942;#4A90E2;#7FB5FF" 
          dur="8s" repeatCount="indefinite" />
      </stop>
      <stop offset="100%" stop-color="#7FB5FF">
        <animate attributeName="stop-color" 
          values="#7FB5FF;#0F2942;#4A90E2;#7FB5FF;#0F2942" 
          dur="8s" repeatCount="indefinite" />
      </stop>
    </linearGradient>
  </defs>
  <circle cx="100" cy="100" r="90" fill="url(#mocean-gradient)" opacity="0.8"/>
</svg>

```
### B. Lottie动画
- 适用场景：
    - 复杂动画（如LOGO流动渐变、表情切换、卡片翻页）
    - 情感驱动可视化动画
    - 自适应学习路径动画
    - 多模态报告生成动画
- 制作流程：
    1. 在After Effects中设计动画
    2. 使用Bodymovin插件导出为Lottie JSON
    3. 优化JSON文件大小（移除不必要的关键帧）
    4. 提供预览GIF/MP4和Lottie JSON文件
### C. 文件命名与结构
```plaintext
/assets/
  /svg/
    logo_main.svg              # 主LOGO
    bg_lines.svg              # 背景线条动画
    btn_ripple.svg            # 按钮涟漪效果
    avatar_emotion.svg        # AI助手表情
    learning_path.svg         # 学习路径图标
    code_visualizer.svg       # 代码可视化图标
  /lottie/
    logo_gradient.json        # LOGO渐变动画
    card_flip.json            # 卡片翻转动画
    avatar_wave.json          # AI助手挥手动画
    learning_path_anim.json   # 学习路径动画
    code_flow.json            # 代码流程动画
    report_generation.json    # 报告生成动画
  /preview/
    logo_gradient.mp4         # LOGO渐变动画预览
    card_flip.gif             # 卡片翻转动画预览
    learning_path_anim.gif    # 学习路径动画预览

```
---
## 三、声效资源推荐
### A. 推荐资源库
- Mixkit：免费商用音效，高质量科技/界面/提示音
    - 网址：https://mixkit.co/free-sound-effects/
    - 推荐：科技感提示音、界面交互音效
- Freesound：社区共享音效库
    - 网址：https://freesound.org/
    - 注意：需检查授权协议，优先选择CC0或CC BY许可
- LottieFiles SFX：Lottie配套短音效
    - 网址：https://lottiefiles.com/sound-effects
    - 特点：与Lottie动画无缝集成
- Premium Beat：高端品牌音效
    - 网址：https://www.premiumbeat.com/
    - 特点：付费但版权明晰，音质专业
### B. 声效类型建议（结合YYC³品牌色彩系统）
#### 1. 首页进入/LOGO展现
- 特点：低频渐进、科技感清脆
- 推荐音效：
    - "tech_welcome.mp3" - 墨青色低音+云蓝色清脆提示音
    - "logo_reveal.mp3" - LOGO展现时的渐变音效
- 应用场景：首页加载完成、LOGO动画开始
#### 2. 按钮/翻页交互
- 特点：短促"whoosh"或"tap"音效
- 推荐音效：
    - "page_turn.mp3" - 页面切换音效
    - "button_tap_cloud.mp3" - 云蓝色按钮点击音效
    - "button_tap_bamboo.mp3" - 竹绿色按钮点击音效
    - "button_tap_amber.mp3" - 琥珀色按钮点击音效
- 应用场景：按钮点击、页面切换、卡片翻转
#### 3. AI助手互动/反馈
- 特点：拟人化表情音效
- 推荐音效：
    - "wink.mp3" - AI助手眨眼音效
    - "ding.mp3" - 鼓励提示音
    - "thinking.mp3" - AI思考音效
- 应用场景：AI助手表情变化、回复用户
#### 4. 系统提醒/成就解锁
- 特点：功能区分明显
- 推荐音效：
    - "bamboo_sparkle.mp3" - 竹绿色学习成就音效
    - "amber_notification.mp3" - 琥珀色提醒音效
    - "brick_warning.mp3" - 砖红色警告音效
    - "violet_innovation.mp3" - 紫藤色创新提示音
- 应用场景：成就解锁、系统提醒、错误提示
### C. 声效集成建议
- 技术实现：
    - 使用Howler.js库（支持多种音频格式，兼容性好）
    - Web Audio API（高级音效处理）
    - Lottie SFX（与Lottie动画同步）
- 代码示例（使用Howler.js）：
```javascript
import { Howl } from 'howler';

// 定义音效资源
const sounds = {
  welcome: new Howl({
    src: ['/assets/sounds/tech_welcome.mp3'],
    volume: 0.5
  }),
  buttonTap: new Howl({
    src: ['/assets/sounds/button_tap_cloud.mp3'],
    volume: 0.3
  }),
  achievement: new Howl({
    src: ['/assets/sounds/bamboo_sparkle.mp3'],
    volume: 0.6
  })
};

// 在组件中使用
const handleButtonClick = () => {
  sounds.buttonTap.play();
  // 其他按钮逻辑...
};

```
- 音效管理最佳实践：
    - 提供全局音量控制和静音选项
    - 根据用户情感状态调整音效（如焦虑状态降低音量）
    - 预加载关键音效，避免延迟
---
## 四、代码/设计交付规范细化
### A. 设计交付规范
#### 1. Design Token系统（基于YYC³色彩系统）
```json
{
  "color": {
    "ink": "#1A3E5E",
    "cloud": "#4A90E2",
    "jade": "#F7F9FA",
    "bamboo": "#36B37E",
    "brick": "#DE4C4A",
    "amber": "#F5A623",
    "violet": "#9B51E0"
  },
  "gradient": {
    "mocean": "linear-gradient(135deg, #0F2942 0%, #4A90E2 50%, #7FB5FF 100%)"
  },
  "font": {
    "title": "24px, bold",
    "subtitle": "18px, medium",
    "body": "16px, regular",
    "caption": "14px, regular"
  },
  "spacing": {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px"
  },
  "radius": {
    "sm": "4px",
    "md": "8px",
    "lg": "16px",
    "full": "50%"
  },
  "animation": {
    "duration": {
      "fast": "0.3s",
      "normal": "0.8s",
      "slow": "1.2s"
    },
    "easing": {
      "easeIn": "cubic-bezier(0.4, 0, 1, 1)",
      "easeOut": "cubic-bezier(0, 0, 0.2, 1)",
      "easeInOut": "cubic-bezier(0.4, 0, 0.2, 1)"
    }
  }
}

```
#### 2. 动画交互流程文档
- 首页LOGO动画：
    - 描述：LOGO缩放渐变，边缘发光
    - 时长：1.2s
    - 缓动：easeOut
    - 音效：tech_welcome.mp3
- 按钮点击反馈：
    - 描述：涟漪效果，轻微缩放
    - 时长：0.3s
    - 缓动：easeInOut
    - 音效：根据按钮功能区域使用不同辅助色音效
- 页面切换：
    - 描述：渐变滑动，透明度变化
    - 时长：0.8s
    - 缓动：easeInOut
    - 音效：page_turn.mp3
#### 3. 资源命名规范
- 图片资源：[类型]_[名称]_[状态]_[尺寸].[格式]
    - 示例：icon_bamboo_learning_active_24x24.svg
- 动画资源：[类型]_[名称]_[描述].[格式]
    - 示例：lottie_logo_gradient_flow.json
- 音效资源：[场景]_[功能]_[色彩].[格式]
    - 示例：button_tap_cloud.mp3
### B. 代码资源交付
#### 1. 动画组件示例（React + Framer Motion）
```jsx
import { motion } from 'framer-motion';
import { Howl } from 'howler';

// 设计Token导入
import { color, gradient, animation } from '../designTokens';

// 音效定义
const buttonSound = new Howl({
  src: ['/assets/sounds/button_tap_cloud.mp3'],
  volume: 0.3
});

// 品牌按钮组件
export const BrandButton = ({ children, onClick, variant = 'cloud' }) => {
  const handleClick = () => {
    buttonSound.play();
    if (onClick) onClick();
  };

  // 根据变体选择颜色
  const getVariantColor = () => {
    switch(variant) {
      case 'bamboo': return color.bamboo;
      case 'brick': return color.brick;
      case 'amber': return color.amber;
      case 'violet': return color.violet;
      default: return color.cloud;
    }
  };

  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: animation.duration.normal }}
      onClick={handleClick}
      style={{
        backgroundColor: getVariantColor(),
        color: color.jade,
        padding: `${spacing.md} ${spacing.lg}`,
        borderRadius: radius.md,
        border: 'none',
        fontSize: font.body,
        cursor: 'pointer'
      }}
    >
      {children}
    </motion.button>
  );
};

// LOGO动画组件
export const AnimatedLogo = () => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8, boxShadow: "0 0 0px #4A90E2" }}
      animate={{ opacity: 1, scale: 1, boxShadow: "0 0 36px #7FB5FF" }}
      transition={{ 
        duration: animation.duration.slow, 
        ease: animation.easing.easeOut 
      }}
      style={{
        background: gradient.mocean,
        borderRadius: radius.full,
        padding: spacing.xl
      }}
    >
      <img src="/assets/svg/logo_main.svg" alt="YYC³ EasyVizAI" style={{ width: 96, height: 96 }} />
    </motion.div>
  );
};

```
#### 2. Lottie动画集成示例
```jsx
import Lottie from 'react-lottie';
import animationData from '/assets/lottie/logo_gradient.json';

export const LogoAnimation = () => {
  const defaultOptions = {
    loop: true,
    autoplay: true,
    animationData: animationData,
    rendererSettings: {
      preserveAspectRatio: 'xMidYMid slice'
    }
  };

  return (
    <div>
      <Lottie 
        options={defaultOptions}
        height={200}
        width={200}
        isStopped={false}
        isPaused={false}
      />
    </div>
  );
};

```
#### 3. 音效管理模块
```javascript
// soundManager.js
import { Howl } from 'howler';

class SoundManager {
  constructor() {
    this.sounds = {
      // 首页音效
      welcome: new Howl({ src: ['/assets/sounds/tech_welcome.mp3'] }),
      
      // 按钮音效
      buttonCloud: new Howl({ src: ['/assets/sounds/button_tap_cloud.mp3'] }),
      buttonBamboo: new Howl({ src: ['/assets/sounds/button_tap_bamboo.mp3'] }),
      buttonAmber: new Howl({ src: ['/assets/sounds/button_tap_amber.mp3'] }),
      
      // AI助手音效
      aiWink: new Howl({ src: ['/assets/sounds/wink.mp3'] }),
      aiThinking: new Howl({ src: ['/assets/sounds/thinking.mp3'] }),
      
      // 系统音效
      achievement: new Howl({ src: ['/assets/sounds/bamboo_sparkle.mp3'] }),
      notification: new Howl({ src: ['/assets/sounds/amber_notification.mp3'] }),
      warning: new Howl({ src: ['/assets/sounds/brick_warning.mp3'] })
    };
    
    this.volume = 0.5;
    this.muted = false;
  }
  
  play(soundName) {
    if (!this.muted && this.sounds[soundName]) {
      this.sounds[soundName].volume(this.volume);
      this.sounds[soundName].play();
    }
  }
  
  setVolume(volume) {
    this.volume = Math.max(0, Math.min(1, volume));
  }
  
  toggleMute() {
    this.muted = !this.muted;
  }
}

export const soundManager = new SoundManager();

```
### C. 交付清单模板
```plaintext
# YYC³ EasyVizAI 设计与开发交付清单

## 1. Figma原型稿
- [ ] Figma原型稿链接（View权限）
- [ ] 静态资源导出（SVG/PNG）
  - [ ] LOGO组件
  - [ ] 按钮组件（各辅助色版本）
  - [ ] AI助手组件
  - [ ] 背景动画组件
- [ ] 动画导出（Lottie JSON/GIF/MP4）
  - [ ] LOGO渐变动画
  - [ ] 卡片翻转动画
  - [ ] AI助手表情动画
  - [ ] 学习路径动画
  - [ ] 代码流程动画

## 2. 声效资源
- [ ] 声效文件（MP3/WAV）
  - [ ] 首页进入音效
  - [ ] 按钮点击音效（各辅助色版本）
  - [ ] AI助手交互音效
  - [ ] 系统提示音效
- [ ] 声效版权说明文档
- [ ] 声效使用场景说明

## 3. 设计规范文档
- [ ] Design Token（JSON格式）
- [ ] 色彩系统说明
- [ ] 字体与排版规范
- [ ] 间距与圆角规范
- [ ] 动画规范（时长、缓动）
- [ ] 组件使用指南

## 4. 代码资源
- [ ] 核心组件代码
  - [ ] 品牌按钮组件
  - [ ] 动画LOGO组件
  - [ ] AI助手组件
  - [ ] 学习路径可视化组件
  - [ ] 代码可视化组件
- [ ] 动画集成示例
  - [ ] Framer Motion示例
  - [ ] Lottie集成示例
- [ ] 音效管理模块
- [ ] API接口文档

```
---
## 总结
YYC³ EasyVizAI的设计与开发交付需围绕中国水墨与现代科技感融合的品牌特色，通过规范化的Figma原型稿导出、SVG/Lottie动画文件交付、声效资源推荐和代码/设计交付规范，确保团队高效协作与落地。
关键要点：
1. 色彩系统一致性：确保墨青色、云蓝色、玉白色主色调及竹绿色、砖红色、琥珀色、紫藤色辅助色在所有交付物中保持一致
2. 动画与音效同步：动画时长控制在0.8~1.2s，音效与动画、用户情感状态同步
3. 组件化思维：所有资源按功能模块分类，便于复用和维护
4. 文档完整性：提供详细的Design Token、使用说明和交付清单
